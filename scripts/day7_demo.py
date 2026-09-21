"""Day 7 Demonstration Script: Structured Logging & Production Debugging.

Demonstrates:
1. Centralized logging configuration setup (console + file log in JSON format).
2. RUN 1 — Successful Pipeline Execution (step start/end, duration, record counts).
3. RUN 2 — Deliberately Failed Pipeline Execution (intentional invalid data triggering Day 6 ProcessingError).
4. Top-level exception catching with full traceback preservation in log file (logs/day7_demo.log).
"""

import json
from pathlib import Path
import sys

# Ensure src/ directory is in Python path for script execution
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from task_analytics import (
    CleanDataStep,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PipelineError,
    PriorityFilterStep,
    configure_logging,
)

LOG_FILE_PATH = Path(__file__).resolve().parent.parent / "logs" / "day7_demo.log"


def run_successful_pipeline():
    """RUN 1 — Executes pipeline with valid task records."""
    raw_tasks = [
        {"id": 1, "title": "  Implement Auth API  ", "priority": "HIGH", "complexity": "5", "status": "in_progress"},
        {"id": 2, "title": "  Fix DB Connection Pool ", "priority": "medium", "complexity": "3", "status": "completed"},
        {"id": 3, "title": None, "priority": "low", "complexity": "1", "status": "pending"},
        {"id": 4, "title": "Refactor Logging Module", "priority": "HIGH", "complexity": "8", "status": "in_progress"},
        None,
    ]

    pipeline = Pipeline([
        CleanDataStep(required_keys=["title"]),
        NormalizeDataStep(target_fields=["title", "priority"], numeric_fields=["complexity"]),
        PriorityFilterStep(priority="high"),
    ])

    result = pipeline.run(raw_tasks)
    return result


def run_deliberately_failed_pipeline():
    """RUN 2 — Executes pipeline with invalid input to trigger a ProcessingError."""
    # Record with non-numeric string for complexity field which fails float conversion in NormalizeDataStep
    corrupted_tasks = [
        {"id": 101, "title": "Database Migration", "complexity": "INVALID_NON_NUMERIC_VALUE", "priority": "high"},
    ]

    pipeline = Pipeline([
        CleanDataStep(required_keys=["title"]),
        NormalizeDataStep(numeric_fields=["complexity"]),
    ])

    # Will raise ProcessingError chained from ValueError
    return pipeline.run(corrupted_tasks)


def main():
    # 1. Initialize Centralized Logging
    logger = configure_logging(
        level="DEBUG",
        log_file=LOG_FILE_PATH,
        env="production",
    )

    logger.info("==================================================")
    logger.info("  DAY 7: STRUCTURED LOGGING DEMONSTRATION STARTED  ")
    logger.info("==================================================")

    # --------------------------------------------------------------------------
    # RUN 1: Successful Pipeline Execution
    # --------------------------------------------------------------------------
    logger.info(">>> STARTING RUN 1: SUCCESSFUL PIPELINE RUN <<<", extra={"run_id": "run-001-success"})
    try:
        results = run_successful_pipeline()
        logger.info(
            f">>> RUN 1 FINISHED SUCCESSFULLY with {len(results)} processed records <<<",
            extra={"run_id": "run-001-success", "records_processed": len(results)},
        )
    except Exception as exc:
        logger.exception("RUN 1 unexpectedly failed: %s", exc)

    # --------------------------------------------------------------------------
    # RUN 2: Deliberately Failed Pipeline Execution
    # --------------------------------------------------------------------------
    logger.info(">>> STARTING RUN 2: DELIBERATELY FAILED PIPELINE RUN <<<", extra={"run_id": "run-002-failure"})
    try:
        run_deliberately_failed_pipeline()
    except PipelineError as exc:
        # Catch top-level project exception and log with traceback
        logger.exception(
            "Captured expected PipelineError in RUN 2: %s",
            exc,
            extra={"run_id": "run-002-failure", "error_class": exc.__class__.__name__},
        )
        logger.info(">>> RUN 2 FAILED AS EXPECTED AND WAS CONTROLLED SAFELY <<<", extra={"run_id": "run-002-failure"})

    logger.info("==================================================")
    logger.info("  DAY 7: STRUCTURED LOGGING DEMONSTRATION COMPLETE ")
    logger.info("==================================================")

    # --------------------------------------------------------------------------
    # Output Console Summary & Inspect Saved Log File
    # --------------------------------------------------------------------------
    print("\n==================================================================")
    print("                DAY 7 LOGGING DEMONSTRATION SUMMARY               ")
    print("==================================================================")
    print(f"Log File Location: {LOG_FILE_PATH}")
    print("File Exists:", LOG_FILE_PATH.exists())
    print("-" * 66)

    if LOG_FILE_PATH.exists():
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Total Log Records Written: {len(lines)}")
        print("\n--- SAMPLE LOG RECORD (SUCCESS RUN) ---")
        for line in lines:
            if "run-001-success" in line:
                parsed = json.loads(line)
                print(json.dumps(parsed, indent=2))
                break

        print("\n--- SAMPLE LOG RECORD (FAILED RUN WITH TRACEBACK) ---")
        for line in lines:
            if "run-002-failure" in line and "traceback" in line:
                parsed = json.loads(line)
                print(f"Timestamp: {parsed.get('timestamp')}")
                print(f"Level:     {parsed.get('level')}")
                print(f"Error:     {parsed.get('error_type')}: {parsed.get('error_message')}")
                print("Traceback Snippet:")
                tb_lines = parsed.get("traceback", "").splitlines()
                for tb_line in tb_lines[-6:]:
                    print(f"  {tb_line}")
                break

    print("==================================================================\n")


if __name__ == "__main__":
    main()
