from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import time
from ..logging.base import BaseLogger, LogEvent

class AlertCondition:
    def __init__(self, 
                 name: str,
                 condition_fn: Callable[[List[LogEvent]], bool],
                 alert_message: str,
                 cooldown: timedelta = timedelta(minutes=5)):
        self.name = name
        self.condition_fn = condition_fn
        self.alert_message = alert_message
        self.cooldown = cooldown
        self.last_triggered = None
        
    def check(self, events: List[LogEvent]) -> Optional[str]:
        if self.condition_fn(events):
            now = datetime.now()
            if (not self.last_triggered or 
                now - self.last_triggered > self.cooldown):
                self.last_triggered = now
                return self.alert_message
        return None

class BumpersMonitor:
    def __init__(self, 
                 logger: BaseLogger,
                 alert_handlers: List[Callable[[str], None]],
                 check_interval: int = 60):
        self.logger = logger
        self.alert_handlers = alert_handlers
        self.check_interval = check_interval
        self.conditions: List[AlertCondition] = []
        self._stop_flag = False
        self._monitor_thread = None
        
    def add_condition(self, condition: AlertCondition):
        """Add a monitoring condition"""
        self.conditions.append(condition)
        
    def _check_conditions(self):
        """Check all monitoring conditions"""
        # Get recent events (last hour)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        events = self.logger.get_events(start_time=start_time)
        
        for condition in self.conditions:
            if alert := condition.check(events):
                for handler in self.alert_handlers:
                    handler(alert)
                    
    def start(self):
        """Start the monitoring thread"""
        def monitor_loop():
            while not self._stop_flag:
                self._check_conditions()
                time.sleep(self.check_interval)
                
        self._monitor_thread = threading.Thread(target=monitor_loop)
        self._monitor_thread.start()
        
    def stop(self):
        """Stop the monitoring thread"""
        self._stop_flag = True
        if self._monitor_thread:
            self._monitor_thread.join() 