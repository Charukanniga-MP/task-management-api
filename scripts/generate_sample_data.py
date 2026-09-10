"""Script to generate sample CSV datasets of different row counts for testing.

Outputs files to data/raw/ directory:
  - sample_100.csv
  - sample_1000.csv
  - sample_10000.csv

These datasets are used to compare eager vs lazy data loading performance.
"""

import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_csv_data(filepath: Path, num_rows: int, seed: int = 42) -> Path:
    """Generate a sample task management dataset and write it to a CSV file.

    Args:
        filepath: Destination Path object for the CSV file.
        num_rows: Number of data rows to generate.
        seed: Random seed for reproducible dataset generation.

    Returns:
        Path: Path to the written CSV file.
    """
    random.seed(seed)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    priorities = ["low", "medium", "high", "critical"]
    statuses = ["todo", "in_progress", "completed"]
    task_types = [
        "Bug fix", "Feature implementation", "Code review",
        "Refactoring", "Documentation update", "Database migration",
        "Unit test writing", "API integration", "Performance optimization"
    ]

    fieldnames = [
        "task_id",
        "title",
        "priority",
        "status",
        "estimated_hours",
        "logged_hours",
        "created_at",
    ]

    base_date = datetime(2026, 1, 1, 9, 0, 0)

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_rows + 1):
            task_type = random.choice(task_types)
            est = round(random.uniform(1.0, 40.0), 1)
            logged = round(random.uniform(0.0, est * 1.5), 1)
            created_dt = base_date + timedelta(minutes=i * 5)

            writer.writerow({
                "task_id": f"TASK-{i:06d}",
                "title": f"{task_type} for module {i % 50}",
                "priority": random.choice(priorities),
                "status": random.choice(statuses),
                "estimated_hours": est,
                "logged_hours": logged,
                "created_at": created_dt.isoformat(),
            })

    print(f"Successfully generated {num_rows:,} rows -> {filepath}")
    return filepath


def main():
    # Resolve repository root path
    repo_root = Path(__file__).resolve().parent.parent
    raw_data_dir = repo_root / "data" / "raw"

    row_counts = [100, 1000, 10000]

    print("Generating sample CSV datasets under data/raw/...")
    for count in row_counts:
        out_path = raw_data_dir / f"sample_{count}.csv"
        generate_csv_data(out_path, count)

    print("Sample data generation complete.")


if __name__ == "__main__":
    main()
