"""
Timezone-aware datetime utilities.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional


def utc_now() -> datetime:
    """Return current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


def format_iso(dt: Optional[datetime] = None) -> str:
    """Format datetime as ISO 8601 string."""
    if dt is None:
        dt = utc_now()
    return dt.isoformat()


def format_relative_time(dt: datetime) -> str:
    """Format a datetime into a friendly human-readable relative time (e.g., '5 mins ago')."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = utc_now()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 0:
        return "just now"
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m ago" if minutes > 1 else "1m ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago" if hours > 1 else "1h ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days}d ago" if days > 1 else "1d ago"
    else:
        return dt.strftime("%b %d, %Y")
