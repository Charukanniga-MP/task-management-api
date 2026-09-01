from app.models.task import Task
from app.utils.validation import validate_task
from app.utils.helpers import generate_id


class TaskService:
    def __init__(self):
        self.tasks = []

    def create_task(self, title, description):
        if not validate_task(title, description):
            return "Invalid task details"

        task_id = generate_id(self.tasks)
        task = Task(task_id, title, description)
        self.tasks.append(task)

        return task

    def get_tasks(self):
        return [str(task) for task in self.tasks]