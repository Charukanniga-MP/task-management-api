"""Task domain model with full type hints.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Represents task domain entity state and string formatting.
"""


class Task:
    """Represents a Task entity in the system."""

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str,
        status: str = "pending",
        priority: str = "medium",
    ) -> None:
        self.task_id: int = task_id
        self.title: str = title
        self.description: str = description
        self.status: str = status
        self.priority: str = priority

    def __str__(self) -> str:
        return (
            f"Task(id={self.task_id}, "
            f"title={self.title}, "
            f"description={self.description}, "
            f"status={self.status}, "
            f"priority={self.priority})"
        )