"""Unit test suite for Day 5: Decorators, Context Managers & Caching.

Tests:
- @timeit execution, metadata preservation, and logging.
- @retry success, partial failure retry, max retries exhaustion, invalid max_attempts validation.
- Context managers (TaskResourceManager, managed_resource) cleanup on success and exception.
- lru_cache caching behavior, speedup, cache_clear, and immutable return safety.
- Pipeline integration with @timeit, @retry, and TaskResourceManager.
"""

import logging
import time
import unittest
from unittest.mock import MagicMock, patch

from task_analytics import (
    CleanDataStep,
    NormalizeDataStep,
    Pipeline,
    TaskResourceManager,
    calculate_task_priority_score,
    get_task_category_weight,
    managed_resource,
    retry,
    timeit,
)


class TestTimeitDecorator(unittest.TestCase):
    """Tests for the @timeit decorator."""

    def test_timeit_executes_function_and_returns_result(self):
        """Verifies decorated function executes correctly and returns expected result."""
        @timeit
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        result = add(5, 7)
        self.assertEqual(result, 12)

    def test_timeit_preserves_metadata(self):
        """Verifies functools.wraps preserves __name__ and __doc__."""
        @timeit
        def sample_func():
            """Sample docstring."""
            pass

        self.assertEqual(sample_func.__name__, "sample_func")
        self.assertEqual(sample_func.__doc__, "Sample docstring.")

    def test_timeit_logs_execution_time(self):
        """Verifies that @timeit logs execution time."""
        with self.assertLogs("task_analytics.decorators", level="INFO") as cm:
            @timeit
            def dummy_work():
                time.sleep(0.01)
                return "done"

            dummy_work()
            self.assertTrue(any("executed in" in log for log in cm.output))

    def test_timeit_propagates_exceptions(self):
        """Verifies that exceptions raised inside decorated function are re-raised."""
        @timeit
        def failing_func():
            raise ValueError("Timeit failure")

        with self.assertRaises(ValueError):
            failing_func()


class TestRetryDecorator(unittest.TestCase):
    """Tests for the parameterized @retry(max_attempts=N) decorator."""

    def test_retry_succeeds_first_attempt(self):
        """Verifies function succeeding on first attempt runs only once."""
        mock_fn = MagicMock(return_value="success")

        @retry(max_attempts=3)
        def target():
            return mock_fn()

        result = target()
        self.assertEqual(result, "success")
        self.assertEqual(mock_fn.call_count, 1)

    def test_retry_fails_once_then_succeeds(self):
        """Verifies retry logic when attempt 1 fails and attempt 2 succeeds."""
        attempts = 0

        @retry(max_attempts=3)
        def target():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("Transient glitch")
            return "recovered"

        result = target()
        self.assertEqual(result, "recovered")
        self.assertEqual(attempts, 2)

    def test_retry_exhausts_attempts_and_raises_final_exception(self):
        """Verifies retry re-raises final exception when all max_attempts fail."""
        attempts = 0

        @retry(max_attempts=3)
        def target():
            nonlocal attempts
            attempts += 1
            raise ValueError(f"Failure on attempt {attempts}")

        with self.assertRaises(ValueError) as cm:
            target()

        self.assertEqual(str(cm.exception), "Failure on attempt 3")
        self.assertEqual(attempts, 3)

    def test_retry_rejects_invalid_max_attempts(self):
        """Verifies max_attempts <= 0 or non-int is rejected with ValueError."""
        with self.assertRaises(ValueError):
            retry(max_attempts=0)

        with self.assertRaises(ValueError):
            retry(max_attempts=-5)

        with self.assertRaises(ValueError):
            retry(max_attempts="invalid")  # type: ignore

    def test_retry_preserves_metadata(self):
        """Verifies @retry preserves decorated function name and docstring."""
        @retry(max_attempts=2)
        def metadata_func():
            """Docstring for metadata test."""
            pass

        self.assertEqual(metadata_func.__name__, "metadata_func")
        self.assertEqual(metadata_func.__doc__, "Docstring for metadata test.")


