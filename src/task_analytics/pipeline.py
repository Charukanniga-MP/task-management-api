"""Pipeline module implementing Composition over Inheritance for task analytics data processing.

This module provides:
- Step: Abstract base class defining the step interface.
- Concrete Steps: CleanDataStep, NormalizeDataStep, FilterDataStep, PriorityFilterStep.
- Pipeline: Container class composed of Step objects executed sequentially.
- EncapsulationDemo: Demonstration of Python public, protected, and private attributes.
- clean_text: Standalone utility function demonstrating function vs class selection.
"""

from abc import ABC, abstractmethod
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union

from task_analytics.context_managers import TaskResourceManager, managed_resource
from task_analytics.decorators import retry, timeit
from task_analytics.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class Step(ABC):
    """Abstract Base Class representing a single step in a data processing pipeline.

    All concrete steps must inherit from this class and implement the `execute` method.
    """

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the data processing transformation.

        Args:
            data: Input data to be processed.

        Returns:
            Transformed data.
        """
        pass


class CleanDataStep(Step):
    """Concrete step that removes None values, empty dictionaries, or invalid records."""

    def __init__(self, required_keys: Optional[List[str]] = None):
        """Initialize CleanDataStep.

        Args:
            required_keys: Optional list of keys that must be present and non-empty in dict records.
        """
        self.required_keys = required_keys or []

    def execute(self, data: Any) -> Any:
        """Removes None elements, empty items, or records missing required keys.

        Args:
            data: List of items/records or a single record.

        Returns:
            Cleaned list or record.

        Raises:
            ProcessingError: If data is an invalid unsupported type.
        """
        if data is not None and not isinstance(data, (list, dict, str)):
            raise ProcessingError(
                f"Pipeline processing failed in CleanDataStep: expected list, dict, or str, got {type(data).__name__}."
            )

        if isinstance(data, list):
            cleaned = []
            for item in data:
                if item is None:
                    continue
                if isinstance(item, dict):
                    # Filter out empty dicts or dicts missing required keys
                    if not item:
                        continue
                    if self.required_keys and any(
                        item.get(k) is None or item.get(k) == "" for k in self.required_keys
                    ):
                        continue
                    cleaned.append(dict(item))
                elif isinstance(item, str):
                    if item.strip():
                        cleaned.append(item.strip())
                else:
                    cleaned.append(item)
            return cleaned
        elif isinstance(data, dict):
            if not data:
                return {}
            return {k: v for k, v in data.items() if v is not None}
        return data


class NormalizeDataStep(Step):
    """Concrete step that normalizes data fields (e.g. lowercasing strings, trimming whitespace, converting numeric fields)."""

    def __init__(
        self,
        target_fields: Optional[List[str]] = None,
        numeric_fields: Optional[List[str]] = None,
    ):
        """Initialize NormalizeDataStep.

        Args:
            target_fields: Specific dict keys to normalize strings for. If None, normalizes all string values.
            numeric_fields: Specific dict keys that must be converted to float.
        """
        self.target_fields = target_fields
        self.numeric_fields = numeric_fields or []

    def execute(self, data: Any) -> Any:
        """Normalizes string fields and converts numeric fields in input records.

        Args:
            data: List of dictionaries or a single dictionary.

        Returns:
            Normalized list of dictionaries or single dictionary.

        Raises:
            ProcessingError: If type conversion fails on a numeric field, chained from original exception.
        """
        if isinstance(data, list):
            return [self._normalize_record(record) for record in data]
        elif isinstance(data, dict):
            return self._normalize_record(data)
        elif isinstance(data, str):
            return data.strip().lower()
        return data

    def _normalize_record(self, record: Any) -> Any:
        if not isinstance(record, dict):
            return record
        normalized = dict(record)
        for key, value in normalized.items():
            if key in self.numeric_fields:
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError) as original_error:
                    raise ProcessingError(
                        f"Pipeline processing failed in NormalizeDataStep: "
                        f"cannot convert value '{value}' for field '{key}' to float."
                    ) from original_error
            elif isinstance(value, str):
                if self.target_fields is None or key in self.target_fields:
                    normalized[key] = value.strip().lower()
        return normalized


class FilterDataStep(Step):
    """Concrete step that filters data records based on field key-value matching or predicate."""

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        predicate: Optional[Callable[[Any], bool]] = None,
    ):
        """Initialize FilterDataStep.

        Args:
            field: Dictionary key to inspect.
            value: Target value that the field must equal.
            predicate: Optional custom function taking a record and returning bool.
        """
        self.field = field
        self.value = value
        self.predicate = predicate

    def execute(self, data: Any) -> Any:
        """Filters a list of data records according to key-value match or predicate.

        Args:
            data: List of records.

        Returns:
            Filtered list of records.
        """
        if not isinstance(data, list):
            return data

        filtered = []
        for item in data:
            if self.predicate is not None:
                if self.predicate(item):
                    filtered.append(item)
            elif self.field is not None and isinstance(item, dict):
                if item.get(self.field) == self.value:
                    filtered.append(item)
            else:
                filtered.append(item)
        return filtered


class PriorityFilterStep(Step):
    """Concrete step that filters tasks specifically by priority level."""

    def __init__(self, priority: str = "high"):
        """Initialize PriorityFilterStep.

        Args:
            priority: Target priority string (e.g. 'high', 'medium', 'low').
        """
        self.priority = priority.strip().lower()

    def execute(self, data: Any) -> Any:
        """Filters tasks matching the configured priority level.

        Args:
            data: List of task dictionaries.

        Returns:
            List of tasks matching priority.
        """
        if not isinstance(data, list):
            return data
        return [
            task
            for task in data
            if isinstance(task, dict)
            and str(task.get("priority", "")).strip().lower() == self.priority
        ]


class RemoveDuplicatesStep(Step):
    """Concrete step that removes duplicate dict records based on a unique key or exact record matching.

    Demonstrates OPEN/CLOSED PRINCIPLE (OCP):
    This new preprocessing step can be added to any Pipeline without modifying the Pipeline class.
    """

    def __init__(self, key: Optional[str] = None):
        """Initialize RemoveDuplicatesStep.

        Args:
            key: Dictionary key to identify unique records (e.g. 'id' or 'title').
                 If None, deduplicates identical dictionary or primitive records.
        """
        self.key = key

    def execute(self, data: Any) -> Any:
        """Removes duplicate items from input records.

        Args:
            data: List of records or single record.

        Returns:
            Deduplicated list of records or original record.
        """
        if not isinstance(data, list):
            return data

        seen = set()
        unique_records = []
        for item in data:
            if isinstance(item, dict):
                if self.key is not None:
                    lookup_val = item.get(self.key)
                    if lookup_val is not None and lookup_val in seen:
                        continue
                    if lookup_val is not None:
                        seen.add(lookup_val)
                else:
                    # Convert dict items to sorted tuple representation for set lookup
                    dict_tuple = tuple(sorted(item.items()))
                    if dict_tuple in seen:
                        continue
                    seen.add(dict_tuple)
                unique_records.append(item)
            else:
                if item in seen:
                    continue
                seen.add(item)
                unique_records.append(item)

        return unique_records


class DataLoader:
    """Class responsible for fetching/loading data from external sources or callables.

    Demonstrates SINGLE RESPONSIBILITY PRINCIPLE (SRP):
    Data loading logic (retries, fetching, source connection) is isolated from
    Pipeline execution orchestration.
    """

    def __init__(self, max_retries: int = 3):
        """Initialize DataLoader with retry policy.

        Args:
            max_retries: Maximum attempt count for retrying failed data loads.
        """
        self.max_retries = max_retries

    def load(self, fetcher_fn: Callable[[], Any]) -> Any:
        """Loads data by executing fetcher_fn with automatic retry logic.

        Args:
            fetcher_fn: Callable that returns input data or raises an exception.

        Returns:
            Fetched data.
        """
        @retry(max_attempts=self.max_retries)
        def _fetch():
            return fetcher_fn()

        return _fetch()


class Pipeline:
    """Pipeline composed of executable Step objects executed in sequence.

    Demonstrates COMPOSITION OVER INHERITANCE:
    The Pipeline class contains (is composed of) Step objects rather than inheriting
    from them. Steps can be added, removed, or swapped at runtime without changing
    the Pipeline implementation.
    """

    def __init__(self, steps: Optional[List[Step]] = None):
        """Initialize Pipeline with a sequence of steps.

        Args:
            steps: List of Step objects.

        Raises:
            TypeError: If any element in steps is not an instance of Step.
        """
        self.steps: List[Step] = []
        if steps is not None:
            self._validate_steps(steps)
            self.steps = list(steps)

    @staticmethod
    def _count_records(data: Any) -> int:
        """Helper function to calculate record counts for log context metadata (DRY principle)."""
        if isinstance(data, list):
            return len(data)
        return 1 if data is not None else 0

    def _validate_steps(self, steps: List[Step]) -> None:
        for i, step in enumerate(steps):
            if not isinstance(step, Step):
                raise TypeError(
                    f"Invalid step at index {i}: Expected instance of Step, got {type(step).__name__}"
                )

    def add_step(self, step: Step) -> "Pipeline":
        """Appends a new Step to the pipeline sequence.

        Args:
            step: Step instance to add.

        Returns:
            Self for method chaining.
        """
        if not isinstance(step, Step):
            raise TypeError(f"Expected instance of Step, got {type(step).__name__}")
        self.steps.append(step)
        return self

    def replace_step(self, index: int, new_step: Step) -> "Pipeline":
        """Replaces a step at the specified index with a new step.

        Args:
            index: Zero-based index of the step to replace.
            new_step: New Step instance.

        Returns:
            Self for method chaining.
        """
        if not isinstance(new_step, Step):
            raise TypeError(f"Expected instance of Step, got {type(new_step).__name__}")
        if index < 0 or index >= len(self.steps):
            raise IndexError(f"Step index {index} out of range (0..{len(self.steps)-1})")
        self.steps[index] = new_step
        return self

    @timeit
    def run(self, data: Any) -> Any:
        """Executes each step sequentially on the data.

        Decorated with @timeit to log pipeline execution duration.
        Instruments structured logging for pipeline/step starts, completions, durations,
        and processed record counts.

        Args:
            data: Input data to be processed.

        Returns:
            Final transformed data result.
        """
        pipeline_start = time.perf_counter()
        initial_count = self._count_records(data)
        logger.info(
            "Pipeline execution started.",
            extra={"records_processed": initial_count, "step_count": len(self.steps)},
        )

        current_data = data
        for step in self.steps:
            step_name = step.__class__.__name__
            step_start = time.perf_counter()
            logger.info(
                f"Step started: {step_name}",
                extra={"pipeline_step": step_name},
            )
            try:
                current_data = step.execute(current_data)
                step_duration = time.perf_counter() - step_start
                step_records = self._count_records(current_data)
                logger.info(
                    f"Step completed: {step_name}",
                    extra={
                        "pipeline_step": step_name,
                        "duration": round(step_duration, 6),
                        "records_processed": step_records,
                    },
                )
            except Exception as exc:
                step_duration = time.perf_counter() - step_start
                logger.error(
                    f"Step failed: {step_name} - {exc}",
                    extra={
                        "pipeline_step": step_name,
                        "duration": round(step_duration, 6),
                    },
                    exc_info=True,
                )
                raise

        total_duration = time.perf_counter() - pipeline_start
        final_count = self._count_records(current_data)
        logger.info(
            "Pipeline execution completed.",
            extra={"duration": round(total_duration, 6), "records_processed": final_count},
        )
        return current_data

    def load_data_source(self, fetcher_fn: Callable[[], Any]) -> Any:
        """Loads data from a data source or stream with automatic retries on failure.

        Delegates to DataLoader (Single Responsibility Principle).

        Args:
            fetcher_fn: Callable that returns input data or raises an exception.

        Returns:
            Fetched data.
        """
        return DataLoader(max_retries=3).load(fetcher_fn)

    def run_with_resource(self, resource_name: str, data: Any) -> Any:
        """Executes the pipeline within a managed resource context.

        Guarantees that resource cleanup/release occurs even if pipeline execution
        raises an exception.

        Args:
            resource_name: Name or path identifier of the resource.
            data: Input data for the pipeline.

        Returns:
            Transformed data result.
        """
        with TaskResourceManager(resource_name) as resource:
            return self.run(data)

    def __repr__(self) -> str:
        step_names = [type(s).__name__ for s in self.steps]
        return f"Pipeline(steps={step_names})"


class EncapsulationDemo:
    """Demonstrates Python encapsulation access conventions:

    - public attribute: name
    - protected convention: _name (internal use indicator)
    - private name-mangled attribute: __name (Python name mangling with _Class__name)
    """

    def __init__(self, name: str, protected_val: str, private_val: str):
        self.name = name                 # Public attribute: accessible everywhere
        self._protected_val = protected_val  # Protected attribute by convention
        self.__private_val = private_val    # Private attribute (name-mangled to _EncapsulationDemo__private_val)

    def get_private_val(self) -> str:
        """Public getter providing controlled access to the private attribute."""
        return self.__private_val

    def set_private_val(self, val: str) -> None:
        """Public setter providing controlled modification of the private attribute."""
        if not val or not isinstance(val, str):
            raise ValueError("Private value must be a non-empty string.")
        self.__private_val = val


def clean_text(text: str) -> str:
    """Simple standalone function demonstrating when a function is better than a class.

    If a computation requires no persistent internal state, configuration, or reusable
    object behavior, a pure function is simpler and clearer than creating a class.

    Args:
        text: Input string.

    Returns:
        Cleaned, stripped, lowercased string.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return text.strip().lower()

