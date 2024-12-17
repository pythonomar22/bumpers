import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from .base import BaseLogger, LogEvent

class FileLogger(BaseLogger):
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_log_file = os.path.join(
            log_dir, 
            f"bumpers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )
        
    def log_event(self, event: LogEvent):
        """Log event to a JSONL file"""
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
            
    def get_events(self,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  event_type: Optional[str] = None) -> List[LogEvent]:
        """Read and filter events from log file"""
        events = []
        
        with open(self.current_log_file, 'r') as f:
            for line in f:
                event_dict = json.loads(line.strip())
                event_time = datetime.fromisoformat(event_dict['timestamp'])
                
                if start_time and event_time < start_time:
                    continue
                if end_time and event_time > end_time:
                    continue
                if event_type and event_dict['event_type'] != event_type:
                    continue
                    
                events.append(LogEvent(**event_dict))
                
        return events 