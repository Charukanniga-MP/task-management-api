"""Unit tests for CSVBatchIterator, csv_batch_generator, and itertools utilities.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src/ package directory is on Python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from task_analytics.data_iterator import (
    CSVBatchIterator,
    chain_csv_files,
    csv_batch_generator,
    islice_csv,
    load_csv_eager,
)


class TestCSVBatchIterator(unittest.TestCase):
    """Test suite for custom CSV iterator and generator modules."""

    def setUp(self):
        """Create temporary CSV files for test cases."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)

        # 1. Standard CSV file with 250 rows
        self.file_250 = self.temp_dir_path / "sample_250.csv"
        self._create_dummy_csv(self.file_250, row_count=250)

        # 2. Empty CSV file (0 data rows, header only)
        self.file_empty = self.temp_dir_path / "sample_empty.csv"
        self._create_dummy_csv(self.file_empty, row_count=0)

        # 3. Directory with multiple CSV files
        self.multi_dir = self.temp_dir_path / "multi_csv"
        self.multi_dir.mkdir()
        self._create_dummy_csv(self.multi_dir / "a.csv", row_count=30)
        self._create_dummy_csv(self.multi_dir / "b.csv", row_count=20)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _create_dummy_csv(self, filepath: Path, row_count: int):
        fieldnames = ["task_id", "title", "priority", "estimated_hours"]
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(1, row_count + 1):
                writer.writerow({
                    "task_id": f"TASK-{i}",
                    "title": f"Test Task {i}",
                    "priority": "high",
                    "estimated_hours": 5.0,
                })

    def test_iterator_creation(self):
        """Test iterator initialization and parameter validation."""
        iterator = CSVBatchIterator(self.file_250, batch_size=50)
        self.assertEqual(iterator.batch_size, 50)
        self.assertEqual(len(iterator.file_paths), 1)

        # Invalid batch_size
        with self.assertRaises(ValueError):
            CSVBatchIterator(self.file_250, batch_size=0)

        # Non-existent path
        with self.assertRaises(FileNotFoundError):
            CSVBatchIterator(self.temp_dir_path / "non_existent.csv")

    def test_correct_batch_size(self):
        """Test that every full batch returned matches the specified batch size."""
        batch_size = 100
        iterator = CSVBatchIterator(self.file_250, batch_size=batch_size)

        batches = list(iterator)
        # 250 items with batch_size 100 -> [100, 100, 50]
        self.assertEqual(len(batches), 3)
        self.assertEqual(len(batches[0]), 100)
        self.assertEqual(len(batches[1]), 100)
        self.assertEqual(len(batches[2]), 50)

    def test_multiple_batches(self):
        """Test processing multiple batches sequentially."""
        iterator = CSVBatchIterator(self.file_250, batch_size=80)
        batch_counts = [len(batch) for batch in iterator]
        # 250 items with batch_size 80 -> 80 + 80 + 80 + 10
        self.assertEqual(batch_counts, [80, 80, 80, 10])
        self.assertEqual(sum(batch_counts), 250)

    def test_final_smaller_batch(self):
        """Test that the final batch correctly contains remaining items."""
        iterator = CSVBatchIterator(self.file_250, batch_size=150)
        batches = list(iterator)
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 150)
        self.assertEqual(len(batches[1]), 100)

    def test_empty_dataset(self):
        """Test iterating over an empty CSV file (header only)."""
        iterator = CSVBatchIterator(self.file_empty, batch_size=50)
        batches = list(iterator)
        self.assertEqual(len(batches), 0)

    def test_stop_iteration(self):
        """Test that calling next() beyond exhaustion explicitly raises StopIteration."""
        iterator = CSVBatchIterator(self.file_empty, batch_size=10)
        iter_obj = iter(iterator)
        with self.assertRaises(StopIteration):
            next(iter_obj)

        # Test explicit next() calls on small file
        file_small = self.temp_dir_path / "small.csv"
        self._create_dummy_csv(file_small, row_count=5)
        it = iter(CSVBatchIterator(file_small, batch_size=5))
        batch = next(it)
        self.assertEqual(len(batch), 5)
        with self.assertRaises(StopIteration):
            next(it)

    def test_generator_behavior(self):
        """Test generator function csv_batch_generator yields expected batches."""
        gen = csv_batch_generator(self.file_250, batch_size=100)
        batches = list(gen)
        self.assertEqual(len(batches), 3)
        self.assertEqual(len(batches[0]), 100)
        self.assertEqual(len(batches[1]), 100)
        self.assertEqual(len(batches[2]), 50)
        self.assertEqual(batches[0][0]["task_id"], "TASK-1")

    def test_itertools_integration(self):
        """Test itertools helper functions: islice_csv and chain_csv_files."""
        # Test islice_csv peeking first 5 items
        slice_result = islice_csv(self.file_250, start=0, stop=5)
        self.assertEqual(len(slice_result), 5)
        self.assertEqual(slice_result[0]["task_id"], "TASK-1")
        self.assertEqual(slice_result[4]["task_id"], "TASK-5")

        # Test chain_csv_files
        file_a = self.multi_dir / "a.csv"
        file_b = self.multi_dir / "b.csv"
        chained = list(chain_csv_files([file_a, file_b]))
        self.assertEqual(len(chained), 50)  # 30 + 20

    def test_directory_iterator(self):
        """Test lazy iteration over a directory containing multiple CSV files."""
        iterator = CSVBatchIterator(self.multi_dir, batch_size=15)
        batches = list(iterator)
        # Total rows = 30 + 20 = 50. With batch_size=15: [15, 15, 15, 5]
        total_rows = sum(len(b) for b in batches)
        self.assertEqual(total_rows, 50)
        self.assertEqual(len(batches), 4)

    def test_eager_vs_lazy_content_equality(self):
        """Test that eager and lazy loaders yield identical content."""
        eager_data = load_csv_eager(self.file_250)
        lazy_batches = list(CSVBatchIterator(self.file_250, batch_size=50))
        flattened_lazy = [row for batch in lazy_batches for row in batch]

        self.assertEqual(len(eager_data), len(flattened_lazy))
        self.assertEqual(eager_data, flattened_lazy)


if __name__ == "__main__":
    unittest.main()
