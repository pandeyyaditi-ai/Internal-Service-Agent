"""
Ticket service for CRUD operations on support tickets.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from app.database.database import database
from app.models.ticket import Ticket, TicketPriority, TicketStatus, TicketCategory, TicketComment
from app.core.logging import get_logger

logger = get_logger("ticket_service")


# Priority auto-assignment keywords
PRIORITY_KEYWORDS = {
    TicketPriority.CRITICAL: [
        "security breach", "data leak", "system down", "production down",
        "all users affected", "emergency", "hacked", "ransomware"
    ],
    TicketPriority.HIGH: [
        "can't work", "blocked", "urgent", "vpn not working", "can't login",
        "locked out", "broken", "not functioning", "critical"
    ],
    TicketPriority.MEDIUM: [
        "slow", "intermittent", "sometimes", "error", "issue",
        "not working properly", "need help"
    ],
    TicketPriority.LOW: [
        "question", "how to", "request", "would like", "when will",
        "suggestion", "enhancement", "nice to have"
    ],
}

# Category auto-detection keywords
CATEGORY_KEYWORDS = {
    TicketCategory.VPN: ["vpn", "remote access", "globalprotect", "connect remotely"],
    TicketCategory.PASSWORD: ["password", "reset", "locked out", "login", "credentials", "mfa"],
    TicketCategory.HARDWARE: ["laptop", "monitor", "keyboard", "mouse", "hardware", "computer", "printer"],
    TicketCategory.SOFTWARE: ["install", "software", "application", "program", "update", "license"],
    TicketCategory.NETWORK: ["wifi", "network", "internet", "connection", "dns", "firewall"],
    TicketCategory.EMAIL: ["email", "outlook", "mailbox", "inbox", "calendar", "teams"],
    TicketCategory.ACCESS: ["access", "permission", "folder", "drive", "share", "sharepoint"],
}


def generate_ticket_id() -> str:
    """Generate a unique ticket ID."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:4].upper()
    return f"TKT-{date_str}-{short_uuid}"


def auto_detect_priority(text: str) -> TicketPriority:
    """Auto-detect ticket priority from text."""
    text_lower = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return priority
    return TicketPriority.MEDIUM


def auto_detect_category(text: str) -> TicketCategory:
    """Auto-detect ticket category from text."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return TicketCategory.GENERAL


async def create_ticket(
    employee_id: str,
    subject: str,
    description: str,
    category: Optional[TicketCategory] = None,
    priority: Optional[TicketPriority] = None,
    conversation_id: Optional[str] = None,
) -> Ticket:
    """Create a new support ticket."""
    ticket_id = generate_ticket_id()

    # Auto-detect category and priority if not provided
    combined_text = f"{subject} {description}"
    if not category:
        category = auto_detect_category(combined_text)
    if not priority:
        priority = auto_detect_priority(combined_text)

    ticket = Ticket(
        ticket_id=ticket_id,
        employee_id=employee_id,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        status=TicketStatus.OPEN,
        conversation_id=conversation_id,
    )

    await database.tickets.insert_one(ticket.to_mongo())
    logger.info(f"Created ticket {ticket_id} for employee {employee_id} (priority: {priority}, category: {category})")
    return ticket


async def get_ticket(ticket_id: str) -> Optional[Ticket]:
    """Get a ticket by ID."""
    doc = await database.tickets.find_one({"ticket_id": ticket_id})
    return Ticket.from_mongo(doc) if doc else None


async def get_tickets(
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Get tickets with filtering and pagination."""
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if category:
        query["category"] = category

    total = await database.tickets.count_documents(query)
    skip = (page - 1) * page_size

    cursor = database.tickets.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    tickets = []
    async for doc in cursor:
        doc.pop("_id", None)
        tickets.append(doc)

    return {
        "tickets": tickets,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


async def update_ticket(
    ticket_id: str,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    assigned_to: Optional[str] = None,
    resolution_notes: Optional[str] = None,
    escalation_reason: Optional[str] = None,
    comment: Optional[str] = None,
    comment_author: str = "IT Agent",
) -> Optional[Ticket]:
    """Update a ticket."""
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    if status:
        update_data["status"] = status.value
        if status == TicketStatus.RESOLVED:
            update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
    if priority:
        update_data["priority"] = priority.value
    if assigned_to:
        update_data["assigned_to"] = assigned_to
    if resolution_notes:
        update_data["resolution_notes"] = resolution_notes
    if escalation_reason:
        update_data["escalation_reason"] = escalation_reason

    update_ops = {"$set": update_data}

    if comment:
        update_ops["$push"] = {
            "comments": {
                "author": comment_author,
                "content": comment,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }

    result = await database.tickets.update_one(
        {"ticket_id": ticket_id},
        update_ops,
    )

    if result.modified_count > 0:
        logger.info(f"Updated ticket {ticket_id}")
        return await get_ticket(ticket_id)
    return None


async def get_ticket_stats() -> Dict[str, Any]:
    """Get ticket statistics for the dashboard."""
    pipeline = [
        {
            "$facet": {
                "by_status": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ],
                "by_category": [
                    {"$group": {"_id": "$category", "count": {"$sum": 1}}}
                ],
                "by_priority": [
                    {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
                ],
                "total": [
                    {"$count": "count"}
                ],
            }
        }
    ]

    result = await database.tickets.aggregate(pipeline).to_list(length=1)

    if not result:
        return {
            "total_tickets": 0,
            "open_tickets": 0,
            "in_progress_tickets": 0,
            "resolved_tickets": 0,
            "escalated_tickets": 0,
            "closed_tickets": 0,
            "resolved_today": 0,
            "tickets_by_category": {},
            "tickets_by_priority": {},
        }

    data = result[0]
    status_counts = {item["_id"]: item["count"] for item in data.get("by_status", [])}
    category_counts = {item["_id"]: item["count"] for item in data.get("by_category", [])}
    priority_counts = {item["_id"]: item["count"] for item in data.get("by_priority", [])}
    total = data.get("total", [{"count": 0}])[0].get("count", 0)

    # Count resolved today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = await database.tickets.count_documents({
        "status": "resolved",
        "resolved_at": {"$gte": today_start.isoformat()},
    })

    return {
        "total_tickets": total,
        "open_tickets": status_counts.get("open", 0),
        "in_progress_tickets": status_counts.get("in_progress", 0),
        "resolved_tickets": status_counts.get("resolved", 0),
        "escalated_tickets": status_counts.get("escalated", 0),
        "closed_tickets": status_counts.get("closed", 0),
        "resolved_today": resolved_today,
        "tickets_by_category": category_counts,
        "tickets_by_priority": priority_counts,
    }
