from typing import Dict, Any
from ..state import AgentState


def no_op_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    agent_state.result = {
        "type": "no_op",
        "message": "No action required for this input",
        "reason": "Not classified as any action"
    }
    
    print("No action required - message classified as NO_OP")
    
    return agent_state.to_dict()