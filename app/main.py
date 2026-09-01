from app.services.user_service import UserService
from app.services.task_service import TaskService


def main():
    user_service = UserService()
    task_service = TaskService()

    user = user_service.create_user("Charu", "charu@gmail.com")
    task = task_service.create_task(
        "Learn Python",
        "Practice modular Python"
    )

    print("Created User:")
    print(user)

    print("\nCreated Task:")
    print(task)

    print("\nAll Users:")
    print(user_service.get_users())

    print("\nAll Tasks:")
    print(task_service.get_tasks())


if __name__ == "__main__":
    main()