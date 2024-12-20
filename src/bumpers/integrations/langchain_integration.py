from langchain.agents import AgentExecutor
from bumpers.validators.resource import ResourceValidator
from bumpers.validators.semantic import SemanticDriftValidator
from bumpers.validators.temporal_relevance import TemporalRelevanceValidator
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.content import ContentFilterValidator
from bumpers.validators.goal_fulfillment import GoalFulfillmentValidator
from bumpers.validators.redundancy_looping import RedundancyLoopingValidator
from bumpers.validators.rate_limit import RateLimitValidator
from bumpers.validators.llm_safety import LLMSafetyValidator
from bumpers.validators.pattern import PatternValidator

class LangChainValidatorMiddleware:
    def __init__(self):
        self.validators = [
            ResourceValidator(),
            SemanticDriftValidator(),
            TemporalRelevanceValidator(),
            ActionWhitelistValidator(allowed_actions=["search", "calculate"]),
            ContentFilterValidator(forbidden_words=["password", "SSN"]),
            GoalFulfillmentValidator(),
            RedundancyLoopingValidator(),
            RateLimitValidator(),
            LLMSafetyValidator(),
            PatternValidator(patterns=[r"forbidden_pattern"])
        ]

    def before_action(self, context: Dict[str, Any]):
        for validator in self.validators:
            result = validator.validate(context)
            if not result.passed:
                raise Exception(f"Validation failed: {result.message}")

    def after_output(self, context: Dict[str, Any]):
        for validator in self.validators:
            result = validator.validate(context)
            if not result.passed:
                raise Exception(f"Validation failed: {result.message}")

# Example of integrating middleware with LangChain's AgentExecutor
agent_executor = AgentExecutor.from_llm_and_tools(
    llm=your_llm,
    tools=your_tools,
    verbose=True,
    callbacks=[LangChainValidatorMiddleware()]
) 