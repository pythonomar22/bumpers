# File: /src/bumpers/types.py

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class ValidationPoint(Enum):
    PRE_ACTION = "pre_action"
    POST_ACTION = "post_action"
    PRE_OUTPUT = "pre_output"
    POST_OUTPUT = "post_output"


class FailStrategy(Enum):
    """Determines how to handle a validation failure."""
    STOP = "stop"         # Raise KeyboardInterrupt to halt the chain
    RAISE_ERROR = "raise" # Raise a RuntimeError but chain may continue if caught
    LOG_ONLY = "log"      # Log the error and continue, no interruption

    # Added below:
    SELF_CORRECT = "self_correct"  # Attempt to rewind and fix mid-chain


@dataclass
class ValidationResult:
    passed: bool
    message: str
    validator_name: str
    validation_point: ValidationPoint
    context: Dict[str, Any]
    fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR
