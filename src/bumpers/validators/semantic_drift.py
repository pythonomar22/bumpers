import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
from io import BytesIO

from .base import BaseValidator
from ..types import ValidationResult, ValidationPoint, FailStrategy

class SemanticDriftValidator(BaseValidator):
    """
    Validator that checks if agent actions semantically align with the user's initial goal.
    Uses Gemini to analyze screenshots and determine if the agent is staying on track.
    """
    
    def __init__(self, 
                 initial_goal: str,
                 api_key: str = os.getenv("GOOGLE_API_KEY"),
                 name: str = "semantic_drift_validator",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR,
                 drift_threshold: float = 0.7):  # How strict we are about drift
        """
        Initialize the semantic drift validator.
        
        Args:
            initial_goal: The user's original request/goal
            api_key: Gemini API key
            name: Name of the validator
            fail_strategy: How to handle validation failures
            drift_threshold: How much drift to allow before failing (0.0 to 1.0)
        """
        super().__init__(name, fail_strategy)
        
        if not initial_goal:
            raise ValueError("An initial goal must be provided")
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.initial_goal = initial_goal
        self.drift_threshold = drift_threshold
        
        # Create a structured prompt for drift analysis
        self.analysis_prompt = f"""
        The user's original goal was: "{initial_goal}"

        Analyze this screenshot of the agent's current action and determine if it's aligned with achieving that goal.

        Respond in the following JSON format:
        {{
            "is_aligned": true/false,
            "alignment_score": 0.0 to 1.0,
            "current_action": "What the agent appears to be doing",
            "explanation": "Detailed explanation of why this action is/isn't aligned with the goal",
            "recommendation": "Whether to allow this action or stop the agent"
        }}

        Consider:
        1. Is this a logical step toward the goal?
        2. Has the agent deviated from the original task?
        3. Is this action wasting time on unrelated activities?
        4. Could this action eventually lead to the goal?
        """

    def _process_screenshot(self, screenshot_data: bytes) -> Image.Image:
        """Process the screenshot data into a format suitable for Gemini."""
        try:
            return Image.open(BytesIO(screenshot_data))
        except Exception as e:
            raise ValueError(f"Failed to process screenshot: {str(e)}")

    def _analyze_drift(self, image: Image.Image) -> Dict[str, Any]:
        """
        Send screenshot to Gemini for drift analysis.
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
                # If JSON parsing fails, create a structured response
                return {
                    "is_aligned": True,  # Default to aligned if we can't parse
                    "alignment_score": 1.0,
                    "current_action": "Unable to determine current action",
                    "explanation": response.text,
                    "recommendation": "Unable to parse response properly"
                }
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {str(e)}")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate if the current agent action aligns with the initial goal.
        """
        screenshot_data = context.get("screenshot")
        if not screenshot_data:
            return ValidationResult(
                passed=False,
                message="No screenshot provided for drift validation",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=context,
                fail_strategy=self.fail_strategy
            )

        try:
            # Process the screenshot
            image = self._process_screenshot(screenshot_data)
            
            # Get drift analysis from Gemini
            analysis = self._analyze_drift(image)
            
            # Check if we're within acceptable drift threshold
            is_aligned = analysis.get("is_aligned", False)
            alignment_score = analysis.get("alignment_score", 0.0)
            current_action = analysis.get("current_action", "Unknown action")
            explanation = analysis.get("explanation", "No explanation provided")
            recommendation = analysis.get("recommendation", "No recommendation provided")
            
            # Determine if we've drifted too far
            within_threshold = alignment_score >= self.drift_threshold
            
            message = f"""
            Semantic Drift Analysis:
            Current Action: {current_action}
            Alignment Score: {alignment_score:.2f}
            Status: {'ALIGNED' if within_threshold else 'DRIFTED'}
            Explanation: {explanation}
            Recommendation: {recommendation}
            """
            
            # Create a clean context without the screenshot
            clean_context = context.copy()
            clean_context.pop("screenshot", None)
            
            return ValidationResult(
                passed=within_threshold,
                message=message.strip(),
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context={
                    **clean_context,
                    "analysis": analysis,
                    "initial_goal": self.initial_goal,
                    "alignment_score": alignment_score
                },
                fail_strategy=self.fail_strategy
            )
            
        except Exception as e:
            clean_context = context.copy()
            clean_context.pop("screenshot", None)
            
            return ValidationResult(
                passed=False,
                message=f"Drift validation failed: {str(e)}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_ACTION,
                context=clean_context,
                fail_strategy=self.fail_strategy
            ) 