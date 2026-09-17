"""Demonstration script for Day 4 — Type Hints & Pydantic Configuration.

Demonstrates:
1. Valid configuration loading & type verification
2. Dataclass vs Pydantic comparison
3. Multi-scenario invalid configuration handling with clear Pydantic validation error reporting
"""

from pathlib import Path
import sys

from pydantic import ValidationError

# Ensure src is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analytics import (
    Device,
    GenericConfigContainer,
    PipelineConfig,
    PipelineMode,
    SimplePipelineConfig,
)


def print_section(title: str) -> None:
    """Print clean visual section headers."""
    print(f"\n{'=' * 75}")
    print(f"  {title}")
    print(f"{'=' * 75}\n")


def demo_valid_config() -> None:
    """Demonstrate loading and accessing a valid configuration."""
    print_section("VALID CONFIGURATION DEMO")

    valid_data_path = Path("data")  # Existing directory in project

    config = PipelineConfig(
        data_path=valid_data_path,
        batch_size=64,
        feature_columns=["completion_rate", "estimated_hours", "actual_hours"],
        mode=PipelineMode.TRAIN,
        device=Device.CPU,
        threshold=0.85,
        options={"max_epochs": 10, "optimizer": "adam"},
    )

    print("Successfully instantiated validated PipelineConfig:")
    print(f"  Representation    : {config!r}")
    print(f"  data_path         : {config.data_path} (Type: {type(config.data_path).__name__})")
    print(f"  batch_size        : {config.batch_size} (Type: {type(config.batch_size).__name__})")
    print(f"  feature_columns   : {config.feature_columns} (Type: {type(config.feature_columns).__name__})")
    print(f"  mode              : {config.mode} (Type: {type(config.mode).__name__})")
    print(f"  device            : {config.device} (Type: {type(config.device).__name__})")
    print(f"  threshold         : {config.threshold} (Type: {type(config.threshold).__name__})")
    print(f"  options           : {config.options} (Type: {type(config.options).__name__})")

    # Generic container demonstration
    container = GenericConfigContainer[PipelineConfig](
        item=config,
        metadata={"environment": "production", "version": 1},
    )
    print(f"\nGeneric Container item type: {type(container.get_item()).__name__}")


def demo_dataclass_vs_pydantic() -> None:
    """Demonstrate difference between Dataclasses and Pydantic validation."""
    print_section("DATACLASS VS PYDANTIC COMPARISON")

    print("1. Dataclass Example (No Runtime Validation):")
    # Dataclass accepts invalid types/values without error at runtime
    ds_config = SimplePipelineConfig(
        data_path=Path("non_existent_folder"),
        batch_size=-100,  # Invalid batch size, but dataclass allows it!
        mode="invalid_mode",
    )
    print(f"   Dataclass created despite invalid values: {ds_config!r}")
    print("   Notice: Dataclasses structure data but DO NOT validate values at runtime.\n")


def demo_invalid_configs() -> None:
    """Demonstrate multi-scenario invalid configuration rejection."""
    valid_path = Path("data")

    # Example 1: Wrong type
    print_section("INVALID CONFIG 1 — WRONG TYPE")
    try:
        PipelineConfig(
            data_path=valid_path,
            batch_size="large",  # Should be integer or numeric string
        )
    except ValidationError as e:
        print("Caught expected Pydantic ValidationError for wrong type:")
        print(e)

    # Example 2: Out of range value
    print_section("INVALID CONFIG 2 — OUT OF RANGE")
    try:
        PipelineConfig(
            data_path=valid_path,
            batch_size=64,
            threshold=1.5,  # Must be between 0.0 and 1.0
        )
    except ValidationError as e:
        print("Caught expected Pydantic ValidationError for out-of-range value:")
        print(e)

    # Example 3: Non-existent path
    print_section("INVALID CONFIG 3 — NON-EXISTENT PATH")
    try:
        PipelineConfig(
            data_path=Path("this/path/does/not/exist/data.csv"),
            batch_size=32,
        )
    except ValidationError as e:
        print("Caught expected Pydantic ValidationError for non-existent path:")
        print(e)

    # Additional Example: Missing required field
    print_section("INVALID CONFIG 4 — MISSING REQUIRED FIELD")
    try:
        PipelineConfig(  # type: ignore[call-arg]
            batch_size=32,  # data_path missing
        )
    except ValidationError as e:
        print("Caught expected Pydantic ValidationError for missing required field:")
        print(e)


def main() -> None:
    """Run all demonstration sections."""
    print("\n" + "#" * 75)
    print("   DAY 4 — TYPE HINTS & PYDANTIC CONFIGURATION DEMONSTRATION")
    print("#" * 75)

    demo_valid_config()
    demo_dataclass_vs_pydantic()
    demo_invalid_configs()

    print_section("DEMONSTRATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
