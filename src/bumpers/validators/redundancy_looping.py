from typing import Dict, Any, List
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class RedundancyLoopingValidator(BaseValidator):
    """
    Detects when the agent repeatedly tries the same or similar actions without making progress.
    For example, if it's asked about the "2025 World Series winner" and it keeps calling
    'search_news 2025 World Series predictions' without finding any new info, this should fail after a certain threshold.
    """

    def __init__(self, 
                 max_repeated_actions: int = 3,
                 name: str = "redundancy_looping",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        super().__init__(name, fail_strategy)
        self.max_repeats = max_repeated_actions
        self.action_history: List[str] = []

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        # Each time PRE_ACTION is validated, record the action.
        action = context.get("action", "")
        action_input = context.get("action_input", "")
        full_action = f"{action}: {action_input}"

        # Check if the last few actions were similar (same action and input)
        self.action_history.append(full_action)

        # If we have exceeded the allowed repeats
        # A simple approach: if the last N actions are identical, it's looping
        if len(self.action_history) > self.max_repeats:
            # Check last N actions
            recent = self.action_history[-self.max_repeats:]
            if all(a == recent[0] for a in recent):
                return ValidationResult(
                    passed=False,
                    message=f"Redundant looping detected: {self.max_repeats} identical actions in a row ({recent[0]}).",
                    validator_name=self.name,
                    validation_point=ValidationPoint.PRE_ACTION,
                    context=context,
                    fail_strategy=self.fail_strategy
                )

        return ValidationResult(
            passed=True,
            message="No excessive redundancy/looping detected.",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context,
            fail_strategy=self.fail_strategy
        )
