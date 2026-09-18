"""
Agent orchestrator — the central brain of the IT Support Agent.
Routes incoming messages through: intent detection → service dispatch → 
response generation → escalation check → audit logging.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.database.database import database
from app.models.conversation import Conversation, Message, MessageRole, ConversationStatus, MessageMetadata
from app.models.audit import AuditActionType, AuditActor
from app.services.intent_detection import detect_intent
from app.services.policy_search import search_and_respond
from app.services.troubleshooting import get_troubleshooting_response
from app.services.ticket_service import create_ticket, get_ticket, get_tickets
from app.services.escalation import evaluate_escalation, process_escalation
from app.services.audit_service import log_action
from app.schemas.chat_schema import ChatMessageResponse
from app.core.logging import get_logger

logger = get_logger("agent")


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return f"CONV-{uuid.uuid4().hex[:8]}"


async def get_or_create_conversation(
    employee_id: str,
    conversation_id: Optional[str] = None,
) -> Conversation:
    """Get an existing conversation or create a new one."""
    if conversation_id:
        doc = await database.conversations.find_one({"conversation_id": conversation_id})
        if doc:
            return Conversation.from_mongo(doc)

    # Create new conversation
    conv = Conversation(
        conversation_id=generate_conversation_id(),
        employee_id=employee_id,
    )
    await database.conversations.insert_one(conv.to_mongo())

    # Log conversation start
    await log_action(
        action_type=AuditActionType.CONVERSATION_STARTED,
        actor=AuditActor.SYSTEM,
        actor_id=employee_id,
        target_entity=conv.conversation_id,
        target_type="conversation",
        details={"employee_id": employee_id},
    )

    return conv


async def process_message(
    employee_id: str,
    message: str,
    conversation_id: Optional[str] = None,
) -> ChatMessageResponse:
    """
    Main entry point: process an incoming user message and generate a response.
    """
    # 1. Get or create conversation
    conversation = await get_or_create_conversation(employee_id, conversation_id)

    # Log incoming message
    await log_action(
        action_type=AuditActionType.CHAT_MESSAGE_RECEIVED,
        actor=AuditActor.EMPLOYEE,
        actor_id=employee_id,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={"message_preview": message[:100]},
    )

    # Store user message
    conversation.add_message(MessageRole.USER, message)

    # 2. Build conversation context for intent detection
    context = _build_context(conversation)

    # 3. Check if we're in a troubleshooting flow
    if conversation.current_intent == "vpn_issue":
        response = await _handle_troubleshooting(conversation, message, employee_id)
    else:
        # 4. Detect intent
        intent_result = await detect_intent(message, context)
        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.5)

        # Log intent detection
        await log_action(
            action_type=AuditActionType.INTENT_DETECTED,
            actor=AuditActor.AGENT,
            target_entity=conversation.conversation_id,
            target_type="conversation",
            details={
                "intent": intent,
                "confidence": confidence,
                "method": intent_result.get("method", "unknown"),
            },
        )

        # 5. Check escalation BEFORE processing
        escalation_result = await evaluate_escalation(
            message=message,
            intent_confidence=confidence,
            resolution_attempts=conversation.resolution_count,
        )

        if escalation_result["should_escalate"]:
            response = await _handle_escalation(
                conversation, employee_id, escalation_result
            )
        else:
            # 6. Route to appropriate handler based on intent
            response = await _dispatch_intent(
                intent, confidence, conversation, message, employee_id, intent_result
            )

    # 7. Store agent response in conversation
    metadata = MessageMetadata(
        intent=response.intent,
        confidence=response.confidence,
        ticket_id=response.ticket_id,
        escalation=response.escalated,
        troubleshooting_step=response.troubleshooting_step,
    )
    if response.sources:
        metadata.sources = [s.model_dump() if hasattr(s, 'model_dump') else s for s in response.sources]

    conversation.add_message(MessageRole.AGENT, response.message, metadata)

    # 8. Save conversation to database
    await database.conversations.update_one(
        {"conversation_id": conversation.conversation_id},
        {"$set": conversation.to_mongo()},
    )

    # Log response
    await log_action(
        action_type=AuditActionType.CHAT_RESPONSE_SENT,
        actor=AuditActor.AGENT,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={
            "intent": response.intent,
            "escalated": response.escalated,
            "has_sources": bool(response.sources),
        },
    )

    return response


async def _dispatch_intent(
    intent: str,
    confidence: float,
    conversation: Conversation,
    message: str,
    employee_id: str,
    intent_result: Dict[str, Any],
) -> ChatMessageResponse:
    """Route to the appropriate handler based on detected intent."""

    if intent == "vpn_issue":
        return await _start_troubleshooting(conversation, employee_id)

    elif intent == "faq":
        return await _handle_faq(conversation, message, confidence)

    elif intent == "ticket_request":
        return await _handle_ticket_request(conversation, message, employee_id)

    elif intent == "escalation":
        escalation_result = {
            "should_escalate": True,
            "reasons": ["User explicitly requested human assistance"],
            "urgency": "high",
        }
        return await _handle_escalation(conversation, employee_id, escalation_result)

    else:  # general
        return await _handle_general(conversation, message)


async def _start_troubleshooting(
    conversation: Conversation,
    employee_id: str,
) -> ChatMessageResponse:
    """Start the VPN troubleshooting flow."""
    conversation.current_intent = "vpn_issue"

    await log_action(
        action_type=AuditActionType.TROUBLESHOOTING_STARTED,
        actor=AuditActor.AGENT,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={"type": "vpn"},
    )

    result = await get_troubleshooting_response(None, "", conversation.conversation_id)

    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=result["message"],
        intent="vpn_issue",
        confidence=0.9,
        troubleshooting_step=result["step"],
        suggested_actions=["yes", "no"],
    )


async def _handle_troubleshooting(
    conversation: Conversation,
    message: str,
    employee_id: str,
) -> ChatMessageResponse:
    """Continue the VPN troubleshooting flow."""
    # Find the current step from the last agent message
    current_step = None
    for msg in reversed(conversation.messages):
        if msg.role == MessageRole.AGENT and msg.metadata and msg.metadata.troubleshooting_step is not None:
            current_step = msg.metadata.troubleshooting_step
            break

    if current_step == -1:
        # Troubleshooting finished — reset intent and re-process
        conversation.current_intent = None
        intent_result = await detect_intent(message, _build_context(conversation))
        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.5)
        return await _dispatch_intent(intent, confidence, conversation, message, employee_id, intent_result)

    result = await get_troubleshooting_response(current_step, message, conversation.conversation_id)

    await log_action(
        action_type=AuditActionType.TROUBLESHOOTING_STEP,
        actor=AuditActor.AGENT,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={"step": result["step"], "resolved": result["is_resolved"]},
    )

    # Handle escalation from troubleshooting
    if result.get("needs_escalation"):
        conversation.current_intent = None
        # Create a ticket for the escalated VPN issue
        ticket = await create_ticket(
            employee_id=employee_id,
            subject="VPN Connection Issue — Escalated from Troubleshooting",
            description="VPN troubleshooting completed without resolution. All standard steps attempted.",
            category="vpn",
            priority="high",
            conversation_id=conversation.conversation_id,
        )

        escalation_result = {
            "should_escalate": True,
            "reasons": ["VPN troubleshooting exhausted all standard steps without resolution"],
            "urgency": "high",
        }
        esc_response = await _handle_escalation(conversation, employee_id, escalation_result)
        esc_response.ticket_id = ticket.ticket_id
        return esc_response

    if result.get("is_resolved"):
        conversation.current_intent = None

    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=result["message"],
        intent="vpn_issue",
        confidence=0.9,
        troubleshooting_step=result["step"],
        suggested_actions=["yes", "no"] if result["step"] >= 0 else None,
    )


async def _handle_faq(
    conversation: Conversation,
    message: str,
    confidence: float,
) -> ChatMessageResponse:
    """Handle FAQ queries by searching the knowledge base."""
    await log_action(
        action_type=AuditActionType.FAQ_SEARCHED,
        actor=AuditActor.AGENT,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={"query": message[:100]},
    )

    search_result = await search_and_respond(message)

    sources = None
    if search_result.get("sources"):
        from app.schemas.chat_schema import SourceReferenceSchema
        sources = [
            SourceReferenceSchema(
                source_name=s["source_name"],
                source_type=s["source_type"],
                relevance_score=s.get("relevance_score"),
                excerpt=s.get("excerpt"),
            )
            for s in search_result["sources"]
        ]

    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=search_result["answer"],
        intent="faq",
        confidence=search_result.get("confidence", confidence),
        sources=sources,
    )


async def _handle_ticket_request(
    conversation: Conversation,
    message: str,
    employee_id: str,
) -> ChatMessageResponse:
    """Handle ticket creation or status check requests."""
    message_lower = message.lower()

    # Check if user wants to check ticket status
    if any(word in message_lower for word in ["status", "check", "track", "my ticket", "update on"]):
        tickets_result = await get_tickets(employee_id=employee_id, page_size=5)
        tickets = tickets_result.get("tickets", [])

        if not tickets:
            return ChatMessageResponse(
                conversation_id=conversation.conversation_id,
                message="You don't have any recent tickets. Would you like me to create a new one?",
                intent="ticket_request",
                confidence=0.8,
                suggested_actions=["Create a ticket", "No thanks"],
            )

        ticket_list = "\n".join([
            f"• **{t['ticket_id']}** — {t['subject']} (Status: `{t['status']}`, Priority: `{t['priority']}`)"
            for t in tickets
        ])

        return ChatMessageResponse(
            conversation_id=conversation.conversation_id,
            message=f"Here are your recent tickets:\n\n{ticket_list}\n\nWould you like more details on any of these?",
            intent="ticket_request",
            confidence=0.85,
        )

    # Create a new ticket
    # Extract subject from the message
    subject = message[:100] if len(message) > 20 else "IT Support Request"
    description = message

    ticket = await create_ticket(
        employee_id=employee_id,
        subject=subject,
        description=description,
        conversation_id=conversation.conversation_id,
    )

    await log_action(
        action_type=AuditActionType.TICKET_CREATED,
        actor=AuditActor.AGENT,
        actor_id=employee_id,
        target_entity=ticket.ticket_id,
        target_type="ticket",
        details={
            "subject": ticket.subject,
            "priority": ticket.priority.value,
            "category": ticket.category.value,
        },
    )

    conversation.linked_ticket_id = ticket.ticket_id

    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=(
            f"I've created a support ticket for you! 🎫\n\n"
            f"**Ticket ID**: `{ticket.ticket_id}`\n"
            f"**Subject**: {ticket.subject}\n"
            f"**Category**: {ticket.category.value}\n"
            f"**Priority**: {ticket.priority.value}\n"
            f"**Status**: Open\n\n"
            f"Our IT team will review this and get back to you based on the priority SLA. "
            f"You can check the status anytime by asking me about your tickets."
        ),
        intent="ticket_request",
        confidence=0.9,
        ticket_id=ticket.ticket_id,
    )


async def _handle_escalation(
    conversation: Conversation,
    employee_id: str,
    escalation_result: Dict[str, Any],
) -> ChatMessageResponse:
    """Handle escalation to human agent."""
    # Create ticket if not exists
    ticket_id = conversation.linked_ticket_id
    if not ticket_id:
        ticket = await create_ticket(
            employee_id=employee_id,
            subject="Escalated Support Request",
            description=f"Escalation reasons: {'; '.join(escalation_result.get('reasons', []))}",
            priority="high",
            conversation_id=conversation.conversation_id,
        )
        ticket_id = ticket.ticket_id
        conversation.linked_ticket_id = ticket_id

    esc_result = await process_escalation(
        conversation_id=conversation.conversation_id,
        employee_id=employee_id,
        reasons=escalation_result.get("reasons", []),
        urgency=escalation_result.get("urgency", "medium"),
        ticket_id=ticket_id,
    )

    await log_action(
        action_type=AuditActionType.ESCALATION_TRIGGERED,
        actor=AuditActor.AGENT,
        target_entity=conversation.conversation_id,
        target_type="conversation",
        details={
            "reasons": escalation_result.get("reasons", []),
            "urgency": escalation_result.get("urgency"),
            "ticket_id": ticket_id,
        },
    )

    conversation.status = ConversationStatus.ESCALATED

    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=esc_result["message"],
        intent="escalation",
        confidence=1.0,
        escalated=True,
        escalation_reason=escalation_result.get("reasons", [""])[0] if escalation_result.get("reasons") else None,
        ticket_id=ticket_id,
    )


async def _handle_general(
    conversation: Conversation,
    message: str,
) -> ChatMessageResponse:
    """Handle general/greeting messages."""
    message_lower = message.lower().strip()

    # Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(message_lower.startswith(g) for g in greetings):
        return ChatMessageResponse(
            conversation_id=conversation.conversation_id,
            message=(
                "Hello! 👋 Welcome to IT Support.\n\n"
                "I'm your AI support assistant. I can help you with:\n\n"
                "• 🌐 **VPN Issues** — Troubleshoot connectivity problems\n"
                "• ❓ **IT Questions** — Password resets, email setup, software requests\n"
                "• 🎫 **Support Tickets** — Create or check ticket status\n"
                "• 🔔 **Escalation** — Connect you with a human agent\n\n"
                "How can I help you today?"
            ),
            intent="general",
            confidence=0.95,
            suggested_actions=[
                "I have a VPN issue",
                "I need to reset my password",
                "Create a ticket",
                "Talk to a human",
            ],
        )

    # Thanks
    thanks_words = ["thank", "thanks", "appreciate", "helpful"]
    if any(w in message_lower for w in thanks_words):
        return ChatMessageResponse(
            conversation_id=conversation.conversation_id,
            message=(
                "You're welcome! 😊 Glad I could help.\n\n"
                "Is there anything else I can assist you with?"
            ),
            intent="general",
            confidence=0.95,
        )

    # Goodbye
    bye_words = ["bye", "goodbye", "see you", "that's all", "nothing else"]
    if any(w in message_lower for w in bye_words):
        conversation.status = ConversationStatus.CLOSED
        return ChatMessageResponse(
            conversation_id=conversation.conversation_id,
            message=(
                "Goodbye! 👋 Have a great day!\n\n"
                "If you need help in the future, don't hesitate to reach out. "
                "You can also check our IT FAQ at https://itportal.company.com for quick answers."
            ),
            intent="general",
            confidence=0.95,
        )

    # Default fallback
    return ChatMessageResponse(
        conversation_id=conversation.conversation_id,
        message=(
            "I'm not sure I understand what you need. Could you rephrase that?\n\n"
            "Here are some things I can help with:\n"
            "• VPN connection issues\n"
            "• Password resets and account access\n"
            "• Software installation requests\n"
            "• General IT questions\n"
            "• Creating support tickets\n\n"
            "Or type **\"talk to human\"** to connect with a live agent."
        ),
        intent="general",
        confidence=0.3,
        suggested_actions=[
            "I have a VPN issue",
            "How do I reset my password?",
            "Create a ticket",
            "Talk to a human",
        ],
    )


def _build_context(conversation: Conversation) -> str:
    """Build conversation context string for intent detection."""
    if not conversation.messages:
        return ""

    recent = conversation.messages[-6:]  # Last 6 messages
    context_parts = []
    for msg in recent:
        role = "User" if msg.role == MessageRole.USER else "Agent"
        context_parts.append(f"{role}: {msg.content[:200]}")

    return "\n".join(context_parts)


async def get_conversations_for_employee(employee_id: str) -> list:
    """Get all conversations for an employee."""
    cursor = database.conversations.find(
        {"employee_id": employee_id}
    ).sort("updated_at", -1)

    conversations = []
    async for doc in cursor:
        doc.pop("_id", None)
        last_msg = None
        messages = doc.get("messages", [])
        if messages:
            last_msg = messages[-1].get("content", "")[:100]

        conversations.append({
            "conversation_id": doc["conversation_id"],
            "employee_id": doc["employee_id"],
            "last_message": last_msg,
            "status": doc.get("status", "active"),
            "current_intent": doc.get("current_intent"),
            "message_count": len(messages),
            "created_at": doc.get("created_at", ""),
            "updated_at": doc.get("updated_at", ""),
        })

    return conversations


async def get_conversation_history(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get full conversation history."""
    doc = await database.conversations.find_one({"conversation_id": conversation_id})
    if not doc:
        return None

    doc.pop("_id", None)
    return doc
