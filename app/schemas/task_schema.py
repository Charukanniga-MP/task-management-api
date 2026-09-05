class TaskSchema:
    def __init__(self, title, description, status="pending", priority="medium"):
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority