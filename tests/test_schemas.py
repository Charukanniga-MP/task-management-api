import unittest
from pydantic import ValidationError as PydanticValidationError
from app.schemas.user_schema import UserSchema
from app.schemas.task_schema import TaskSchema


class TestSchemas(unittest.TestCase):
    def test_valid_user_schema(self) -> None:
        user_schema = UserSchema(name="John Doe", email="john@example.com")
        self.assertEqual(user_schema.name, "John Doe")
        self.assertEqual(user_schema.email, "john@example.com")

    def test_invalid_user_schema_empty_name(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UserSchema(name="", email="john@example.com")

    def test_invalid_user_schema_invalid_email(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UserSchema(name="John", email="invalid-email-address")

    def test_valid_task_schema(self) -> None:
        task_schema = TaskSchema(
            title="Complete Task",
            description="Detailed Description",
            status="in_progress",
            priority="high",
        )
        self.assertEqual(task_schema.title, "Complete Task")
        self.assertEqual(task_schema.status, "in_progress")
        self.assertEqual(task_schema.priority, "high")

    def test_invalid_task_schema_empty_title(self) -> None:
        with self.assertRaises(PydanticValidationError):
            TaskSchema(title="", description="Valid Description")

    def test_invalid_task_schema_status(self) -> None:
        with self.assertRaises(PydanticValidationError):
            TaskSchema(title="Title", description="Desc", status="invalid_status")

    def test_invalid_task_schema_priority(self) -> None:
        with self.assertRaises(PydanticValidationError):
            TaskSchema(title="Title", description="Desc", priority="invalid_priority")


if __name__ == "__main__":
    unittest.main()
