from datetime import timedelta
from typing import List
from ..logging.base import LogEvent
from .monitor import AlertCondition

def create_high_failure_rate_condition(
    threshold: float = 0.3,
    window: timedelta = timedelta(minutes=15)
) -> AlertCondition:
    """Alert when validation failure rate exceeds threshold"""
    def check_failure_rate(events: List[LogEvent]) -> bool:
        validation_events = [e for e in events if e.event_type == 'validation']
        if not validation_events:
            return False
        
        failed = len([e for e in validation_events if e.status == 'fail'])
        rate = failed / len(validation_events)
        return rate > threshold
        
    return AlertCondition(
        name="high_failure_rate",
        condition_fn=check_failure_rate,
        alert_message=f"Validation failure rate exceeded {threshold*100}%",
        cooldown=window
    )
    
def create_repeated_intervention_condition(
    action: str,
    count: int = 3,
    window: timedelta = timedelta(minutes=5)
) -> AlertCondition:
    """Alert when same action is blocked multiple times"""
    def check_repeated_blocks(events: List[LogEvent]) -> bool:
        blocks = [
            e for e in events 
            if (e.event_type == 'intervention' and 
                e.context.get('intervention_type') == 'block_action' and
                e.context.get('action') == action)
        ]
        return len(blocks) >= count
        
    return AlertCondition(
        name=f"repeated_{action}_blocks",
        condition_fn=check_repeated_blocks,
        alert_message=f"Action '{action}' blocked {count} times in {window}",
        cooldown=window
    ) 