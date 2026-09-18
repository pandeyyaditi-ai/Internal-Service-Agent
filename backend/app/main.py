"""
FastAPI application entry point.
Initializes the app, configures CORS, mounts routers, and handles startup/shutdown events.
"""
import os
import sys

# Ensure backend root is on sys.path when executed directly
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.database.database import database
from app.database.seed import seed_database
from app.api.routes import api_router
from app.schemas.response_schema import APIResponse, HealthResponse

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await database.connect()
    await seed_database()
    logger.info("Application started successfully")
    yield
    # Shutdown
    await database.disconnect()
    logger.info("Application shut down")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered IT helpdesk agent for internal employee support",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router)


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint."""
    return APIResponse.ok(data={
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    })


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_healthy = await database.health_check()
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")

    return HealthResponse(
        status="healthy" if db_healthy else "degraded",
        version=settings.APP_VERSION,
        database="connected" if db_healthy else "disconnected",
        gemini="configured" if gemini_configured else "not configured (using fallback)",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

