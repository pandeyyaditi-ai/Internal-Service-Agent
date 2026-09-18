"""
JWT-based security utilities for employee authentication.
Lightweight auth — extracts employee identity from tokens.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with employee data."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_employee_id_from_token(token: str) -> Optional[str]:
    """Extract employee_id from a JWT token."""
    payload = verify_token(token)
    if payload:
        return payload.get("employee_id")
    return None


def create_employee_token(employee_id: str, name: str, department: str) -> str:
    """Convenience function to create a token for an employee."""
    return create_access_token({
        "employee_id": employee_id,
        "name": name,
        "department": department,
        "type": "access"
    })
