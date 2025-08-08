from typing import Dict, Any
from ..state import AgentState
from ..utils.llm_client import LLMClient


def generate_draft_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.input_message:
        raise ValueError("No input message found in state")
    
    llm_client = LLMClient()
    
    context_text = "\n".join(agent_state.retrieved_context) if agent_state.retrieved_context else ""
    
    prompt = f"""
You are a professional customer support representative. Generate a polite, formal email reply based on the following:

ORIGINAL MESSAGE:
From: {agent_state.input_message.sender}
Subject: {agent_state.input_message.subject}
Body: {agent_state.input_message.body}

RELEVANT CONTEXT:
{context_text}

Instructions:
- Be professional and empathetic
- Address the customer's concerns directly
- Use the context information to provide accurate details
- Keep the tone formal but friendly
- End with an offer for further assistance

Generate only the email body (do not include headers like To:, From:, Subject:):
"""
    
    draft_reply = llm_client.generate_response(prompt)
    agent_state.draft_reply = draft_reply
    
    print("✍️ Generated draft reply using LLM")
    
    return agent_state.to_dict()