"""
Employee data model.
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
from typing import Optional


class Employee(BaseModel):
    """Employee model representing an internal user."""

    employee_id: str = Field(..., description="Unique employee identifier (e.g., EMP-001)")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., description="Corporate email address")
    department: str = Field(..., description="Department name")
    role: str = Field(default="Employee", description="Job role/title")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    manager_id: Optional[str] = Field(default=None, description="Direct manager's employee ID")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP-001",
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "department": "Engineering",
                "role": "Software Engineer",
                "phone": "+1-555-0101",
                "manager_id": "EMP-010",
                "is_active": True,
            }
        }

    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        data = self.model_dump()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_mongo(cls, doc: dict) -> "Employee":
        """Create Employee from MongoDB document."""
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
