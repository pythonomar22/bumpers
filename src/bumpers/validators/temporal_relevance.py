from typing import Dict, Any
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class TemporalRelevanceValidator(BaseValidator):
    """
    Ensures that the agent respects time-based aspects of the query.
    For example, if user asks "tomorrow's weather" or "yesterday's tweet",
    check if the final output references or attempts to address that specific timeframe.
    """

    def __init__(self, 
                 name: str = "temporal_relevance",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        super().__init__(name, fail_strategy)

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        question = context.get("question", "").lower()
        output = context.get("output", "").lower()

        # Identify temporal markers in the question
        # For simplicity, we just look for words like "yesterday", "tomorrow", "next week".
        temporal_keywords = ["yesterday", "tomorrow", "today", "tonight", "next week"]
        question_temporal_terms = [t for t in temporal_keywords if t in question]

        # If no temporal terms in question, pass by default
        if not question_temporal_terms:
            return ValidationResult(
                passed=True,
                message="No temporal constraints identified in the question.",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )

        # If temporal terms are in question, ensure the output addresses them.
        # For instance, if question asked about "tomorrow", the output should mention something about the future.
        # This is a naive check. In practice, you might want more robust time reasoning.
        missing_temporal = [term for term in question_temporal_terms if term not in output]

        if missing_temporal:
            return ValidationResult(
                passed=False,
                message=f"Temporal request not addressed. Missing terms: {missing_temporal}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )

        return ValidationResult(
            passed=True,
            message="Temporal aspects addressed.",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context,
            fail_strategy=self.fail_strategy
        )
