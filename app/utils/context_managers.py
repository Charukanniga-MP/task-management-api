"""Custom context managers for resource management and execution tracking.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Handles context execution lifecycle and timing independently.
"""

import time
from typing import Optional
from app.utils.logger import logger


class OperationTimer:
    """Context manager to measure and log the execution time of a code block."""

    def __init__(self, operation_name: str = "Operation") -> None:
        self.operation_name = operation_name
        self.start_time: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "OperationTimer":
        self.start_time = time.perf_counter()
        logger.info(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> bool:
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        if exc_type is not None:
            logger.error(
                f"Operation '{self.operation_name}' failed after {self.elapsed_ms:.2f}ms with error: {exc_val}"
            )
        else:
            logger.info(
                f"Operation '{self.operation_name}' completed in {self.elapsed_ms:.2f}ms"
            )
        return False  # Propagate exceptions normally
