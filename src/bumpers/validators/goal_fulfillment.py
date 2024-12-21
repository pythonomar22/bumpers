from typing import Dict, Any
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class GoalFulfillmentValidator(BaseValidator):
    """
    Checks if the final answer actually addresses the user's original question.
    If the user asked for specific info (e.g., tomorrow's weather in New York),
    the validator ensures the final answer includes that info rather than just
    a generic response.
    """

    def __init__(self, 
                 name: str = "goal_fulfillment",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        super().__init__(name, fail_strategy)

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        question = context.get("question", "").lower()
        output = context.get("output", "").lower()

        # Basic heuristic: ensure keywords from the question are present in the output.
        # This is a simple approach—more sophisticated logic could parse time-based requests
        # or domain-specific queries and verify the answer more robustly.
        
        # Example: If user asked "tomorrow's weather in New York"
        # Check if output mentions "new york" and something about weather/forecast
        # In a real scenario, you'd integrate a more clever NLU approach.

        # For now, we just check if some key terms from the question appear in the answer.
        # If the question is complex, you might parse or extract key entities and check them.
        question_terms = [word for word in question.split() if len(word) > 3]
        required_terms = question_terms[:3]  # Just pick a few representative words

        # If too simplistic, just checking presence:
        missing_terms = [term for term in required_terms if term not in output]

        if missing_terms:
            return ValidationResult(
                passed=False,
                message=f"Goal not fulfilled. Missing key terms: {missing_terms}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )
        
        return ValidationResult(
            passed=True,
            message="Goal appears to be fulfilled.",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context,
            fail_strategy=self.fail_strategy
        )
