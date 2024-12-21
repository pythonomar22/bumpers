import time
from typing import Dict, Any
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class RateLimitValidator(BaseValidator):
    """Prevents too many actions in a short time period"""
    def __init__(self, max_actions_per_minute: int = 10, name: str = "rate_limit", fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        super().__init__(name, fail_strategy)
        self.max_actions = max_actions_per_minute
        self.action_timestamps = []

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        current_time = time.time()
        # Remove timestamps older than 1 minute
        self.action_timestamps = [t for t in self.action_timestamps 
                                if current_time - t < 60]
        self.action_timestamps.append(current_time)
        
        if len(self.action_timestamps) > self.max_actions:
            return ValidationResult(
                passed=False,
                message=f"Rate limit exceeded: {self.max_actions} actions per minute",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context,
                fail_strategy=self.fail_strategy
            )
            
        return ValidationResult(
            passed=True,
            message="Within rate limits",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context,
            fail_strategy=self.fail_strategy
        ) 