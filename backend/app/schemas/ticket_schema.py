"""
Ticket request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.ticket import TicketPriority, TicketStatus, TicketCategory


class TicketCreateRequest(BaseModel):
    """Request to create a new ticket."""
    employee_id: str = Field(..., description="Employee creating the ticket")
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    category: TicketCategory = Field(default=TicketCategory.GENERAL)
    priority: Optional[TicketPriority] = Field(default=None, description="Auto-assigned if not provided")
    conversation_id: Optional[str] = Field(default=None, description="Link to chat conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP-001",
                "subject": "VPN Connection Timeout",
                "description": "Getting timeout error when connecting to corporate VPN from home network.",
                "category": "vpn",
                "priority": "high"
            }
        }


class TicketUpdateRequest(BaseModel):
    """Request to update an existing ticket."""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    comment: Optional[str] = Field(default=None, description="Add a comment to the ticket")
    tags: Optional[List[str]] = None


class TicketResponse(BaseModel):
    """Full ticket response."""
    ticket_id: str
    employee_id: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_to: Optional[str] = None
    conversation_id: Optional[str] = None
    comments: List[dict] = []
    resolution_notes: Optional[str] = None
    escalation_reason: Optional[str] = None
    tags: List[str] = []
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None


class TicketListResponse(BaseModel):
    """Paginated list of tickets."""
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TicketStatsResponse(BaseModel):
    """Dashboard ticket statistics."""
    total_tickets: int = 0
    open_tickets: int = 0
    in_progress_tickets: int = 0
    resolved_tickets: int = 0
    escalated_tickets: int = 0
    closed_tickets: int = 0
    resolved_today: int = 0
    avg_resolution_hours: Optional[float] = None
    tickets_by_category: dict = {}
    tickets_by_priority: dict = {}
