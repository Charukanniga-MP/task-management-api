"""Reusable Decorators Module for Task Analytics.

Provides decorators for cross-cutting concerns:
- @timeit: Measures and logs function execution time.
- @retry: Parameterized decorator that retries failing functions up to max_attempts.
"""

from functools import wraps
import logging
import time
from typing import Any, Callable

# Module-level logger relying on centralized logging configuration
logger = logging.getLogger(__name__)


def timeit(func: Callable) -> Callable:
    """Decorator that measures and logs the execution time of a function.

    Preserves function metadata (__name__, __doc__, etc.) using functools.wraps.

    Args:
        func: The function to be timed.

    Returns:
        Wrapped function that measures execution duration.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_sec = time.perf_counter() - start_time
            logger.info(
                f"Function '{func.__name__}' executed in {elapsed_sec:.6f} seconds.",
                extra={"function": func.__name__, "duration": round(elapsed_sec, 6)},
            )
            return result
        except Exception as exc:
            elapsed_sec = time.perf_counter() - start_time
            logger.warning(
                f"Function '{func.__name__}' failed after {elapsed_sec:.6f} seconds: {exc}",
                extra={"function": func.__name__, "duration": round(elapsed_sec, 6)},
            )
            raise

    return wrapper


def retry(max_attempts: int = 3) -> Callable:
    """Parameterized decorator that retries a function upon exception up to max_attempts.

    Args:
        max_attempts: Maximum number of execution attempts (must be an integer >= 1).

    Returns:
        Decorator function.

    Raises:
        ValueError: If max_attempts is not an integer or is less than or equal to 0.
    """
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts <= 0:
        raise ValueError(f"max_attempts must be a positive integer, got: {max_attempts}")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception = Exception("No attempts were executed")
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} for '{func.__name__}' failed: {exc}. Retrying...",
                            extra={"function": func.__name__, "attempt": attempt, "max_attempts": max_attempts},
                        )
                    else:
                        logger.error(
                            f"Attempt {attempt}/{max_attempts} for '{func.__name__}' failed: {exc}. All retries exhausted.",
                            extra={"function": func.__name__, "attempt": attempt, "max_attempts": max_attempts},
                        )
            raise last_exception

        return wrapper

    return decorator
