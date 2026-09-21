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

---

## Day 4 — Type Hints & Pydantic for Configuration

Day 4 introduces robust configuration modeling using Python type hints, dataclasses, fixed-choice Enums, and Pydantic v2 runtime validation.

---

### 1. Python Type Hints

#### What are Type Hints?
Type hints (introduced in PEP 484) allow developers to annotate the expected data types of function arguments, return values, and class fields.

```python
from typing import Optional, Union, List, Dict, Generic, TypeVar

# Basic and generic containers
feature_columns: List[str] = ["completion_rate", "estimated_hours"]
options: Optional[Dict[str, Union[int, float, str]]] = {"lr": 0.001, "optimizer": "adam"}
```

#### Key Constructs
- **`Optional[T]`**: Indicates a value can be of type `T` or `None`.
- **`Union[X, Y]` / `X | Y`**: Indicates a value can be either type `X` or type `Y`.
- **`List[T]` / `Dict[K, V]`**: Generic collection type hints specifying element/key-value types.
- **`Generic[T]` & `TypeVar`**: Enables creating type-safe generic classes and reusable components.

#### Why Type Hints are Useful
1. **Self-Documenting Code**: Clear documentation for function callers and developers.
2. **IDE Autocompletion & Refactoring**: Enhances code navigation and autocomplete support.
3. **Static Analysis**: Enables static analysis tools like `mypy` to detect bugs before execution.

> [!IMPORTANT]
> **Type hints do NOT perform runtime validation by themselves.** In standard Python, passing an integer to a function expecting a string will not raise a runtime error unless explicit validation is performed.

---

### 2. Dataclass vs Pydantic

| Feature | Dataclass (`@dataclass`) | Pydantic (`BaseModel`) |
| :--- | :--- | :--- |
| **Primary Purpose** | Simple data storage & boilerplate reduction | Runtime data validation & schema enforcement |
| **Generated Boilerplate** | Automatically generates `__init__`, `__repr__`, `__eq__` | Automatically generates `__init__`, `__repr__`, serialization (`model_dump`) |
| **Runtime Validation** | ❌ None by default | ✅ Automatic type coercion & field validation |
| **Path & Range Checks** | ❌ Manual code needed in `__post_init__` | ✅ Built-in `@field_validator` & `Field()` constraints |
| **Best Used For** | Internal state structures, DTOs where input is trusted | API parameters, config loading, external JSON/YAML parsing |

#### Dataclass Example:
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SimplePipelineConfig:
    data_path: Path
    batch_size: int = 32
    mode: str = "train"

# Note: Dataclass permits invalid values like batch_size=-100 at runtime without error.
```

---

### 3. Pydantic Configuration Model & Enums

#### Fixed-Choice Enums
```python
from enum import Enum

class Device(str, Enum):
    CPU = "cpu"
    GPU = "gpu"

class PipelineMode(str, Enum):
    TRAIN = "train"
    INFERENCE = "inference"
    EVAL = "eval"
```

#### Pydantic v2 `PipelineConfig`
```python
from pathlib import Path
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, field_validator

class PipelineConfig(BaseModel):
    data_path: Path = Field(..., description="Path to input data directory or file.")
    batch_size: int = Field(default=32, description="Batch size (must be > 0).")
    feature_columns: List[str] = Field(default_factory=list)
    mode: PipelineMode = Field(default=PipelineMode.TRAIN)
    device: Device = Field(default=Device.CPU)
    threshold: float = Field(default=0.5, description="Threshold between 0.0 and 1.0.")
    options: Optional[Dict[str, Union[int, float, str]]] = None

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(f"batch_size must be greater than 0, got {value}")
        return value

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError(f"threshold must be between 0.0 and 1.0, got {value}")
        return value

    @field_validator("data_path")
    @classmethod
    def validate_data_path(cls, value: Path) -> Path:
        if not value.resolve().exists():
            raise ValueError(f"data_path must point to an existing path on disk: '{value}'")
        return value
