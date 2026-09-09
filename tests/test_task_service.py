import unittest
from app.services.task_service import TaskService
from app.utils.exceptions import (
    TaskNotFoundError,
    ValidationError,
    InvalidStatusError,
    InvalidPriorityError,
)


class TestTaskService(unittest.TestCase):
    def setUp(self) -> None:
        self.task_service = TaskService()

    def test_create_task_success(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.title, "Task 1")
        self.assertEqual(task.description, "Description 1")
        self.assertEqual(task.status, "pending")

    def test_create_task_invalid_title(self) -> None:
        with self.assertRaises(ValidationError):
            self.task_service.create_task("", "Description 1")

    def test_create_task_invalid_description(self) -> None:
        with self.assertRaises(ValidationError):
            self.task_service.create_task("Task 1", "")

    def test_get_task_success(self) -> None:
        created_task = self.task_service.create_task("Task 2", "Description 2")
        retrieved_task = self.task_service.get_task(created_task.task_id)
        self.assertEqual(retrieved_task, created_task)

    def test_get_task_not_found(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.task_service.get_task(999)

    def test_update_task_success(self) -> None:
        task = self.task_service.create_task("Task 3", "Description 3")
        updated_task = self.task_service.update_task(
            task.task_id, "Updated Title", "Updated Description", "completed"
        )
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.description, "Updated Description")
        self.assertEqual(updated_task.status, "completed")

    def test_update_task_invalid_data(self) -> None:
        task = self.task_service.create_task("Task 4", "Description 4")
        with self.assertRaises(ValidationError):
            self.task_service.update_task(task.task_id, "", "Description 4")
        self.assertEqual(task.title, "Task 4")

    def test_update_task_not_found(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.task_service.update_task(999, "Title", "Description")

    def test_delete_task_success(self) -> None:
        task = self.task_service.create_task("Task 5", "Description 5")
        result = self.task_service.delete_task(task.task_id)
        self.assertEqual(result, "Task deleted successfully")
        with self.assertRaises(TaskNotFoundError):
            self.task_service.get_task(task.task_id)

    def test_delete_task_not_found(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.task_service.delete_task(999)

    def test_update_task_status_pending_to_in_progress(self) -> None:
        task = self.task_service.create_task("Task 6", "Description 6")
        updated_task = self.task_service.update_task_status(task.task_id, "in_progress")
        self.assertEqual(updated_task.status, "in_progress")

    def test_update_task_status_in_progress_to_completed(self) -> None:
        task = self.task_service.create_task("Task 7", "Description 7")
        self.task_service.update_task_status(task.task_id, "in_progress")
        updated_task = self.task_service.update_task_status(task.task_id, "completed")
        self.assertEqual(updated_task.status, "completed")

    def test_update_task_status_invalid_status(self) -> None:
        task = self.task_service.create_task("Task 8", "Description 8")
        with self.assertRaises(InvalidStatusError):
            self.task_service.update_task_status(task.task_id, "invalid_status")
        self.assertEqual(task.status, "pending")

    def test_update_task_status_not_found(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.task_service.update_task_status(999, "in_progress")

    def test_get_tasks_by_status_pending(self) -> None:
        task1 = self.task_service.create_task("Task 1", "Pending task")
        task2 = self.task_service.create_task("Task 2", "In progress task")
        self.task_service.update_task_status(task2.task_id, "in_progress")

        pending_tasks = self.task_service.get_tasks_by_status("pending")
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0], task1)

    def test_get_tasks_by_status_in_progress(self) -> None:
        task1 = self.task_service.create_task("Task 1", "Pending task")
        task2 = self.task_service.create_task("Task 2", "In progress task")
        self.task_service.update_task_status(task2.task_id, "in_progress")

        in_progress_tasks = self.task_service.get_tasks_by_status("in_progress")
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0], task2)

    def test_get_tasks_by_status_completed(self) -> None:
        task1 = self.task_service.create_task("Task 1", "Pending task")
        task2 = self.task_service.create_task("Task 2", "Completed task")
        self.task_service.update_task_status(task2.task_id, "completed")

        completed_tasks = self.task_service.get_tasks_by_status("completed")
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0], task2)

    def test_get_tasks_by_status_invalid_status(self) -> None:
        self.task_service.create_task("Task 1", "Pending task")
        with self.assertRaises(InvalidStatusError):
            self.task_service.get_tasks_by_status("invalid_status")

    def test_create_task_low_priority(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1", priority="low")
        self.assertEqual(task.priority, "low")

    def test_create_task_medium_priority(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1", priority="medium")
        self.assertEqual(task.priority, "medium")

    def test_create_task_high_priority(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1", priority="high")
        self.assertEqual(task.priority, "high")

    def test_create_task_invalid_priority(self) -> None:
        with self.assertRaises(ValidationError):
            self.task_service.create_task("Task 1", "Description 1", priority="invalid")

    def test_update_task_priority_success(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1")
        updated_task = self.task_service.update_task_priority(task.task_id, "high")
        self.assertEqual(updated_task.priority, "high")

    def test_update_task_priority_invalid_priority(self) -> None:
        task = self.task_service.create_task("Task 1", "Description 1")
        with self.assertRaises(InvalidPriorityError):
            self.task_service.update_task_priority(task.task_id, "invalid")
        self.assertEqual(task.priority, "medium")

    def test_update_task_priority_not_found(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.task_service.update_task_priority(999, "high")

    def test_search_tasks_exact_title(self) -> None:
        task1 = self.task_service.create_task("Buy groceries", "Buy milk and eggs")
        task2 = self.task_service.create_task("Clean house", "Clean kitchen")
        results = self.task_service.search_tasks("Buy groceries")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], task1)

    def test_search_tasks_partial_title(self) -> None:
        task1 = self.task_service.create_task("Buy groceries", "Buy milk and eggs")
        task2 = self.task_service.create_task("Clean house", "Clean kitchen")
        results = self.task_service.search_tasks("groceries")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], task1)

    def test_search_tasks_case_insensitive(self) -> None:
        task1 = self.task_service.create_task("Buy Groceries", "Buy milk and eggs")
        results = self.task_service.search_tasks("BUY GROCERIES")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], task1)

        results_lower = self.task_service.search_tasks("buy groceries")
        self.assertEqual(len(results_lower), 1)
        self.assertEqual(results_lower[0], task1)

    def test_search_tasks_no_matching_task(self) -> None:
        self.task_service.create_task("Buy groceries", "Buy milk and eggs")
        results = self.task_service.search_tasks("Nonexistent Task")
        self.assertEqual(results, [])

    def test_search_tasks_empty_keyword(self) -> None:
        self.task_service.create_task("Buy groceries", "Buy milk and eggs")
        results = self.task_service.search_tasks("")
        self.assertEqual(results, [])

    def test_get_tasks_paginated_first_page(self) -> None:
        tasks = [self.task_service.create_task(f"Task {i}", f"Desc {i}") for i in range(1, 8)]
        result = self.task_service.get_tasks_paginated(page=1, limit=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, tasks[0:3])

    def test_get_tasks_paginated_second_page(self) -> None:
        tasks = [self.task_service.create_task(f"Task {i}", f"Desc {i}") for i in range(1, 8)]
        result = self.task_service.get_tasks_paginated(page=2, limit=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, tasks[3:6])

    def test_get_tasks_paginated_fewer_remaining_tasks(self) -> None:
        tasks = [self.task_service.create_task(f"Task {i}", f"Desc {i}") for i in range(1, 8)]
        result = self.task_service.get_tasks_paginated(page=3, limit=3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, tasks[6:7])

    def test_get_tasks_paginated_beyond_available_tasks(self) -> None:
        [self.task_service.create_task(f"Task {i}", f"Desc {i}") for i in range(1, 8)]
        result = self.task_service.get_tasks_paginated(page=4, limit=3)
        self.assertEqual(result, [])

    def test_get_tasks_paginated_invalid_page(self) -> None:
        self.task_service.create_task("Task 1", "Desc 1")
        with self.assertRaises(ValidationError):
            self.task_service.get_tasks_paginated(page=0, limit=5)
        with self.assertRaises(ValidationError):
            self.task_service.get_tasks_paginated(page=-1, limit=5)

    def test_get_tasks_paginated_invalid_limit(self) -> None:
        self.task_service.create_task("Task 1", "Desc 1")
        with self.assertRaises(ValidationError):
            self.task_service.get_tasks_paginated(page=1, limit=0)
        with self.assertRaises(ValidationError):
            self.task_service.get_tasks_paginated(page=1, limit=-5)

    def test_sort_tasks_by_title_ascending(self) -> None:
        t1 = self.task_service.create_task("Banana", "Desc B")
        t2 = self.task_service.create_task("Apple", "Desc A")
        t3 = self.task_service.create_task("Cherry", "Desc C")
        sorted_tasks = self.task_service.sort_tasks(sort_by="title", descending=False)
        self.assertEqual([t.title for t in sorted_tasks], ["Apple", "Banana", "Cherry"])

    def test_sort_tasks_by_title_descending(self) -> None:
        t1 = self.task_service.create_task("Banana", "Desc B")
        t2 = self.task_service.create_task("Apple", "Desc A")
        t3 = self.task_service.create_task("Cherry", "Desc C")
        sorted_tasks = self.task_service.sort_tasks(sort_by="title", descending=True)
        self.assertEqual([t.title for t in sorted_tasks], ["Cherry", "Banana", "Apple"])

    def test_sort_tasks_by_priority(self) -> None:
        t1 = self.task_service.create_task("Task 1", "Desc 1", priority="medium")
        t2 = self.task_service.create_task("Task 2", "Desc 2", priority="low")
        t3 = self.task_service.create_task("Task 3", "Desc 3", priority="high")
        
        sorted_asc = self.task_service.sort_tasks(sort_by="priority", descending=False)
        self.assertEqual([t.priority for t in sorted_asc], ["low", "medium", "high"])

        sorted_desc = self.task_service.sort_tasks(sort_by="priority", descending=True)
        self.assertEqual([t.priority for t in sorted_desc], ["high", "medium", "low"])

    def test_sort_tasks_by_status(self) -> None:
        t1 = self.task_service.create_task("Task 1", "Desc 1")
        t2 = self.task_service.create_task("Task 2", "Desc 2")
        t3 = self.task_service.create_task("Task 3", "Desc 3")
        
        self.task_service.update_task_status(t1.task_id, "completed")
        self.task_service.update_task_status(t2.task_id, "pending")
        self.task_service.update_task_status(t3.task_id, "in_progress")

        sorted_asc = self.task_service.sort_tasks(sort_by="status", descending=False)
        self.assertEqual([t.status for t in sorted_asc], ["pending", "in_progress", "completed"])

        sorted_desc = self.task_service.sort_tasks(sort_by="status", descending=True)
        self.assertEqual([t.status for t in sorted_desc], ["completed", "in_progress", "pending"])

    def test_sort_tasks_invalid_sort_field(self) -> None:
        self.task_service.create_task("Task 1", "Desc 1")
        with self.assertRaises(ValidationError):
            self.task_service.sort_tasks(sort_by="invalid_field")

    def test_sort_tasks_does_not_modify_original_list(self) -> None:
        t1 = self.task_service.create_task("Banana", "Desc B")
        t2 = self.task_service.create_task("Apple", "Desc A")
        t3 = self.task_service.create_task("Cherry", "Desc C")
        
        original_copy = list(self.task_service.tasks)
        sorted_tasks = self.task_service.sort_tasks(sort_by="title")
        
        self.assertNotEqual(self.task_service.tasks, sorted_tasks)
        self.assertEqual(self.task_service.tasks, original_copy)
        self.assertEqual(self.task_service.tasks, [t1, t2, t3])

    def test_get_task_statistics_no_tasks(self) -> None:
        stats = self.task_service.get_task_statistics()
        expected = {
            "total_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "completed_tasks": 0,
            "low_priority_tasks": 0,
            "medium_priority_tasks": 0,
            "high_priority_tasks": 0,
        }
        self.assertEqual(stats, expected)

    def test_get_task_statistics_multiple_tasks(self) -> None:
        t1 = self.task_service.create_task("Task 1", "Desc 1", priority="low")
        t2 = self.task_service.create_task("Task 2", "Desc 2", priority="medium")
        t3 = self.task_service.create_task("Task 3", "Desc 3", priority="high")
        self.task_service.update_task_status(t2.task_id, "in_progress")
        self.task_service.update_task_status(t3.task_id, "completed")

        stats = self.task_service.get_task_statistics()
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["pending_tasks"], 1)
        self.assertEqual(stats["in_progress_tasks"], 1)
        self.assertEqual(stats["completed_tasks"], 1)
        self.assertEqual(stats["low_priority_tasks"], 1)
        self.assertEqual(stats["medium_priority_tasks"], 1)
        self.assertEqual(stats["high_priority_tasks"], 1)

    def test_get_task_statistics_status_counts(self) -> None:
        t1 = self.task_service.create_task("Task 1", "Desc 1")
        t2 = self.task_service.create_task("Task 2", "Desc 2")
        t3 = self.task_service.create_task("Task 3", "Desc 3")
        t4 = self.task_service.create_task("Task 4", "Desc 4")
        t5 = self.task_service.create_task("Task 5", "Desc 5")
        
        self.task_service.update_task_status(t3.task_id, "in_progress")
        self.task_service.update_task_status(t4.task_id, "completed")
        self.task_service.update_task_status(t5.task_id, "completed")

        stats = self.task_service.get_task_statistics()
        self.assertEqual(stats["pending_tasks"], 2)
        self.assertEqual(stats["in_progress_tasks"], 1)
        self.assertEqual(stats["completed_tasks"], 2)

    def test_get_task_statistics_priority_counts(self) -> None:
        self.task_service.create_task("Task 1", "Desc 1", priority="low")
        self.task_service.create_task("Task 2", "Desc 2", priority="low")
        self.task_service.create_task("Task 3", "Desc 3", priority="medium")
        self.task_service.create_task("Task 4", "Desc 4", priority="high")
        self.task_service.create_task("Task 5", "Desc 5", priority="high")
        self.task_service.create_task("Task 6", "Desc 6", priority="high")

        stats = self.task_service.get_task_statistics()
        self.assertEqual(stats["low_priority_tasks"], 2)
        self.assertEqual(stats["medium_priority_tasks"], 1)
        self.assertEqual(stats["high_priority_tasks"], 3)

    def test_get_task_statistics_total_task_count(self) -> None:
        for i in range(4):
            self.task_service.create_task(f"Task {i}", f"Desc {i}")
        stats = self.task_service.get_task_statistics()
        self.assertEqual(stats["total_tasks"], 4)

    def test_task_service_iterator(self) -> None:
        t1 = self.task_service.create_task("Task 1", "Desc 1")
        t2 = self.task_service.create_task("Task 2", "Desc 2")
        iterated_tasks = [task for task in self.task_service]
        self.assertEqual(iterated_tasks, [t1, t2])


if __name__ == "__main__":
    unittest.main()
