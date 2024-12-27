# File: examples/langchain_comparison_example.py

from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

import os
from PIL import Image

# Bumpers imports
from bumpers.core.engine import CoreValidationEngine, ValidationPoint
from bumpers.logging.file_logger import FileLogger
from bumpers.validators.vision import VisionValidator
from bumpers.validators.semantic_drift import SemanticDriftValidator
from bumpers.validators.base import FailStrategy

# Configure API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyBIql6exKxd8uhLjsz27OKKWwBiW9hI5X8"

# Set up Bumpers validation
logger = FileLogger("logs")
validation_engine = CoreValidationEngine(logger=logger)

# Create and register the vision validator for safety
vision_validator = VisionValidator(
    prompt="""
    Make sure the screenshot doesn't ask for my social security number.
    """,
    api_key=os.environ["GOOGLE_API_KEY"],
    fail_strategy=FailStrategy.RAISE_ERROR
)

# Create and register the semantic drift validator
drift_validator = SemanticDriftValidator(
    initial_goal="Find me the cheapest flight to LAX",
    api_key=os.environ["GOOGLE_API_KEY"],
    drift_threshold=0.7,  # We'll allow some deviation but not too much
    fail_strategy=FailStrategy.RAISE_ERROR  # Stop the agent if it drifts too far
)

# Register both validators
validation_engine.register_validator(vision_validator, ValidationPoint.PRE_ACTION)
validation_engine.register_validator(drift_validator, ValidationPoint.PRE_ACTION)

def test_validators():
    # Test cases with different screenshots
    test_cases = [
        {
            "name": "Flight Search",
            "image": "image.png"
        }
    ]
    
    for test in test_cases:
        try:
            print(f"\nTesting: {test['name']}")
            print("=" * 50)
            
            # Read the image
            with open(test["image"], "rb") as f:
                screenshot_data = f.read()
            
            # Create context with screenshot
            context = {
                "screenshot": screenshot_data,
                "action": "process_page"
            }
            
            # Run validation
            results = validation_engine.validate(ValidationPoint.PRE_ACTION, context)
            
            # Print results from both validators
            for result in results:
                print(f"\nValidator: {result.validator_name}")
                print("-" * 30)
                print(f"Passed: {result.passed}")
                print(f"Message:\n{result.message}")
                
                if not result.passed:
                    print("\nAnalysis Details:")
                    print(result.context.get("analysis", {}))
                    
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"Error during validation: {str(e)}")

if __name__ == "__main__":
    test_validators()
