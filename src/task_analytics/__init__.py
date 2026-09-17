"""Task Management Analytics package.

Provides foundation for task predictive modeling, productivity metrics, and ML analytics.
"""

from task_analytics.config import (
    Device,
    GenericConfigContainer,
    PipelineConfig,
    PipelineMode,
    SimplePipelineConfig,
)
from task_analytics.data_iterator import (
    CSVBatchIterator,
    chain_csv_files,
    csv_batch_generator,
    islice_csv,
    load_csv_eager,
)
from task_analytics.pipeline import (
    CleanDataStep,
    EncapsulationDemo,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PriorityFilterStep,
    Step,
    clean_text,
)

__version__ = "0.1.0"

__all__ = [
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
    "Pipeline",
    "EncapsulationDemo",
    "clean_text",
    "Device",
    "PipelineMode",
    "SimplePipelineConfig",
    "PipelineConfig",
    "GenericConfigContainer",
]

