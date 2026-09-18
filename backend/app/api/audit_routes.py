"""
Audit trail API routes.
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.schemas.response_schema import APIResponse
from app.services.audit_service import get_audit_logs, get_audit_entry, get_recent_actions, get_audit_stats
from app.core.logging import get_logger

logger = get_logger("audit_routes")
router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=APIResponse)
async def list_audit_logs(
    action_type: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    target_entity: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List audit logs with optional filters."""
    try:
        result = await get_audit_logs(
            action_type=action_type,
            actor=actor,
            target_entity=target_entity,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return APIResponse.ok(data=result)
    except Exception as e:
        logger.error(f"List audit logs error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/stats", response_model=APIResponse)
async def audit_stats():
    """Get audit log statistics."""
    try:
        stats = await get_audit_stats()
        return APIResponse.ok(data=stats)
    except Exception as e:
        logger.error(f"Audit stats error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/recent", response_model=APIResponse)
async def recent_audit_logs(limit: int = Query(20, ge=1, le=100)):
    """Get the most recent audit log entries."""
    try:
        logs = await get_recent_actions(limit=limit)
        return APIResponse.ok(data=logs)
    except Exception as e:
        logger.error(f"Recent audit logs error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/{audit_id}", response_model=APIResponse)
async def get_audit_detail(audit_id: str):
    """Get a specific audit log entry."""
    try:
        entry = await get_audit_entry(audit_id)
        if not entry:
            return APIResponse.fail(error="Audit entry not found")
        return APIResponse.ok(data=entry)
    except Exception as e:
        logger.error(f"Get audit entry error: {e}")
        return APIResponse.fail(error=str(e))
