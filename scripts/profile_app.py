"""Performance profiling script for the Task Management API.

Uses cProfile and pstats to analyze execution performance of bulk user and task operations.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cProfile
import pstats
import io
from app.services.user_service import UserService
from app.services.task_service import TaskService


def run_workload() -> None:
    """Executes a workload of user and task creation, updates, searches, and statistics."""
    user_service = UserService()
    task_service = TaskService()

    # Bulk User Creation
    for i in range(100):
        user_service.create_user(f"User_{i}", f"user_{i}@example.com")

    # Bulk Task Creation
    priorities = ["low", "medium", "high"]
    for i in range(200):
        priority = priorities[i % 3]
        task_service.create_task(
            f"Task Title {i}", f"Task Description {i}", priority=priority
        )

    # Updates and Filtering
    for task in list(task_service)[:50]:
        task_service.update_task_status(task.task_id, "in_progress")

    for task in list(task_service)[50:100]:
        task_service.update_task_status(task.task_id, "completed")

    # Search, Sort, Statistics
    task_service.search_tasks("Title 1")
    task_service.sort_tasks(sort_by="priority", descending=True)
    task_service.get_task_statistics()


def main() -> None:
    print("=== Task Management API Performance Profiling ===")
    pr = cProfile.Profile()
    pr.enable()

    run_workload()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)

    print(s.getvalue())
    print("=== Profiling Complete ===")


if __name__ == "__main__":
    main()
