"""
Ticket API routes — CRUD operations for support tickets.
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.schemas.ticket_schema import (
    TicketCreateRequest, TicketUpdateRequest,
    TicketResponse, TicketListResponse, TicketStatsResponse
)
from app.schemas.response_schema import APIResponse
from app.services.ticket_service import (
    create_ticket, get_ticket, get_tickets, update_ticket, get_ticket_stats
)
from app.services.audit_service import log_action
from app.models.audit import AuditActionType, AuditActor
from app.models.ticket import TicketStatus, TicketPriority
from app.core.logging import get_logger

logger = get_logger("ticket_routes")
router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=APIResponse)
async def create_new_ticket(request: TicketCreateRequest):
    """Create a new support ticket."""
    try:
        ticket = await create_ticket(
            employee_id=request.employee_id,
            subject=request.subject,
            description=request.description,
            category=request.category,
            priority=request.priority,
            conversation_id=request.conversation_id,
        )

        await log_action(
            action_type=AuditActionType.TICKET_CREATED,
            actor=AuditActor.EMPLOYEE,
            actor_id=request.employee_id,
            target_entity=ticket.ticket_id,
            target_type="ticket",
            details={"subject": ticket.subject, "category": ticket.category.value},
        )

        return APIResponse.ok(data=ticket.model_dump())
    except Exception as e:
        logger.error(f"Create ticket error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/stats", response_model=APIResponse)
async def ticket_stats():
    """Get ticket statistics for the dashboard."""
    try:
        stats = await get_ticket_stats()
        return APIResponse.ok(data=stats)
    except Exception as e:
        logger.error(f"Ticket stats error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("", response_model=APIResponse)
async def list_tickets(
    employee_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List tickets with optional filters."""
    try:
        result = await get_tickets(
            employee_id=employee_id,
            status=status,
            priority=priority,
            category=category,
            page=page,
            page_size=page_size,
        )
        return APIResponse.ok(data=result)
    except Exception as e:
        logger.error(f"List tickets error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/{ticket_id}", response_model=APIResponse)
async def get_ticket_detail(ticket_id: str):
    """Get a specific ticket by ID."""
    try:
        ticket = await get_ticket(ticket_id)
        if not ticket:
            return APIResponse.fail(error="Ticket not found")
        return APIResponse.ok(data=ticket.model_dump())
    except Exception as e:
        logger.error(f"Get ticket error: {e}")
        return APIResponse.fail(error=str(e))


@router.put("/{ticket_id}", response_model=APIResponse)
async def update_existing_ticket(ticket_id: str, request: TicketUpdateRequest):
    """Update an existing ticket."""
    try:
        ticket = await update_ticket(
            ticket_id=ticket_id,
            status=request.status,
            priority=request.priority,
            assigned_to=request.assigned_to,
            resolution_notes=request.resolution_notes,
            comment=request.comment,
        )
        if not ticket:
            return APIResponse.fail(error="Ticket not found or no changes made")

        action_type = AuditActionType.TICKET_UPDATED
        if request.status == TicketStatus.RESOLVED:
            action_type = AuditActionType.TICKET_RESOLVED
        elif request.status == TicketStatus.CLOSED:
            action_type = AuditActionType.TICKET_CLOSED

        await log_action(
            action_type=action_type,
            actor=AuditActor.SYSTEM,
            target_entity=ticket_id,
            target_type="ticket",
            details={"updates": request.model_dump(exclude_none=True)},
        )

        return APIResponse.ok(data=ticket.model_dump())
    except Exception as e:
        logger.error(f"Update ticket error: {e}")
        return APIResponse.fail(error=str(e))
