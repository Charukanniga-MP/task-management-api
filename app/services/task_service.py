from app.models.task import Task
from app.utils.validation import validate_task, validate_priority
from app.utils.helpers import generate_id


class TaskService:
    def __init__(self):
        self.tasks = []

    def create_task(self, title, description, priority="medium"):
        if not validate_task(title, description, priority):
            return "Invalid task details"

        task_id = generate_id(self.tasks)
        task = Task(task_id, title, description, priority=priority)
        self.tasks.append(task)

        return task

    def get_tasks(self):
        return [str(task) for task in self.tasks]

    def get_task(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return "Task not found"

    def update_task(self, task_id, title, description, status="pending"):
        task = self.get_task(task_id)
        if task == "Task not found":
            return "Task not found"

        if not validate_task(title, description):
            return "Invalid task details"

        task.title = title
        task.description = description
        task.status = status
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task == "Task not found":
            return "Task not found"

        self.tasks.remove(task)
        return "Task deleted successfully"

    def update_task_status(self, task_id, status):
        task = self.get_task(task_id)
        if task == "Task not found":
            return "Task not found"

        if status not in {"pending", "in_progress", "completed"}:
            return "Invalid status"

        task.status = status
        return task

    def update_task_priority(self, task_id, priority):
        task = self.get_task(task_id)
        if task == "Task not found":
            return "Task not found"

        if not validate_priority(priority):
            return "Invalid priority"

        task.priority = priority
        return task

    def get_tasks_by_status(self, status):
        if status not in {"pending", "in_progress", "completed"}:
            return "Invalid status"

        return [task for task in self.tasks if task.status == status]


