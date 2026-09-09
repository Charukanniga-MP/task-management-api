"""User management service handling user business logic and storage.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Manages state and business logic for users.
- Open/Closed Principle (OCP): Class functionality can be decorated or extended without internal logic changes.
"""

from typing import List, Union
from app.models.user import User
from app.utils.validation import validate_user
from app.utils.helpers import generate_id
from app.utils.exceptions import UserNotFoundError, ValidationError
from app.utils.logger import logger
from app.utils.decorators import log_action


class UserIterator:
    """Iterator class implementing Python's iterator protocol (__iter__ and __next__) for Users."""

    def __init__(self, users: List[User]) -> None:
        self._users: List[User] = users
        self._index: int = 0

    def __iter__(self) -> "UserIterator":
        return self

    def __next__(self) -> User:
        if self._index < len(self._users):
            user = self._users[self._index]
            self._index += 1
            return user
        raise StopIteration


class UserService:
    """Service class providing CRUD operations and iteration for User entities."""

    def __init__(self) -> None:
        self.users: List[User] = []

    def __iter__(self) -> UserIterator:
        """Returns an iterator over the stored users."""
        return UserIterator(self.users)

    @log_action("create_user")
    def create_user(self, name: str, email: str) -> User:
        """Creates a new user after validation. Raises ValidationError if input is invalid."""
        validate_user(name, email)

        user_id = generate_id(self.users)
        user = User(user_id, name, email)
        self.users.append(user)
        logger.info(f"Created user ID {user_id} ({name}, {email})")
        return user

    @log_action("get_users")
    def get_users(self) -> List[str]:
        """Returns list of string representations of all users."""
        return [str(user) for user in self.users]

    @log_action("get_user")
    def get_user(self, user_id: int) -> User:
        """Retrieves a user by ID. Raises UserNotFoundError if not found."""
        for user in self.users:
            if user.user_id == user_id:
                return user
        logger.warning(f"User with ID {user_id} not found")
        raise UserNotFoundError(f"User with ID {user_id} not found")

    @log_action("update_user")
    def update_user(self, user_id: int, name: str, email: str) -> User:
        """Updates an existing user's details. Raises UserNotFoundError or ValidationError."""
        user = self.get_user(user_id)
        validate_user(name, email)

        user.name = name
        user.email = email
        logger.info(f"Updated user ID {user_id} details")
        return user

    @log_action("delete_user")
    def delete_user(self, user_id: int) -> str:
        """Deletes a user by ID. Raises UserNotFoundError if not found."""
        user = self.get_user(user_id)
        self.users.remove(user)
        logger.info(f"Deleted user ID {user_id}")
        return "User deleted successfully"