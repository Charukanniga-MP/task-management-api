"""Day 5 Demonstration Script: Decorators, Context Managers & Caching.

Demonstrates:
1. @timeit decorator measuring execution duration and preserving metadata.
2. @retry(max_attempts=N) decorator recovering from transient failures and exhausting attempts.
3. Context manager resource cleanup during normal and exception flows.
4. Actual Pipeline executing with @timeit, @retry, and TaskResourceManager.
5. functools.lru_cache performance acceleration and cache management.
"""

import sys
import time
from typing import Any, List

from task_analytics import (
    CleanDataStep,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PriorityFilterStep,
    TaskResourceManager,
    calculate_task_priority_score,
    get_task_category_weight,
    managed_resource,
    retry,
    timeit,
)


def print_header(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"=== {title} ===")
    print(f"{'=' * 50}")


def run_timeit_demo() -> None:
    print_header("TIMEIT DEMO")

    @timeit
    def process_task_batch(tasks: List[dict]) -> int:
        """Simulates processing a batch of tasks."""
        time.sleep(0.05)  # Simulate processing delay
        return len(tasks)

    print(f"Decorated Function Name: {process_task_batch.__name__}")
    print(f"Decorated Function Docstring: {process_task_batch.__doc__}")

    sample_tasks = [{"id": 1, "title": "Task A"}, {"id": 2, "title": "Task B"}]
    count = process_task_batch(sample_tasks)
    print(f"Processed {count} tasks successfully.")


def run_retry_demo() -> None:
    print_header("RETRY DEMO")

    attempt_counter = 0

    @retry(max_attempts=3)
    def fetch_unstable_network_data() -> dict:
        """Simulates an external API call that fails on the 1st attempt and succeeds on the 2nd."""
        nonlocal attempt_counter
        attempt_counter += 1
        print(f"  -> Executing fetch_unstable_network_data (Attempt {attempt_counter})...")
        if attempt_counter < 2:
            raise ConnectionError("Temporary network timeout")
        return {"status": "success", "data": [10, 20, 30]}

    print("--- 1. Controlled Retry Recovery (Fail 1x, Succeed 2nd) ---")
    result = fetch_unstable_network_data()
    print(f"Result returned after recovery: {result}")

    print("\n--- 2. Exhausting Max Retries (Fails 3/3 times) ---")
    failing_counter = 0

    @retry(max_attempts=3)
    def always_failing_service() -> None:
        nonlocal failing_counter
        failing_counter += 1
        print(f"  -> Executing always_failing_service (Attempt {failing_counter})...")
        raise TimeoutError("Service permanently unavailable")

    try:
        always_failing_service()
    except TimeoutError as exc:
        print(f"Caught expected final exception after 3 retries: {exc}")


def run_context_manager_demo() -> None:
    print_header("CONTEXT MANAGER DEMO")

    print("--- 1. Class Context Manager (__enter__ / __exit__) - Normal Flow ---")
    with TaskResourceManager("production_db") as res:
        print(f"  Inside with block: Resource status = '{res.resource_data['status']}', is_open = {res.is_open}")

    print(f"  Outside with block: Resource status = '{res.resource_data['status']}', is_open = {res.is_open}")

    print("\n--- 2. Class Context Manager - Exception Handling Flow ---")
    try:
        with TaskResourceManager("temporary_file_buffer") as res_err:
            print("  Inside with block: Simulating an unexpected error...")
            raise RuntimeError("Disk quota exceeded inside block!")
    except RuntimeError as exc:
        print(f"  Caught exception outside block: '{exc}'")
        print(f"  Verified Cleanup: Resource status = '{res_err.resource_data['status']}', is_open = {res_err.is_open}")

    print("\n--- 3. Generator Context Manager (@contextmanager) ---")
    with managed_resource("analytics_stream") as stream:
        print(f"  Stream active: {stream['is_active']}, cleaned_up: {stream['cleaned_up']}")

    print(f"  After exiting stream: active: {stream['is_active']}, cleaned_up: {stream['cleaned_up']}")


def run_pipeline_demo() -> None:
    print_header("PIPELINE DEMO")

    print("--- 1. Executing Pipeline with @timeit & TaskResourceManager ---")
    pipeline = Pipeline([
        CleanDataStep(required_keys=["title"]),
        NormalizeDataStep(target_fields=["status", "priority"]),
        PriorityFilterStep(priority="high"),
    ])

    raw_data = [
        {"title": " Fix Critical Auth Bug ", "status": " IN_PROGRESS ", "priority": " HIGH "},
        {"title": " Update Documentation ", "status": " DONE ", "priority": " LOW "},
        None,
        {"title": " Refactor Database Queries ", "status": " OPEN ", "priority": " HIGH "},
    ]

    # Process using resource manager
    cleaned_data = pipeline.run_with_resource("raw_tasks.json", raw_data)
    print(f"Pipeline Result ({len(cleaned_data)} high-priority tasks):")
    for item in cleaned_data:
        print(f"  - {item}")

    print("\n--- 2. Pipeline Loading Data with @retry ---")
    attempts = 0

    def flaky_data_source():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise IOError("Read error on disk batch")
        return [{"title": " Retried Task ", "status": " PENDING ", "priority": " HIGH "}]

    fetched_data = pipeline.load_data_source(flaky_data_source)
    processed = pipeline.run(fetched_data)
    print(f"Fetched and processed data: {processed}")


def run_cache_demo() -> None:
    print_header("CACHE DEMO")

    calculate_task_priority_score.cache_clear()

    print("--- 1. LRU Cache Performance Demonstration ---")
    # First call (Calculated)
    t0 = time.perf_counter()
    score1 = calculate_task_priority_score("high", 8, 3)
    t1 = time.perf_counter()
    duration1 = (t1 - t0) * 1_000_000

    # Second call with identical arguments (Cache Hit)
    t2 = time.perf_counter()
    score2 = calculate_task_priority_score("high", 8, 3)
    t3 = time.perf_counter()
    duration2 = (t3 - t2) * 1_000_000

    print(f"Call 1 (Computed): score={score1}, duration={duration1:.2f} µs")
    print(f"Call 2 (Cache Hit): score={score2}, duration={duration2:.2f} µs")
    print(f"Cache Statistics: {calculate_task_priority_score.cache_info()}")

    print("\n--- 2. Cache Clearing (cache_clear) ---")
    calculate_task_priority_score.cache_clear()
    print(f"Cache Stats after cache_clear(): {calculate_task_priority_score.cache_info()}")

    print("\n--- 3. Immutable Return Safety ---")
    w1 = get_task_category_weight("bug")
    print(f"Category weight for 'bug': {w1} (Returns float, immune to mutation issues)")


def main() -> None:
    print("\n==================================================")
    print(" TASK MANAGEMENT ANALYTICS - DAY 5 DEMO")
    print(" Decorators, Context Managers & Caching")
    print("==================================================")

    run_timeit_demo()
    run_retry_demo()
    run_context_manager_demo()
    run_pipeline_demo()
    run_cache_demo()

    print("\n==================================================")
    print(" DAY 5 DEMO COMPLETED SUCCESSFULLY")
    print("==================================================\n")


if __name__ == "__main__":
    main()
