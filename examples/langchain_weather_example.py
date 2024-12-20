import os
from langchain.agents import AgentExecutor
from bumpers.integrations.langchain_integration import LangChainValidatorMiddleware
from bumpers.logging.file_logger import FileLogger
from bumpers.analytics.analyzer import BumpersAnalyzer
from bumpers.core.engine import CoreValidationEngine
from bumpers.policy.parser import PolicyParser
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.content import ContentFilterValidator
import json

# Initialize logger
logger = FileLogger("logs")

# Initialize validation engine
cve = CoreValidationEngine()

# Load policies
policy_parser = PolicyParser()
policies = policy_parser.load_policy_file("path/to/policy.yaml")  # Update the path as necessary
cve.load_policies(policies)

# Register validators
action_whitelist = ActionWhitelistValidator(allowed_actions=["search_weather", "calculate"])
content_filter = ContentFilterValidator(forbidden_words=["password", "SSN", "confidential"])
cve.register_validator(action_whitelist, ValidationPoint.PRE_ACTION)
cve.register_validator(content_filter, ValidationPoint.PRE_OUTPUT)

# Initialize middleware
middleware = LangChainValidatorMiddleware()

# Initialize AgentExecutor with LangChain integration
agent_executor = AgentExecutor.from_llm_and_tools(
    llm=your_llm,  # Replace with your LLM instance
    tools=your_tools,  # Replace with your tools
    verbose=True,
    callbacks=[middleware]
)

# Initialize analyzer
analyzer = BumpersAnalyzer(logger)

def main():
    test_questions = [
        "What's the weather like today in New York?",
        "Calculate 50 * 20.",
        "Tell me the company's confidential strategy."  # Should trigger content filter
    ]
    
    for question in test_questions:
        print(f"\nTesting question: {question}")
        try:
            response = agent_executor.invoke({"messages": [{"role": "user", "content": question}]})
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Log current statistics after each question
        stats = analyzer.get_validation_stats()
        print("\nCurrent Statistics:")
        print(json.dumps(stats, indent=2))
    
    # Generate final analytics
    stats = analyzer.get_validation_stats()
    interventions = analyzer.get_intervention_summary()
    
    print("\nFinal Validation Statistics:")
    print(json.dumps(stats, indent=2))
    
    print("\nIntervention Summary:")
    print(json.dumps(interventions, indent=2))

if __name__ == "__main__":
    main() 