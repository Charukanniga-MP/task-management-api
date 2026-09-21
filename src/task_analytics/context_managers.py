"""Context Managers Module for Task Analytics.

Provides resource management tools that guarantee cleanup even if exceptions occur:
- TaskResourceManager: Class-based context manager (__enter__ / __exit__).
- managed_resource: Generator-based context manager using contextlib.contextmanager.
"""

import contextlib
import logging
from typing import Any, Generator, Optional, Union

# Configure module logger
logger = logging.getLogger(__name__)


class TaskResourceManager:
    """Class-based context manager for managing resource lifecycles.

    Demonstrates __enter__ and __exit__ protocol.
    Guarantees resource release/cleanup whether the code block completes normally
    or raises an exception.
    """

    def __init__(self, resource_name: str, resource_data: Optional[Any] = None) -> None:
        """Initialize resource manager.

        Args:
            resource_name: Name or path identifier of the resource.
            resource_data: Optional initial payload or resource handle object.
        """
        self.resource_name = resource_name
        self.resource_data = resource_data or {"status": "uninitialized", "name": resource_name}
        self.is_open: bool = False

    def __enter__(self) -> "TaskResourceManager":
        """Acquires/opens the resource upon entering the with block."""
        self.is_open = True
        if isinstance(self.resource_data, dict):
            self.resource_data["status"] = "active"
        logger.info(f"[Resource Manager] Acquired resource: '{self.resource_name}'")
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> bool:
        """Releases/cleans up the resource upon exiting the with block.

        Args:
            exc_type: Exception type if raised inside with block, else None.
            exc_val: Exception instance if raised inside with block, else None.
            exc_tb: Traceback object if raised inside with block, else None.

        Returns:
            False to propagate exceptions normally.
        """
        self.is_open = False
        if isinstance(self.resource_data, dict):
            self.resource_data["status"] = "closed"

        if exc_type is not None:
            logger.warning(
                f"[Resource Manager] Cleaning up resource '{self.resource_name}' after exception: {exc_val}"
            )
        else:
            logger.info(f"[Resource Manager] Cleaned up resource '{self.resource_name}' successfully.")

        return False  # Never swallow exceptions; allow caller to handle or re-raise


@contextlib.contextmanager
def managed_resource(
    resource_name: str, payload: Optional[Any] = None
) -> Generator[dict, None, None]:
    """Generator-based context manager using contextlib.contextmanager.

    Guarantees cleanup in a finally block even when exceptions are raised inside
    the with block.

    Args:
        resource_name: Name or identifier of the resource.
        payload: Optional initial data payload.

    Yields:
        Resource dictionary representation.
    """
    resource_handle = {
        "name": resource_name,
        "payload": payload,
        "is_active": True,
        "cleaned_up": False,
    }
    logger.info(f"[managed_resource] Opened resource: '{resource_name}'")
    try:
        yield resource_handle
    except Exception as exc:
        logger.warning(
            f"[managed_resource] Exception encountered for '{resource_name}': {exc}"
        )
        raise
    finally:
        resource_handle["is_active"] = False
        resource_handle["cleaned_up"] = True
        logger.info(f"[managed_resource] Resource '{resource_name}' cleaned up.")
