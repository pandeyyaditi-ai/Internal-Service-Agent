"""
Unit tests for intent detection and chat processing logic.
"""
import pytest
from app.services.intent_detection import detect_intent_keywords, INTENTS
from app.schemas.chat_schema import ChatMessageRequest, ChatMessageResponse
from app.models.conversation import MessageRole


def test_detect_intent_keywords():
    """Verify fallback keyword-based intent detection."""
    vpn_res = detect_intent_keywords("My VPN connection dropped and I cannot connect")
    assert vpn_res["intent"] == "vpn_issue"
    assert vpn_res["confidence"] >= 0.35

    faq_res = detect_intent_keywords("How do I reset my password for email?")
    assert faq_res["intent"] == "faq"

    ticket_res = detect_intent_keywords("Please check my ticket status")
    assert ticket_res["intent"] == "ticket_request"

    escalate_res = detect_intent_keywords("I want to talk to human agent right now")
    assert escalate_res["intent"] == "escalation"

    general_res = detect_intent_keywords("Hello, good morning!")
    assert general_res["intent"] == "general"


def test_chat_message_schema():
    """Verify chat schema validation."""
    req = ChatMessageRequest(
        employee_id="EMP-001",
        message="Help with printer"
    )
    assert req.employee_id == "EMP-001"
    assert req.message == "Help with printer"
    assert req.conversation_id is None

    resp = ChatMessageResponse(
        conversation_id="CONV-123",
        message="Here is printer setup instructions",
        intent="faq"
    )
    assert resp.intent == "faq"
    assert resp.conversation_id == "CONV-123"
    assert resp.message == "Here is printer setup instructions"
