"""Custom decorators for cross-cutting concerns like logging and timing.

SOLID Principles Applied:
- Open/Closed Principle (OCP): Adds execution logging and performance tracking without altering core business logic.
"""

import functools
import time
from typing import Any, Callable
from app.utils.logger import logger


def log_action(action_name: str = "") -> Callable:
    """Decorator that logs method entry, arguments, execution duration, and exceptions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            display_name = action_name or func.__name__
            logger.debug(f"Executing '{display_name}' with args={args[1:]}, kwargs={kwargs}")
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"Action '{display_name}' finished in {elapsed_ms:.2f}ms")
                return result
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.warning(f"Action '{display_name}' failed after {elapsed_ms:.2f}ms with exception: {exc}")
                raise
        return wrapper
    return decorator
