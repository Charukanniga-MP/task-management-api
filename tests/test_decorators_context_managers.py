import unittest
from app.utils.decorators import log_action
from app.utils.context_managers import OperationTimer


class TestDecoratorsContextManagers(unittest.TestCase):
    def test_log_action_decorator_success(self) -> None:
        @log_action("test_action")
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)
        self.assertEqual(result, 5)

    def test_log_action_decorator_raises_exception(self) -> None:
        @log_action("failing_action")
        def fail() -> None:
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            fail()

    def test_operation_timer_context_manager_success(self) -> None:
        with OperationTimer("Test Timer") as timer:
            _ = sum(range(100))
        self.assertGreaterEqual(timer.elapsed_ms, 0.0)

    def test_operation_timer_context_manager_exception(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            with OperationTimer("Failing Timer"):
                _ = 1 / 0


if __name__ == "__main__":
    unittest.main()
