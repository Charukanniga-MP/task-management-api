"""Centralized Logging Configuration Module for Task Analytics (Day 7).

Provides:
- JSONFormatter: Custom Formatter producing single-line JSON structured log records.
- TextFormatter: Human-readable Formatter for development console output.
- configure_logging: Single entry point function to initialize structured logging.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Union

# Built-in attributes of logging.LogRecord to filter out custom extra fields
LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    """Custom logging Formatter that outputs log records as structured JSON strings.

    Includes core metadata (timestamp, level, logger, message, location) and dynamically
    captures any extra contextual attributes (step, duration, records_processed, etc.)
    and exception tracebacks.
    """

    def __init__(
        self,
        datefmt: Optional[str] = None,
        include_location: bool = True,
    ) -> None:
        """Initialize JSONFormatter.

        Args:
            datefmt: Optional datetime format string.
            include_location: Whether to include module, function, and line number fields.
        """
        super().__init__(datefmt=datefmt)
        self.include_location = include_location

    def format(self, record: logging.LogRecord) -> str:
        """Format the LogRecord as a single-line JSON string.

        Args:
            record: LogRecord instance to format.

        Returns:
            JSON-serialized string.
        """
        # Determine timestamp in ISO-8601 format
        if self.datefmt:
            timestamp = self.formatTime(record, self.datefmt)
        else:
            timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()

        log_data: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_location:
            log_data["module"] = record.module
            log_data["function"] = record.funcName
            log_data["line"] = record.lineno

        # Extract extra fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS and not key.startswith("_"):
                log_data[key] = value

        # Format exception information if present
        if record.exc_info:
            log_data["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            log_data["error_message"] = str(record.exc_info[1]) if record.exc_info[1] else ""
            log_data["traceback"] = self.formatException(record.exc_info)
        elif record.exc_text:
            log_data["traceback"] = record.exc_text

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Readable log Formatter for development console environments."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        default_fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s]: %(message)s"
        super().__init__(fmt=fmt or default_fmt, datefmt=datefmt or "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        # Append extras if present for console visibility
        extras = []
        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS and not key.startswith("_"):
                extras.append(f"{key}={value}")
        if extras:
            formatted += f" ({', '.join(extras)})"
        return formatted


def configure_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    env: str = "production",
    json_format: Optional[bool] = None,
    logger_name: Optional[str] = "task_analytics",
) -> logging.Logger:
    """Configures centralized logging ONCE for the application or package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) as int or string.
        log_file: Optional file path to write log records to.
        env: Target environment ('production' or 'development').
        json_format: Explicit toggle for JSON formatting. If None, defaults to True in production,
                     False in development.
        logger_name: Target logger name. Defaults to 'task_analytics'. If None, configures root logger.

    Returns:
        Configured Logger instance.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    if json_format is None:
        json_format = env.lower() == "production"

    target_logger = logging.getLogger(logger_name)
    target_logger.setLevel(level)

    # Remove existing handlers from target_logger to prevent duplication
    for handler in list(target_logger.handlers):
        target_logger.removeHandler(handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(TextFormatter())
    target_logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_path = Path(log_file)
        if log_path.parent:
            log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setLevel(level)
        # File handler always uses JSONFormatter for structured audit trail
        file_handler.setFormatter(JSONFormatter())
        target_logger.addHandler(file_handler)

    # Ensure parent loggers do not duplicate messages if configuring child logger
    target_logger.propagate = False

    return target_logger
