"""Main application entry point demonstrating Services, Iterators, Context Managers, and Logging.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Acts solely as orchestrator and entry point for application workflow.
"""

from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.utils.context_managers import OperationTimer
from app.utils.logger import logger
from app.utils.exceptions import TaskManagementError


def main() -> None:
    user_service = UserService()
    task_service = TaskService()

    with OperationTimer("User and Task Initialization"):
        user1 = user_service.create_user("Charu", "charu@gmail.com")
        user2 = user_service.create_user("Alice", "alice@example.com")

        task1 = task_service.create_task(
            "Learn Python", "Practice modular Python", priority="high"
        )
        task2 = task_service.create_task(
            "Build API", "Implement Task Management API", priority="medium"
        )

        task_service.update_task_status(task1.task_id, "in_progress")

    logger.info("--- Iterating over Users (using UserService Iterator) ---")
    for user in user_service:
        logger.info(f"Iterated User: {user}")

    logger.info("--- Iterating over Tasks (using TaskService Iterator) ---")
    for task in task_service:
        logger.info(f"Iterated Task: {task}")

    with OperationTimer("Calculate Task Statistics"):
        stats = task_service.get_task_statistics()
        logger.info(f"Task Statistics Summary: {stats}")

    # Exception Handling Demonstration
    try:
        user_service.get_user(999)
    except TaskManagementError as exc:
        logger.info(f"Demonstrating handled exception: {exc}")


if __name__ == "__main__":
    main()