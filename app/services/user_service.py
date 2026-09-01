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