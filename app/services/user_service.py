from app.models.user import User
from app.utils.validation import validate_user
from app.utils.helpers import generate_id


class UserService:
    def __init__(self):
        self.users = []

    def create_user(self, name, email):
        if not validate_user(name, email):
            return "Invalid user details"

        user_id = generate_id(self.users)
        user = User(user_id, name, email)
        self.users.append(user)

        return user

    def get_users(self):
        return [str(user) for user in self.users]

    def get_user(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user
        return "User not found"

    def update_user(self, user_id, name, email):
        user = self.get_user(user_id)
        if user == "User not found":
            return "User not found"

        if not validate_user(name, email):
            return "Invalid user details"

        user.name = name
        user.email = email
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user == "User not found":
            return "User not found"

        self.users.remove(user)
        return "User deleted successfully"