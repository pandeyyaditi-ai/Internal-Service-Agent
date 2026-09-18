"""
Structured JSON logging with correlation IDs for request tracing.
"""
import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from contextvars import ContextVar

# Context variable for request correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        corr_id = correlation_id_var.get("")
        if corr_id:
            log_entry["correlation_id"] = corr_id

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(f"isa.{name}")


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return str(uuid.uuid4())[:8]


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set the correlation ID for the current context."""
    cid = corr_id or generate_correlation_id()
    correlation_id_var.set(cid)
    return cid
