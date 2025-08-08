from typing import Dict, Any
from datetime import datetime
from ..state import AgentState


def save_draft_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.result:
        raise ValueError("No result to save")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = agent_state.result
    
    print("\n" + "="*80)
    print("DRAFT GENERATED")
    print("="*80)
    
    if result["type"] == "email":
        print(f"Type: Gmail Email Reply")
        print(f"To: {result['to']}")
        print(f"Subject: {result['subject']}")
        print(f"Generated: {timestamp}")
        print("-"*80)
        print("Body:")
        print(result['body'])
        _save_email_draft(result, timestamp)
        
    elif result["type"] == "meeting":
        print(f"Type: Meeting Invitation")
        print(f"Title: {result['title']}")
        print(f"Participants: {', '.join(result.get('participants', []))}")
        print(f"Duration: {result.get('duration', 'TBD')}")
        print(f"Time: {result.get('proposed_time', 'TBD')}")
        print(f"Generated: {timestamp}")
        print("-"*80)
        print("Description:")
        print(result['description'])
        _save_meeting_draft(result, timestamp)
        
        
    elif result["type"] == "no_op":
        print(f"Type: No Action Required")
        print(f"Reason: {result['reason']}")
        print(f"Message: {result['message']}")
        
    print("="*80)
    print("Draft saved successfully (simulated)")
    
    return agent_state.to_dict()


def _save_email_draft(result: Dict[str, Any], timestamp: str):
    try:
        filename = f"/Users/indresh.gupta/Documents/ai-agent-langgraph/data/email_draft_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        with open(filename, "w") as f:
            f.write(f"Type: Gmail Email\n")
            f.write(f"To: {result['to']}\n")
            f.write(f"Subject: {result['subject']}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("-"*40 + "\n")
            f.write(result['body'])
        print(f"Email draft saved to file")
    except Exception as e:
        print(f"Could not save email draft: {e}")


def _save_meeting_draft(result: Dict[str, Any], timestamp: str):
    try:
        filename = f"/Users/indresh.gupta/Documents/ai-agent-langgraph/data/meeting_draft_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        with open(filename, "w") as f:
            f.write(f"Type: Meeting Invitation\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Participants: {', '.join(result.get('participants', []))}\n")
            f.write(f"Duration: {result.get('duration', 'TBD')}\n")
            f.write(f"Proposed Time: {result.get('proposed_time', 'TBD')}\n")
            f.write(f"Location: {result.get('location', 'TBD')}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("-"*40 + "\n")
            f.write(result['description'])
        print(f"Meeting draft saved to file")
    except Exception as e:
        print(f"Could not save meeting draft: {e}")
