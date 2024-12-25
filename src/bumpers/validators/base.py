from abc import ABC, abstractmethod
from typing import Dict, Any
from ..types import FailStrategy, ValidationResult

class BaseValidator(ABC):
    def __init__(self, name: str, fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        self.name = name
        self.fail_strategy = fail_strategy
        
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate the given context and return a ValidationResult."""
        pass
