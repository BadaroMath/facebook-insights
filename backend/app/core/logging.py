"""
Logging configuration for the Facebook Analytics Platform.
Provides structured logging with JSON format for production environments.
"""

import logging
import logging.config
import sys
from typing import Dict, Any
import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging():
    """Configure application logging."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": settings.LOG_FORMAT if settings.LOG_FORMAT in ["json", "standard"] else "standard",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "app": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "motor": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "pymongo": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Set up Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                integrations=[
                    FastApiIntegration(auto_enable=True),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
                send_default_pii=False,
            )
            
            logging.getLogger(__name__).info("✅ Sentry logging initialized")
            
        except ImportError:
            logging.getLogger(__name__).warning("Sentry SDK not installed, skipping Sentry setup")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to initialize Sentry: {e}")


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


# Custom log filters
class HealthCheckFilter(logging.Filter):
    """Filter out health check requests from logs."""
    
    def filter(self, record):
        message = record.getMessage()
        return "/health" not in message and "/metrics" not in message


# Log correlation ID for request tracing
import uuid
from contextvars import ContextVar

correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id.get()


def set_correlation_id(cid: str = None) -> str:
    """Set correlation ID for current context."""
    if cid is None:
        cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid


def log_function_call(func_name: str, args: dict = None, result: Any = None, error: Exception = None):
    """Log function call with arguments and results."""
    logger = get_logger("function_call")
    
    log_data = {
        "function": func_name,
        "correlation_id": get_correlation_id(),
    }
    
    if args:
        log_data["arguments"] = args
    
    if error:
        log_data["error"] = str(error)
        logger.error("Function call failed", **log_data)
    else:
        if result is not None:
            log_data["result"] = str(result)[:200]  # Truncate long results
        logger.info("Function call completed", **log_data)