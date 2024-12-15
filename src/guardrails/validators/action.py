from typing import List, Dict, Any
from .base import BaseValidator
from ..core.engine import ValidationResult, ValidationPoint

class ActionWhitelistValidator(BaseValidator):
    def __init__(self, allowed_actions: List[str], name: str = "action_whitelist"):
        super().__init__(name)
        self.allowed_actions = set(allowed_actions)
        
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        action = context.get("action")
        if not action:
            return ValidationResult(
                passed=False,
                message="No action specified in context",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context
            )
            
        if action not in self.allowed_actions:
            return ValidationResult(
                passed=False,
                message=f"Action '{action}' is not in allowed actions: {self.allowed_actions}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context
            )
            
        return ValidationResult(
            passed=True,
            message=f"Action '{action}' is allowed",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context
        ) 