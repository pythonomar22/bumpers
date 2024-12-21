from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from ..logging.base import BaseLogger, LogEvent
from datetime import datetime
from ..validators.base import FailStrategy  # This is safe now (no engine -> base loop)

class ValidationPoint(Enum):
    PRE_ACTION = "pre_action"
    POST_ACTION = "post_action"
    PRE_OUTPUT = "pre_output"
    POST_OUTPUT = "post_output"

@dataclass
class ValidationResult:
    passed: bool
    message: str
    validator_name: str
    validation_point: ValidationPoint
    context: Dict[str, Any]
    fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR

class ValidationError(Exception):
    def __init__(self, result: ValidationResult):
        self.result = result
        super().__init__(result.message)

class CoreValidationEngine:
    def __init__(self, logger: Optional[BaseLogger] = None):
        self._validators: Dict[ValidationPoint, List['BaseValidator']] = {
            point: [] for point in ValidationPoint
        }
        self.logger = logger
        
    def register_validator(self, validator: 'BaseValidator', point: ValidationPoint):
        """Register a validator to run at a specific validation point"""
        self._validators[point].append(validator)
        
    def _log_validation(self, result: ValidationResult):
        if self.logger:
            self.logger.log_event(LogEvent(
                timestamp=datetime.now(),
                event_type='validation',
                validation_point=result.validation_point.value,
                validator_name=result.validator_name,
                status='pass' if result.passed else 'fail',
                message=result.message,
                context=result.context
            ))
            
    def _log_intervention(self, result: ValidationResult, intervention_type: str):
        if self.logger:
            self.logger.log_event(LogEvent(
                timestamp=datetime.now(),
                event_type='intervention',
                validation_point=result.validation_point.value,
                validator_name=result.validator_name,
                status='intervention',
                message=f"Intervention triggered: {intervention_type}",
                context={
                    **result.context,
                    'intervention_type': intervention_type
                }
            ))
    
    def validate(self, point: ValidationPoint, context: Dict[str, Any]) -> List[ValidationResult]:
        results = []
        
        for validator in self._validators[point]:
            try:
                # validator.validate should return a ValidationResult
                result = validator.validate(context)
                results.append(result)
                self._log_validation(result)
                
                if not result.passed:
                    self._log_intervention(result, 'block_action')
                    raise ValidationError(result)
                    
            except Exception as e:
                if not isinstance(e, ValidationError):
                    # unexpected error in validator code
                    result = ValidationResult(
                        passed=False,
                        message=f"Validator failed with error: {str(e)}",
                        validator_name=validator.name,
                        validation_point=point,
                        context=context,
                        fail_strategy=validator.fail_strategy
                    )
                    results.append(result)
                    self._log_validation(result)
                    self._log_intervention(result, 'error')
                    raise ValidationError(result)
                raise
                
        return results
