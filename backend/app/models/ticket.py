"""
Support ticket data model.
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    VPN = "vpn"
    PASSWORD = "password"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    EMAIL = "email"
    ACCESS = "access"
    GENERAL = "general"


class TicketComment(BaseModel):
    """A comment/update on a ticket."""
    author: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ticket(BaseModel):
    """Support ticket model."""

    ticket_id: str = Field(..., description="Unique ticket ID (e.g., TKT-20240101-001)")
    employee_id: str = Field(..., description="Employee who created the ticket")
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    category: TicketCategory = Field(default=TicketCategory.GENERAL)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    assigned_to: Optional[str] = Field(default=None, description="Assigned support agent")
    conversation_id: Optional[str] = Field(default=None, description="Linked chat conversation")
    comments: List[TicketComment] = Field(default_factory=list)
    resolution_notes: Optional[str] = Field(default=None)
    escalation_reason: Optional[str] = Field(default=None)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TKT-20240101-001",
                "employee_id": "EMP-001",
                "subject": "Cannot connect to VPN",
                "description": "Getting timeout error when trying to connect to corporate VPN from home.",
                "category": "vpn",
                "priority": "high",
                "status": "open",
            }
        }

    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        data = self.model_dump()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        data["comments"] = [
            {**c, "timestamp": c["timestamp"].isoformat() if isinstance(c["timestamp"], datetime) else c["timestamp"]}
            for c in data["comments"]
        ]
        return data

    @classmethod
    def from_mongo(cls, doc: dict) -> "Ticket":
        """Create Ticket from MongoDB document."""
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
