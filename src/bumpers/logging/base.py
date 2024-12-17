from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class LogEvent:
    timestamp: datetime
    event_type: str  # 'validation', 'action', 'intervention'
    validation_point: str
    validator_name: Optional[str]
    status: str  # 'pass', 'fail', 'error'
    message: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'validation_point': self.validation_point,
            'validator_name': self.validator_name,
            'status': self.status,
            'message': self.message,
            'context': self.context
        }

class BaseLogger(ABC):
    @abstractmethod
    def log_event(self, event: LogEvent):
        """Log a single event"""
        pass
        
    @abstractmethod
    def get_events(self, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  event_type: Optional[str] = None) -> List[LogEvent]:
        """Retrieve events matching the given criteria"""
        pass 