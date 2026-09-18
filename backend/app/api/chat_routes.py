"""
Chat API routes — handles messaging and conversation management.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import json
from app.schemas.chat_schema import ChatMessageRequest, ChatMessageResponse
from app.schemas.response_schema import APIResponse
from app.services.agent import process_message, get_conversations_for_employee, get_conversation_history
from app.core.logging import get_logger

logger = get_logger("chat_routes")
router = APIRouter(prefix="/chat", tags=["Chat"])

# WebSocket connection manager
class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, employee_id: str):
        await websocket.accept()
        self.active_connections[employee_id] = websocket
        logger.info(f"WebSocket connected: {employee_id}")

    def disconnect(self, employee_id: str):
        self.active_connections.pop(employee_id, None)
        logger.info(f"WebSocket disconnected: {employee_id}")

    async def send_message(self, employee_id: str, message: dict):
        ws = self.active_connections.get(employee_id)
        if ws:
            await ws.send_json(message)


manager = ConnectionManager()


@router.post("/message", response_model=APIResponse)
async def send_message(request: ChatMessageRequest):
    """Send a chat message and receive an AI response."""
    try:
        response = await process_message(
            employee_id=request.employee_id,
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return APIResponse.ok(data=response.model_dump())
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/conversations/{employee_id}", response_model=APIResponse)
async def get_conversations(employee_id: str):
    """Get all conversations for an employee."""
    try:
        conversations = await get_conversations_for_employee(employee_id)
        return APIResponse.ok(data=conversations)
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        return APIResponse.fail(error=str(e))


@router.get("/conversation/{conversation_id}", response_model=APIResponse)
async def get_conversation(conversation_id: str):
    """Get full conversation history."""
    try:
        history = await get_conversation_history(conversation_id)
        if not history:
            return APIResponse.fail(error="Conversation not found")
        return APIResponse.ok(data=history)
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        return APIResponse.fail(error=str(e))


@router.websocket("/ws/{employee_id}")
async def websocket_chat(websocket: WebSocket, employee_id: str):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket, employee_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
                message = msg_data.get("message", "")
                conversation_id = msg_data.get("conversation_id")

                # Process through the agent
                response = await process_message(
                    employee_id=employee_id,
                    message=message,
                    conversation_id=conversation_id,
                )

                await websocket.send_json(response.model_dump())

            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                logger.error(f"WebSocket processing error: {e}")
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(employee_id)
