# 🛡️ Bumpers

Add safety guardrails to your AI agents with just a few lines of code. Bumpers is a Python library that helps you build safer AI applications by validating agent actions and outputs in real-time.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

## ✨ Features

- 🔒 **Validation Engine**: Pre-built validators for common safety checks
- 🤖 **Framework Support**: Works with both custom agents and popular frameworks like LangChain
- 🚫 **Action Control**: Whitelist allowed actions and block dangerous operations
- 🔍 **Content Filtering**: Detect and block sensitive or inappropriate content
- 📊 **Semantic Monitoring**: Track semantic drift and goal fulfillment
- ⏱️ **Rate Limiting**: Prevent infinite loops and resource abuse
- 📝 **Logging & Analytics**: Track and analyze agent behavior

## 🚀 Quick Start

### Installation

1. Install:
```bash
pip install bumpers
```

### Basic Usage with LangChain

```python
from langchain.agents import AgentExecutor
from bumpers.core.engine import CoreValidationEngine
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.content import ContentFilterValidator
from bumpers.integrations.langchain_callback import BumpersLangChainCallback

# Set up validation engine
validation_engine = CoreValidationEngine()

# Add validators
validation_engine.register_validator(
    ActionWhitelistValidator(allowed_actions=["search", "calculate"]),
    ValidationPoint.PRE_ACTION
)
validation_engine.register_validator(
    ContentFilterValidator(forbidden_words=["confidential", "secret"]),
    ValidationPoint.PRE_OUTPUT
)

# Create Bumpers callback
bumpers_callback = BumpersLangChainCallback(validation_engine=validation_engine)

# Add to your LangChain agent
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[bumpers_callback]  # Add Bumpers protection
)

# Use normally - Bumpers will automatically protect your agent
result = agent_executor.invoke({"input": "What's 2 + 2?"})
```

## 🛡️ Available Validators

### Action Control
- `ActionWhitelistValidator`: Restrict which actions an agent can perform
- `ResourceValidator`: Prevent resource-intensive operations
- `RateLimitValidator`: Control action frequency

### Content Safety
- `ContentFilterValidator`: Block sensitive or inappropriate content
- `LLMSafetyValidator`: Use LLMs to validate content safety
- `PatternValidator`: Block content matching specific patterns

### Semantic Control
- `SemanticDriftValidator`: Keep responses on topic
- `GoalFulfillmentValidator`: Ensure answers address the original question
- `TemporalRelevanceValidator`: Validate time-based responses

### Chain Control
- `ChainLengthValidator`: Limit action chain length
- `RedundancyLoopingValidator`: Detect and prevent action loops

## 🔍 Monitoring & Analytics

Track agent behavior and get alerts:

```python
from bumpers.monitoring.monitor import BumpersMonitor
from bumpers.monitoring.conditions import create_high_failure_rate_condition

def alert_handler(message):
    print(f"🚨 Alert: {message}")

# Create monitor
monitor = BumpersMonitor(
    logger=logger,
    alert_handlers=[alert_handler]
)

# Add conditions
monitor.add_condition(
    create_high_failure_rate_condition(threshold=0.3)
)

# Start monitoring
monitor.start()
```

## 📊 Analytics

Analyze agent behavior:

```python
from bumpers.analytics.analyzer import BumpersAnalyzer

analyzer = BumpersAnalyzer(logger)

# Get validation statistics
stats = analyzer.get_validation_stats()
print("Validation Stats:", stats)

# Get intervention summary
summary = analyzer.get_intervention_summary()
print("Interventions:", summary)
```

## 🎯 Fail Strategies

Customize how validators handle failures:

```python
from bumpers.validators.base import FailStrategy

validator = ContentFilterValidator(
    forbidden_words=["confidential"],
    fail_strategy=FailStrategy.STOP  # Immediately halt execution
)

validator = RateLimitValidator(
    max_actions_per_minute=10,
    fail_strategy=FailStrategy.RAISE_ERROR  # Raise exception but allow catching
)

validator = PatternValidator(
    patterns=[r"sensitive\s+data"],
    fail_strategy=FailStrategy.LOG_ONLY  # Just log the violation
)
```

## 🔧 Custom Validators

Create your own validators:

```python
from bumpers.validators.base import BaseValidator
from bumpers.core.engine import ValidationResult, ValidationPoint

class CustomValidator(BaseValidator):
    def __init__(self, name: str = "custom"):
        super().__init__(name)

    def validate(self, context: dict) -> ValidationResult:
        # Implement your validation logic
        return ValidationResult(
            passed=True,
            message="Validation passed",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_ACTION,
            context=context
        )
```

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=pythonomar22/bumpers&type=Date)](https://star-history.com/#yourusername/bumpers&Date)