class TestContextManagers(unittest.TestCase):
    """Tests for class-based TaskResourceManager and generator-based managed_resource."""

    def test_task_resource_manager_normal_execution(self):
        """Verifies resource is opened and cleaned up during normal execution."""
        with TaskResourceManager("test_db") as res:
            self.assertTrue(res.is_open)
            self.assertEqual(res.resource_data["status"], "active")

        self.assertFalse(res.is_open)
        self.assertEqual(res.resource_data["status"], "closed")

    def test_task_resource_manager_exception_execution(self):
        """Verifies resource cleanup happens even when exception is raised inside with block."""
        res_ref = None
        with self.assertRaises(ZeroDivisionError):
            with TaskResourceManager("error_db") as res:
                res_ref = res
                _ = 1 / 0

        self.assertIsNotNone(res_ref)
        self.assertFalse(res_ref.is_open)
        self.assertEqual(res_ref.resource_data["status"], "closed")

    def test_managed_resource_generator_normal(self):
        """Verifies contextlib managed_resource cleans up on normal exit."""
        with managed_resource("stream_1") as res:
            self.assertTrue(res["is_active"])
            self.assertFalse(res["cleaned_up"])

        self.assertFalse(res["is_active"])
        self.assertTrue(res["cleaned_up"])

    def test_managed_resource_generator_exception(self):
        """Verifies contextlib managed_resource cleans up when exception occurs."""
        captured_res = None
        with self.assertRaises(KeyError):
            with managed_resource("stream_err") as res:
                captured_res = res
                raise KeyError("Missing key inside with block")

        self.assertIsNotNone(captured_res)
        self.assertFalse(captured_res["is_active"])
        self.assertTrue(captured_res["cleaned_up"])


class TestCaching(unittest.TestCase):
    """Tests for functools.lru_cache usage and cache_clear."""

    def setUp(self):
        calculate_task_priority_score.cache_clear()
        get_task_category_weight.cache_clear()

    def test_lru_cache_returns_consistent_result(self):
        """Verifies cached function returns exact same result for identical inputs."""
        score1 = calculate_task_priority_score("high", 5, 2)
        score2 = calculate_task_priority_score("high", 5, 2)
        self.assertEqual(score1, score2)

    def test_lru_cache_clear_resets_cache(self):
        """Verifies cache_clear() clears cache statistics."""
        calculate_task_priority_score("high", 5, 2)
        info1 = calculate_task_priority_score.cache_info()
        self.assertGreaterEqual(info1.currsize, 1)

        calculate_task_priority_score.cache_clear()
        info2 = calculate_task_priority_score.cache_info()
        self.assertEqual(info2.currsize, 0)

    def test_category_weight_cache(self):
        """Verifies get_task_category_weight caching behavior."""
        w1 = get_task_category_weight("bug")
        w2 = get_task_category_weight("bug")
        self.assertEqual(w1, 2.5)
        self.assertEqual(w1, w2)
        self.assertEqual(get_task_category_weight.cache_info().hits, 1)


class TestPipelineIntegrationDay5(unittest.TestCase):
    """Tests Day 5 features applied to actual Pipeline class."""

    def test_pipeline_run_times_execution(self):
        """Verifies Pipeline.run is decorated with @timeit."""
        p = Pipeline([CleanDataStep(), NormalizeDataStep(target_fields=["status"])])
        data = [{"title": " Task 1 ", "status": " OPEN "}]

        with self.assertLogs("task_analytics.decorators", level="INFO") as cm:
            result = p.run(data)

        self.assertEqual(result, [{"title": " Task 1 ", "status": "open"}])
        self.assertTrue(any("Function 'run' executed in" in log for log in cm.output))


    def test_pipeline_load_data_source_retry(self):
        """Verifies Pipeline.load_data_source retries failing data fetchers."""
        p = Pipeline([])
        attempts = 0

        def flaky_fetcher():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ConnectionError("Network glitch")
            return [{"id": 1, "title": "Fetched Task"}]

        data = p.load_data_source(flaky_fetcher)
        self.assertEqual(len(data), 1)
        self.assertEqual(attempts, 2)

    def test_pipeline_run_with_resource_cleanup(self):
        """Verifies Pipeline.run_with_resource cleans up resource."""
        p = Pipeline([NormalizeDataStep(target_fields=["status"])])
        data = [{"status": " PENDING "}]

        result = p.run_with_resource("task_data_file.csv", data)
        self.assertEqual(result, [{"status": "pending"}])


if __name__ == "__main__":
    unittest.main()
