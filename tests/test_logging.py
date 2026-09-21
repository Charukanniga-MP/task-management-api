"""Unit Tests for Centralized Structured Logging Module (Day 7).

Tests:
- configure_logging centralization and handler deduplication.
- JSONFormatter field serialization and exception traceback capturing.
- TextFormatter development mode output.
- Pipeline execution logging (start, step start/complete/duration/records, pipeline finish).
- Pipeline failure logging with traceback details.
- Data iterator logging events.
- Decorator logging with structured extra attributes.
"""

import io
import json
import logging
from pathlib import Path
import tempfile
import unittest

from task_analytics.data_iterator import CSVBatchIterator
from task_analytics.decorators import timeit
from task_analytics.exceptions import ProcessingError
from task_analytics.logging_config import (
    JSONFormatter,
    TextFormatter,
    configure_logging,
)
from task_analytics.pipeline import (
    CleanDataStep,
    NormalizeDataStep,
    Pipeline,
)


class TestLoggingConfig(unittest.TestCase):
    """Test suite for centralized logging configuration and formatters."""

    def setUp(self):
        self.test_logger_name = "test_analytics_logger"
        self.logger = logging.getLogger(self.test_logger_name)

    def tearDown(self):
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)

    def test_configure_logging_creates_handlers_without_duplicates(self):
        """Verify configure_logging configures logger level and does not duplicate handlers."""
        configure_logging(level="DEBUG", logger_name=self.test_logger_name, env="production")
        self.assertEqual(len(self.logger.handlers), 1)
        self.assertEqual(self.logger.level, logging.DEBUG)

        # Re-configure logging and check handlers count remains 1
        configure_logging(level="INFO", logger_name=self.test_logger_name, env="development")
        self.assertEqual(len(self.logger.handlers), 1)
        self.assertEqual(self.logger.level, logging.INFO)

    def test_json_formatter_structure(self):
        """Verify JSONFormatter formats standard and extra record fields into valid JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Step completed successfully",
            args=(),
            exc_info=None,
            func="execute_step",
        )
        record.pipeline_step = "CleanDataStep"
        record.duration = 0.015
        record.records_processed = 100

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["logger"], "test_logger")
        self.assertEqual(data["message"], "Step completed successfully")
        self.assertEqual(data["function"], "execute_step")
        self.assertEqual(data["line"], 42)
        self.assertEqual(data["pipeline_step"], "CleanDataStep")
        self.assertEqual(data["duration"], 0.015)
        self.assertEqual(data["records_processed"], 100)
        self.assertIn("timestamp", data)

    def test_json_formatter_exception_traceback(self):
        """Verify JSONFormatter captures error type, error message, and traceback when exc_info is present."""
        formatter = JSONFormatter()
        try:
            raise ProcessingError("Invalid data format encountered")
        except ProcessingError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_file.py",
            lineno=99,
            msg="Step execution failed",
            args=(),
            exc_info=exc_info,
            func="run_step",
        )

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["level"], "ERROR")
        self.assertEqual(data["error_type"], "ProcessingError")
        self.assertEqual(data["error_message"], "Invalid data format encountered")
        self.assertIn("Traceback (most recent call last):", data["traceback"])

    def test_text_formatter_output(self):
        """Verify TextFormatter produces readable development logs."""
        formatter = TextFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Dev mode log message",
            args=(),
            exc_info=None,
            func="dev_func",
        )
        record.step = "NormalizeDataStep"
        output = formatter.format(record)
        self.assertIn("[INFO]", output)
        self.assertIn("Dev mode log message", output)
        self.assertIn("step=NormalizeDataStep", output)

    def test_file_logging(self):
        """Verify configure_logging generates log entries in a log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test_run.log"
            logger = configure_logging(
                level="INFO",
                log_file=log_file,
                env="production",
                logger_name="file_test_logger",
            )
            logger.info("File logging test event", extra={"test_key": "test_value"})

            self.assertTrue(log_file.exists())
            content = log_file.read_text(encoding="utf-8")
            self.assertIn("File logging test event", content)
            self.assertIn("test_key", content)

            # Close and remove handlers to release Windows file lock
            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)


