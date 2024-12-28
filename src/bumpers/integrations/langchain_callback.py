# File: /src/bumpers/integrations/langchain_callback.py

import sys
from typing import Any, Dict, List, Optional, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
from ..types import FailStrategy, ValidationResult


class BumpersLangChainCallback(BaseCallbackHandler):
    """
    A LangChain callback handler that integrates Bumpers validation into the agent execution flow.

    Respects the fail_strategy from each validator:
      - STOP => raise KeyboardInterrupt (halts chain)
      - RAISE_ERROR => raise RuntimeError (LangChain may catch or log it)
      - LOG_ONLY => print/log the violation but continue
      - SELF_CORRECT => can be intercepted by a specialized self-correct callback
      - (or custom fail strategies)
    """

    def __init__(self, validation_engine: CoreValidationEngine, max_turns: int = 10):
        super().__init__()
        self.validation_engine = validation_engine
        self.max_turns = max_turns
        self.current_question: str = ""
        self.turn = 0

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        prompts: Union[List[str], Dict, str],
        **kwargs: Any
    ) -> None:
        """
        Called at the start of each chain run. We parse the user's prompt,
        store it in self.current_question, and log it once so you see the query.
        """
        user_prompt = ""

        # Attempt to parse the prompt
        if isinstance(prompts, dict) and "input" in prompts:
            user_prompt = prompts["input"]
        elif isinstance(prompts, list) and prompts and isinstance(prompts[0], str):
            user_prompt = prompts[0]
        elif "input" in kwargs and isinstance(kwargs["input"], str):
            user_prompt = kwargs["input"]

        self.current_question = user_prompt or ""

        # Log the prompt so you can see if it's the original or corrected
        print(f"[BUMPERS] Starting chain run. Prompt: {self.current_question}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """
        Whenever the agent chooses a tool, do pre-action validation.
        """
        self.turn += 1
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

    def on_tool_end(self, output: str, tool: str, **kwargs: Any) -> None:
        """
        After a tool finishes, do pre-output validation before returning control to the agent.
        """
        validation_context = {
            "question": self.current_question,
            "output": output,
            "turn": self.turn,
        }
        try:
            self.validation_engine.validate(ValidationPoint.PRE_OUTPUT, validation_context)
        except ValidationError as e:
            self._handle_failure(e)

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """
        At the final step, validate the final output with pre-output.
        """
        final_output = finish.return_values.get("output", "")
        validation_context = {
            "question": self.current_question,
            "output": final_output,
            "turn": self.turn + 1,
        }
        try:
            self.validation_engine.validate(ValidationPoint.PRE_OUTPUT, validation_context)
        except ValidationError as e:
            self._handle_failure(e)

    def _handle_failure(self, error: ValidationError):
        """
        If a validator fails, handle it according to fail_strategy.
        We'll do minimal logging here.
        """
        strategy = error.result.fail_strategy
        msg = error.result.message
        validator_name = error.result.validator_name

        print(f"[BUMPERS] Validation failed => Strategy={strategy}, Validator='{validator_name}', Message='{msg}'")

        if strategy == FailStrategy.STOP:
            raise KeyboardInterrupt(msg)
        elif strategy == FailStrategy.RAISE_ERROR:
            raise RuntimeError(msg)
        elif strategy == FailStrategy.LOG_ONLY:
            print(f"[BUMPERS] LOG_ONLY => {msg}")
        elif strategy == FailStrategy.SELF_CORRECT:
            # By default, we raise a KeyboardInterrupt. A specialized SelfCorrectingLangChainCallback
            # might override this to handle self-correction logic.
            raise KeyboardInterrupt(f"SELF_CORRECT triggered => {msg}")
        else:
            # fallback for unknown strategy
            raise RuntimeError(msg)
