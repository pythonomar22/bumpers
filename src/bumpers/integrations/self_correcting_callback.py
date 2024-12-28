import copy
import sys
from typing import Any, Dict, List, Optional, Union

# New OpenAI SDK import
from openai import OpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

# Bumpers imports
from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
from ..validators.base import FailStrategy
from .langchain_callback import BumpersLangChainCallback


class SelfCorrectingLangChainCallback(BumpersLangChainCallback):
    """A callback that handles self-correction when validation fails."""
    
    def __init__(
        self,
        validation_engine: CoreValidationEngine,
        openai_api_key: str,
        max_turns: int = 10,
        max_self_correct: int = 1,
        model_name: str = "gpt-3.5-turbo",
    ):
        super().__init__(validation_engine=validation_engine, max_turns=max_turns)
        self.openai_api_key = openai_api_key
        self.max_self_correct = max_self_correct
        self.model_name = model_name
        self._agent_executor_ref = None
        self.self_correct_count = 0
        self.run_number = 0
        self.current_chain_stopped = False

    def attach_agent_executor(self, agent_executor: Any):
        """Store reference to agent executor for self-correction."""
        self._agent_executor_ref = agent_executor

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        prompts: Union[List[str], Dict, str],
        **kwargs: Any
    ) -> None:
        """Print clear run header and track run number."""
        self.run_number += 1
        self.current_chain_stopped = False  # Reset flag
        
        # Extract user prompt
        user_prompt = ""
        if isinstance(prompts, dict) and "input" in prompts:
            user_prompt = prompts["input"]
        elif isinstance(prompts, list):
            user_prompt = prompts[0] if prompts else ""
        else:
            user_prompt = str(prompts)

        # Clear run header
        if self.self_correct_count > 0:
            print(f"\n[RUN #{self.run_number} - CORRECTED]")
        else:
            print(f"\n[RUN #{self.run_number}]")
        print(f"Agent received prompt: {user_prompt}\n")

        super().on_chain_start(serialized, prompts, **kwargs)

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Validate before action and handle failures."""
        if self.current_chain_stopped:
            # If chain was stopped due to validation, prevent further actions
            raise KeyboardInterrupt("Chain stopped due to validation failure")
            
        self.turn += 1
        print(f"Agent: Attempting action '{action.tool}' with input '{action.tool_input}'")
        
        validation_context = {
            "question": self.current_question,
            "action": action.tool,
            "action_input": action.tool_input,
            "turn": self.turn,
        }
        
        try:
            self.validation_engine.validate(ValidationPoint.PRE_ACTION, validation_context)
        except ValidationError as e:
            self._handle_failure(e)
            self.current_chain_stopped = True
            raise KeyboardInterrupt("Chain stopped due to validation failure")
            return None

    def _handle_failure(self, error: ValidationError):
        """Handle validation failure with clear output."""
        strategy = error.result.fail_strategy
        if strategy != FailStrategy.SELF_CORRECT:
            super()._handle_failure(error)
            return

        print(f"\nValidation Failed: {error.result.message}")
        
        if self.self_correct_count >= self.max_self_correct:
            print("\nMaximum correction attempts reached. Halting.")
            raise KeyboardInterrupt("Max self-corrections reached")

        self.self_correct_count += 1

        # Generate correction
        system_correction = self._generate_dynamic_correction(
            user_prompt=self.current_question,
            fail_message=error.result.message
        )

        if not self._agent_executor_ref:
            raise KeyboardInterrupt("No agent reference available for correction")

        print("\nSystem Correction:")
        print(f'"{system_correction}"\n')

        # Start new chain with correction
        try:
            new_input = f"{system_correction}\n\nOriginal request: {self.current_question}"
            self.turn = 0
            # We need to properly handle the chain completion here
            result = self._agent_executor_ref.invoke({"input": new_input})
            # After correction chain completes, exit cleanly
            sys.exit(0)
        except Exception as e:
            print(f"Error during correction: {str(e)}")
            raise KeyboardInterrupt("Correction failed")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Print final output clearly."""
        if not self.current_chain_stopped:
            final_output = finish.return_values.get("output", "")
            print(f"\nFinal Result [Run #{self.run_number}]: {final_output}\n")

    def _generate_dynamic_correction(self, user_prompt: str, fail_message: str) -> str:
        """Generate a correction that guides the agent to a safer approach."""
        client = OpenAI(api_key=self.openai_api_key)

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system", 
                    "content": """You are a safety guidance system that helps AI agents correct their behavior.
                    When an agent makes a potentially harmful decision, you provide guidance to:
                    1. Explain why their previous action was unsafe
                    2. Guide them toward a safer alternative
                    3. Keep them focused on the user's original goal
                    Be direct and concise in your correction."""
                },
                {
                    "role": "user",
                    "content": f"""The agent just tried an unsafe action.

                    Original user request: {user_prompt}
                    Safety violation: {fail_message}

                    Generate a correction message for the agent that:
                    1. Acknowledges what they tried to do
                    2. Explains why it wasn't allowed
                    3. Guides them to either:
                       - Find a safer way to help the user
                       - Explain why they can't help with this request
                    """
                },
            ],
        )

        correction_text = completion.choices[0].message.content.strip()

        # Format the correction as a clear instruction to the agent
        return f"""Previous Action Blocked: {fail_message}

Guidance for Agent:
{correction_text}

Remember: Stay focused on helping the user while maintaining safety."""
