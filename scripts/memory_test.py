"""Memory usage measurement script comparing Eager vs. Lazy CSV loading.

Uses Python's `tracemalloc` standard library module to track current memory
and peak memory consumption when iterating through datasets of varying sizes:
  - 100 rows
  - 1,000 rows
  - 10,000 rows

Demonstrates that lazy batch iteration keeps memory constant (O(Batch Size)),
whereas eager loading grows linearly (O(N)) with dataset row count.
"""

import gc
import os
import sys
import tracemalloc
from pathlib import Path

# Add project src directory to path if needed
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from task_analytics.data_iterator import CSVBatchIterator, load_csv_eager
from generate_sample_data import generate_csv_data


def measure_eager_loading(csv_path: Path) -> tuple[float, float, int]:
    """Measure memory usage for eager loading (loading full CSV into list).

    Returns:
        tuple: (current_kb, peak_kb, row_count)
    """
    gc.collect()
    tracemalloc.reset_peak()
    tracemalloc.start()

    # Perform eager loading
    dataset = load_csv_eager(csv_path)
    row_count = len(dataset)

    # Process dataset (simulate iteration/computation)
    processed_count = sum(1 for row in dataset)

    current_b, peak_b = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    current_kb = current_b / 1024
    peak_kb = peak_b / 1024

    return current_kb, peak_kb, processed_count


def measure_lazy_loading(csv_path: Path, batch_size: int = 100) -> tuple[float, float, int]:
    """Measure memory usage for lazy batch iteration.

    Returns:
        tuple: (current_kb, peak_kb, total_rows_processed)
    """
    gc.collect()
    tracemalloc.reset_peak()
    tracemalloc.start()

    iterator = CSVBatchIterator(csv_path, batch_size=batch_size)
    processed_count = 0

    for batch in iterator:
        # Simulate batch processing
        processed_count += len(batch)

    current_b, peak_b = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    current_kb = current_b / 1024
    peak_kb = peak_b / 1024

    return current_kb, peak_kb, processed_count


def run_memory_benchmark(batch_size: int = 100):
    """Execute memory measurement benchmark across multiple dataset sizes."""
    raw_data_dir = repo_root / "data" / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    sizes = [100, 1000, 10000]

    # Ensure sample CSV files exist
    for size in sizes:
        file_path = raw_data_dir / f"sample_{size}.csv"
        if not file_path.exists():
            print(f"Sample data file {file_path.name} not found. Generating...")
            generate_csv_data(file_path, size)

    print("=" * 65)
    print("      DATASET MEMORY PROFILING BENCHMARK (tracemalloc)")
    print("=" * 65)

    eager_results = {}
    lazy_results = {}

    print("\n--- 1. EAGER LOADING (Loads entire dataset into memory list) ---")
    for size in sizes:
        file_path = raw_data_dir / f"sample_{size}.csv"
        current_kb, peak_kb, count = measure_eager_loading(file_path)
        eager_results[size] = (current_kb, peak_kb)
        print(f"\nDataset size: {size}")
        print(f"Current memory: {current_kb:10.2f} KB")
        print(f"Peak memory:    {peak_kb:10.2f} KB")

    print("\n" + "-" * 65)
    print(f"--- 2. LAZY BATCH ITERATOR (batch_size={batch_size}) ---")
    for size in sizes:
        file_path = raw_data_dir / f"sample_{size}.csv"
        current_kb, peak_kb, count = measure_lazy_loading(file_path, batch_size=batch_size)
        lazy_results[size] = (current_kb, peak_kb)
        print(f"\nDataset size: {size}")
        print(f"Current memory: {current_kb:10.2f} KB")
        print(f"Peak memory:    {peak_kb:10.2f} KB")

    print("\n" + "=" * 65)
    print("                      COMPARISON SUMMARY")
    print("=" * 65)
    print(f"{'Dataset Size':<15} | {'Eager Peak (KB)':<18} | {'Lazy Peak (KB)':<18} | {'Memory Savings':<15}")
    print("-" * 75)

    for size in sizes:
        eager_peak = eager_results[size][1]
        lazy_peak = lazy_results[size][1]
        savings = (1 - (lazy_peak / eager_peak)) * 100 if eager_peak > 0 else 0
        print(f"{size:<15} | {eager_peak:18.2f} | {lazy_peak:18.2f} | {savings:14.1f}%")

    print("\nKey Finding:")
    print("  Eager loading peak memory increases proportionally with dataset row count (O(N)).")
    print("  Lazy batch iteration keeps peak memory virtually constant (O(Batch Size)),")
    print("  making it essential for processing large-scale machine learning datasets.")
    print("=" * 65)


if __name__ == "__main__":
    run_memory_benchmark()
