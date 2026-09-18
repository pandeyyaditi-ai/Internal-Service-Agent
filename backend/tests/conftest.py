"""
Pytest configuration and shared fixtures for backend testing.
"""
import pytest
import os
import sys

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Override environment variables for testing
os.environ["SQLITE_DB_PATH"] = "test_service_agent.db"
os.environ["GEMINI_API_KEY"] = "mock_test_key"
os.environ["LOG_LEVEL"] = "WARNING"


@pytest.fixture
def mock_employee():
    return {
        "employee_id": "EMP-001",
        "name": "Sarah Connor",
        "email": "sarah.connor@company.com",
        "department": "Engineering",
        "role": "Senior Software Engineer"
    }


@pytest.fixture
def mock_ticket_payload():
    return {
        "employee_id": "EMP-001",
        "subject": "VPN connection drops constantly",
        "description": "AnyConnect disconnects every 10 minutes when working from home.",
        "category": "vpn",
        "priority": "high"
    }
