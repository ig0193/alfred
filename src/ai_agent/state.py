from re import S
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class InputType(str, Enum):
    EMAIL = "email"
    COMMAND = "command"


class ActionType(str, Enum):
    EMAIL_REPLY = "email_reply"
    SCHEDULE_MEETING = "schedule_meeting"
    NO_OP = "no_op"
    UNKNOWN = "unknown"


class Message(BaseModel):
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: str
    timestamp: Optional[str] = None
    input_type: InputType = InputType.EMAIL
    source: str = "gmail"  # gmail, cli, api


class AgentState(BaseModel):
    input_message: Optional[Message] = None
    action_type: Optional[ActionType] = None
    action_confidence: Optional[float] = None
    tool: Optional[str] = None
    retrieved_context: Optional[List[str]] = Field(default_factory=list)
    draft_reply: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_message": self.input_message.dict() if self.input_message else None,
            "action_type": self.action_type.value if self.action_type else None,
            "action_confidence": self.action_confidence,
            "tool": self.tool,
            "retrieved_context": self.retrieved_context,
            "draft_reply": self.draft_reply,
            "result": self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        input_message = None
        if data.get("input_message"):
            input_message = Message(**data["input_message"])
        
        action_type = None
        if data.get("action_type"):
            action_type = ActionType(data["action_type"])
        
        return cls(
            input_message=input_message,
            action_type=action_type,
            action_confidence=data.get("action_confidence"),
            tool=data.get("tool"),
            retrieved_context=data.get("retrieved_context", []),
            draft_reply=data.get("draft_reply"),
            result=data.get("result")
        )