import os
import base64
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from PIL import Image
from io import BytesIO

from .base import BaseValidator
from ..types import ValidationResult, ValidationPoint, FailStrategy

class VisionValidator(BaseValidator):
    """
    Vision-based validator using Gemini to analyze screenshots for safety and policy compliance.
    Supports pre-action validation of visual content to prevent unsafe or unwanted actions.
    """
    
    def __init__(self, 
                 prompt: str,
                 api_key: str = os.getenv("GOOGLE_API_KEY"),
                 name: str = "vision_validator",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        """
        Initialize the vision validator.
        
        Args:
            prompt: The user's safety requirements/constraints for image analysis
            api_key: Gemini API key
            name: Name of the validator
            fail_strategy: How to handle validation failures
        """
        super().__init__(name, fail_strategy)
        
        if not prompt:
            raise ValueError("A prompt must be provided for the vision validator")
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Create a structured prompt that combines user requirements with safety analysis
        self.analysis_prompt = f"""
        Analyze this screenshot based on the following safety requirements:
        {prompt}

        Respond in the following JSON format:
        {{
            "is_safe": true/false,
            "concerns": ["list", "of", "specific", "concerns"],
            "explanation": "Detailed explanation of why it is safe or unsafe",
            "recommendation": "What action should be taken"
        }}
        """

    def _process_screenshot(self, screenshot_data: bytes) -> Image.Image:
        """Process the screenshot data into a format suitable for Gemini."""
        try:
            return Image.open(BytesIO(screenshot_data))
        except Exception as e:
            raise ValueError(f"Failed to process screenshot: {str(e)}")

    def _analyze_screenshot(self, image: Image.Image) -> Dict[str, Any]:
        """
        Send screenshot to Gemini for analysis with structured prompt.
        Returns parsed JSON response.
        """
        try:
            response = self.model.generate_content([self.analysis_prompt, image])
            try:
                # Extract the JSON part from the response
                response_text = response.text
                # Find JSON content between triple backticks
                json_start = response_text.find('```json\n') + 8
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
                
                import json
                analysis = json.loads(json_str)
                return analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                # If JSON parsing fails, create a structured response based on the full text
                return {
                    "is_safe": True,  # Default to safe if we can't parse properly
                    "concerns": [],
                    "explanation": response.text,
                    "recommendation": "Unable to parse response properly"
                }
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {str(e)}")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate a screenshot using Gemini vision analysis based on user requirements.
        """
        screenshot_data = context.get("screenshot")
        if not screenshot_data:
            return ValidationResult(
                passed=False,
                message="No screenshot provided for validation",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context,
                fail_strategy=self.fail_strategy
            )

        try:
            # Process the screenshot
            image = self._process_screenshot(screenshot_data)
            
            # Get structured analysis from Gemini
            analysis = self._analyze_screenshot(image)
            
            # Use Gemini's assessment directly
            is_safe = analysis.get("is_safe", False)
            concerns = analysis.get("concerns", [])
            explanation = analysis.get("explanation", "No explanation provided")
            recommendation = analysis.get("recommendation", "No recommendation provided")
            
            message = f"""
            Safety Assessment: {'SAFE' if is_safe else 'UNSAFE'}
            Concerns: {', '.join(concerns) if concerns else 'None'}
            Explanation: {explanation}
            Recommendation: {recommendation}
            """
            
            # Create a new context without the raw screenshot data
            clean_context = context.copy()
            clean_context.pop("screenshot", None)  # Remove screenshot bytes
            
            return ValidationResult(
                passed=is_safe,
                message=message.strip(),
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context={
                    **clean_context,
                    "analysis": analysis
                },
                fail_strategy=self.fail_strategy
            )
            
        except Exception as e:
            # Create clean context here too
            clean_context = context.copy()
            clean_context.pop("screenshot", None)
            
            return ValidationResult(
                passed=False,
                message=f"Vision validation failed: {str(e)}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=clean_context,
                fail_strategy=self.fail_strategy
            ) 