from typing import List, Dict, Any
from .base import BaseValidator
from ..core.engine import ValidationResult, ValidationPoint

class ContentFilterValidator(BaseValidator):
    def __init__(self, 
                 forbidden_words: List[str] = None,
                 max_length: int = None,
                 name: str = "content_filter"):
        super().__init__(name)
        self.forbidden_words = set(forbidden_words or [])
        self.max_length = max_length
        
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        content = context.get("output")
        if not content:
            return ValidationResult(
                passed=False,
                message="No content to validate",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context
            )
            
        # Check for forbidden words
        if self.forbidden_words:
            found_words = [word for word in self.forbidden_words 
                         if word.lower() in content.lower()]
            if found_words:
                return ValidationResult(
                    passed=False,
                    message=f"Found forbidden words: {found_words}",
                    validator_name=self.name,
                    validation_point=ValidationPoint.PRE_OUTPUT,
                    context=context
                )
                
        # Check content length
        if self.max_length and len(content) > self.max_length:
            return ValidationResult(
                passed=False,
                message=f"Content exceeds maximum length of {self.max_length}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context
            )
            
        return ValidationResult(
            passed=True,
            message="Content validation passed",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context
        ) 