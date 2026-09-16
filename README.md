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

---

## 8. Day 3: OOP for Pipelines — Composition Over Inheritance

### Overview & Objective
Day 3 introduces modular Object-Oriented Design patterns for data processing pipelines. We implement a flexible data transformation pipeline using **Composition over Inheritance**, abstract base classes (`abc.ABC`), runtime step swapping, Python encapsulation, and clear guidelines on choosing between functions and classes.

---

### Core Concepts & Architecture

#### 1. Abstract Base Class (`Step`)
The `Step` class defines a strict contract using Python's standard `abc` module:
```python
from abc import ABC, abstractmethod

class Step(ABC):
    @abstractmethod
    def execute(self, data):
        pass
```
- Instantiating `Step` directly raises `TypeError`.
- Any concrete subclass must implement `execute(self, data)`.

#### 2. Interchangeable Concrete Steps
We implement 4 concrete processing steps following the `Step` interface:
- **`CleanDataStep`**: Removes `None` items, empty dictionaries, or records missing required keys.
- **`NormalizeDataStep`**: Normalizes string values (stripping whitespace, lowercasing).
- **`FilterDataStep`**: Filters data records matching specified field criteria or custom predicate functions.
- **`PriorityFilterStep`**: Filters tasks specifically matching a given priority level (`high`, `medium`, `low`).

#### 3. Pipeline Class (Composition)
The `Pipeline` class is **composed of** (contains) `Step` objects:
```python
class Pipeline:
    def __init__(self, steps: list[Step]):
        self.steps = list(steps)

    def run(self, data):
        for step in self.steps:
            data = step.execute(data)
        return data
```
- `Pipeline` does **not** inherit from concrete step classes.
- It receives step instances and processes data sequentially.

#### 4. Runtime Step Swapping
Because `Pipeline` relies on step composition rather than hardcoded inheritance, step objects can be replaced dynamically at runtime without modifying the `Pipeline` class definition:
```python
# Initial Pipeline
pipeline = Pipeline([CleanDataStep(), NormalizeDataStep(), FilterDataStep(field="status", value="in_progress")])
result1 = pipeline.run(data)

# Swap Step at Runtime (without changing Pipeline class)
pipeline.replace_step(2, PriorityFilterStep(priority="high"))
result2 = pipeline.run(data)
```

---

### Composition vs. Inheritance Guide

| Concept | Definition | Pipeline Application |
| :--- | :--- | :--- |
| **Inheritance** ("Is-a") | Subclass inherits properties/methods from parent class. | Used for `Step(ABC)` interface contract where every concrete step *is a* `Step`. |
| **Composition** ("Has-a") | Class contains references to objects of other classes to build functionality. | Used for `Pipeline` where a pipeline *has* multiple `Step` objects. |

#### Key Takeaways:
- **Why Composition for Pipelines?**: Steps can be reordered, added, or swapped dynamically at runtime without subclassing `Pipeline`.
- **Risks of Deep Inheritance**: Rigid hierarchies lead to the *fragile base class problem*, tight coupling, and difficulty modifying parent behavior without breaking downstream subclasses.
- **When Inheritance is Appropriate**: Defining shared abstract contracts or tightly coupled domain models with true "is-a" relationships.
- **When Composition is Appropriate**: Combining interchangeable behaviors, dynamic workflows, and assembling components with "has-a" relationships.

---

### Python Encapsulation Conventions

Python uses naming conventions rather than language-enforced access keywords (like `private`/`protected` in Java/C++):

```python
class EncapsulationDemo:
    def __init__(self, name: str, protected_val: str, private_val: str):
        self.name = name                 # Public: accessible anywhere
        self._protected_val = protected_val  # Protected: convention indicating internal use
        self.__private_val = private_val    # Private: compiler name-mangles to _EncapsulationDemo__private_val
```
- **Public (`name`)**: Accessible and modifiable anywhere.
- **Protected (`_name`)**: Signals to developers that the attribute is intended for internal package use.
- **Private (`__name`)**: Triggers Python's **name mangling** (prefixed with `_ClassName`), preventing accidental overrides in subclasses.

---

### Function vs. Class Guidelines

#### Standalone Function Example:
```python
def clean_text(text: str) -> str:
    return text.strip().lower()
```

#### Selection Rule of Thumb:
- **Use a Function**: When performing stateless data transformations where no internal state, configuration, or object identity is maintained.
- **Use a Class**: When encapsulating state, maintaining configuration, managing resources, or implementing polymorphic interfaces (such as `Step`).

---

### Running Demonstration & Tests

#### Run Day 3 Pipeline Demonstration Script
```bash
python scripts/pipeline_demo.py
```

#### Run Full Unit Test Suite (Including Day 1, Day 2, and Day 3 tests)
```bash
python -m unittest discover tests
```