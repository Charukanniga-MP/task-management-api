import unittest
from app.services.user_service import UserService
from app.utils.exceptions import UserNotFoundError, ValidationError


class TestUserService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()

    def test_create_user_success(self) -> None:
        user = self.user_service.create_user("Alice", "alice@example.com")
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")

    def test_create_user_invalid_name(self) -> None:
        with self.assertRaises(ValidationError):
            self.user_service.create_user("", "alice@example.com")

    def test_create_user_invalid_email(self) -> None:
        with self.assertRaises(ValidationError):
            self.user_service.create_user("Alice", "invalid-email")

    def test_get_user_success(self) -> None:
        created_user = self.user_service.create_user("Bob", "bob@example.com")
        retrieved_user = self.user_service.get_user(created_user.user_id)
        self.assertEqual(retrieved_user, created_user)

    def test_get_user_not_found(self) -> None:
        with self.assertRaises(UserNotFoundError):
            self.user_service.get_user(999)

    def test_update_user_success(self) -> None:
        user = self.user_service.create_user("Charlie", "charlie@example.com")
        updated_user = self.user_service.update_user(
            user.user_id, "Charlie Updated", "charlie_new@example.com"
        )
        self.assertEqual(updated_user.name, "Charlie Updated")
        self.assertEqual(updated_user.email, "charlie_new@example.com")

    def test_update_user_invalid_data(self) -> None:
        user = self.user_service.create_user("David", "david@example.com")
        with self.assertRaises(ValidationError):
            self.user_service.update_user(user.user_id, "", "invalid-email")
        self.assertEqual(user.name, "David")

    def test_update_user_not_found(self) -> None:
        with self.assertRaises(UserNotFoundError):
            self.user_service.update_user(999, "New Name", "new@example.com")

    def test_delete_user_success(self) -> None:
        user = self.user_service.create_user("Eve", "eve@example.com")
        result = self.user_service.delete_user(user.user_id)
        self.assertEqual(result, "User deleted successfully")
        with self.assertRaises(UserNotFoundError):
            self.user_service.get_user(user.user_id)

    def test_delete_user_not_found(self) -> None:
        with self.assertRaises(UserNotFoundError):
            self.user_service.delete_user(999)

    def test_user_service_iterator(self) -> None:
        u1 = self.user_service.create_user("User 1", "u1@example.com")
        u2 = self.user_service.create_user("User 2", "u2@example.com")
        iterated_users = [user for user in self.user_service]
        self.assertEqual(iterated_users, [u1, u2])

    def test_get_users(self) -> None:
        u1 = self.user_service.create_user("User 1", "u1@example.com")
        users_str = self.user_service.get_users()
        self.assertEqual(len(users_str), 1)
        self.assertEqual(users_str[0], str(u1))


if __name__ == "__main__":
    unittest.main()
