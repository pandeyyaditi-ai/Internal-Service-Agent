"""
Master API router aggregating all sub-routers.
"""
from fastapi import APIRouter
from app.api.chat_routes import router as chat_router
from app.api.ticket_routes import router as ticket_router
from app.api.audit_routes import router as audit_router

api_router = APIRouter(prefix="/api")
api_router.include_router(chat_router)
api_router.include_router(ticket_router)
api_router.include_router(audit_router)
