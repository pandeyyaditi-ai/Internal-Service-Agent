"""
Unit tests for Ticket service functions and priority/category auto-detection.
"""
import pytest
from app.models.ticket import TicketPriority, TicketCategory
from app.services.ticket_service import (
    generate_ticket_id,
    auto_detect_priority,
    auto_detect_category,
)
from app.utils.validators import validate_ticket_id


def test_generate_ticket_id():
    """Ensure ticket ID adheres to TKT-YYYYMMDD-XXXX convention."""
    ticket_id = generate_ticket_id()
    assert ticket_id.startswith("TKT-")
    parts = ticket_id.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 4  # Hex suffix


def test_auto_detect_priority():
    """Test keyword-based priority assignment."""
    assert auto_detect_priority("System is totally down, emergency!") == TicketPriority.CRITICAL
    assert auto_detect_priority("I am blocked and can't work because VPN fails") == TicketPriority.HIGH
    assert auto_detect_priority("The software is a bit slow intermittently") == TicketPriority.MEDIUM
    assert auto_detect_priority("I have a quick question or suggestion for improvement") == TicketPriority.LOW


def test_auto_detect_category():
    """Test keyword-based category assignment."""
    assert auto_detect_category("GlobalProtect VPN connection failed") == TicketCategory.VPN
    assert auto_detect_category("Forgot my password and MFA reset needed") == TicketCategory.PASSWORD
    assert auto_detect_category("Laptop monitor and keyboard not turning on") == TicketCategory.HARDWARE
    assert auto_detect_category("Need license to install Photoshop software") == TicketCategory.SOFTWARE
    assert auto_detect_category("Outlook email inbox not syncing with Teams") == TicketCategory.EMAIL
    assert auto_detect_category("Something strange happened with random stuff") == TicketCategory.GENERAL
