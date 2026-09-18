"""
Chat conversation data model.
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class MessageMetadata(BaseModel):
    """Metadata attached to a message."""
    intent: Optional[str] = None
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None
    ticket_id: Optional[str] = None
    escalation: Optional[bool] = None
    troubleshooting_step: Optional[int] = None


class Message(BaseModel):
    """A single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[MessageMetadata] = None


class Conversation(BaseModel):
    """Chat conversation model."""

    conversation_id: str = Field(..., description="Unique conversation ID")
    employee_id: str = Field(..., description="Employee in this conversation")
    messages: List[Message] = Field(default_factory=list)
    current_intent: Optional[str] = Field(default=None, description="Current detected intent")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    resolution_count: int = Field(default=0, description="Number of resolution attempts")
    linked_ticket_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "CONV-abc123",
                "employee_id": "EMP-001",
                "messages": [
                    {"role": "user", "content": "I can't connect to the VPN"},
                    {"role": "agent", "content": "I'd be happy to help you troubleshoot your VPN connection."}
                ],
                "current_intent": "vpn_issue",
                "status": "active"
            }
        }

    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        data = self.model_dump()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        for msg in data["messages"]:
            if isinstance(msg["timestamp"], datetime):
                msg["timestamp"] = msg["timestamp"].isoformat()
        return data

    @classmethod
    def from_mongo(cls, doc: dict) -> "Conversation":
        """Create Conversation from MongoDB document."""
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)

    def add_message(self, role: MessageRole, content: str, metadata: Optional[MessageMetadata] = None):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content, metadata=metadata))
        self.updated_at = datetime.now(timezone.utc)
