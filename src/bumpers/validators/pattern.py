import re
from typing import Dict, Any, List
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class PatternValidator(BaseValidator):
    """Detects potentially harmful patterns in actions/outputs"""
    def __init__(self, patterns: List[str], name: str = "pattern_matcher", fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        super().__init__(name, fail_strategy)
        self.patterns = [re.compile(p) for p in patterns]

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        text = context.get("output", "") + context.get("action_input", "")
        for pattern in self.patterns:
            if pattern.search(text):
                return ValidationResult(
                    passed=False,
                    message=f"Matched forbidden pattern: {pattern.pattern}",
                    validator_name=self.name,
                    validation_point=ValidationPoint.PRE_OUTPUT,
                    context=context,
                    fail_strategy=self.fail_strategy
                )
                
        return ValidationResult(
            passed=True,
            message="No forbidden patterns detected",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context,
            fail_strategy=self.fail_strategy
        ) 