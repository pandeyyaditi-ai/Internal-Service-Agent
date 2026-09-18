"""
Database seeder — populates MongoDB with sample data on first run.
Seeds employees, tickets, and initial audit logs.
"""
from datetime import datetime, timezone, timedelta
from app.database.database import database
from app.core.logging import get_logger

logger = get_logger("seed")


SAMPLE_EMPLOYEES = [
    {
        "employee_id": "EMP-001",
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com",
        "department": "Engineering",
        "role": "Senior Software Engineer",
        "phone": "+1-555-0101",
        "manager_id": "EMP-005",
        "is_active": True,
    },
    {
        "employee_id": "EMP-002",
        "name": "Bob Martinez",
        "email": "bob.martinez@company.com",
        "department": "Marketing",
        "role": "Marketing Manager",
        "phone": "+1-555-0102",
        "manager_id": "EMP-005",
        "is_active": True,
    },
    {
        "employee_id": "EMP-003",
        "name": "Carol Chen",
        "email": "carol.chen@company.com",
        "department": "Finance",
        "role": "Financial Analyst",
        "phone": "+1-555-0103",
        "manager_id": "EMP-005",
        "is_active": True,
    },
    {
        "employee_id": "EMP-004",
        "name": "David Kim",
        "email": "david.kim@company.com",
        "department": "Engineering",
        "role": "DevOps Engineer",
        "phone": "+1-555-0104",
        "manager_id": "EMP-005",
        "is_active": True,
    },
    {
        "employee_id": "EMP-005",
        "name": "Eva Williams",
        "email": "eva.williams@company.com",
        "department": "IT",
        "role": "IT Director",
        "phone": "+1-555-0105",
        "manager_id": None,
        "is_active": True,
    },
]