class TestPipelineLogging(unittest.TestCase):
    """Test suite verifying Pipeline instrumentation with structured logging."""

    def setUp(self):
        self.log_capture = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setFormatter(JSONFormatter())

        self.pipeline_logger = logging.getLogger("task_analytics.pipeline")
        self.pipeline_logger.setLevel(logging.INFO)
        self.pipeline_logger.addHandler(self.handler)
        self.pipeline_logger.propagate = False

    def tearDown(self):
        self.pipeline_logger.removeHandler(self.handler)

    def test_pipeline_successful_run_logs(self):
        """Verify pipeline logs start, step start/complete, duration, records processed, and completion."""
        pipeline = Pipeline([
            CleanDataStep(required_keys=["name"]),
            NormalizeDataStep(target_fields=["name"]),
        ])

        raw_data = [{"name": "  Task A  "}, {"name": "Task B"}, None]
        result = pipeline.run(raw_data)

        self.assertEqual(len(result), 2)
        log_output = self.log_capture.getvalue()
        lines = [json.loads(line) for line in log_output.strip().splitlines() if line.strip()]

        messages = [l["message"] for l in lines]
        self.assertIn("Pipeline execution started.", messages)
        self.assertIn("Step started: CleanDataStep", messages)
        self.assertIn("Step completed: CleanDataStep", messages)
        self.assertIn("Step started: NormalizeDataStep", messages)
        self.assertIn("Step completed: NormalizeDataStep", messages)
        self.assertIn("Pipeline execution completed.", messages)

        # Verify step complete record contains duration and records_processed
        clean_step_log = next(l for l in lines if l.get("pipeline_step") == "CleanDataStep" and "completed" in l["message"])
        self.assertIn("duration", clean_step_log)
        self.assertIn("records_processed", clean_step_log)
        self.assertEqual(clean_step_log["records_processed"], 2)

    def test_pipeline_failed_run_logs_traceback(self):
        """Verify pipeline logs step failure with exc_info traceback when an exception is raised."""
        pipeline = Pipeline([
            NormalizeDataStep(numeric_fields=["amount"]),
        ])

        invalid_data = [{"amount": "not_a_number"}]

        with self.assertRaises(ProcessingError):
            pipeline.run(invalid_data)

        log_output = self.log_capture.getvalue()
        lines = [json.loads(line) for line in log_output.strip().splitlines() if line.strip()]

        failed_log = next(l for l in lines if l["level"] == "ERROR")
        self.assertEqual(failed_log["pipeline_step"], "NormalizeDataStep")
        self.assertEqual(failed_log["error_type"], "ProcessingError")
        self.assertIn("traceback", failed_log)
        self.assertIn("cannot convert value 'not_a_number'", failed_log["error_message"])


class TestDataIteratorAndDecoratorLogging(unittest.TestCase):
    """Test suite for data iterator and decorator logging."""

    def setUp(self):
        self.log_capture = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setFormatter(JSONFormatter())

        self.dec_logger = logging.getLogger("task_analytics.decorators")
        self.dec_logger.setLevel(logging.INFO)
        self.dec_logger.addHandler(self.handler)
        self.dec_logger.propagate = False

        self.iter_logger = logging.getLogger("task_analytics.data_iterator")
        self.iter_logger.setLevel(logging.INFO)
        self.iter_logger.addHandler(self.handler)
        self.iter_logger.propagate = False

    def tearDown(self):
        self.dec_logger.removeHandler(self.handler)
        self.iter_logger.removeHandler(self.handler)

    def test_timeit_decorator_logging(self):
        """Verify @timeit logs execution duration and function name in extra fields."""
        @timeit
        def sample_function(x, y):
            return x + y

        result = sample_function(10, 20)
        self.assertEqual(result, 30)

        log_output = self.log_capture.getvalue()
        data = json.loads(log_output.strip())
        self.assertEqual(data["function"], "sample_function")
        self.assertIn("duration", data)
        self.assertIn("sample_function", data["message"])

    def test_csv_batch_iterator_logging(self):
        """Verify CSVBatchIterator logs file open and completion events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "sample.csv"
            csv_path.write_text("id,name\n1,Task A\n2,Task B\n", encoding="utf-8")

            iterator = CSVBatchIterator(csv_path, batch_size=10)
            batches = list(iterator)

            self.assertEqual(len(batches), 1)

            log_output = self.log_capture.getvalue()
            lines = [json.loads(l) for l in log_output.strip().splitlines() if l.strip()]

            messages = [l["message"] for l in lines]
            self.assertTrue(any("Opened CSV file" in m for m in messages))
            self.assertTrue(any("Exhausted all CSV data streams" in m for m in messages))


if __name__ == "__main__":
    unittest.main()
