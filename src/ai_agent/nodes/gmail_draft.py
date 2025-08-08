from typing import Dict, Any
from ..state import AgentState, ActionType
from ..utils.llm_client import LLMClient


def gmail_draft_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.input_message:
        raise ValueError("No input message found in state")
    
    llm_client = LLMClient()
    message = agent_state.input_message
    context_text = "\n".join(agent_state.retrieved_context or [])
    
    prompt = f"""
You are a professional customer support representative. Generate a polite, formal email reply.

ORIGINAL MESSAGE:
From: {message.sender}
Subject: {message.subject}
Body: {message.body}

RELEVANT CONTEXT:
{context_text}

Instructions:
- Be professional and empathetic
- Address the customer's concerns directly  
- Use the context information to provide accurate details
- Keep the tone formal but friendly
- End with an offer for further assistance
- Do not include email headers (To:, From:, Subject:)

Generate only the email body:
"""
    
    draft_body = llm_client.generate_response(prompt)
    
    draft_result = {
        "type": "email",
        "to": message.sender,
        "subject": f"Re: {message.subject}",
        "body": draft_body,
        "original_message_id": getattr(message, 'message_id', None)
    }
    
    agent_state.result = draft_result
    agent_state.tool = "gmail"
    
    print("Generated Gmail draft reply")
    
    return agent_state.to_dict()