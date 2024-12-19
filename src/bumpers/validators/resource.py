from typing import Dict, Any
from .base import BaseValidator
from ..core.engine import ValidationResult, ValidationPoint

class ResourceValidator(BaseValidator):
    """Prevents excessive resource usage in calculations"""
    def __init__(self, max_memory_mb: int = 100, name: str = "resource_usage"):
        super().__init__(name)
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        if context.get("action") == "calculate":
            # Check if calculation might be resource-intensive
            expression = context.get("action_input", "")
            if "**" in expression or any(str(n) for n in expression if len(str(n)) > 5):
                return ValidationResult(
                    passed=False,
                    message="Calculation might be too resource-intensive",
                    validator_name=self.name,
                    validation_point=ValidationPoint.PRE_ACTION,
                    context=context
                )
                
        return ValidationResult(
            passed=True,
            message="Resource usage acceptable",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context
        ) 