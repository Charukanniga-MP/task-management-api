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