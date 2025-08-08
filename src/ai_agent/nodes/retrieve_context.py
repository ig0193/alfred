from typing import Dict, Any
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from data.context_store import MockContextStore
from ..state import AgentState, ActionType


def retrieve_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.input_message or not agent_state.action_type:
        raise ValueError("Missing input message or action type in state")
    
    if agent_state.action_type == ActionType.NO_OP:
        agent_state.retrieved_context = []
        print("Skipping context retrieval for NO_OP action")
        return agent_state.to_dict()
    
    context_store = MockContextStore()
    
    search_text = _build_search_query(agent_state)
    relevant_contexts = context_store.fuzzy_search(search_text, action_type=agent_state.action_type)
    
    agent_state.retrieved_context = relevant_contexts
    
    print(f"Retrieved {len(relevant_contexts)} context items for {agent_state.action_type.value}:")
    for i, context in enumerate(relevant_contexts[:3], 1):
        print(f"   {i}. {context[:80]}...")
    
    return agent_state.to_dict()


def _build_search_query(agent_state: AgentState) -> str:
    message = agent_state.input_message
    print(message)
    
    if agent_state.action_type == ActionType.EMAIL_REPLY:
        return f"{message.subject or ''} {message.body}"
    else:
        return message.body