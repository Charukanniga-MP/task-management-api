"""Centralized logging utility for the Task Management API.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Logger configuration is isolated to a single module.
"""

import logging
import sys


def get_logger(name: str = "task_management_api") -> logging.Logger:
    """Configures and returns a logger instance with standard stream formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = get_logger()