def _get_sample_tickets() -> list:
    """Generate sample tickets with realistic dates."""
    now = datetime.now(timezone.utc)
    return [
        {
            "ticket_id": "TKT-20240101-A1B2",
            "employee_id": "EMP-001",
            "subject": "VPN connection timeout from home network",
            "description": "Getting timeout error (Error 800) when trying to connect to corporate VPN. Tried restarting client and flushing DNS. Issue persists on WiFi but works on ethernet.",
            "category": "vpn",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "IT Support Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Agent", "content": "Investigating VPN server logs for connection attempts.", "timestamp": (now - timedelta(hours=2)).isoformat()},
            ],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["vpn", "remote-work"],
            "created_at": (now - timedelta(hours=6)).isoformat(),
            "updated_at": (now - timedelta(hours=2)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240101-C3D4",
            "employee_id": "EMP-002",
            "subject": "Need Adobe Creative Cloud license",
            "description": "Our team needs Adobe Creative Cloud for creating marketing materials. Requesting license for my account.",
            "category": "software",
            "priority": "medium",
            "status": "open",
            "assigned_to": None,
            "conversation_id": None,
            "comments": [],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["software", "license"],
            "created_at": (now - timedelta(hours=12)).isoformat(),
            "updated_at": (now - timedelta(hours=12)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240101-E5F6",
            "employee_id": "EMP-003",
            "subject": "Cannot access shared finance folder",
            "description": "I need access to \\\\fileserver\\departments\\finance\\reports. My manager approved the request.",
            "category": "access",
            "priority": "medium",
            "status": "resolved",
            "assigned_to": "IT Support Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Support Team", "content": "Access granted. Please try logging out and back in.", "timestamp": (now - timedelta(hours=20)).isoformat()},
            ],
            "resolution_notes": "Added user to finance-reports security group in Active Directory.",
            "escalation_reason": None,
            "tags": ["access", "file-share"],
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": (now - timedelta(hours=20)).isoformat(),
            "resolved_at": (now - timedelta(hours=20)).isoformat(),
        },
        {
            "ticket_id": "TKT-20240101-G7H8",
            "employee_id": "EMP-004",
            "subject": "Docker Desktop not starting after Windows update",
            "description": "After the latest Windows update, Docker Desktop fails to start with 'WSL 2 installation is incomplete' error.",
            "category": "software",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "IT Support Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Agent", "content": "This is a known issue after KB5034441. Running WSL update fix.", "timestamp": (now - timedelta(hours=3)).isoformat()},
            ],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["docker", "windows-update", "development"],
            "created_at": (now - timedelta(hours=8)).isoformat(),
            "updated_at": (now - timedelta(hours=3)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240101-I9J0",
            "employee_id": "EMP-001",
            "subject": "Laptop keyboard not responding intermittently",
            "description": "My Dell XPS 15 keyboard stops responding randomly for a few seconds, then comes back. Happens several times a day. Already tried updating drivers.",
            "category": "hardware",
            "priority": "medium",
            "status": "open",
            "assigned_to": None,
            "conversation_id": None,
            "comments": [],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["hardware", "laptop", "keyboard"],
            "created_at": (now - timedelta(hours=4)).isoformat(),
            "updated_at": (now - timedelta(hours=4)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240102-K1L2",
            "employee_id": "EMP-002",
            "subject": "Outlook calendar not syncing with Teams",
            "description": "My Outlook calendar events are not showing up in Microsoft Teams. I've tried clearing the Teams cache but the issue persists.",
            "category": "email",
            "priority": "low",
            "status": "resolved",
            "assigned_to": "IT Support Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Support Team", "content": "Reauthorized the calendar connector. Please restart Teams.", "timestamp": (now - timedelta(days=2)).isoformat()},
            ],
            "resolution_notes": "Calendar sync issue resolved by reauthorizing Exchange connector in Teams admin.",
            "escalation_reason": None,
            "tags": ["email", "teams", "calendar"],
            "created_at": (now - timedelta(days=3)).isoformat(),
            "updated_at": (now - timedelta(days=2)).isoformat(),
            "resolved_at": (now - timedelta(days=2)).isoformat(),
        },
        {
            "ticket_id": "TKT-20240102-M3N4",
            "employee_id": "EMP-003",
            "subject": "MFA not working on new phone",
            "description": "I got a new phone and now I can't log in because MFA is still tied to my old phone. Need MFA reset.",
            "category": "password",
            "priority": "high",
            "status": "escalated",
            "assigned_to": "IT Security Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Agent", "content": "Escalating to IT Security for MFA reset — requires identity verification.", "timestamp": (now - timedelta(hours=1)).isoformat()},
            ],
            "resolution_notes": None,
            "escalation_reason": "MFA reset requires IT Security verification — cannot be done by automated agent",
            "tags": ["mfa", "security", "phone"],
            "created_at": (now - timedelta(hours=3)).isoformat(),
            "updated_at": (now - timedelta(hours=1)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240102-O5P6",
            "employee_id": "EMP-004",
            "subject": "Request for second external monitor",
            "description": "I need a second external monitor for my development setup. Currently have one Dell U2723QE, requesting the same model.",
            "category": "hardware",
            "priority": "low",
            "status": "open",
            "assigned_to": None,
            "conversation_id": None,
            "comments": [],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["hardware", "monitor", "request"],
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": (now - timedelta(days=1)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240102-Q7R8",
            "employee_id": "EMP-001",
            "subject": "Suspicious email received — possible phishing",
            "description": "Received an email from 'IT-Support@c0mpany.com' (note the zero) asking to verify my credentials. Did not click any links. Reporting as potential phishing.",
            "category": "general",
            "priority": "critical",
            "status": "in_progress",
            "assigned_to": "IT Security Team",
            "conversation_id": None,
            "comments": [
                {"author": "IT Security Team", "content": "Confirmed phishing attempt. Blocking sender domain and alerting all employees.", "timestamp": (now - timedelta(minutes=30)).isoformat()},
            ],
            "resolution_notes": None,
            "escalation_reason": "Security incident — phishing attempt",
            "tags": ["security", "phishing", "critical"],
            "created_at": (now - timedelta(hours=1)).isoformat(),
            "updated_at": (now - timedelta(minutes=30)).isoformat(),
            "resolved_at": None,
        },
        {
            "ticket_id": "TKT-20240103-S9T0",
            "employee_id": "EMP-005",
            "subject": "Office WiFi slow on Floor 3",
            "description": "Multiple employees on Floor 3 reporting very slow WiFi speeds. Affecting video calls and file downloads. Started this morning.",
            "category": "network",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "Network Team",
            "conversation_id": None,
            "comments": [
                {"author": "Network Team", "content": "Identified AP-FL3-02 as overloaded. Redistributing load across backup APs.", "timestamp": (now - timedelta(minutes=45)).isoformat()},
            ],
            "resolution_notes": None,
            "escalation_reason": None,
            "tags": ["network", "wifi", "floor-3"],
            "created_at": (now - timedelta(hours=2)).isoformat(),
            "updated_at": (now - timedelta(minutes=45)).isoformat(),
            "resolved_at": None,
        },
    ]


async def seed_database():
    """Seed the database with sample data if collections are empty."""
    try:
        # Check if already seeded
        employee_count = await database.employees.count_documents({})
        if employee_count > 0:
            logger.info("Database already seeded — skipping")
            return

        logger.info("Seeding database with sample data...")

        # Seed employees
        now = datetime.now(timezone.utc).isoformat()
        for emp in SAMPLE_EMPLOYEES:
            emp["created_at"] = now
            emp["updated_at"] = now
        await database.employees.insert_many(SAMPLE_EMPLOYEES)
        logger.info(f"Seeded {len(SAMPLE_EMPLOYEES)} employees")

        # Seed tickets
        tickets = _get_sample_tickets()
        await database.tickets.insert_many(tickets)
        logger.info(f"Seeded {len(tickets)} tickets")

        # Seed initial audit log
        await database.audit_logs.insert_one({
            "audit_id": "AUD-SEED-000001",
            "action_type": "system_startup",
            "actor": "system",
            "actor_id": "system",
            "target_entity": None,
            "target_type": None,
            "details": {"message": "Database seeded with initial data"},
            "timestamp": now,
        })

        logger.info("Database seeding complete!")

    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise
