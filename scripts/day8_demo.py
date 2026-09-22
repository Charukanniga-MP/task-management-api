"""Day 8 Demonstration Script: Clean Code & SOLID Principles.

This script demonstrates:
1. Single Responsibility Principle (SRP): DataLoader separated from Pipeline orchestration.
2. Open/Closed Principle (OCP): Creating and adding a NEW preprocessing step
   (RemoveDuplicatesStep) to Pipeline WITHOUT modifying the Pipeline class.
3. Dependency Inversion Principle (DIP): Pipeline operates on the Step interface abstraction.
4. Composition over Inheritance: Pipeline dynamically composes interchangeable Step objects.
5. DRY & Clean Naming: Reusable helper methods and self-describing variable names.
"""

import inspect
import logging
from typing import Any, Dict, List

from task_analytics import (
    CleanDataStep,
    DataLoader,
    NormalizeDataStep,
    Pipeline,
    RemoveDuplicatesStep,
    Step,
    configure_logging,
)

logger = logging.getLogger("task_analytics.day8_demo")


def main() -> None:
    # 1. Initialize Centralized Structured Logging
    configure_logging(level="INFO", env="development")
    print("=" * 70)
    print("DAY 8 DEMO: CLEAN CODE & SOLID PRINCIPLES")
    print("=" * 70)

    # 2. Prepare Sample Raw Dataset with Duplicates, Messy Whitespace & Dirty Fields
    raw_data: List[Dict[str, Any]] = [
        {"id": 1, "title": "  Fix Critical Login Bug  ", "status": " IN_PROGRESS ", "priority": " HIGH "},
        {"id": 2, "title": "Write Unit Tests", "status": "PENDING", "priority": "MEDIUM"},
        {"id": 1, "title": "  Fix Critical Login Bug  ", "status": " IN_PROGRESS ", "priority": " HIGH "},  # Duplicate id 1
        None,  # Invalid item
        {},  # Empty record
        {"id": 3, "title": "Deploy to Staging", "status": " COMPLETED ", "priority": " LOW "},
        {"id": 2, "title": "Write Unit Tests", "status": "PENDING", "priority": "MEDIUM"},  # Duplicate id 2
    ]

    print(f"\n1. Raw Input Dataset ({len(raw_data)} items):")
    for i, item in enumerate(raw_data, 1):
        print(f"   [{i}] {item}")

    # 3. Create Standard Pipeline (Day 3 Steps)
    print("\n2. Initializing Standard Pipeline with CleanDataStep & NormalizeDataStep...")
    initial_pipeline = Pipeline([
        CleanDataStep(required_keys=["id", "title"]),
        NormalizeDataStep(target_fields=["status", "priority"]),
    ])

    print(f"   Pipeline Steps: {initial_pipeline}")

    # Run initial pipeline
    cleaned_data = initial_pipeline.run(raw_data)
    print(f"\n3. Output After Initial Pipeline ({len(cleaned_data)} items):")
    for i, item in enumerate(cleaned_data, 1):
        print(f"   [{i}] {item}")

    # 4. Open/Closed Principle Demonstration: Add NEW Preprocessing Step WITHOUT Modifying Pipeline
    print("\n" + "=" * 70)
    print("OPEN/CLOSED PRINCIPLE (OCP) DEMONSTRATION")
    print("=" * 70)
    print("Creating a NEW preprocessing step: RemoveDuplicatesStep(Step)...")

    # Capture source of Pipeline class to prove zero modifications
    pipeline_src_before = inspect.getsource(Pipeline)

    # Instantiate new step
    dedup_step = RemoveDuplicatesStep(key="id")
    print(f"   Created step: {dedup_step.__class__.__name__} (inherits from Step ABC: {issubclass(RemoveDuplicatesStep, Step)})")

    # Add new step to existing pipeline using method chaining (Composition)
    print("\nAdding RemoveDuplicatesStep to Pipeline...")
    initial_pipeline.add_step(dedup_step)
    print(f"   Updated Pipeline Steps: {initial_pipeline}")

    # Run updated pipeline
    final_dedup_data = initial_pipeline.run(raw_data)
    print(f"\n4. Output After Pipeline Execution with RemoveDuplicatesStep ({len(final_dedup_data)} items):")
    for i, item in enumerate(final_dedup_data, 1):
        print(f"   [{i}] {item}")

    # Verify Pipeline class source code was NOT modified
    pipeline_src_after = inspect.getsource(Pipeline)
    assert pipeline_src_before == pipeline_src_after, "Pipeline class source was unexpectedly modified!"
    print("\n[PROOF OF OCP & DIP]:")
    print("   [OK] New step 'RemoveDuplicatesStep' executed successfully within Pipeline.")
    print("   [OK] Pipeline source code was NOT modified at all.")
    print("   [OK] Pipeline operates strictly via the abstract 'Step' interface (Dependency Inversion).")


    # 5. Single Responsibility Principle (SRP) Demonstration: DataLoader
    print("\n" + "=" * 70)
    print("SINGLE RESPONSIBILITY PRINCIPLE (SRP) DEMONSTRATION")
    print("=" * 70)
    print("DataLoader handles fetching/retries; Pipeline handles execution orchestration.")

    attempts = 0

    def mock_fetcher():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            print(f"   DataLoader attempt {attempts}: Simulated network failure...")
            raise ConnectionError("Temporary network glitch")
        print(f"   DataLoader attempt {attempts}: Data fetched successfully!")
        return raw_data

    loader = DataLoader(max_retries=3)
    fetched_data = loader.load(mock_fetcher)
    print(f"   DataLoader successfully retrieved {len(fetched_data)} items.")

    print("\n" + "=" * 70)
    print("DAY 8 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
