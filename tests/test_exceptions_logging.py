import unittest
from app.utils.exceptions import (
    TaskManagementError,
    UserNotFoundError,
    TaskNotFoundError,
    ValidationError,
    InvalidStatusError,
    InvalidPriorityError,
)
from app.utils.logger import get_logger


class TestExceptionsLogging(unittest.TestCase):
    def test_exception_inheritance(self) -> None:
        self.assertTrue(issubclass(UserNotFoundError, TaskManagementError))
        self.assertTrue(issubclass(TaskNotFoundError, TaskManagementError))
        self.assertTrue(issubclass(ValidationError, TaskManagementError))
        self.assertTrue(issubclass(InvalidStatusError, ValidationError))
        self.assertTrue(issubclass(InvalidPriorityError, ValidationError))

    def test_logger_instance(self) -> None:
        logger = get_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")


if __name__ == "__main__":
    unittest.main()
