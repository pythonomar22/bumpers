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
from bumpers.validators.base import FailStrategy

# Configure API keys
os.environ["GEMINI_API_KEY"] = "AIzaSyCodmhT1wjBPsVSw94RAIRqBVkkdtQ-jl4"

# Set up Bumpers validation
logger = FileLogger("logs")
validation_engine = CoreValidationEngine(logger=logger)

# Create and register the vision validator
vision_validator = VisionValidator(
    prompt="""
    Make sure the screenshot doesn't ask for my social security number.
    """,
    api_key=os.environ["GEMINI_API_KEY"],  # Pass the key explicitly
    fail_strategy=FailStrategy.RAISE_ERROR
)

validation_engine.register_validator(vision_validator, ValidationPoint.PRE_ACTION)

def test_vision_validation():
    # Load a test image
    image_path = "shouldfail.png"  # Replace with your image path
    
    try:
        # Read the image
        with open(image_path, "rb") as f:
            screenshot_data = f.read()
        
        # Create context with screenshot
        context = {
            "screenshot": screenshot_data,
            "action": "process_page",
            "description": "Testing vision validation"
        }
        
        # Run validation
        result = validation_engine.validate(ValidationPoint.PRE_ACTION, context)
        
        print("\nVision Validation Results:")
        print("=" * 50)
        print(f"Passed: {result[0].passed}")
        print(f"Message:\n{result[0].message}")
        print("-" * 50)
        
        if not result[0].passed:
            print("Analysis Details:")
            print(result[0].context.get("analysis", {}))
            
    except Exception as e:
        print(f"Error during vision validation: {str(e)}")

if __name__ == "__main__":
    test_vision_validation()
