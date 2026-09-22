"""Task Management Analytics package.

Provides foundation for task predictive modeling, productivity metrics, and ML analytics.
"""

from task_analytics.caching import (
    calculate_task_priority_score,
    get_task_category_weight,
)
from task_analytics.config import (
    Device,
    GenericConfigContainer,
    PipelineConfig,
    PipelineMode,
    SimplePipelineConfig,
)
from task_analytics.context_managers import (
    TaskResourceManager,
    managed_resource,
)
from task_analytics.data_iterator import (
    CSVBatchIterator,
    chain_csv_files,
    csv_batch_generator,
    islice_csv,
    load_csv_eager,
)
from task_analytics.decorators import retry, timeit
from task_analytics.exceptions import (
    ConfigError,
    DataValidationError,
    PipelineError,
    ProcessingError,
)
from task_analytics.logging_config import (
    JSONFormatter,
    TextFormatter,
    configure_logging,
)
from task_analytics.pipeline import (
    CleanDataStep,
    DataLoader,
    EncapsulationDemo,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PriorityFilterStep,
    RemoveDuplicatesStep,
    Step,
    clean_text,
)

__version__ = "0.1.0"

__all__ = [
    "configure_logging",
    "JSONFormatter",
    "TextFormatter",
    "PipelineError",
    "ConfigError",
    "DataValidationError",
    "ProcessingError",
    "CSVBatchIterator",
    "csv_batch_generator",
    "load_csv_eager",
    "islice_csv",
    "chain_csv_files",
    "Step",
    "CleanDataStep",
    "NormalizeDataStep",
    "FilterDataStep",
    "PriorityFilterStep",
    "RemoveDuplicatesStep",
    "DataLoader",
    "Pipeline",
    "EncapsulationDemo",
    "clean_text",
    "Device",
    "PipelineMode",
    "SimplePipelineConfig",
    "PipelineConfig",
    "GenericConfigContainer",
    "timeit",
    "retry",
    "TaskResourceManager",
    "managed_resource",
    "calculate_task_priority_score",
    "get_task_category_weight",
]



