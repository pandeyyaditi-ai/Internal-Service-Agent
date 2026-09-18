"""
Core __init__ for the core module.
"""
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

__all__ = ["settings", "get_logger", "setup_logging"]
