from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
from ..logging.base import BaseLogger, LogEvent

class BumpersAnalyzer:
    def __init__(self, logger: BaseLogger):
        self.logger = logger
        
    def get_validation_stats(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate statistics about validations"""
        events = self.logger.get_events(
            start_time=start_time,
            end_time=end_time,
            event_type='validation'
        )
        
        stats = {
            'total_validations': len(events),
            'failed_validations': len([e for e in events if e.status == 'fail']),
            'validator_stats': Counter(e.validator_name for e in events),
            'failure_reasons': Counter(
                e.message for e in events if e.status == 'fail'
            ),
            'validation_points': Counter(e.validation_point for e in events)
        }
        
        return stats
        
    def get_intervention_summary(self,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze intervention patterns"""
        events = self.logger.get_events(
            start_time=start_time,
            end_time=end_time,
            event_type='intervention'
        )
        
        summary = {
            'total_interventions': len(events),
            'intervention_types': Counter(
                e.context.get('intervention_type') for e in events
            ),
            'blocked_actions': Counter(
                e.context.get('action') for e in events 
                if e.context.get('intervention_type') == 'block_action'
            )
        }
        
        return summary 