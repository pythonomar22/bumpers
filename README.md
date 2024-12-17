# Bumpers 🛡️

A Python library for adding safety guardrails, monitoring, and validation to AI agents. Bumpers helps ensure AI agents operate within defined boundaries and provides real-time monitoring of their behavior.

## Features

- 🔒 **Validation Engine**: Pre-action and pre-output validation  
- 📜 **Policy Management**: YAML-based policy definitions  
- ⛔️ **Content Filtering**: Block sensitive or inappropriate content  
- 🎯 **Semantic Drift Detection**: Keep AI responses on topic  
- 📊 **Real-time Monitoring**: Alert on suspicious patterns  
- 📝 **Logging & Analytics**: Track and analyze agent behavior  

## Installation

```bash
pip install bumpers
```

## Quick Start

```python
from bumpers.core.engine import CoreValidationEngine
from bumpers.policy.parser import PolicyParser
from bumpers.integrations.react import GuardedReActAgent
from bumpers.logging.file_logger import FileLogger

# Initialize components
logger = FileLogger("logs")
engine = CoreValidationEngine(logger=logger)
parser = PolicyParser()

# Load policy
policy = parser.load_policy_file('policies/policy.yaml')
validators = parser.create_validators(policy)

# Register validators
for validator in validators:
    engine.register_validator(validator)

# Create guarded agent
agent = GuardedReActAgent(
    validation_engine=engine,
    bot_class=YourAgentClass,
    prompt=your_prompt
)

# Use the agent
result = agent.query("What is 2 + 2?", known_actions)
```

## Policy Definition

Define validation rules in YAML:

```yaml
validators:
  - name: "allowed_actions"
    type: "ActionWhitelist"
    parameters:
      allowed_actions: ["calculate", "wikipedia"]
    applies_to: "PRE_ACTION"
    on_fail: "block_action"
  
  - name: "content_filter"
    type: "ContentFilter"
    parameters:
      forbidden_words: ["confidential", "secret"]
      max_length: 1000
    applies_to: "PRE_OUTPUT"
    on_fail: "block_response"
```

## Available Validators

### ActionWhitelistValidator

Ensures agents only use approved actions.

```python
validator = ActionWhitelistValidator(
    allowed_actions=["calculate", "wikipedia"]
)
```

### ContentFilterValidator

Filters output based on forbidden words and length.

```python
validator = ContentFilterValidator(
    forbidden_words=["confidential", "secret"],
    max_length=1000
)
```

### SemanticDriftValidator

Prevents responses from going off-topic.

```python
validator = SemanticDriftValidator(
    embedding_model=your_embedding_model,
    similarity_threshold=0.7
)
```

## Monitoring & Alerts

Set up real-time monitoring with custom alerts:

```python
from guardrails.monitoring.monitor import GuardrailsMonitor
from guardrails.monitoring.conditions import (
    create_high_failure_rate_condition,
    create_repeated_intervention_condition
)

def alert_handler(message: str):
    print(f"🚨 ALERT: {message}")

monitor = GuardrailsMonitor(
    logger=logger,
    alert_handlers=[alert_handler],
    check_interval=30
)

# Add monitoring conditions
monitor.add_condition(
    create_high_failure_rate_condition(threshold=0.3)
)
monitor.add_condition(
    create_repeated_intervention_condition(
        action="wikipedia",
        count=2
    )
)

# Start monitoring
monitor.start()
```

## Logging & Analytics

Track and analyze agent behavior:

```python
from guardrails.analytics.analyzer import GuardrailsAnalyzer

analyzer = GuardrailsAnalyzer(logger)

# Get statistics
stats = analyzer.get_validation_stats()
interventions = analyzer.get_intervention_summary()

print("Validation Statistics:", stats)
print("Intervention Summary:", interventions)
```

## Integration Examples

### With ReAct Agent

```python
from guardrails.integrations.react import GuardedReActAgent

agent = GuardedReActAgent(
    validation_engine=cve,
    bot_class=ChatBot,
    prompt=prompt
)

result = agent.query(
    "What is 20 15?",
    known_actions={"calculate": calculate}
)
```

## Validation Points

- `PRE_ACTION`: Validates actions before execution
- `PRE_OUTPUT`: Validates responses before sending to user

## Custom Validators

Create custom validators by inheriting from `BaseValidator`:

```python
from guardrails.validators.base import BaseValidator
from guardrails.core.engine import ValidationResult, ValidationPoint

class CustomValidator(BaseValidator):
    def __init__(self, name: str = "custom"):
        super().__init__(name)

    def validate(self, context: dict) -> ValidationResult:
        # Implement validation logic
        return ValidationResult(
            passed=True,
            message="Validation passed",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context
        )
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 **Documentation**: [docs/](docs/)
- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/guardrails/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/guardrails/discussions)

## Citation

If you use Guardrails in your research, please cite:

```bibtex
@software{guardrails2024,
  author = {Your Name},
  title = {Guardrails: Safety Validation for AI Agents},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/guardrails}
}
