import copy
import sys
from typing import Any, Dict, List, Optional, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from langchain_community.chat_models import ChatOpenAI  # or any LLM from LangChain

# Bumpers imports
from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
from ..validators.base import FailStrategy
from .langchain_callback import BumpersLangChainCallback


class SelfCorrectingLangChainCallback(BumpersLangChainCallback):
    """
    A specialized callback that extends BumpersLangChainCallback, providing:
      1. Automatic "rewind" to last safe checkpoint if fail_strategy=SELF_CORRECT
      2. Optionally uses a correction LLM to dynamically craft the System Correction message.

    How it works:
      - We track conversation "checkpoints" (messages + optional environment state).
      - If a validator triggers SELF_CORRECT, we:
          a) Rewind to the last safe checkpoint,
          b) Generate (or reuse) a "System Correction" message,
          c) Prepend that correction to the conversation,
          d) Raise `KeyboardInterrupt` to halt the chain.

    The user (or your code) then:
      - Catches the KeyboardInterrupt
      - Re-runs the chain with the updated conversation (the new "System Correction" at the top).

    Usage:
      - Attach this callback to an AgentExecutor.
      - Ensure your "run loop" handles KeyboardInterrupt to do the second run (or re-run automatically).
    """

    def __init__(
        self,
        validation_engine: CoreValidationEngine,
        max_turns: int = 10,
        system_correction: str = (
            "Your previous attempt was disallowed. Please correct your approach "
            "and remain aligned with the user's goal. Avoid repeating the invalid step."
        ),
        correction_llm: Optional["ChatOpenAI"] = None,
        auto_re_run: bool = False,
    ):
        """
        :param validation_engine: The Bumpers CoreValidationEngine
        :param max_turns: Max turns before forcibly stopping
        :param system_correction: A fallback static correction message
        :param correction_llm: (Optional) An LLM to generate dynamic correction messages
        :param auto_re_run: If True, attempts to re-run the chain automatically inside
                            this callback (be cautious with infinite loops). If False,
                            we raise KeyboardInterrupt so user code can handle re-running.
        """
        super().__init__(validation_engine=validation_engine, max_turns=max_turns)
        self.static_correction = system_correction
        self.correction_llm = correction_llm
        self.auto_re_run = auto_re_run

        # A list of conversation checkpoints
        self.checkpoints: List[Dict[str, Any]] = []
        self.last_safe_index = 0

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        prompts: Union[List[str], Dict, str],
        **kwargs: Any
    ) -> None:
        """Reset checkpoints and store the initial prompt(s)."""
        super().on_chain_start(serialized, prompts, **kwargs)

        self.checkpoints.clear()
        self.last_safe_index = 0

        # Convert prompts into a list of strings if needed
        if isinstance(prompts, dict):
            # e.g. {"input": "..."}
            first_prompt = prompts.get("input", "")
            all_prompts = [first_prompt]
        elif isinstance(prompts, list):
            all_prompts = prompts[:]
        else:
            all_prompts = [str(prompts)]

        initial_checkpoint = {
            "messages": all_prompts,
            "environment": None,
        }
        self.checkpoints.append(initial_checkpoint)

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """
        Validate the chosen action with PRE_ACTION. If valid, checkpoint; if not, self-correct.
        """
        # Let the base class track current_question, increment self.turn, etc.
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
            return

        # If action is valid, checkpoint
        prev_checkpoint = self.checkpoints[-1]
        new_checkpoint = {
            "messages": copy.deepcopy(prev_checkpoint["messages"]),
            "environment": None,  # If you have a browser or environment state, store it here
        }
        self.checkpoints.append(new_checkpoint)
        self.last_safe_index = len(self.checkpoints) - 1

    def on_tool_end(self, output: str, tool: str, **kwargs: Any) -> None:
        """Validate the tool's output with PRE_OUTPUT before returning to the agent."""
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
        """Validate the final output with PRE_OUTPUT."""
        validation_context = {
            "question": self.current_question,
            "output": finish.return_values.get("output", ""),
            "turn": self.turn + 1,
        }
        try:
            self.validation_engine.validate(ValidationPoint.PRE_OUTPUT, validation_context)
        except ValidationError as e:
            self._handle_failure(e)

    def _handle_failure(self, error: ValidationError):
        """
        If SELF_CORRECT => generate correction message & either auto-re-run or raise KeyboardInterrupt.
        Otherwise, fallback to parent's logic for STOP, RAISE_ERROR, LOG_ONLY, etc.
        """
        if error.result.fail_strategy != FailStrategy.SELF_CORRECT:
            # Let the parent handle STOP, RAISE_ERROR, LOG_ONLY
            super()._handle_failure(error)
            return

        # It's SELF_CORRECT
        print(f"[BUMPERS] Validation triggered SELF_CORRECT => {error.result.message}")

        # 1) Rewind to last safe checkpoint
        if self.last_safe_index < len(self.checkpoints):
            safe_checkpoint = self.checkpoints[self.last_safe_index]
        else:
            safe_checkpoint = self.checkpoints[0]

        # 2) Generate or reuse the system correction text
        correction_text = self._generate_correction_text(
            fail_message=error.result.message,
            user_prompt=self.current_question,
        )

        # 3) Insert it at the top of the messages
        corrected_messages = copy.deepcopy(safe_checkpoint["messages"])
        corrected_messages.insert(0, correction_text)

        if self.auto_re_run:
            # Potentially do an in-callback re-run (advanced usage).
            print("[BUMPERS] auto_re_run=True => Attempting immediate chain re-run with corrected_messages.")
            # (Implementation omitted to avoid infinite loops. Typically user code handles re-run.)
        else:
            # Raise KeyboardInterrupt for the user’s code to do the second run
            raise KeyboardInterrupt(
                f"SELF_CORRECT triggered. Use these corrected messages:\n"
                f"{corrected_messages}\n"
            )

    def _generate_correction_text(self, fail_message: str, user_prompt: str) -> str:
        """
        If we have an LLM, we ask it to craft a dynamic system correction. Otherwise, we
        fallback to a static correction message.
        """
        if self.correction_llm is None:
            # Use the static user-supplied text
            return (
                f"System Correction: {self.static_correction}\n"
                f"Reason: {fail_message}\n"
            )
        else:
            # Dynamically generate the correction text via LLM
            prompt_text = f"""
You are a guardrail system. The user request was: '{user_prompt}'.
A validator triggered because: '{fail_message}'.
Generate a short "System Correction" message instructing the AI assistant 
to avoid that invalid approach and remain aligned with the user's original goal.
"""
            # If your LLM is a ChatOpenAI, we can call .generate() or .call_as_llm():
            response = self.correction_llm.generate([prompt_text])
            correction_msg = response.generations[0][0].text.strip()

            return f"System Correction: {correction_msg}\nReason: {fail_message}\n"