```

---

### 4. Static Type Checking (`mypy`) vs Runtime Validation (`Pydantic`)

- **Python Type Hints**: Annotations describing expected types.
- **`mypy`**: Static analysis tool that inspects source code **before execution** to verify type consistency.
- **Pydantic**: Validates actual values **at runtime** when objects are instantiated, parsing strings/coercing types and raising `ValidationError` on bad input.

---

### 5. Running Day 4 Demo & Tests

#### Run Day 4 Configuration Demonstration Script
```bash
python scripts/config_demo.py
```

#### Run `mypy` Static Type Checker
```bash
python -m mypy src/task_analytics/config.py scripts/config_demo.py tests/test_config.py
```

#### Run Full Test Suite (Day 1–4)
```bash
python -m pytest -v
```

---

## 9. Day 5 — Decorators, Context Managers & Caching

Day 5 introduces modular Python mechanisms for managing cross-cutting concerns (logging, timing, exception retries, resource lifecycles, and caching) without polluting core business logic.

---

### 1. Python Decorators & `functools.wraps`

#### What is a Decorator?
A decorator is a function that takes another function as an argument, adds extra behavior (such as timing, logging, or authentication), and returns a modified wrapper function.

#### Why `functools.wraps` is Critical
When a function is wrapped by a decorator, its standard attributes (`__name__`, `__doc__`, `__module__`) are replaced by the wrapper function's metadata. 
`@functools.wraps(func)` copies the original function's metadata to the wrapper function, preserving docstrings and function names for debugging and documentation tools.

---

### 2. Custom Decorators: `@timeit` and Parameterized `@retry`

#### `@timeit` Decorator
Measures function execution duration using `time.perf_counter()` and logs the execution duration along with the function name:
```python
from functools import wraps
import time, logging

logger = logging.getLogger("task_analytics.decorators")

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"Function '{func.__name__}' executed in {duration:.6f} seconds.")
        return res
    return wrapper
```

#### Parameterized `@retry(max_attempts=N)`
A decorator that accepts arguments uses a three-tier function structure:
```text
retry(max_attempts=3)  --> Returns a Decorator function
   ↓
decorator(func)        --> Returns a Wrapper function
   ↓
wrapper(*args, **kwargs) --> Executes target function with retry loop
```

```python
def retry(max_attempts: int = 3):
    if max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts:
                        raise exc
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {exc}. Retrying...")
        return wrapper
    return decorator
