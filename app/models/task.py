class Task:
    def __init__(self, task_id, title, description, status="pending"):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = status

    def __str__(self):
        return (
            f"Task(id={self.task_id}, "
            f"title={self.title}, "
            f"description={self.description}, "
            f"status={self.status})"
        )