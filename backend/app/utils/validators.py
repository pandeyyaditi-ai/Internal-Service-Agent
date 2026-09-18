"""
Validation and sanitization helpers.
"""
import re
from typing import Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
TICKET_ID_REGEX = re.compile(r"^TICK-\d{4,8}$", re.IGNORECASE)


def sanitize_string(value: Optional[str]) -> str:
    """Trim leading/trailing whitespace and remove potentially dangerous control characters."""
    if not value:
        return ""
    # Strip null bytes and control chars except newlines and tabs
    sanitized = "".join(ch for ch in value if ch in ("\n", "\t", "\r") or (ord(ch) >= 32 and ord(ch) != 127))
    return sanitized.strip()


def validate_email(email: str) -> bool:
    """Check if the string is a valid email address."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_ticket_id(ticket_id: str) -> bool:
    """Check if the ticket ID matches TICK-XXXX format."""
    if not ticket_id or not isinstance(ticket_id, str):
        return False
    return bool(TICKET_ID_REGEX.match(ticket_id.strip()))
