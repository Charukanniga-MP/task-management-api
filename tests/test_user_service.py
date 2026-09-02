import unittest
from app.services.user_service import UserService


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()

    def test_create_user_success(self):
        user = self.user_service.create_user("Alice", "alice@example.com")
        self.assertNotEqual(user, "Invalid user details")
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")

    def test_create_user_invalid_name(self):
        result = self.user_service.create_user("", "alice@example.com")
        self.assertEqual(result, "Invalid user details")

    def test_create_user_invalid_email(self):
        result = self.user_service.create_user("Alice", "invalid-email")
        self.assertEqual(result, "Invalid user details")

    def test_get_user_success(self):
        created_user = self.user_service.create_user("Bob", "bob@example.com")
        retrieved_user = self.user_service.get_user(created_user.user_id)
        self.assertEqual(retrieved_user, created_user)

    def test_get_user_not_found(self):
        result = self.user_service.get_user(999)
        self.assertEqual(result, "User not found")

    def test_update_user_success(self):
        user = self.user_service.create_user("Charlie", "charlie@example.com")
        updated_user = self.user_service.update_user(user.user_id, "Charlie Updated", "charlie_new@example.com")
        self.assertNotEqual(updated_user, "User not found")
        self.assertNotEqual(updated_user, "Invalid user details")
        self.assertEqual(updated_user.name, "Charlie Updated")
        self.assertEqual(updated_user.email, "charlie_new@example.com")

    def test_update_user_invalid_data(self):
        user = self.user_service.create_user("David", "david@example.com")
        result = self.user_service.update_user(user.user_id, "", "invalid-email")
        self.assertEqual(result, "Invalid user details")
        # Ensure user object was not modified
        self.assertEqual(user.name, "David")

    def test_update_user_not_found(self):
        result = self.user_service.update_user(999, "New Name", "new@example.com")
        self.assertEqual(result, "User not found")

    def test_delete_user_success(self):
        user = self.user_service.create_user("Eve", "eve@example.com")
        result = self.user_service.delete_user(user.user_id)
        self.assertEqual(result, "User deleted successfully")
        self.assertEqual(self.user_service.get_user(user.user_id), "User not found")

    def test_delete_user_not_found(self):
        result = self.user_service.delete_user(999)
        self.assertEqual(result, "User not found")


if __name__ == "__main__":
    unittest.main()
