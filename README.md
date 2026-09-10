# Task Management Analytics

A production-grade Python & Machine Learning repository foundation for Task Management Analytics. This repository provides a reproducible environment, standardized directory structure (`src/` layout), packaging configuration (`pyproject.toml`), and dependency pinning.

---

## 1. Project Domain & Overview

**Domain**: Task Management Analytics & Predictive Modeling  
**Objective**: Build predictive models and analytics pipelines for task completion estimation, priority classification, and developer productivity insights.

---

## 2. Repository Directory Structure

```text
task-management-api/
│
├── src/
│   └── task_analytics/
│       └── __init__.py          # Core package initialization
│
├── app/                         # Task Management REST API implementation
│
├── data/
│   ├── raw/                     # Immutable raw datasets (CSV, JSON, SQL dumps)
│   └── processed/               # Cleaned, transformed, & feature-engineered datasets
│
├── notebooks/                   # Jupyter notebooks for EDA and experimentation
├── configs/                     # Model hyperparameters and pipeline configuration files
├── scripts/                     # Executable scripts (data extraction, training, evaluation)
├── tests/                       # Automated test suite (unit and integration tests)
│
├── .gitignore                   # Comprehensive Python & ML git ignore file
├── README.md                    # Project documentation
├── pyproject.toml               # Packaging & build configuration (PEP 517/518)
└── requirements.txt             # Pinned dependency specification
```

### Directory Usage Guide
- **`data/raw/`**: Store initial raw dataset files. (Git ignored except `.gitkeep`).
- **`data/processed/`**: Store feature-engineered data ready for training. (Git ignored except `.gitkeep`).
- **`notebooks/`**: Store Jupyter notebooks (`.ipynb`) for exploratory analysis and prototyping.
- **`configs/`**: Store configuration files (YAML, JSON, TOML) for dataset paths and hyperparameter settings.
- **`scripts/`**: Executable CLI scripts for batch data loading, preprocessing, and model training.
- **`tests/`**: Unit tests verifying model components, data transformers, and API services.

---

## 3. Environment Architecture & Technical Concepts

### Why `venv` is Used
Python's built-in `venv` module creates lightweight, isolated virtual environments without requiring third-party tools or administrative privileges. It prevents package version collisions between global system Python and project-specific dependencies.

### What `Conda` Solves
`Conda` is a cross-language package and environment manager. Unlike `pip` (which manages Python packages), `Conda` handles system-level C/C++ libraries, CUDA GPU drivers, BLAS/LAPACK binaries, and non-Python dependencies commonly required in complex data science and deep learning stacks.

### What `Poetry` Solves
`Poetry` provides modern dependency management and packaging for Python. It automatically creates lockfiles (`poetry.lock`), resolves complex dependency graphs deterministically, and simplifies publishing packages to PyPI.

### Dependency Specification: Loose vs. Pinned vs. Lockfiles
- **Loose Versions** (`pandas>=2.0.0`): Specifies minimum constraints, allowing flexible package updates. However, it risks non-deterministic builds if upstream packages introduce breaking API changes.
- **Pinned Versions** (`pandas==2.2.3`): Locks exact versions for all primary dependencies, ensuring identical package installations across team environments.
- **Lockfiles** (`poetry.lock` / `requirements.lock`): Records exact version hashes for all primary and transitive (sub-dependency) packages for cryptographic environment reproducibility.

### Why Reproducibility Matters in ML Projects
Machine learning pipelines depend heavily on data processing libraries, numerical compute backends, and estimator implementations. Subtle version differences (e.g., changes in `scikit-learn` split algorithms or `pandas` indexing behavior) can alter model feature matrices, metrics, or inference predictions. Reproducible environments ensure identical experimental results across developer machines, CI/CD pipelines, and production deployments.

---

## 4. Environment Setup & Quickstart

### Prerequisites
- Python 3.10 or higher
- Git

### One-Line Setup Command

**Windows (PowerShell)**:
```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -e .
```

