from typing import Dict, Any
from .base import BaseValidator
from ..core.engine import ValidationResult, ValidationPoint

class ChainLengthValidator(BaseValidator):
    """Prevents too many chained actions"""
    def __init__(self, max_chain_length: int = 3, name: str = "chain_length"):
        super().__init__(name)
        self.max_length = max_chain_length
        self.current_chain = 0

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        self.current_chain += 1
        if self.current_chain > self.max_length:
            return ValidationResult(
                passed=False,
                message=f"Chain length exceeded maximum of {self.max_length} actions",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context
            )
            
        return ValidationResult(
            passed=True,
            message=f"Chain length within limits: {self.current_chain}/{self.max_length}",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context
        ) 