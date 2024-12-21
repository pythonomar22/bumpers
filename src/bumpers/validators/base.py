from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

class FailStrategy(Enum):
    """Determines how to handle a validation failure."""
    STOP = "stop"         # Raise KeyboardInterrupt to halt the chain
    RAISE_ERROR = "raise" # Raise a RuntimeError but chain may continue if caught
    LOG_ONLY = "log"      # Log the error and continue, no interruption

class BaseValidator(ABC):
    def __init__(self, name: str, fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        """
        Args:
            name: Name of this validator
            fail_strategy: Determines what happens if this validator fails.
        """
        self.name = name
        self.fail_strategy = fail_strategy
        
    @abstractmethod
    def validate(self, context: Dict[str, Any]): 
        """
        Validate the given context and return a ValidationResult.
        
        We do not import ValidationResult or ValidationPoint here to avoid circular imports.
        The engine.py file will handle creating and using ValidationResult.
        
        Returns:
            A ValidationResult instance created in the validator implementation files 
            (those validators can import ValidationResult from engine.py themselves).
        """
        pass
