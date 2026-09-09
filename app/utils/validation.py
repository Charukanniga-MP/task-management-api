"""Validation utility leveraging Pydantic schemas and custom exceptions.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Bridges data contracts (schemas) and service validation operations.
"""

from typing import Any
from pydantic import ValidationError as PydanticValidationError
from app.schemas.user_schema import UserSchema
from app.schemas.task_schema import TaskSchema
from app.utils.exceptions import (
    ValidationError,
    InvalidPriorityError,
    InvalidStatusError,
)


def validate_user(name: Any, email: Any) -> bool:
    """Validates user data using UserSchema. Raises ValidationError on invalid input."""
    try:
        UserSchema(name=name, email=email)
        return True
    except (PydanticValidationError, TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid user details: {exc}") from exc


def validate_priority(priority: Any) -> bool:
    """Validates task priority. Raises InvalidPriorityError on invalid input."""
    if priority not in {"low", "medium", "high"}:
        raise InvalidPriorityError(f"Invalid priority '{priority}'")
    return True


def validate_status(status: Any) -> bool:
    """Validates task status. Raises InvalidStatusError on invalid input."""
    if status not in {"pending", "in_progress", "completed"}:
        raise InvalidStatusError(f"Invalid status '{status}'")
    return True


def validate_task(
    title: Any, description: Any, priority: str = "medium", status: str = "pending"
) -> bool:
    """Validates task data using TaskSchema. Raises ValidationError on invalid input."""
    try:
        TaskSchema(
            title=title, description=description, priority=priority, status=status
        )
        return True
    except (PydanticValidationError, TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid task details: {exc}") from exc