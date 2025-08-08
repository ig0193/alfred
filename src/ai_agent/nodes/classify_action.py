from typing import Dict, Any
from ..state import AgentState, ActionType, InputType
from ..utils.llm_client import LLMClient


def classify_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    if not agent_state.input_message:
        raise ValueError("No input message found in state")
    
    message = agent_state.input_message
    
    # Direct routing for automatic scraped messages
    if message.source == "gmail":
        action_type, confidence = _classify_scraped_action(message)
    elif message.source == "cli":
        action_type, confidence = _classify_user_command(message)
        print(f"Classified CLI command: {action_type.value} (confidence: {confidence:.2f})")
    else:
        action_type, confidence = ActionType.NO_OP, 1.0

    
    agent_state.action_type = action_type
    agent_state.action_confidence = confidence
    
    return agent_state.to_dict()


def _classify_scraped_action(message) -> tuple[ActionType, float]:
    llm_client = LLMClient()
    
    prompt = f"""
        Analyze this email and classify the required action.
        Return only the action type and confidence score.

        EMAIL:
        From: {message.sender}
        Subject: {message.subject}
        Body: {message.body}

        ACTIONS:
        - EMAIL_REPLY: Email requires a substantive response
        - NO_OP: Newsletters, notifications, spam, or emails that don't need replies  

        Return format: ACTION_TYPE:CONFIDENCE_SCORE
        Example: EMAIL_REPLY:0.95
        Response:
        """
    
    try:
        response = llm_client.generate_response(prompt)
        
        if "EMAIL_REPLY" in response.upper():
            return ActionType.EMAIL_REPLY, 0.9
        else:
            return ActionType.NO_OP, 1.0
    except Exception as e:
        print(f"LLM classification failed: {e}, falling back to rules")
        return ActionType.NO_OP, 1.0


# todo
def _classify_user_command(message) -> tuple[ActionType, float]:
    llm_client = LLMClient()
    print(message)
    prompt = f"""
        Analyze this command and classify the required action.
        Return only the action type and confidence score.

        Command:
        {message}

        ACTIONS:
        - SETUP_CALENDAR_INVITE: Setup calendar invite
        - NO_OP: None of the other actions  

        Return format: ACTION_TYPE:CONFIDENCE_SCORE
        Example: SETUP_CALENDAR_INVITE:0.95
        Response:
        """
    
    try:
        response = llm_client.generate_response(prompt)
        
        return ActionType.NO_OP, 1.0
    except Exception as e:
        print(f"LLM classification failed: {e}, falling back to rules")
        return ActionType.NO_OP, 1.0
    
    
    