```

---

### 3. Context Managers & Resource Safety

Context managers implement the `with` statement protocol to guarantee that setup and teardown actions (such as opening files or database connections) are executed predictably.

#### Class-Based (`__enter__` and `__exit__`)
```python
class TaskResourceManager:
    def __init__(self, resource_name: str):
        self.resource_name = resource_name

    def __enter__(self):
        logger.info(f"Acquired resource: {self.resource_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"Cleaned up resource: {self.resource_name}")
        return False  # Do not swallow exceptions
```

#### Generator-Based (`@contextlib.contextmanager`)
```python
import contextlib

@contextlib.contextmanager
def managed_resource(resource_name: str):
    logger.info(f"Opened resource: {resource_name}")
    try:
        yield {"name": resource_name}
    finally:
        logger.info(f"Cleaned up resource: {resource_name}")
```

> **Cleanup Guarantee**: In both implementations, cleanup occurs in the `finally` block or `__exit__` method even if an exception is raised inside the `with` block!

---

### 4. Caching & `functools.lru_cache`

#### How `lru_cache` Works
`@lru_cache(maxsize=128)` caches function return values for specific argument combinations. Repeated calls with identical inputs return immediately without recalculation.
- `maxsize`: Upper bound on cached entries.
- `cache_clear()`: Resets the cache dictionary.

#### Caching Dangers & Mitigation
1. **Mutable Return Values**: Modifying a cached dictionary or list mutates the shared cache entry, affecting subsequent callers.
   - *Mitigation*: Return immutable types (`float`, `tuple`, `str`) or return copies.
2. **Unbounded Memory Growth**: Using `maxsize=None` can cause memory leaks if inputs are unbounded.
   - *Mitigation*: Always specify a reasonable `maxsize` (e.g. 128).
3. **Stale Data**: Cached outputs can become outdated if underlying data sources change.
   - *Mitigation*: Use `func.cache_clear()` when data updates.

---

### 5. Application to Actual Pipeline

All three Day 5 features are integrated directly into `Pipeline`:
- `@timeit` applied to `Pipeline.run(data)` to monitor total execution duration.
- `@retry(max_attempts=3)` applied to `Pipeline.load_data_source(fetcher_fn)` to recover from transient data read/fetch errors.
- `TaskResourceManager` applied to `Pipeline.run_with_resource(resource_name, data)` to guarantee data resource cleanup.

---

### 6. Running Day 5 Demo & Test Suite

#### Run Day 5 Demonstration Script
```bash
python scripts/day5_demo.py
```

#### Run Full Test Suite (Day 1–Day 5)
```bash
python -m pytest -v
```

---

## 9. Day 6 — Exception Hierarchies & Error Design

### 1. Python Exception Hierarchy & Custom Exceptions
In Python, all built-in exceptions inherit from `BaseException`, with standard application errors inheriting from `Exception`. Creating custom exceptions allows projects to define specific error categories that represent real failure modes in the application domain.

```text
Exception
└── PipelineError
    ├── ConfigError
    ├── DataValidationError
    └── ProcessingError
```

### 2. Project Exception Hierarchy
All project-specific exceptions derive from a single base class `PipelineError`:

- **`PipelineError(Exception)`**: Base exception for all pipeline and task analytics errors.
  - Catching `PipelineError` at the top level catches all project-specific errors without swallowing unrelated Python system exceptions (`KeyboardInterrupt`, `SystemExit`, `MemoryError`, `TypeError`).
- **`ConfigError(PipelineError)`**: Raised when configuration validation, instantiation, or loading fails (e.g. invalid `batch_size <= 0`, out-of-range `threshold`, or non-existent `data_path`).
- **`DataValidationError(PipelineError)`**: Raised when input data is missing, malformed, or fails type/schema validation (e.g. non-existent CSV files, negative batch sizes, or corrupt CSV rows).
- **`ProcessingError(PipelineError)`**: Raised when a pipeline step or transformation fails during execution (e.g. type conversion failures in `NormalizeDataStep`, invalid record structures in `CleanDataStep`).

### 3. Catching Base vs Specific Exceptions
- Catching `PipelineError` allows top-level entry points to catch **all** known project errors in a single handler:
  ```python
  try:
      run_pipeline()
  except PipelineError as error:
      print(f"Pipeline failed: {error}")
  ```
- Catching a specific subclass (`ConfigError`, `DataValidationError`, `ProcessingError`) allows precise, tailored recovery at intermediate layers:
  ```python
  try:
      config = validate_pipeline_config(config_dict)
  except ConfigError as err:
      logger.warning("Configuration invalid; loading fallback defaults...")
  ```

### 4. Error Message Design Principles
Every custom error message is designed to explain clearly to the user without needing to read the source code:
1. **WHAT failed**: High-level failure operation.
2. **WHERE it failed**: The exact component, class, or function name.
3. **WHY it failed**: The exact parameter, value, or condition that triggered the failure.

*Example*:
> `"Pipeline processing failed in NormalizeDataStep: cannot convert value 'abc' for field 'estimated_hours' to float."`

### 5. Exception Propagation & Layering Strategy
- **Low-Level Code**: Detects anomalies and raises specific custom exceptions (`ConfigError`, `DataValidationError`, `ProcessingError`).
- **Intermediate Code**: Lets exceptions propagate upward cleanly. Intermediate layers only catch exceptions they can actually handle or recover from.
- **Top-Level Code**: Catches `PipelineError`, logs/displays user-facing error messages cleanly without exposing raw Python tracebacks.

### 6. Exception Chaining (`raise ... from original_error`)
When catching a lower-level Python exception (e.g. `ValueError`) and re-raising a project-specific `ProcessingError`, exception chaining preserves the original cause via `__cause__`:

```python
try:
    value = float(raw_value)
except ValueError as original_error:
    raise ProcessingError(
        f"Pipeline processing failed in NormalizeDataStep: cannot convert value '{raw_value}' to float."
    ) from original_error
```

### 7. `try / except / else / finally` Semantics
- **`try`**: Contains code that may raise an exception.
- **`except`**: Catches and handles specific exception(s) if raised inside `try`.
- **`else`**: Executes **ONLY** when the `try` block completes successfully without raising any exception.
- **`finally`**: Executes **ALWAYS**, regardless of whether an exception occurred, was caught, or was re-raised. (Used for cleanup/resource release).

### 8. Dangers of Bare `except:` & Broad `except Exception:`
- Bare `except:` catches `BaseException`, including `KeyboardInterrupt` and `SystemExit`, preventing users from stopping scripts with Ctrl+C.
- Broad `except Exception:` catches all standard exceptions, including unexpected syntax bugs, `TypeError`, or `NameError`, hiding real programming bugs.
- Silently swallowing errors (`except Exception: pass`) leads to silent data corruption and makes debugging nearly impossible.
- **Best Practice**: Catch specific exceptions (`except ConfigError:`) or project base exceptions (`except PipelineError:`).

### 9. Running Day 6 Demo & Test Suite

#### Run Day 6 Demonstration Script
```bash
python scripts/day6_demo.py
```

#### Run Full Test Suite (Day 1–Day 6)
```bash
python -m pytest -v
```

---

## 10. Day 7 — Structured Logging & Production Debugging

### 1. Fundamentals of Python Logging
Logging is the systematic recording of events, diagnostics, operational state, and errors during application execution. Unlike simple output printing, standard Python logging (`import logging`) provides thread safety, log levels, output destinations (handlers), message formatting, and metadata contextualization.

- **Logger**: The application entry point (`logger = logging.getLogger(__name__)`). Loggers provide methods (`info()`, `debug()`, `warning()`, `error()`, `exception()`) to emit log records.
- **Handler**: Determines where log records are dispatched (e.g., `StreamHandler` for standard stdout/stderr, `FileHandler` for disk log files).
- **Formatter**: Defines the layout and layout formatting of log records into output text or structured JSON.

### 2. Standard Log Level Hierarchy
Python logging defines 5 standard severity levels used to categorize messages:

| Log Level | Numeric | Meaning & Typical Usage |
| :--- | :--- | :--- |
| **`DEBUG`** | 10 | Fine-grained internal info for developers (e.g., CSV batch yields, internal parameter values). |
| **`INFO`** | 20 | High-level operational milestones (e.g., pipeline start/completion, step start/completion). |
| **`WARNING`** | 30 | Recoverable or unexpected situations that don't halt execution (e.g., retrying a failed fetch). |
| **`ERROR`** | 40 | Failed operations or step failures that disrupt normal processing. |
| **`CRITICAL`** | 50 | Severe application-level failures requiring immediate intervention. |

### 3. Centralized Logging Configuration (`configure_logging`)
Centralized logging ensures that logging setup occurs **once** at the application entry point using `src/task_analytics/logging_config.py`.

```python
from task_analytics import configure_logging

# Configure logging centrally for production with file logging
logger = configure_logging(
    level="DEBUG",
    log_file="logs/day7_demo.log",
    env="production",
)
```

All other application modules simply instantiate module loggers:
```python
import logging
logger = logging.getLogger(__name__)
```
Module-level configuration calls (such as `logging.basicConfig()`) are strictly forbidden inside library code to prevent duplicate handlers or conflicting formats.

### 4. Structured / JSON Logging Architecture
Production systems ingest logs into centralized log indexing and monitoring platforms (e.g., Datadog, Elasticsearch, CloudWatch). Structured JSON format renders each log record as a single-line valid JSON object:

```json
{
  "timestamp": "2026-09-21T15:09:50.802494+00:00",
  "level": "INFO",
  "logger": "task_analytics.pipeline",
  "message": "Step completed: CleanDataStep",
  "module": "pipeline",
  "function": "run",
  "line": 322,
  "pipeline_step": "CleanDataStep",
  "duration": 0.000368,
  "records_processed": 1
}
```

Key attributes in structured log records:
- Core Metadata: `timestamp`, `level`, `logger`, `message`, `module`, `function`, `line`.
- Contextual Extras: `pipeline_step`, `duration`, `records_processed`, `files_processed`, `run_id`.
- Exception Extras: `error_type`, `error_message`, `traceback`.

### 5. Development vs. Production Logging
- **Development Mode (`env="development"`)**: Human-readable formatted console text output (`TextFormatter`) for quick visual debugging.
- **Production Mode (`env="production"`)**: Single-line structured JSON records (`JSONFormatter`) with disk file persistence (`logs/day7_demo.log`).

### 6. Why `print()` is Inappropriate for Production Pipelines
1. **No Severity Levels**: `print()` cannot distinguish between informational messages and critical crashes.
2. **No Destination Routing**: `print()` writes only to standard output (`sys.stdout`) without built-in support for log files or rotation.
3. **Missing Metadata**: `print()` lacks automated timestamps, logger names, module names, line numbers, or execution contexts.
4. **Not Machine-Readable**: Unstructured text from `print()` cannot be parsed cleanly by log aggregators.
5. **Thread Safety**: `print()` is not guaranteed to be thread-safe in multi-threaded environments.

### 7. Exception Tracebacks with `logger.exception()`
When handling errors, calling `logger.error(str(e))` loses the stack traceback!
`logger.exception("Message")` or `logger.error("Message", exc_info=True)` automatically captures the full stack trace and exception cause chain:

```python
try:
    pipeline.run(invalid_data)
except PipelineError as exc:
    logger.exception("Caught pipeline processing failure: %s", exc)
```

In `JSONFormatter`, tracebacks are formatted cleanly into the `"traceback"` field of the JSON log entry, enabling complete offline failure diagnosis without rerunning the code.

### 8. Pipeline & Data Iterator Instrumentation
- **`Pipeline.run()`**: Logs execution start (`INFO`), step start (`INFO`), step completion (`INFO`) with step duration and processed record count, and step failure (`ERROR`) with full `exc_info` traceback.
- **`CSVBatchIterator`**: Logs CSV file opens (`INFO`), file completions (`INFO`), and batch yields (`DEBUG`).
- **`@timeit` / `@retry`**: Log function duration and attempt retries using structured extras (`function`, `duration`, `attempt`).

### 9. Running Day 7 Demo & Test Suite

#### Run Day 7 Demonstration Script
```bash
python scripts/day7_demo.py
```
This executes two deterministic runs:
1. **RUN 1 (SUCCESSFUL RUN)**: Processes valid tasks and logs step/duration/record metrics.
2. **RUN 2 (DELIBERATELY FAILED RUN)**: Intentionally triggers a `ProcessingError` in `NormalizeDataStep`, catching `PipelineError` at top level and saving the full traceback to `logs/day7_demo.log`.

#### Inspect Generated Log File
The demonstration log file is saved to:
`logs/day7_demo.log`

#### Run Full Test Suite (Day 1–Day 7)
```bash
python -m pytest -v
```
or
```bash
python -m unittest discover -s tests -v
```