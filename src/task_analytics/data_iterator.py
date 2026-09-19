"""Iterators, Generators & Memory-Efficient Data Handling Module.

This module provides lazy-loading iterators, generators, and eager baseline
utilities for processing CSV datasets without loading entire files into memory.

Iteration Protocol Concepts Explained:
-------------------------------------
1. __iter__():
   The entry point for Python's iteration protocol. When a object is passed to
   iter() or used in a for-loop, Python calls __iter__(). It must return an iterator
   object (usually `self` if the class implements __next__).

2. __next__():
   Called by Python on each step of iteration (e.g. inside a for-loop).
   It computes/fetches the next item in sequence and returns it.

3. StopIteration:
   A built-in exception raised inside __next__() when there are no more items
   left to iterate over. Python's for-loops automatically catch StopIteration
   and terminate cleanly.

4. Generators & `yield`:
   A generator function uses the `yield` keyword instead of `return`. When called,
   it returns a generator iterator without running the code immediately.
   Each call to next() executes code up to the next `yield`, returning the value
   and freezing execution state until the next iteration.
"""

import csv
import itertools
import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

from task_analytics.exceptions import DataValidationError


class CSVBatchIterator:
    """Custom lazy-loading iterator over CSV file(s) that yields data batch-by-batch.

    Demonstrates Python's Iteration Protocol (__iter__, __next__, StopIteration).

    Attributes:
        file_paths (List[Path]): List of CSV file paths to iterate over.
        batch_size (int): Number of rows to return per batch.
        dict_reader (bool): If True, returns list of dicts. If False, list of lists.
    """

    def __init__(
        self,
        path: Union[str, Path],
        batch_size: int = 100,
        dict_reader: bool = True,
    ):
        """Initialize the CSVBatchIterator.

        Args:
            path: Path to a CSV file or directory containing CSV files.
            batch_size: Number of rows per batch (must be >= 1).
            dict_reader: Whether to parse CSV rows as dictionaries.

        Raises:
            DataValidationError: If batch_size < 1 or path does not exist.
        """
        if batch_size < 1:
            raise DataValidationError(
                f"Data validation failed in CSVBatchIterator: batch_size must be at least 1, got {batch_size}."
            )

        input_path = Path(path)
        if not input_path.exists():
            raise DataValidationError(
                f"Data validation failed in CSVBatchIterator: path '{input_path}' does not exist."
            )

        if input_path.is_dir():
            # Find all CSV files in directory sorted deterministically
            self.file_paths = sorted(list(input_path.glob("*.csv")))
            if not self.file_paths:
                # Store directory path even if empty for iteration setup
                self.file_paths = []
        else:
            self.file_paths = [input_path]

        self.batch_size = batch_size
        self.dict_reader = dict_reader

        # State tracking for iteration
        self._current_file_idx = 0
        self._current_file_obj = None
        self._csv_reader = None

    def __iter__(self) -> "CSVBatchIterator":
        """Demonstrates __iter__() in Python Iteration Protocol.

        When a for-loop starts, Python calls `iter(obj)`, which calls `obj.__iter__()`.
        We reset internal iteration pointers and open the first file lazily,
        returning `self` as the iterator object.
        """
        self._close_current_file()
        self._current_file_idx = 0
        self._open_next_file()
        return self

    def __next__(self) -> List[Union[Dict[str, Any], List[str]]]:
        """Demonstrates __next__() and StopIteration in Python Iteration Protocol.

        Called on each step of iteration to fetch the next batch of rows.
        Never loads the full file into memory; reads up to `batch_size` lines.

        Returns:
            List of rows (dicts or lists) up to length `batch_size`.

        Raises:
            StopIteration: When all CSV files and rows have been fully consumed.
        """
        batch = []

        while len(batch) < self.batch_size:
            if self._csv_reader is None:
                # No open file reader available; check if more files exist
                if not self._open_next_file():
                    break

            try:
                # Read the next single row from the CSV stream lazily
                row = next(self._csv_reader)
                batch.append(row)
            except StopIteration:
                # Reached end of current CSV file; close it and move to next file
                self._close_current_file()
                if not self._open_next_file():
                    break

        # If batch is empty, we have exhausted all data streams.
        # Raising StopIteration tells Python's iteration loop to terminate cleanly.
        if not batch:
            self._close_current_file()
            raise StopIteration

        return batch

    def _open_next_file(self) -> bool:
        """Helper to lazily open the next available CSV file in file_paths."""
        if self._current_file_idx >= len(self.file_paths):
            return False

        target_file = self.file_paths[self._current_file_idx]
        self._current_file_idx += 1

        self._current_file_obj = open(target_file, mode="r", encoding="utf-8", newline="")
        if self.dict_reader:
            self._csv_reader = csv.DictReader(self._current_file_obj)
        else:
            self._csv_reader = csv.reader(self._current_file_obj)

        return True

    def _close_current_file(self) -> None:
        """Helper to close the active file object and release memory/handles."""
        if self._current_file_obj is not None:
            try:
                self._current_file_obj.close()
            except Exception:
                pass
            self._current_file_obj = None
            self._csv_reader = None

    def close(self) -> None:
        """Clean up file handle explicitly."""
        self._close_current_file()

    def __enter__(self) -> "CSVBatchIterator":
        """Context manager entry."""
        return self.__iter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit ensures file streams are cleanly closed."""
        self.close()


def csv_batch_generator(
    path: Union[str, Path],
    batch_size: int = 100,
    dict_reader: bool = True,
) -> Generator[List[Union[Dict[str, Any], List[str]]], None, None]:
    """Lazy generator yielding CSV data batch-by-batch using the `yield` keyword.

    Demonstrates how Python generators work:
    - Calling this function returns a generator object without running code immediately.
    - Each call to next() executes until `yield batch` is hit.
    - State (file pointer, line count, active batch) is suspended until the next iteration.

    Args:
        path: Path to CSV file or directory of CSV files.
        batch_size: Number of rows per batch.
        dict_reader: Parse rows as dicts if True.

    Yields:
        List of CSV rows up to size `batch_size`.
    """
    input_path = Path(path)
    if not input_path.exists():
        raise DataValidationError(
            f"Data validation failed in csv_batch_generator: path '{input_path}' does not exist."
        )

    files = sorted(list(input_path.glob("*.csv"))) if input_path.is_dir() else [input_path]

    for target_file in files:
        with open(target_file, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f) if dict_reader else csv.reader(f)
            batch = []
            for row in reader:
                batch.append(row)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch


def load_csv_eager(
    path: Union[str, Path],
    dict_reader: bool = True,
) -> List[Union[Dict[str, Any], List[str]]]:
    """Eager loading function that reads an entire CSV file into memory as a list.

    WARNING: This keeps the entire dataset loaded in RAM simultaneously.
    Used as baseline comparison to contrast with lazy iterators/generators.

    Args:
        path: Path to CSV file or directory of CSV files.
        dict_reader: Parse rows as dicts if True.

    Returns:
        List containing ALL rows from the CSV file(s).
    """
    input_path = Path(path)
    if not input_path.exists():
        raise DataValidationError(
            f"Data validation failed in load_csv_eager: path '{input_path}' does not exist."
        )

    files = sorted(list(input_path.glob("*.csv"))) if input_path.is_dir() else [input_path]
    all_data = []

    for target_file in files:
        with open(target_file, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f) if dict_reader else csv.reader(f)
            all_data.extend(list(reader))

    return all_data


def islice_csv(
    path: Union[str, Path],
    start: int = 0,
    stop: Union[int, None] = 10,
    dict_reader: bool = True,
) -> List[Union[Dict[str, Any], List[str]]]:
    """Demonstrates `itertools.islice` for lazy slicing of CSV streams.

    Allows peeking or taking a slice of rows without loading the rest of the CSV.

    Args:
        path: CSV file path.
        start: Starting row index.
        stop: Ending row index (exclusive).
        dict_reader: Parse rows as dicts if True.

    Returns:
        List of selected CSV rows.
    """
    input_path = Path(path)
    if not input_path.exists():
        raise DataValidationError(
            f"Data validation failed in islice_csv: path '{input_path}' does not exist."
        )
    with open(input_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f) if dict_reader else csv.reader(f)
        # itertools.islice consumes only the specified slice lazily
        sliced_items = itertools.islice(reader, start, stop)
        return list(sliced_items)


def chain_csv_files(
    file_paths: List[Union[str, Path]],
    dict_reader: bool = True,
) -> Generator[Union[Dict[str, Any], List[str]], None, None]:
    """Demonstrates `itertools.chain` concept to lazily join multiple CSV streams.

    Args:
        file_paths: List of CSV file paths.
        dict_reader: Parse rows as dicts if True.

    Yields:
        Individual CSV rows sequentially across all files without loading all files into memory.
    """
    def _file_row_generator(fp: Path):
        with open(fp, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f) if dict_reader else csv.reader(f)
            for row in reader:
                yield row

    generators = [_file_row_generator(Path(p)) for p in file_paths]
    # itertools.chain creates a single continuous iterator across all file generators
    for item in itertools.chain.from_iterable(generators):
        yield item
