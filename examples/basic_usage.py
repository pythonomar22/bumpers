from guardrails.core.engine import CoreValidationEngine, ValidationPoint
from guardrails.validators.action import ActionWhitelistValidator
from guardrails.policy.parser import PolicyParser

# Initialize the Core Validation Engine
cve = CoreValidationEngine()

# Load policy from file
parser = PolicyParser()
policy = parser.load_policy_file('policies/basic.yaml')
validators = parser.create_validators(policy)

# Register validators
for validator in validators:
    cve.register_validator(validator, ValidationPoint.PRE_ACTION)

# Example usage with a ReAct agent
def safe_execute_action(action: str, context: Dict[str, Any]):
    # Validate before executing action
    validation_context = {
        "action": action,
        **context
    }
    
    try:
        cve.validate(ValidationPoint.PRE_ACTION, validation_context)
        # If validation passes, execute the action
        result = execute_action(action, context)
        return result
    except ValidationError as e:
        print(f"Validation failed: {e.result.message}")
        # Handle the validation failure (e.g., try alternative action)
        return None 