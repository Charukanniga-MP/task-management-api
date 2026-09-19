"""Unit test suite for Day 6 Exception Hierarchy and Error Design.

Tests:
- PipelineError base class and inheritance hierarchy for ConfigError, DataValidationError, ProcessingError
- ConfigError raised on invalid configuration parameters
- DataValidationError raised on invalid/missing data or negative batch_size
- ProcessingError raised on pipeline step failure with exception chaining (preserving __cause__)
- Top-level exception handling catching PipelineError
- try / except / else / finally control flow semantics
"""

from pathlib import Path
import unittest

from task_analytics.config import PipelineConfig, validate_pipeline_config
from task_analytics.data_iterator import CSVBatchIterator
from task_analytics.exceptions import (
    ConfigError,
    DataValidationError,
    PipelineError,
    ProcessingError,
)
from task_analytics.pipeline import CleanDataStep, NormalizeDataStep, Pipeline


class TestExceptionHierarchy(unittest.TestCase):
    """Test suite verifying inheritance relationships of custom exceptions."""

    def test_pipeline_error_is_base(self):
        """Verifies PipelineError inherits directly from Exception."""
        self.assertTrue(issubclass(PipelineError, Exception))

    def test_config_error_inheritance(self):
        """Verifies ConfigError inherits from PipelineError."""
        self.assertTrue(issubclass(ConfigError, PipelineError))
        err = ConfigError("Config error message")
        self.assertIsInstance(err, PipelineError)
        self.assertIsInstance(err, Exception)

    def test_data_validation_error_inheritance(self):
        """Verifies DataValidationError inherits from PipelineError."""
        self.assertTrue(issubclass(DataValidationError, PipelineError))
        err = DataValidationError("Data error message")
        self.assertIsInstance(err, PipelineError)
        self.assertIsInstance(err, Exception)

    def test_processing_error_inheritance(self):
        """Verifies ProcessingError inherits from PipelineError."""
        self.assertTrue(issubclass(ProcessingError, PipelineError))
        err = ProcessingError("Processing error message")
        self.assertIsInstance(err, PipelineError)
        self.assertIsInstance(err, Exception)


class TestLowLevelExceptionRaising(unittest.TestCase):
    """Test suite verifying low-level components raise appropriate custom exceptions."""

    def test_invalid_config_raises_config_error(self):
        """Verifies invalid configuration parameters raise ConfigError."""
        # 1. Invalid batch size via helper
        with self.assertRaises(ConfigError) as ctx_batch:
            validate_pipeline_config({"data_path": "data", "batch_size": -5})
        err_msg = str(ctx_batch.exception)
        self.assertIn("Configuration failed", err_msg)  # WHAT failed
        self.assertIn("PipelineConfig", err_msg)        # WHERE it failed
        self.assertIn("batch_size must be greater than 0", err_msg)  # WHY it failed

        # 2. Non-existent path via helper
        with self.assertRaises(ConfigError) as ctx_path:
            validate_pipeline_config({"data_path": Path("non_existent_path_xyz_999")})
        self.assertIn("data_path must point to an existing path on disk", str(ctx_path.exception))

    def test_invalid_data_iterator_raises_data_validation_error(self):
        """Verifies invalid data loading inputs raise DataValidationError."""
        # 1. Invalid batch size <= 0
        with self.assertRaises(DataValidationError) as ctx_batch:
            CSVBatchIterator(path="data", batch_size=0)
        self.assertIn("Data validation failed in CSVBatchIterator", str(ctx_batch.exception))
        self.assertIn("batch_size must be at least 1", str(ctx_batch.exception))

        # 2. Non-existent file path
        with self.assertRaises(DataValidationError) as ctx_file:
            CSVBatchIterator(path="non_existent_file_123.csv")
        self.assertIn("Data validation failed in CSVBatchIterator", str(ctx_file.exception))
        self.assertIn("does not exist", str(ctx_file.exception))

    def test_processing_error_with_exception_chaining(self):
        """Verifies ProcessingError is raised on step failure and preserves original __cause__."""
        step = NormalizeDataStep(numeric_fields=["estimated_hours"])
        bad_data = [{"task_id": "T1", "estimated_hours": "not_a_number"}]

        with self.assertRaises(ProcessingError) as ctx:
            step.execute(bad_data)

        err = ctx.exception
        # Verify message structure (WHAT, WHERE, WHY)
        self.assertIn("Pipeline processing failed in NormalizeDataStep", str(err))
        self.assertIn("cannot convert value 'not_a_number'", str(err))

        # Verify exception chaining preserves original cause
        self.assertIsNotNone(err.__cause__)
        self.assertIsInstance(err.__cause__, ValueError)

    def test_clean_data_step_invalid_type_raises_processing_error(self):
        """Verifies CleanDataStep raises ProcessingError when receiving invalid type."""
        step = CleanDataStep()
        with self.assertRaises(ProcessingError) as ctx:
            step.execute(12345)  # Unsupported type integer
        self.assertIn("Pipeline processing failed in CleanDataStep", str(ctx.exception))


class TestTopLevelHandlingAndControlFlow(unittest.TestCase):
    """Test suite verifying top-level error catching and try/except/else/finally behavior."""

    def test_top_level_handler_catches_all_custom_exceptions(self):
        """Verifies catching PipelineError catches ConfigError, DataValidationError, and ProcessingError."""
        exceptions_to_test = [
            ConfigError("Configuration failed in PipelineConfig: test"),
            DataValidationError("Data validation failed in CSVBatchIterator: test"),
            ProcessingError("Pipeline processing failed in NormalizeDataStep: test"),
        ]

        caught_count = 0
        for exc in exceptions_to_test:
            try:
                raise exc
            except PipelineError:
                caught_count += 1

        self.assertEqual(caught_count, 3)

    def test_try_except_else_finally_success_flow(self):
        """Verifies 'else' executes on success and 'finally' executes always."""
        executed_steps = []

        try:
            executed_steps.append("try")
            result = 10 + 20
        except Exception:
            executed_steps.append("except")
        else:
            executed_steps.append("else")
        finally:
            executed_steps.append("finally")

        self.assertEqual(result, 30)
        self.assertEqual(executed_steps, ["try", "else", "finally"])

    def test_try_except_else_finally_failure_flow(self):
        """Verifies 'else' is skipped on error and 'finally' executes always."""
        executed_steps = []

        try:
            executed_steps.append("try")
            raise ConfigError("Test error")
        except ConfigError:
            executed_steps.append("except")
        else:
            executed_steps.append("else")
        finally:
            executed_steps.append("finally")

        self.assertEqual(executed_steps, ["try", "except", "finally"])


if __name__ == "__main__":
    unittest.main()
