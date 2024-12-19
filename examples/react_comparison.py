from bumpers.validators.llm_safety import LLMSafetyValidator

# In the validator setup section:
llm_safety = LLMSafetyValidator()

# Register the validator for both pre-action and pre-output validation
cve.register_validator(llm_safety, ValidationPoint.PRE_ACTION)
cve.register_validator(llm_safety, ValidationPoint.PRE_OUTPUT) 