import unittest
from app.services.task_service import TaskService


class TestTaskService(unittest.TestCase):
    def setUp(self):
        self.task_service = TaskService()

    def test_create_task_success(self):
        task = self.task_service.create_task("Task 1", "Description 1")
        self.assertNotEqual(task, "Invalid task details")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.title, "Task 1")
        self.assertEqual(task.description, "Description 1")
        self.assertEqual(task.status, "pending")

    def test_create_task_invalid_title(self):
        result = self.task_service.create_task("", "Description 1")
        self.assertEqual(result, "Invalid task details")

    def test_create_task_invalid_description(self):
        result = self.task_service.create_task("Task 1", "")
        self.assertEqual(result, "Invalid task details")

    def test_get_task_success(self):
        created_task = self.task_service.create_task("Task 2", "Description 2")
        retrieved_task = self.task_service.get_task(created_task.task_id)
        self.assertEqual(retrieved_task, created_task)

    def test_get_task_not_found(self):
        result = self.task_service.get_task(999)
        self.assertEqual(result, "Task not found")

    def test_update_task_success(self):
        task = self.task_service.create_task("Task 3", "Description 3")
        updated_task = self.task_service.update_task(
            task.task_id, "Updated Title", "Updated Description", "completed"
        )
        self.assertNotEqual(updated_task, "Task not found")
        self.assertNotEqual(updated_task, "Invalid task details")
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.description, "Updated Description")
        self.assertEqual(updated_task.status, "completed")

    def test_update_task_invalid_data(self):
        task = self.task_service.create_task("Task 4", "Description 4")
        result = self.task_service.update_task(task.task_id, "", "Description 4")
        self.assertEqual(result, "Invalid task details")
        # Ensure task object was not modified
        self.assertEqual(task.title, "Task 4")

    def test_update_task_not_found(self):
        result = self.task_service.update_task(999, "Title", "Description")
        self.assertEqual(result, "Task not found")

    def test_delete_task_success(self):
        task = self.task_service.create_task("Task 5", "Description 5")
        result = self.task_service.delete_task(task.task_id)
        self.assertEqual(result, "Task deleted successfully")
        self.assertEqual(self.task_service.get_task(task.task_id), "Task not found")

    def test_delete_task_not_found(self):
        result = self.task_service.delete_task(999)
        self.assertEqual(result, "Task not found")

    def test_update_task_status_pending_to_in_progress(self):
        task = self.task_service.create_task("Task 6", "Description 6")
        updated_task = self.task_service.update_task_status(task.task_id, "in_progress")
        self.assertNotEqual(updated_task, "Task not found")
        self.assertNotEqual(updated_task, "Invalid status")
        self.assertEqual(updated_task.status, "in_progress")

    def test_update_task_status_in_progress_to_completed(self):
        task = self.task_service.create_task("Task 7", "Description 7")
        self.task_service.update_task_status(task.task_id, "in_progress")
        updated_task = self.task_service.update_task_status(task.task_id, "completed")
        self.assertNotEqual(updated_task, "Task not found")
        self.assertNotEqual(updated_task, "Invalid status")
        self.assertEqual(updated_task.status, "completed")

    def test_update_task_status_invalid_status(self):
        task = self.task_service.create_task("Task 8", "Description 8")
        result = self.task_service.update_task_status(task.task_id, "invalid_status")
        self.assertEqual(result, "Invalid status")
        self.assertEqual(task.status, "pending")

    def test_update_task_status_not_found(self):
        result = self.task_service.update_task_status(999, "in_progress")
        self.assertEqual(result, "Task not found")


if __name__ == "__main__":
    unittest.main()

