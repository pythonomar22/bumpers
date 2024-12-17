from typing import Dict, Any
import yaml
from ..core.engine import ValidationPoint
from ..validators.action import ActionWhitelistValidator
from ..validators.content import ContentFilterValidator

class PolicyParser:
    @staticmethod
    def load_policy_file(filepath: str) -> Dict[str, Any]:
        """Load and parse a YAML policy file"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
            
    def create_validators(self, policy: Dict[str, Any]):
        """Create validator instances based on policy configuration"""
        validators = []
        
        if 'validators' not in policy:
            return validators
            
        for validator_config in policy['validators']:
            validator_type = validator_config.get('type')
            if validator_type == 'ActionWhitelist':
                validators.append(
                    ActionWhitelistValidator(
                        allowed_actions=validator_config['parameters']['allowed_actions'],
                        name=validator_config.get('name', 'action_whitelist')
                    )
                )
            elif validator_type == 'ContentFilter':
                validators.append(
                    ContentFilterValidator(
                        forbidden_words=validator_config['parameters'].get('forbidden_words'),
                        max_length=validator_config['parameters'].get('max_length'),
                        name=validator_config.get('name', 'content_filter')
                    )
                )
                
        return validators 