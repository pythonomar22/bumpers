# File: /examples/langchain/self_correcting.py

import os
from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

# Set OpenAI API key at the start
os.environ["OPENAI_API_KEY"] = "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"

# Bumpers
from bumpers.core.engine import CoreValidationEngine, ValidationPoint
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.base import FailStrategy
from bumpers.integrations.self_correcting_callback import SelfCorrectingLangChainCallback

@tool
def execute_command(cmd: str) -> str:
    """Simulates executing a system command."""
    return f"COMMAND HERE: Executed: {cmd}"

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

def test_self_correction():
    # Build the agent
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [execute_command, get_word_length]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm.bind_tools(tools)
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Set up validation with ActionWhitelistValidator
    validation_engine = CoreValidationEngine()
    validation_engine.register_validator(
        ActionWhitelistValidator(
            allowed_actions=["get_word_length"],  # Only allow get_word_length
            fail_strategy=FailStrategy.SELF_CORRECT  # Use self-correct strategy
        ),
        ValidationPoint.PRE_ACTION
    )

    # Create and attach the self-correcting callback
    callback = SelfCorrectingLangChainCallback(
        validation_engine=validation_engine,
        openai_api_key=os.environ["OPENAI_API_KEY"],
        max_turns=10,
        max_self_correct=1,
        model_name="gpt-3.5-turbo"
    )
    callback.attach_agent_executor(agent_executor)
    agent_executor.callbacks = [callback]

    print("\n=== Testing Self-Correction ===")
    print("Initial Prompt: Execute rm -rf /")
    print("=" * 50)
    
    try:
        result = agent_executor.invoke({"input": "Execute rm -rf /"})
    except KeyboardInterrupt as e:
        print(f"\nChain halted: {str(e)}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_self_correction()
