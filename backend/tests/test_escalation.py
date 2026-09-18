"""
Unit tests for escalation rules engine.
"""
import pytest
from app.models.ticket import TicketPriority
from app.services.escalation import (
    check_keyword_escalation,
    check_confidence_escalation,
    check_resolution_attempt_escalation,
    check_priority_escalation,
    CONFIDENCE_THRESHOLD,
    MAX_RESOLUTION_ATTEMPTS,
)


def test_keyword_escalation():
    """Verify that user asking for human help triggers escalation."""
    reason = check_keyword_escalation("Please connect me to a human agent right now")
    assert reason is not None
    assert "human agent" in reason

    reason_negative = check_keyword_escalation("How do I reset my Outlook password?")
    assert reason_negative is None


def test_confidence_escalation():
    """Verify low confidence (< 0.4) triggers escalation."""
    assert check_confidence_escalation(0.2) is not None
    assert check_confidence_escalation(0.39) is not None
    assert check_confidence_escalation(0.40) is None
    assert check_confidence_escalation(0.85) is None


def test_resolution_attempt_escalation():
    """Verify max failed attempts (>= 3) triggers escalation."""
    assert check_resolution_attempt_escalation(3) is not None
    assert check_resolution_attempt_escalation(4) is not None
    assert check_resolution_attempt_escalation(2) is None
    assert check_resolution_attempt_escalation(0) is None


def test_priority_escalation():
    """Verify critical tickets trigger escalation."""
    assert check_priority_escalation(TicketPriority.CRITICAL.value) is not None
    assert check_priority_escalation(TicketPriority.HIGH.value) is None
    assert check_priority_escalation(TicketPriority.LOW.value) is None
