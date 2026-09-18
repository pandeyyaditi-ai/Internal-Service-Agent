"""
Chat request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """Incoming chat message from employee."""
    employee_id: str = Field(..., description="Employee sending the message")
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID, or None for new")

    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP-001",
                "message": "I can't connect to the VPN from home",
                "conversation_id": None
            }
        }


class SourceReferenceSchema(BaseModel):
    """A source reference for an FAQ/policy answer."""
    source_name: str = Field(..., description="Name of the source document")
    source_type: str = Field(default="faq", description="Type: faq, policy, guide")
    relevance_score: Optional[float] = Field(default=None, description="0.0 to 1.0")
    excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from source")


class ChatMessageResponse(BaseModel):
    """Agent's response to a chat message."""
    conversation_id: str
    message: str = Field(..., description="Agent's response text")
    intent: Optional[str] = Field(default=None, description="Detected intent")
    confidence: Optional[float] = Field(default=None, description="Intent confidence score")
    sources: Optional[List[SourceReferenceSchema]] = Field(default=None)
    ticket_id: Optional[str] = Field(default=None, description="Created/referenced ticket ID")
    escalated: bool = Field(default=False, description="Whether conversation was escalated")
    escalation_reason: Optional[str] = Field(default=None)
    troubleshooting_step: Optional[int] = Field(default=None, description="Current step in troubleshooting flow")
    suggested_actions: Optional[List[str]] = Field(default=None, description="Quick action suggestions")


class ConversationHistoryResponse(BaseModel):
    """Response containing conversation history."""
    conversation_id: str
    employee_id: str
    messages: List[Dict[str, Any]]
    status: str
    current_intent: Optional[str] = None
    created_at: str
    updated_at: str


class ConversationListItem(BaseModel):
    """Summary of a conversation for list view."""
    conversation_id: str
    employee_id: str
    last_message: Optional[str] = None
    status: str
    current_intent: Optional[str] = None
    message_count: int = 0
    created_at: str
    updated_at: str
