"""
Unified API response wrapper schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class APIResponse(BaseModel):
    """Unified API response wrapper."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(default=None, description="Response payload")
    error: Optional[str] = Field(default=None, description="Error message if unsuccessful")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @classmethod
    def ok(cls, data: Any = None, metadata: Dict[str, Any] = None) -> "APIResponse":
        """Create a successful response."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, metadata: Dict[str, Any] = None) -> "APIResponse":
        """Create an error response."""
        return cls(success=False, error=error, metadata=metadata)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = ""
    database: str = "connected"
    gemini: str = "configured"
