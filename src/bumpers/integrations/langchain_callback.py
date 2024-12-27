import sys
from typing import Any, Dict, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
from ..types import FailStrategy, ValidationResult


class BumpersLangChainCallback(BaseCallbackHandler):
    """
    A LangChain callback handler that integrates Bumpers validation into the agent execution flow.
    Respects the fail_strategy from each validator:
      - STOP => raise KeyboardInterrupt (halting the chain)
      - RAISE_ERROR => raise RuntimeError (LangChain may swallow or log it)
      - LOG_ONLY => just logs
      - AUTO_CORRECT => attempt a self-healing re-prompt
    """

    def __init__(self, validation_engine: CoreValidationEngine, max_turns: int = 10):
        super().__init__()
        self.validation_engine = validation_engine
        self.max_turns = max_turns
        self.current_question: str = ""
        self.turn = 0

        self.auto_correct_count = 0
        self.max_auto_correct = 3

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        prompts: Any,   # This can be a list OR dict, as your logs show
        **kwargs: Any
    ) -> None:
        """
        Called at the start of a chain run. We'll debug-print everything to see how to get the actual user prompt.
        """
        print("\n[BUMPERS] on_chain_start DEBUG:")
        print(f"  serialized = {serialized}")
        print(f"  prompts    = {prompts}")
        print(f"  kwargs     = {kwargs}")

        user_prompt = ""

        # 1) If `prompts` is a dict with an 'input' key (like your logs), we capture that
        if isinstance(prompts, dict) and "input" in prompts:
            user_prompt = prompts["input"]
            print(f"[BUMPERS] (Dictionary scenario) Found user_prompt in prompts['input'] => '{user_prompt}'")

        # 2) If `prompts` is a list of strings, then we do the usual approach:
        elif isinstance(prompts, list) and len(prompts) > 0 and isinstance(prompts[0], str):
            user_prompt = prompts[0]
            print(f"[BUMPERS] (List scenario) Using prompts[0] => '{user_prompt}'")

        # 3) If we still don't have anything, try `kwargs["input"]` if it exists
        elif "input" in kwargs and isinstance(kwargs["input"], str):
            user_prompt = kwargs["input"]
            print(f"[BUMPERS] (kwargs scenario) Found user_prompt in kwargs['input'] => '{user_prompt}'")

        # 4) Otherwise, we fallback to an empty string
        self.current_question = user_prompt or ""
        print(f"[BUMPERS] => self.current_question='{self.current_question}'\n")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        self.turn += 1
        validation_context = {
            "question": self.current_question,
            "action": action.tool,
            "action_input": action.tool_input,
            "turn": self.turn,
        }

        # Debug
        print(
            f"[BUMPERS] on_agent_action => turn={self.turn}, tool='{action.tool}', "
            f"question='{self.current_question[:60]}...'")

        # Validate at PRE_ACTION
        try:
            self.validation_engine.validate(ValidationPoint.PRE_ACTION, validation_context)
        except ValidationError as e:
            self._handle_failure(e)

    def on_tool_end(self, output: str, tool: str, **kwargs: Any) -> None:
        # Debug
        print(f"[BUMPERS] on_tool_end => turn={self.turn}, tool='{tool}', output='{output[:60]}...'")

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
        # Debug
        print("[BUMPERS] on_agent_finish => final check on PRE_OUTPUT...")

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
        """
        strategy = error.result.fail_strategy
        print(
            f"[BUMPERS] _handle_failure => fail_strategy={strategy}, "
            f"validator='{error.result.validator_name}', msg='{error.result.message}'"
        )

        if strategy == FailStrategy.STOP:
            raise KeyboardInterrupt(error.result.message)
        elif strategy == FailStrategy.RAISE_ERROR:
            raise RuntimeError(error.result.message)
        elif strategy == FailStrategy.LOG_ONLY:
            print(f"[BUMPERS] LOG_ONLY => {error.result.message}")
        elif strategy == FailStrategy.AUTO_CORRECT:
            print(f"[BUMPERS] AUTO_CORRECT => {error.result.message}")
            self._attempt_auto_correction(error.result)
        else:
            print(f"[BUMPERS] Unknown strategy => defaulting to RAISE_ERROR")
            raise RuntimeError(error.result.message)

    def _attempt_auto_correction(self, result: ValidationResult):
        """
        Attempt to alter self.current_question so future calls see a corrective prompt.
        """
        self.auto_correct_count += 1
        if self.auto_correct_count > self.max_auto_correct:
            print("[BUMPERS] Too many auto-corrections, halting chain.")
            raise KeyboardInterrupt("Max auto-correct attempts exceeded")

        # Construct a short 'reminder' prompt
        correction = (
            f"\nSystem Correction:\n"
            f"You encountered a policy violation: {result.message}\n"
            f"Please remove any references to jokes, since user forbade jokes.\n"
            f"Focus only on question: '{self.current_question}'."
        )

        self.current_question += correction
        print(f"[BUMPERS] Appended correction => {correction}")
        print(f"[BUMPERS] Now self.current_question => {self.current_question}")
