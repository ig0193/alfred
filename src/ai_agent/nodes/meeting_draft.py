from typing import Dict, Any
import re
from datetime import datetime, timedelta
from ..state import AgentState
from ..utils.llm_client import LLMClient


def meeting_draft_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.input_message:
        raise ValueError("No input message found in state")
    
    message = agent_state.input_message
    context_text = "\n".join(agent_state.retrieved_context or [])
    
    meeting_details = _extract_meeting_details(message.body)
    
    llm_client = LLMClient()
    
    prompt = f"""
Based on this meeting request, generate a structured meeting invitation.

REQUEST: {message.body}

CONTEXT:
{context_text}

EXTRACTED DETAILS:
- Participants: {meeting_details.get('participants', 'Not specified')}
- Topic: {meeting_details.get('topic', 'Not specified')}
- Duration: {meeting_details.get('duration', '30 minutes')}
- Proposed Time: {meeting_details.get('time', 'Not specified')}

Generate:
1. Meeting title
2. Description/agenda
3. Recommended duration
4. Any preparation notes

Format as professional meeting invitation content:
"""
    
    meeting_content = llm_client.generate_response(prompt)
    
    draft_result = {
        "type": "meeting",
        "title": meeting_details.get('topic', 'Meeting'),
        "participants": meeting_details.get('participants', []),
        "proposed_time": meeting_details.get('time'),
        "duration": meeting_details.get('duration', '30 minutes'),
        "description": meeting_content,
        "location": "TBD - Will send calendar invite"
    }
    
    agent_state.result = draft_result
    agent_state.tool = "calendar"
    
    print("Generated meeting invitation draft")
    
    return agent_state.to_dict()


def _extract_meeting_details(command_text: str) -> Dict[str, Any]:
    details = {}
    
    command_lower = command_text.lower()
    
    participant_patterns = [
        r'with\s+([a-zA-Z\s]+?)(?:\s+about|\s+regarding|\s+on|\s+for|$)',
        r'meet\s+([a-zA-Z\s]+?)(?:\s+about|\s+regarding|\s+on|\s+for|$)'
    ]
    
    for pattern in participant_patterns:
        match = re.search(pattern, command_lower)
        if match:
            participant = match.group(1).strip()
            if len(participant) > 2 and len(participant) < 50:
                details['participants'] = [participant.title()]
                break
    
    topic_patterns = [
        r'about\s+([^,\n]+?)(?:\s+(?:next|on|at)|$)',
        r'regarding\s+([^,\n]+?)(?:\s+(?:next|on|at)|$)',
        r'for\s+([^,\n]+?)(?:\s+(?:next|on|at)|$)'
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, command_lower)
        if match:
            topic = match.group(1).strip()
            if len(topic) > 3:
                details['topic'] = topic.title()
                break
    
    time_patterns = [
        r'(next\s+\w+(?:\s+at\s+\d+(?::\d+)?\s*(?:am|pm)?)?)',
        r'(on\s+\w+(?:\s+at\s+\d+(?::\d+)?\s*(?:am|pm)?)?)',
        r'(at\s+\d+(?::\d+)?\s*(?:am|pm)?)',
        r'(\d+(?::\d+)?\s*(?:am|pm))'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, command_lower)
        if match:
            details['time'] = match.group(1).strip()
            break
    
    if 'planning' in command_lower or 'review' in command_lower:
        details['duration'] = '60 minutes'
    else:
        details['duration'] = '30 minutes'
    
    return details