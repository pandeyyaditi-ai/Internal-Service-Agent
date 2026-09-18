"""
Audit log data model for compliance tracking.
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum


class AuditActionType(str, Enum):
    CHAT_MESSAGE_RECEIVED = "chat_message_received"
    CHAT_RESPONSE_SENT = "chat_response_sent"
    INTENT_DETECTED = "intent_detected"
    FAQ_SEARCHED = "faq_searched"
    TROUBLESHOOTING_STARTED = "troubleshooting_started"
    TROUBLESHOOTING_STEP = "troubleshooting_step"
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    TICKET_RESOLVED = "ticket_resolved"
    TICKET_CLOSED = "ticket_closed"
    ESCALATION_TRIGGERED = "escalation_triggered"
    ESCALATION_RESOLVED = "escalation_resolved"
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_CLOSED = "conversation_closed"
    SYSTEM_ERROR = "system_error"


class AuditActor(str, Enum):
    AGENT = "agent"
    EMPLOYEE = "employee"
    SYSTEM = "system"


class AuditLog(BaseModel):
    """Audit log entry for tracking all agent actions."""

    audit_id: str = Field(..., description="Unique audit entry ID")
    action_type: AuditActionType = Field(..., description="Type of action performed")
    actor: AuditActor = Field(..., description="Who performed the action")
    actor_id: Optional[str] = Field(default=None, description="ID of the actor (employee_id or 'system')")
    target_entity: Optional[str] = Field(default=None, description="Entity affected (ticket_id, conversation_id)")
    target_type: Optional[str] = Field(default=None, description="Type of target entity")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context/details")
    ip_address: Optional[str] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "AUD-20240101-001",
                "action_type": "ticket_created",
                "actor": "agent",
                "actor_id": "system",
                "target_entity": "TKT-20240101-001",
                "target_type": "ticket",
                "details": {"subject": "VPN issue", "priority": "high"},
            }
        }

    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        data = self.model_dump()
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_mongo(cls, doc: dict) -> "AuditLog":
        """Create AuditLog from MongoDB document."""
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
