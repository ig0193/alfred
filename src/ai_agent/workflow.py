from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import AgentState, ActionType
from .nodes.receive_message import receive_message_node
from .nodes.classify_action import classify_action_node
from .nodes.retrieve_context import retrieve_context_node
from .nodes.gmail_draft import gmail_draft_node
from .nodes.meeting_draft import meeting_draft_node
from .nodes.no_op import no_op_node
from .nodes.save_draft import save_draft_node


def create_workflow() -> StateGraph:
    workflow = StateGraph(dict)
    
    workflow.add_node("receive_message", receive_message_node)
    workflow.add_node("classify_action", classify_action_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("gmail_draft", gmail_draft_node)
    workflow.add_node("meeting_draft", meeting_draft_node)
    workflow.add_node("no_op", no_op_node)
    workflow.add_node("save_draft", save_draft_node)
    
    workflow.set_entry_point("receive_message")
    
    workflow.add_edge("classify_action", "retrieve_context")
    
    workflow.add_conditional_edges(
        "retrieve_context",
        _route_to_action_handler,
        {
            "gmail_draft": "gmail_draft",
            "meeting_draft": "meeting_draft",
            "no_op": "no_op"
        }
    )
    workflow.add_conditional_edges('receive_message',
    _empty_input_message_handler, {
       "classify_action": "classify_action",
       "no_op": "no_op"
    })
    
    workflow.add_edge("gmail_draft", "save_draft")
    workflow.add_edge("meeting_draft", "save_draft")
    workflow.add_edge("no_op", END)
    workflow.add_edge("save_draft", END)
    
    return workflow.compile()

def _empty_input_message_handler(state: Dict[str, Any]) -> str:
    agent_state = AgentState.from_dict(state)
    if agent_state.input_message is None:
        return "no_op"
    else:
        return "classify_action"

def _route_to_action_handler(state: Dict[str, Any]) -> str:
    agent_state = AgentState.from_dict(state)
    
    if agent_state.action_type == ActionType.EMAIL_REPLY:
        return "gmail_draft"
    elif agent_state.action_type == ActionType.SCHEDULE_MEETING:
        return "meeting_draft"
    else:
        return "no_op"


async def run_workflow(initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
    if initial_state is None:
        initial_state = {}
    
    app = create_workflow()
    
    print("Starting AI Agent Workflow...")
    print("-" * 50)
    
    final_state = await app.ainvoke(initial_state)
    
    print("\nWorkflow completed successfully!")
    print(f"Final state keys: {list(final_state.values())}")
    
    return final_state