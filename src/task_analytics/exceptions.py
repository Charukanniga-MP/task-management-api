"""Custom Exception Hierarchy for Task Analytics & Pipeline Processing (Day 6).

Defines project-specific exceptions structured as a clean hierarchy:

    Exception
        └── PipelineError
              ├── ConfigError
              ├── DataValidationError
              └── ProcessingError

Design Philosophy:
- Specific custom exceptions are raised at the low-level source of failure.
- Errors contain structured messages detailing: WHAT failed, WHERE it failed, WHY it failed.
- Higher-level layers allow exceptions to propagate to a top-level error handler.
- Low-level Python exceptions are wrapped using exception chaining (`raise ... from original_error`).
"""


class PipelineError(Exception):
    """Base exception for all pipeline and task analytics errors.
    
    Catching PipelineError at top-level catches all project-specific failures
    without swallowing unrelated Python system exceptions.
    """

    pass


class ConfigError(PipelineError, ValueError):
    """Raised when configuration validation, instantiation, or loading fails.
    
    WHAT: Configuration initialization/validation failure.
    WHERE: PipelineConfig or config loader layer.
    WHY: Invalid field values, out-of-range thresholds, missing required paths, etc.
    """

    pass


class DataValidationError(PipelineError, ValueError, FileNotFoundError):
    """Raised when input data is missing, malformed, or fails schema/type validation.
    
    WHAT: Data loading or row validation failure.
    WHERE: Data iterator or data loader layer (e.g. CSVBatchIterator).
    WHY: Non-existent files, negative batch size, corrupted CSV rows, etc.
    """

    pass


class ProcessingError(PipelineError, RuntimeError):
    """Raised when a pipeline step or transformation fails during execution.
    
    WHAT: Processing transformation failure.
    WHERE: Concrete Step instance (e.g. CleanDataStep, NormalizeDataStep).
    WHY: Type conversion failure, missing required keys, unhandled record structure.
    """

    pass
