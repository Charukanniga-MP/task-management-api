"""Day 3 Demonstration Script: OOP for Pipelines using Composition over Inheritance.

Demonstrates:
1. Creating data processing pipelines via Composition.
2. Abstract Base Class Step enforcement across concrete steps.
3. Sequential data processing through pipeline.run().
4. Runtime step swapping WITHOUT modifying the Pipeline class.
5. Python Encapsulation conventions (public, protected _, private __).
6. Function vs Class usage example.
"""

import sys
from pathlib import Path

# Add src to Python path to ensure task_analytics can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analytics import (
    CleanDataStep,
    EncapsulationDemo,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PriorityFilterStep,
    clean_text,
)


def main():
    print("==================================================================")
    print("   DAY 3: OOP FOR PIPELINES - COMPOSITION OVER INHERITANCE DEMO   ")
    print("==================================================================\n")

    # 1. Sample Dirty Input Dataset
    raw_tasks = [
        {"title": "  Fix Authentication Bug ", "status": " IN_PROGRESS ", "priority": " HIGH "},
        None,  # Invalid None record
        {},    # Empty dictionary
        {"title": " Write Unit Tests ", "status": " COMPLETED ", "priority": " LOW "},
        {"title": "", "status": "PENDING", "priority": "MEDIUM"},  # Missing title
        {"title": " Refactor Pipeline Code ", "status": " IN_PROGRESS ", "priority": " HIGH "},
        {"title": " Deploy to Staging ", "status": " IN_PROGRESS ", "priority": " MEDIUM "},
    ]

    print("--- 1. INITIAL RAW DATASET ---")
    print(f"Total raw items: {len(raw_tasks)}")
    for i, task in enumerate(raw_tasks, 1):
        print(f"  Item {i}: {task}")
    print()

    # 2. Pipeline Composition - Run 1 (Filter by status='in_progress')
    print("--- 2. INITIAL PIPELINE CONFIGURATION ---")
    step_clean = CleanDataStep(required_keys=["title"])
    step_normalize = NormalizeDataStep(target_fields=["status", "priority"])
    step_filter_status = FilterDataStep(field="status", value="in_progress")

    pipeline_1 = Pipeline([step_clean, step_normalize, step_filter_status])
    print(f"Pipeline created: {pipeline_1}")
    print(f"Executing pipeline on raw dataset...")

    result_1 = pipeline_1.run(raw_tasks)

    print("\n--- 3. RESULT OF INITIAL PIPELINE (Filter: status == 'in_progress') ---")
    print(f"Output record count: {len(result_1)}")
    for record in result_1:
        print(f"  -> {record}")
    print()

    # 3. RUNTIME STEP SWAPPING DEMONSTRATION
    print("==================================================================")
    print("               DEMONSTRATION: RUNTIME STEP SWAPPING               ")
    print("==================================================================")
    print("Notice: We will replace the FilterDataStep (status filter)")
    print("with a PriorityFilterStep (priority='high') at runtime.")
    print("The Pipeline class implementation remains COMPLETELY UNCHANGED!\n")

    # Method A: Swapping step inside existing pipeline instance
    print("Swapping step in pipeline at index 2...")
    step_priority_high = PriorityFilterStep(priority="high")
    pipeline_1.replace_step(2, step_priority_high)

    print(f"Updated Pipeline: {pipeline_1}")
    result_2 = pipeline_1.run(raw_tasks)

    print("\n--- RESULT OF UPDATED PIPELINE (Filter swapped to: priority == 'high') ---")
    print(f"Output record count: {len(result_2)}")
    for record in result_2:
        print(f"  -> {record}")
    print()

    # Method B: Creating another pipeline instance with interchangeable steps
    print("Creating a second pipeline instance with a different step sequence...")
    pipeline_2 = Pipeline([
        CleanDataStep(required_keys=["title"]),
        NormalizeDataStep(),
        PriorityFilterStep(priority="low"),
    ])
    print(f"Pipeline 2 created: {pipeline_2}")
    result_3 = pipeline_2.run(raw_tasks)

    print("\n--- RESULT OF PIPELINE 2 (Filter: priority == 'low') ---")
    print(f"Output record count: {len(result_3)}")
    for record in result_3:
        print(f"  -> {record}")
    print()

    # 4. ENCAPSULATION DEMONSTRATION
    print("==================================================================")
    print("                  DEMONSTRATION: ENCAPSULATION                    ")
    print("==================================================================")
    demo_obj = EncapsulationDemo(
        name="AnalyticsPipeline",
        protected_val="ProtectedConfigValue",
        private_val="SecretApiKey123",
    )

    print(f"Public attribute  (demo_obj.name):            {demo_obj.name}")
    print(f"Protected attr    (demo_obj._protected_val):   {demo_obj._protected_val} (convention only)")
    print(f"Private getter    (demo_obj.get_private_val()): {demo_obj.get_private_val()}")

    print("\nAttempting direct access to private attribute (demo_obj.__private_val)...")
    try:
        val = getattr(demo_obj, "__private_val")
    except AttributeError as e:
        print(f"  -> AttributeError raised as expected: {e}")

    mangled_val = getattr(demo_obj, "_EncapsulationDemo__private_val")
    print(f"Accessing via name mangling (demo_obj._EncapsulationDemo__private_val): {mangled_val}")
    print("Explanation: Python does not enforce access restrictions like Java/C++; name mangling prefixing _ClassName avoids accidental subclass overrides.")
    print()

    # 5. FUNCTION VS CLASS DEMONSTRATION
    print("==================================================================")
    print("                DEMONSTRATION: FUNCTION VS CLASS                  ")
    print("==================================================================")
    raw_str = "   Sample Task Title STRING   "
    cleaned_str = clean_text(raw_str)
    print(f"Raw string:     '{raw_str}'")
    print(f"clean_text():   '{cleaned_str}'")
    print("Rule of thumb: Use a pure function when transforming data without maintaining internal state.")
    print("Use a class when encapsulating state, behavior, or implementing polymorphic interfaces (like Step).")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
