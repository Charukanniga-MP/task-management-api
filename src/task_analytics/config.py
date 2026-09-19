"""Configuration management module for task_analytics (Day 4).

Demonstrates:
1. Python Type Hints (Optional, Union, List, Dict, Generic)
2. Dataclass configuration representation & boilerplate reduction
3. Fixed-choice string Enums (Device, PipelineMode)
4. Pydantic v2 BaseModel runtime validation & field validators
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, ValidationError, field_validator

from task_analytics.exceptions import ConfigError

# ==============================================================================
# 1. ENUMS (Fixed-Choice Fields)
# ==============================================================================


class Device(str, Enum):
    """Supported computing devices for execution."""

    CPU = "cpu"
    GPU = "gpu"


class PipelineMode(str, Enum):
    """Supported pipeline execution modes."""

    TRAIN = "train"
    INFERENCE = "inference"
    EVAL = "eval"


# ==============================================================================
# 2. DATACLASS EXAMPLE
# ==============================================================================


@dataclass
class SimplePipelineConfig:
    """Dataclass implementation of pipeline configuration.

    Dataclasses automatically generate boilerplate methods such as:
    - __init__: Instance constructor
    - __repr__: Human-readable string representation
    - __eq__: Value-based equality comparison

    IMPORTANT: Dataclasses primarily structure data and eliminate boilerplate code.
    They do NOT provide runtime input validation by default (e.g. passing a string
    for batch_size or a non-existent path will succeed without error at instantiation).
    """

    data_path: Path
    batch_size: int = 32
    mode: str = "train"
    threshold: float = 0.5


# ==============================================================================
# 3. GENERIC TYPE HINT DEMONSTRATION
# ==============================================================================

T = TypeVar("T")


class GenericConfigContainer(Generic[T]):
    """Generic container demonstrating Python generic typing (Generic[T]).

    Allows holding typed configuration metadata or result items.
    """

    def __init__(self, item: T, metadata: Optional[Dict[str, Union[int, str]]] = None) -> None:
        self.item: T = item
        self.metadata: Optional[Dict[str, Union[int, str]]] = metadata

    def get_item(self) -> T:
        return self.item


# ==============================================================================
# 4. PYDANTIC CONFIGURATION MODEL (Runtime Validated)
# ==============================================================================


class PipelineConfig(BaseModel):
    """Pydantic configuration model for data/pipeline execution.

    Uses Pydantic v2 syntax for runtime data validation, coercion, and error checking.
    Rejects bad input at load time.
    """

    data_path: Path = Field(
        ...,
        description="Path to existing data file or directory.",
    )
    batch_size: int = Field(
        default=32,
        description="Number of samples per processing batch (must be > 0).",
    )
    feature_columns: List[str] = Field(
        default_factory=list,
        description="List of feature column names to extract/process.",
    )
    mode: PipelineMode = Field(
        default=PipelineMode.TRAIN,
        description="Execution mode: train, inference, or eval.",
    )
    device: Device = Field(
        default=Device.CPU,
        description="Compute target device: cpu or gpu.",
    )
    threshold: float = Field(
        default=0.5,
        description="Decision threshold (must be between 0.0 and 1.0).",
    )
    options: Optional[Dict[str, Union[int, float, str]]] = Field(
        default=None,
        description="Optional dictionary of additional execution options.",
    )

    # --------------------------------------------------------------------------
    # Pydantic v2 Field Validators
    # --------------------------------------------------------------------------

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, value: int) -> int:
        """Validate that batch_size is strictly positive (> 0)."""
        if value <= 0:
            raise ConfigError(
                f"Configuration failed in PipelineConfig: batch_size must be greater than 0, got {value}."
            )
        return value

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        """Validate that threshold lies within range [0.0, 1.0]."""
        if value < 0.0 or value > 1.0:
            raise ConfigError(
                f"Configuration failed in PipelineConfig: threshold must be between 0.0 and 1.0, got {value}."
            )
        return value

    @field_validator("data_path")
    @classmethod
    def validate_data_path(cls, value: Path) -> Path:
        """Validate that data_path points to an existing file or directory.

        Does NOT create the path if missing, ensuring validation fails cleanly.
        """
        resolved_path = value.resolve()
        if not resolved_path.exists():
            raise ConfigError(
                f"Configuration failed in PipelineConfig: data_path must point to an existing path on disk: '{value}'."
            )
        return value


def validate_pipeline_config(config_dict: Dict[str, Any]) -> PipelineConfig:
    """Helper function to load and validate pipeline configuration dictionary.

    Args:
        config_dict: Dictionary containing configuration parameters.

    Returns:
        Validated PipelineConfig instance.

    Raises:
        ConfigError: If configuration fails validation, detailing WHAT, WHERE, and WHY.
    """
    try:
        return PipelineConfig(**config_dict)
    except ValidationError as err:
        raise ConfigError(
            f"Configuration failed in PipelineConfig: invalid configuration options provided. {err}"
        ) from err
