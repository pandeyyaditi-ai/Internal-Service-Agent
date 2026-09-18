"""
Escalation service.
Rules engine that determines when to escalate conversations to human agents.
"""
from typing import Dict, Any, Optional
from app.database.database import database
from app.models.ticket import TicketStatus, TicketPriority
from app.core.logging import get_logger

logger = get_logger("escalation")

# Escalation thresholds
CONFIDENCE_THRESHOLD = 0.4  # Auto-escalate if intent confidence below this
MAX_RESOLUTION_ATTEMPTS = 3  # Auto-escalate after this many failed attempts

# Keywords that trigger immediate escalation
ESCALATION_KEYWORDS = [
    "talk to human", "human agent", "real person", "escalate",
    "speak to someone", "transfer me", "not helpful", "supervisor",
    "manager", "live agent", "connect me to", "talk to agent",
    "this isn't working", "useless", "frustrated", "give up",
]


def check_keyword_escalation(message: str) -> Optional[str]:
    """Check if user message contains escalation keywords."""
    message_lower = message.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in message_lower:
            return f"User requested human assistance (keyword: '{keyword}')"
    return None


def check_confidence_escalation(confidence: float) -> Optional[str]:
    """Check if intent confidence is too low for reliable automation."""
    if confidence < CONFIDENCE_THRESHOLD:
        return f"Intent confidence too low ({confidence:.2f} < {CONFIDENCE_THRESHOLD}) — unable to reliably determine user's need"
    return None


def check_resolution_attempt_escalation(attempt_count: int) -> Optional[str]:
    """Check if too many resolution attempts have been made."""
    if attempt_count >= MAX_RESOLUTION_ATTEMPTS:
        return f"Issue unresolved after {attempt_count} attempts — automated resolution insufficient"
    return None


def check_priority_escalation(priority: str) -> Optional[str]:
    """Check if ticket priority warrants escalation."""
    if priority == TicketPriority.CRITICAL.value:
        return f"Critical priority issue requires human oversight"
    return None


async def evaluate_escalation(
    message: str,
    intent_confidence: float = 1.0,
    resolution_attempts: int = 0,
    ticket_priority: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate whether a conversation should be escalated.
    Returns escalation decision with reason.
    """
    reasons = []

    # Check all escalation rules
    keyword_reason = check_keyword_escalation(message)
    if keyword_reason:
        reasons.append(keyword_reason)

    confidence_reason = check_confidence_escalation(intent_confidence)
    if confidence_reason:
        reasons.append(confidence_reason)

    attempt_reason = check_resolution_attempt_escalation(resolution_attempts)
    if attempt_reason:
        reasons.append(attempt_reason)

    if ticket_priority:
        priority_reason = check_priority_escalation(ticket_priority)
        if priority_reason:
            reasons.append(priority_reason)

    should_escalate = len(reasons) > 0

    if should_escalate:
        logger.info(f"Escalation triggered for conversation {conversation_id}: {'; '.join(reasons)}")

    return {
        "should_escalate": should_escalate,
        "reasons": reasons,
        "primary_reason": reasons[0] if reasons else None,
        "urgency": _determine_urgency(reasons),
    }


def _determine_urgency(reasons: list) -> str:
    """Determine escalation urgency level."""
    if not reasons:
        return "none"

    reason_text = " ".join(reasons).lower()

    if "critical" in reason_text or "security" in reason_text:
        return "critical"
    elif "keyword" in reason_text or "frustrated" in reason_text:
        return "high"
    elif "attempts" in reason_text:
        return "medium"
    else:
        return "low"


def get_escalation_message(reasons: list, urgency: str) -> str:
    """Generate an appropriate escalation message for the user."""
    if urgency == "critical":
        return (
            "🚨 **This issue has been escalated to our IT support team with CRITICAL priority.**\n\n"
            "A senior IT specialist will be assigned to your case immediately. "
            "You can expect a response within **1 hour**.\n\n"
            f"**Reason for escalation**: {reasons[0]}\n\n"
            "In the meantime, if this is a security concern, please also contact "
            "IT Security directly at security@company.com or ext. 9999."
        )
    elif urgency == "high":
        return (
            "🔔 **I'm connecting you with a human IT support agent.**\n\n"
            "Your request has been escalated to our support team. "
            "A team member will reach out to you within **4 hours** during business hours.\n\n"
            f"**Reason**: {reasons[0]}\n\n"
            "You can also reach us directly:\n"
            "- 📞 Phone: ext. 5555\n"
            "- 📧 Email: support@company.com\n"
            "- 🏢 Walk-in: IT Help Desk, Building A, Floor 2"
        )
    else:
        return (
            "📋 **I've escalated your issue to our IT support team.**\n\n"
            "A support agent will review your case and follow up with you. "
            "Expected response time: **1 business day**.\n\n"
            f"**Reason**: {reasons[0]}\n\n"
            "I've created a ticket to track this — you can check its status anytime."
        )


async def process_escalation(
    conversation_id: str,
    employee_id: str,
    reasons: list,
    urgency: str,
    ticket_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process an escalation: update conversation status and ticket if applicable.
    """
    # Update conversation status
    await database.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"status": "escalated"}},
    )

    # Update ticket if exists
    if ticket_id:
        await database.tickets.update_one(
            {"ticket_id": ticket_id},
            {
                "$set": {
                    "status": TicketStatus.ESCALATED.value,
                    "escalation_reason": reasons[0] if reasons else "Manual escalation",
                    "assigned_to": "IT Support Team",
                },
                "$push": {
                    "comments": {
                        "author": "IT Agent",
                        "content": f"Auto-escalated: {'; '.join(reasons)}",
                        "timestamp": __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        ).isoformat(),
                    }
                },
            },
        )

    message = get_escalation_message(reasons, urgency)

    return {
        "message": message,
        "escalated": True,
        "urgency": urgency,
        "reasons": reasons,
    }
