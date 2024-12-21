import sys
from typing import Any, Dict, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
from ..validators.base import FailStrategy

class BumpersLangChainCallback(BaseCallbackHandler):
    """
    A LangChain callback handler that integrates Bumpers validation into the agent execution flow.
    Respects the fail_strategy from each validator:
      - STOP => raise KeyboardInterrupt (halting the chain)
      - RAISE_ERROR => raise RuntimeError (LangChain may swallow or log it)
      - LOG_ONLY => print/log the error, no interruption
    """

    def __init__(self, validation_engine: CoreValidationEngine, max_turns: int = 10):
        super().__init__()
        self.validation_engine = validation_engine
        self.max_turns = max_turns
        self.current_question: str = ""
        self.turn = 0

    def _handle_failure(self, error: ValidationError):
        """Handle validation failure according to the fail strategy of the failing validator."""
        strategy = error.result.fail_strategy

        if strategy == FailStrategy.STOP:
            print(f"[BUMPERS] Validation failed with STOP strategy: {error.result.message}")
            # Halt the entire chain
            raise KeyboardInterrupt(error.result.message)
        elif strategy == FailStrategy.RAISE_ERROR:
            print(f"[BUMPERS] Validation failed with RAISE_ERROR strategy: {error.result.message}")
            # Raise a RuntimeError. Chain may continue if LangChain handles it.
            raise RuntimeError(error.result.message)
        elif strategy == FailStrategy.LOG_ONLY:
            print(f"[BUMPERS] Validation failed with LOG_ONLY strategy: {error.result.message}")
            # Just log, no interruption
        else:
            # Unrecognized strategy, default to raise error
            print(f"[BUMPERS] Validation failed with unknown strategy. Using RAISE_ERROR. {error.result.message}")
            raise RuntimeError(error.result.message)

    def on_chain_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called at the start of a chain run"""
        # More safely extract the current question from prompts
        if prompts and isinstance(prompts, list) and len(prompts) > 0:
            self.current_question = prompts[0]
        elif serialized and isinstance(serialized, dict):
            # If we can't get the question from prompts, try the inputs
            self.current_question = serialized.get("input", "")
        else:
            # If neither source is available, use empty string
            self.current_question = ""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
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
        validation_context = {
            "question": self.current_question,
            "output": finish.return_values.get("output", ""),
            "turn": self.turn + 1,
        }
        try:
            self.validation_engine.validate(ValidationPoint.PRE_OUTPUT, validation_context)
        except ValidationError as e:
            self._handle_failure(e)
