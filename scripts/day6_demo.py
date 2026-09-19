"""Day 6 Demonstration Script — Exception Hierarchies & Error Design.

Demonstrates:
1. Top-level exception handling catching `PipelineError`
2. Low-level custom error raising for:
   - ConfigError (invalid configuration settings)
   - DataValidationError (data/path loading failure)
   - ProcessingError (pipeline step execution failure with exception chaining)
3. Structured error messages explaining WHAT, WHERE, and WHY
4. `try / except / else / finally` control flow semantics (success vs failure)
"""

import sys
from pathlib import Path

# Add src to sys.path if running as standalone script
repo_root = Path(__file__).resolve().parent.parent
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from task_analytics.config import validate_pipeline_config
from task_analytics.data_iterator import CSVBatchIterator
from task_analytics.exceptions import (
    ConfigError,
    DataValidationError,
    PipelineError,
    ProcessingError,
)
from task_analytics.pipeline import CleanDataStep, NormalizeDataStep, Pipeline


def print_section(title: str) -> None:
    """Print formatted section header."""
    print(f"\n{'=' * 75}")
    print(f"  {title}")
    print(f"{'=' * 75}")


def demo_config_error() -> None:
    """Demonstrates ConfigError failure mode."""
    print_section("1. DEMONSTRATION: ConfigError (Configuration Failure)")
    
    invalid_config_data = {
        "data_path": "data",
        "batch_size": -10,  # Invalid negative batch size
        "mode": "train",
    }

    try:
        print("[SETUP] Attempting to load invalid configuration (batch_size = -10)...")
        _ = validate_pipeline_config(invalid_config_data)
    except PipelineError as error:
        print("\n[TOP-LEVEL ERROR HANDLER CATCH]")
        print(f"Pipeline Error Caught : {type(error).__name__}")
        print(f"User-Facing Error Message:\n  --> {error}")


def demo_data_validation_error() -> None:
    """Demonstrates DataValidationError failure mode."""
    print_section("2. DEMONSTRATION: DataValidationError (Data Loading/Validation Failure)")

    non_existent_file = "data/non_existent_sample_999.csv"

    try:
        print(f"[SETUP] Attempting to initialize CSVBatchIterator with non-existent file: '{non_existent_file}'...")
        _ = CSVBatchIterator(path=non_existent_file, batch_size=50)
    except PipelineError as error:
        print("\n[TOP-LEVEL ERROR HANDLER CATCH]")
        print(f"Pipeline Error Caught : {type(error).__name__}")
        print(f"User-Facing Error Message:\n  --> {error}")


def demo_processing_error_with_chaining() -> None:
    """Demonstrates ProcessingError with exception chaining (`raise ... from original_error`)."""
    print_section("3. DEMONSTRATION: ProcessingError with Exception Chaining")

    print("[SETUP] Executing NormalizeDataStep with non-numeric value in numeric_fields...")
    step = NormalizeDataStep(numeric_fields=["estimated_hours"])
    invalid_records = [
        {"task_id": "TASK-101", "estimated_hours": "INVALID_FLOAT_VALUE"}
    ]

    try:
        _ = step.execute(invalid_records)
    except PipelineError as error:
        print("\n[TOP-LEVEL ERROR HANDLER CATCH]")
        print(f"Pipeline Error Caught : {type(error).__name__}")
        print(f"User-Facing Error Message:\n  --> {error}")
        
        # Display underlying exception cause from chaining
        if error.__cause__:
            print(f"\n[DEBUG / TRACEBACK CAUSE] Exception Chaining Preserved:")
            print(f"  Original Exception Cause : {type(error.__cause__).__name__}: {error.__cause__}")


def demo_try_except_else_finally() -> None:
    """Demonstrates try / except / else / finally control flow semantics."""
    print_section("4. DEMONSTRATION: try / except / else / finally Control Flow")

    print("\n--- CASE A: Successful Execution ---")
    try:
        print("  [try block]      Executing valid computation...")
        result = 100 / 5
    except ZeroDivisionError as e:
        print(f"  [except block]   Caught error: {e}")
    else:
        print(f"  [else block]     SUCCESS! Executed ONLY because no exception was raised. Result = {result}")
    finally:
        print("  [finally block]  CLEANUP! Executed ALWAYS (on success or failure).")

    print("\n--- CASE B: Failing Execution ---")
    try:
        print("  [try block]      Executing division by zero...")
        result = 100 / 0
    except ZeroDivisionError as e:
        print(f"  [except block]   CAUGHT EXCEPTION! Handled expected error: {e}")
    else:
        print("  [else block]     SKIPPED! Does not run when exception occurs.")
    finally:
        print("  [finally block]  CLEANUP! Executed ALWAYS (on success or failure).")


def run_full_day6_demo() -> None:
    """Run all Day 6 error design demonstrations."""
    print("=" * 75)
    print("         DAY 6 TASK — EXCEPTION HIERARCHIES & ERROR DESIGN DEMO         ")
    print("=" * 75)

    demo_config_error()
    demo_data_validation_error()
    demo_processing_error_with_chaining()
    demo_try_except_else_finally()

    print_section("DEMONSTRATION SUMMARY")
    print("All custom exceptions correctly inherit from PipelineError.")
    print("Top-level handlers catch PipelineError while preserving specific error diagnostics.")
    print("Every error message explicitly details WHAT failed, WHERE it failed, and WHY it failed.")


if __name__ == "__main__":
    run_full_day6_demo()
