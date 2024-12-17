from typing import Dict, Any, Optional, List
from ..core.engine import CoreValidationEngine, ValidationPoint, ValidationError
import re

class GuardedReActAgent:
    def __init__(self, validation_engine: CoreValidationEngine, bot_class, prompt: str, max_turns: int = 5):
        self.validation_engine = validation_engine
        self.bot_class = bot_class
        self.prompt = prompt
        self.max_turns = max_turns
        self.action_re = re.compile(r'^Action: (\w+): (.*)$')
        
    def _validate_action(self, action: str, action_input: str, context: Dict[str, Any]) -> bool:
        """Validate an action before execution"""
        validation_context = {
            "action": action,
            "action_input": action_input,
            **context
        }
        
        try:
            self.validation_engine.validate(ValidationPoint.PRE_ACTION, validation_context)
            return True
        except ValidationError as e:
            print(f"Action validation failed: {e.result.message}")
            return False
            
    def _validate_output(self, output: str, context: Dict[str, Any]) -> bool:
        """Validate the final output before returning to user"""
        validation_context = {
            "output": output,
            **context
        }
        
        try:
            self.validation_engine.validate(ValidationPoint.PRE_OUTPUT, validation_context)
            return True
        except ValidationError as e:
            print(f"Output validation failed: {e.result.message}")
            return False
    
    def query(self, question: str, known_actions: Dict[str, callable]) -> List[Dict[str, str]]:
        """
        Execute a query with bumpers enforcement
        """
        i = 0
        bot = self.bot_class(system=self.prompt)
        next_prompt = question
        
        while i < self.max_turns:
            i += 1
            result = bot(next_prompt)
            print(result)
            
            # Extract actions from result
            actions = [self.action_re.match(a) for a in result.split('\n') 
                      if self.action_re.match(a)]
            
            if actions:
                # There is an action to run
                action, action_input = actions[0].groups()
                
                # Validate action before execution
                if not self._validate_action(action, action_input, 
                                          {"question": question, "turn": i}):
                    # If validation fails, we could:
                    # 1. Try to get another action from the agent
                    next_prompt = "The previous action was not allowed. Please try a different approach."
                    continue
                    
                if action not in known_actions:
                    print(f"Unknown action: {action}: {action_input}")
                    next_prompt = "That action is not available. Please try something else."
                    continue
                    
                print(f" -- running {action} {action_input}")
                observation = known_actions[action](action_input)
                print("Observation:", observation)
                
                # Validate observation before sending back to agent
                if not self._validate_output(str(observation), 
                                          {"question": question, "turn": i}):
                    next_prompt = "The previous observation was invalid. Please try a different approach."
                    continue
                    
                next_prompt = f"Observation: {observation}"
            else:
                # No more actions, validate final answer
                if self._validate_output(result, {"question": question, "turn": i}):
                    return bot.messages
                else:
                    # If final answer validation fails, could try to get a new answer
                    next_prompt = "Please revise your answer and try again."
                    continue
                    
        return bot.messages 