**Linux / macOS**:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -e .
```

*What this setup command does*:
1. Creates an isolated virtual environment (`venv`).
2. Activates the virtual environment.
3. Installs the project in editable mode (`pip install -e .`) along with all pinned core dependencies (`numpy==2.1.3`, `pandas==2.2.3`, `pydantic==2.10.4`, `scikit-learn==1.6.0`, `requests==2.32.3`).

---

## 5. Verification & Testing

### Verify Environment Installation
Confirm installed packages match pinned versions:
```bash
pip list
```

### Run Unit Test Suite
Execute all tests using Python's `unittest`:
```bash
python -m unittest discover tests
```

---

## 6. Pinned Dependency Matrix

| Dependency | Pinned Version | Purpose |
| :--- | :--- | :--- |
| `numpy` | `2.1.3` | High-performance numerical computations |
| `pandas` | `2.2.3` | Structured data manipulation & feature engineering |
| `pydantic` | `2.10.4` | Data structure validation & schemas |
| `scikit-learn` | `1.6.0` | Classical Machine Learning estimators & evaluation |
| `requests` | `2.32.3` | HTTP client for external API integration |

---

## 7. Day 2: Iterators, Generators & Memory-Efficient Data Handling

### Overview
Day 2 introduces memory-efficient data loading primitives required for large-scale Machine Learning and analytics pipelines. Rather than loading massive CSV datasets entirely into memory, we implement custom batch iterators and generator functions using Python's iteration protocol.

---

### Core Concepts

#### 1. Python Iteration Protocol
Python objects become iterable by implementing two magic methods:
- `__iter__()`: Returns the iterator object itself. Called when iteration starts (`iter(obj)` or `for item in obj:`).
- `__next__()`: Returns the next value or batch from the data stream.
- `StopIteration`: A built-in standard exception raised inside `__next__()` to signal that all items have been consumed, causing `for` loops to stop gracefully.

#### 2. Generators and the `yield` Keyword
A generator function produces a sequence of results lazily using `yield` instead of `return`. When called, a generator returns a generator object without running immediately. Execution pauses at each `yield`, preserving function local variables and execution state until the next item is requested.

#### 3. Eager vs. Lazy Evaluation
- **Eager Loading**: Reads the entire CSV file into a Python `list` at once ($O(N)$ memory complexity).
- **Lazy Loading**: Reads and processes data stream line-by-line or batch-by-batch ($O(\text{Batch Size})$ memory complexity).

#### 4. Why Memory Efficiency Matters in ML
Real-world machine learning datasets often exceed available system RAM (tens to hundreds of gigabytes). Eager loading leads to `MemoryError` crashes and high swap usage. Lazy batch iteration enables **out-of-core computing**, streaming mini-batches directly into feature processing pipelines and deep learning batch gradient descent steps without memory inflation.

---

### Running Sample Data Generation & Memory Profiling

#### Generate Sample Datasets (100, 1,000, 10,000 rows)
```bash
python scripts/generate_sample_data.py
```
*Creates CSV files under `data/raw/` (automatically excluded from Git by `.gitignore`).*

#### Run Memory Profiling Benchmark (`tracemalloc`)
```bash
python scripts/memory_test.py
```

---

### Empirical Memory Profiling Results

Measured using Python's standard `tracemalloc` library (`batch_size = 100`):

| Dataset Size (Rows) | Eager Peak Memory | Lazy Peak Memory | Memory Savings |
| :--- | :--- | :--- | :--- |
| **100** | 116.87 KB | 115.89 KB | **0.8%** |
| **1,000** | 810.62 KB | 196.07 KB | **75.8%** |
| **10,000** | 7,839.66 KB (~7.8 MB) | 207.97 KB (~0.2 MB) | **97.3%** |

#### Benchmark Conclusion
- **Eager Loading**: Peak memory grows linearly with dataset row count ($O(N)$).
- **Lazy Batch Iterator**: Peak memory remains virtually constant ($O(\text{Batch Size}) \approx 200 \text{ KB}$) across 100, 1,000, and 10,000 row datasets.