from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.engine import ValidationResult, ValidationPoint

class BaseValidator(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate the given context and return a ValidationResult.
        
        Args:
            context: Dictionary containing the context to validate
            
        Returns:
            ValidationResult indicating whether validation passed/failed
        """
        pass 