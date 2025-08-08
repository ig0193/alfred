from typing import List, Dict, Optional
import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ai_agent.state import ActionType
except ImportError:
    ActionType = None


class MockContextStore:
    def __init__(self):
        self.email_context = {
            "system outage": [
                "RCA-2024-001: Database connection pool exhaustion caused by memory leak in connection driver.",
                "Prevention: Implemented connection pooling monitoring and automated restart procedures.",
                "SLA Impact: 99.9% uptime target maintained through quick response protocols."
            ],
            "production environment": [
                "Production deployment checklist updated after incident review.",
                "Monitoring thresholds adjusted for early detection of similar issues.",
                "Backup systems verified and tested monthly."
            ],
            "database outage": [
                "Database backup procedures verified and tested weekly.",
                "Payment processing failover systems activated during outages.",
                "Customer communication templates for service disruptions available."
            ],
            "customer communication": [
                "Professional response templates for customer inquiries available.",
                "Standard escalation procedures for urgent customer issues documented.",
                "Customer satisfaction surveys show 95% positive response to incident communications."
            ]
        }
        
        self.meeting_context = {
            "meeting scheduling": [
                "Standard meeting duration: 30 minutes for planning sessions, 60 minutes for reviews.",
                "Conference room availability: Check Outlook calendar for room bookings.",
                "Meeting best practices: Send agenda 24 hours in advance."
            ],
            "q1 planning": [
                "Q1 planning typically includes budget review, goal setting, and resource allocation.",
                "Previous Q1 planning meetings included: Sales targets, Marketing campaigns, Engineering roadmap.",
                "Recommended attendees for Q1 planning: Department heads, Project managers, Finance team."
            ],
            "team meetings": [
                "Weekly standup meetings: Mondays 9 AM, Conference Room A.",
                "Monthly all-hands meetings: First Friday of each month, Main auditorium.",
                "Quarterly reviews: End of each quarter, includes performance metrics and planning."
            ]
        }
        
    
    def fuzzy_search(self, query: str, action_type=None, threshold: float = 0.3) -> List[str]:
        if ActionType and action_type == ActionType.EMAIL_REPLY:
            context_data = self.email_context
        elif ActionType and action_type == ActionType.SCHEDULE_MEETING:
            context_data = self.meeting_context
        else:
            context_data = {**self.email_context, **self.meeting_context, **self.slack_context}
        
        query_lower = query.lower()
        results = []
        
        for key, contexts in context_data.items():
            if any(word in query_lower for word in key.split()):
                results.extend(contexts)
        
        query_words = set(re.findall(r'\w+', query_lower))
        for key, contexts in context_data.items():
            key_words = set(re.findall(r'\w+', key.lower()))
            overlap = len(query_words.intersection(key_words))
            if overlap >= max(1, len(key_words) * threshold):
                results.extend(contexts)
        
        return list(set(results))