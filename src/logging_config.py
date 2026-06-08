"""
Structured Logging Configuration - JSON logging with rotation

Implements:
- JSON formatted logs
- Log rotation (10MB per file, keep 10 files)
- Contextual information
- Configurable log levels
"""

import logging
import json
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "segment"):
            log_data["segment"] = record.segment
        if hasattr(record, "campaign_id"):
            log_data["campaign_id"] = record.campaign_id

        try:
            return json.dumps(log_data)
        except (TypeError, ValueError):
            # Fallback if JSON serialization fails
            return str(log_data)


class TextFormatter(logging.Formatter):
    """Simple text formatter for console output"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text"""
        if record.exc_info:
            return (
                f"[{record.levelname}] {record.name}: {record.getMessage()}\n"
                f"{self.formatException(record.exc_info)}"
            )
        return f"[{record.levelname}] {record.name}: {record.getMessage()}"


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: str = "logs/app.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 10
) -> logging.Logger:
    """
    Configure structured logging

    Args:
        log_level: DEBUG, INFO, WARNING, ERROR
        log_format: "json" or "text"
        log_file: Path to log file
        max_bytes: Max file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured root logger
    """
    # Create logs directory if needed
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Get root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(getattr(logging, log_level))

    if log_format == "json":
        console.setFormatter(JSONFormatter())
    else:
        console.setFormatter(TextFormatter())

    root.addHandler(console)

    # File handler with rotation
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level))

        if log_format == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(TextFormatter())

        root.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not configure file logging: {e}")

    return root


# Initialize default logging on import
logger = configure_logging()


def get_logger(name: str) -> logging.Logger:
    """Get logger for module"""
    return logging.getLogger(name)
