"""Custom exception classes for the Task Management API.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Each exception represents a specific error domain.
- Open/Closed Principle (OCP): New exception types can extend TaskManagementError without modifying existing catch blocks.
"""


class TaskManagementError(Exception):
    """Base exception for all application-specific errors."""
    pass


class UserNotFoundError(TaskManagementError):
    """Raised when a requested user cannot be found."""
    pass


class TaskNotFoundError(TaskManagementError):
    """Raised when a requested task cannot be found."""
    pass


class ValidationError(TaskManagementError):
    """Raised when data validation fails."""
    pass


class InvalidStatusError(ValidationError):
    """Raised when an invalid task status is provided."""
    pass


class InvalidPriorityError(ValidationError):
    """Raised when an invalid task priority is provided."""
    pass
