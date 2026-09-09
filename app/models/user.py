"""User domain model with full type hints.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Represents user domain entity state and string formatting.
"""


class User:
    """Represents a User entity in the system."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        self.user_id: int = user_id
        self.name: str = name
        self.email: str = email

    def __str__(self) -> str:
        return f"User(id={self.user_id}, name={self.name}, email={self.email})"