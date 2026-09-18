"""
Audit service for logging all agent actions.
Provides write and query capabilities for the audit trail.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from app.database.database import database
from app.models.audit import AuditLog, AuditActionType, AuditActor
from app.core.logging import get_logger

logger = get_logger("audit_service")


def generate_audit_id() -> str:
    """Generate a unique audit ID."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"AUD-{date_str}-{short_uuid}"


async def log_action(
    action_type: AuditActionType,
    actor: AuditActor,
    actor_id: Optional[str] = None,
    target_entity: Optional[str] = None,
    target_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> AuditLog:
    """Log an action to the audit trail."""
    audit_entry = AuditLog(
        audit_id=generate_audit_id(),
        action_type=action_type,
        actor=actor,
        actor_id=actor_id,
        target_entity=target_entity,
        target_type=target_type,
        details=details or {},
        correlation_id=correlation_id,
    )

    try:
        await database.audit_logs.insert_one(audit_entry.to_mongo())
        logger.info(f"Audit logged: {action_type.value} by {actor.value} on {target_entity}")
    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")

    return audit_entry


async def get_audit_logs(
    action_type: Optional[str] = None,
    actor: Optional[str] = None,
    target_entity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Query audit logs with filtering and pagination."""
    query = {}

    if action_type:
        query["action_type"] = action_type
    if actor:
        query["actor"] = actor
    if target_entity:
        query["target_entity"] = target_entity

    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        if date_filter:
            query["timestamp"] = date_filter

    total = await database.audit_logs.count_documents(query)
    skip = (page - 1) * page_size

    cursor = database.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(page_size)
    logs = []
    async for doc in cursor:
        doc.pop("_id", None)
        logs.append(doc)

    return {
        "logs": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


async def get_audit_entry(audit_id: str) -> Optional[Dict[str, Any]]:
    """Get a single audit log entry by ID."""
    doc = await database.audit_logs.find_one({"audit_id": audit_id})
    if doc:
        doc.pop("_id", None)
        return doc
    return None


async def get_recent_actions(limit: int = 20) -> List[Dict[str, Any]]:
    """Get the most recent audit log entries."""
    cursor = database.audit_logs.find().sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc.pop("_id", None)
        logs.append(doc)
    return logs


async def get_audit_stats() -> Dict[str, Any]:
    """Get audit log statistics for the dashboard."""
    total = await database.audit_logs.count_documents({})

    # Count by action type
    pipeline = [
        {"$group": {"_id": "$action_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    action_counts = {}
    async for doc in database.audit_logs.aggregate(pipeline):
        action_counts[doc["_id"]] = doc["count"]

    # Count today's actions
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await database.audit_logs.count_documents({
        "timestamp": {"$gte": today_start.isoformat()}
    })

    return {
        "total_entries": total,
        "today_entries": today_count,
        "by_action_type": action_counts,
    }
