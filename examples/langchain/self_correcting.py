# File: /examples/langchain/self_correcting.py

import os

# LangChain & ChatOpenAI (with explicit API key)
from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

# Bumpers
from bumpers.core.engine import CoreValidationEngine, ValidationPoint
from bumpers.validators.base import BaseValidator, FailStrategy
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.types import ValidationResult
from bumpers.integrations.self_correcting_callback import SelfCorrectingLangChainCallback

# --------------------------------------------------------------------------
# 1) Provide your OpenAI API key to ChatOpenAI to avoid the KeyError
# --------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")


# --------------------------------------------------------------------------
# 2) Example Tools
# --------------------------------------------------------------------------
@tool
def execute_command(cmd: str) -> str:
    """Simulates executing a system command."""
    return f"COMMAND HERE: Executed: {cmd}"

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


# --------------------------------------------------------------------------
# 3) Example Validator => triggers SELF_CORRECT if user tries "rm -rf /"
# --------------------------------------------------------------------------
class NoDangerousCommandsValidator(BaseValidator):
    def __init__(self, name="no_dangerous_commands"):
        super().__init__(name=name, fail_strategy=FailStrategy.SELF_CORRECT)

    def validate(self, context: dict) -> ValidationResult:
        action = context.get("action", "")
        action_input = context.get("action_input", "")
        if action == "execute_command" and "rm -rf /" in str(action_input).lower():
            return ValidationResult(
                passed=False,
                message="Attempted to run a dangerous command (rm -rf /).",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context,
                fail_strategy=self.fail_strategy,
            )
        return ValidationResult(
            passed=True,
            message="No dangerous commands found.",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context,
            fail_strategy=self.fail_strategy,
        )


# --------------------------------------------------------------------------
# 4) Build the LLM + Agent
# --------------------------------------------------------------------------
def build_agent():
    # Pass the explicit API key. If you have it set in an environment variable,
    # you'll want to do:
    #     openai_api_key=os.environ["OPENAI_API_KEY"]
    # or a fallback approach as shown here:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )

    tools = [execute_command, get_word_length]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    pipeline = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm.bind_tools(tools)
        | OpenAIToolsAgentOutputParser()
    )

    return AgentExecutor(agent=pipeline, tools=tools, verbose=True)


# --------------------------------------------------------------------------
# 5) Build the Validation Engine
# --------------------------------------------------------------------------
def build_validation_engine():
    engine = CoreValidationEngine()

    # Whitelist both => won't STOP for using `execute_command`
    action_whitelist = ActionWhitelistValidator(
        allowed_actions=["execute_command", "get_word_length"],
        fail_strategy=FailStrategy.LOG_ONLY
    )
    engine.register_validator(action_whitelist, ValidationPoint.PRE_ACTION)

    # Danger => SELF_CORRECT if "rm -rf /"
    engine.register_validator(NoDangerousCommandsValidator(), ValidationPoint.PRE_ACTION)

    return engine


# --------------------------------------------------------------------------
# 6) Two-run Example
# --------------------------------------------------------------------------
def run_example(query: str):
    """
    We'll do a single run with the given query. If SELF_CORRECT triggers,
    we catch the KeyboardInterrupt, build a second run with an updated prompt.
    """

    print("\n=======================================================")
    print(f"USER QUERY: {query}")
    print("=======================================================")

    # Build agent + validation
    agent = build_agent()
    validation_engine = build_validation_engine()

    # Option A: no dynamic LLM => static system_correction
    # callback = SelfCorrectingLangChainCallback(
    #     validation_engine=validation_engine,
    #     system_correction="Your previous attempt was invalid. Avoid destructive commands."
    # )

    # Option B: dynamic LLM => pass ChatOpenAI for correction text
    dynamic_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )
    callback = SelfCorrectingLangChainCallback(
        validation_engine=validation_engine,
        correction_llm=dynamic_llm,
        system_correction="(Fallback) Please avoid the invalid approach.",
        auto_re_run=False
    )

    agent.callbacks = [callback]

    print("--- RUN #1 ---")
    try:
        result1 = agent.invoke({"input": query})
        print(f"RUN #1 OUTPUT: {result1['output']}")
        return
    except KeyboardInterrupt as ke:
        # SELF_CORRECT triggered
        reason = str(ke)
        print(f"[BUMPERS] SELF_CORRECT triggered in RUN #1:\n{reason}")

    # Build a "corrected" prompt for run #2
    corrected_prompt = (
        "System Correction:\n"
        "(*The dynamic correction from our LLM was prepended here*)\n"
        f"Reason: {reason}\n"
        f"(Original user request: '{query}')\n"
        "Please provide a safer alternative or explanation instead of the destructive command."
    )

    print("\n--- RUN #2 (Corrected) ---")
    agent2 = build_agent()
    agent2.callbacks = [SelfCorrectingLangChainCallback(validation_engine=validation_engine)]
    try:
        result2 = agent2.invoke({"input": corrected_prompt})
        print(f"RUN #2 OUTPUT: {result2['output']}")
    except Exception as e2:
        print(f"[BUMPERS] Error in second run: {str(e2)}")


# --------------------------------------------------------------------------
# 7) Main
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # Example 1: Normal question => single run
    run_example("What is the length of 'Bananas'?")

    # Example 2: Potentially dangerous => triggers self-correct => second run
    run_example("Execute rm -rf /")
