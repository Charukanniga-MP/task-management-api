"""Task management service handling task business logic, storage, and statistics.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Manages state and business operations for tasks.
- Open/Closed Principle (OCP): Methods decorated with cross-cutting concerns without modifying core logic.
"""

from typing import Dict, List, Union
from app.models.task import Task
from app.utils.validation import validate_task, validate_priority, validate_status
from app.utils.helpers import generate_id
from app.utils.exceptions import (
    TaskNotFoundError,
    ValidationError,
    InvalidStatusError,
    InvalidPriorityError,
)
from app.utils.logger import logger
from app.utils.decorators import log_action


class TaskIterator:
    """Iterator class implementing Python's iterator protocol (__iter__ and __next__) for Tasks."""

    def __init__(self, tasks: List[Task]) -> None:
        self._tasks: List[Task] = tasks
        self._index: int = 0

    def __iter__(self) -> "TaskIterator":
        return self

    def __next__(self) -> Task:
        if self._index < len(self._tasks):
            task = self._tasks[self._index]
            self._index += 1
            return task
        raise StopIteration


class TaskService:
    """Service class providing CRUD operations, sorting, filtering, statistics, and iteration for Tasks."""

    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def __iter__(self) -> TaskIterator:
        """Returns an iterator over the stored tasks."""
        return TaskIterator(self.tasks)

    @log_action("create_task")
    def create_task(self, title: str, description: str, priority: str = "medium") -> Task:
        """Creates a new task. Raises ValidationError if inputs are invalid."""
        validate_task(title, description, priority=priority)

        task_id = generate_id(self.tasks)
        task = Task(task_id, title, description, priority=priority)
        self.tasks.append(task)
        logger.info(f"Created task ID {task_id} ('{title}', priority='{priority}')")
        return task

    @log_action("get_tasks")
    def get_tasks(self) -> List[str]:
        """Returns list of string representations of all tasks."""
        return [str(task) for task in self.tasks]

    @log_action("get_tasks_paginated")
    def get_tasks_paginated(self, page: int = 1, limit: int = 5) -> List[Task]:
        """Returns a paginated list of tasks. Raises ValidationError for invalid page/limit."""
        if page <= 0:
            raise ValidationError("Invalid page")
        if limit <= 0:
            raise ValidationError("Invalid limit")

        start_index = (page - 1) * limit
        end_index = start_index + limit
        return self.tasks[start_index:end_index]

    @log_action("get_task")
    def get_task(self, task_id: int) -> Task:
        """Retrieves a task by ID. Raises TaskNotFoundError if not found."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        logger.warning(f"Task with ID {task_id} not found")
        raise TaskNotFoundError(f"Task with ID {task_id} not found")

    @log_action("update_task")
    def update_task(
        self, task_id: int, title: str, description: str, status: str = "pending"
    ) -> Task:
        """Updates task details. Raises TaskNotFoundError, ValidationError, or InvalidStatusError."""
        task = self.get_task(task_id)
        validate_task(title, description, status=status)

        task.title = title
        task.description = description
        task.status = status
        logger.info(f"Updated task ID {task_id} details")
        return task

    @log_action("delete_task")
    def delete_task(self, task_id: int) -> str:
        """Deletes a task by ID. Raises TaskNotFoundError if not found."""
        task = self.get_task(task_id)
        self.tasks.remove(task)
        logger.info(f"Deleted task ID {task_id}")
        return "Task deleted successfully"

    @log_action("update_task_status")
    def update_task_status(self, task_id: int, status: str) -> Task:
        """Updates task status. Raises TaskNotFoundError or InvalidStatusError."""
        task = self.get_task(task_id)
        validate_status(status)

        task.status = status
        logger.info(f"Updated task ID {task_id} status to '{status}'")
        return task

    @log_action("update_task_priority")
    def update_task_priority(self, task_id: int, priority: str) -> Task:
        """Updates task priority. Raises TaskNotFoundError or InvalidPriorityError."""
        task = self.get_task(task_id)
        validate_priority(priority)

        task.priority = priority
        logger.info(f"Updated task ID {task_id} priority to '{priority}'")
        return task

    @log_action("get_tasks_by_status")
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Returns tasks filtered by status. Raises InvalidStatusError for invalid status."""
        validate_status(status)
        return [task for task in self.tasks if task.status == status]

    @log_action("search_tasks")
    def search_tasks(self, keyword: str) -> List[Task]:
        """Searches tasks by title keyword (case-insensitive)."""
        if not keyword or not isinstance(keyword, str):
            return []

        keyword_lower = keyword.lower()
        return [task for task in self.tasks if keyword_lower in task.title.lower()]

    @log_action("sort_tasks")
    def sort_tasks(self, sort_by: str = "title", descending: bool = False) -> List[Task]:
        """Sorts tasks by title, priority, or status. Raises ValidationError for invalid field."""
        if sort_by not in {"title", "priority", "status"}:
            raise ValidationError("Invalid sort field")

        priority_order = {"low": 1, "medium": 2, "high": 3}
        status_order = {"pending": 1, "in_progress": 2, "completed": 3}

        if sort_by == "priority":
            key_func = lambda task: priority_order.get(task.priority, 0)
        elif sort_by == "status":
            key_func = lambda task: status_order.get(task.status, 0)
        else:
            key_func = lambda task: getattr(task, sort_by)

        return sorted(self.tasks, key=key_func, reverse=descending)

    @log_action("get_task_statistics")
    def get_task_statistics(self) -> Dict[str, int]:
        """Calculates and returns task counts by status and priority."""
        stats = {
            "total_tasks": len(self.tasks),
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "completed_tasks": 0,
            "low_priority_tasks": 0,
            "medium_priority_tasks": 0,
            "high_priority_tasks": 0,
        }

        for task in self.tasks:
            if task.status == "pending":
                stats["pending_tasks"] += 1
            elif task.status == "in_progress":
                stats["in_progress_tasks"] += 1
            elif task.status == "completed":
                stats["completed_tasks"] += 1

            if task.priority == "low":
                stats["low_priority_tasks"] += 1
            elif task.priority == "medium":
                stats["medium_priority_tasks"] += 1
            elif task.priority == "high":
                stats["high_priority_tasks"] += 1

        logger.info(f"Calculated task statistics: {stats}")
        return stats