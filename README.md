# Task Management API

A modular Python-based task management application developed during internship, featuring advanced Python patterns, object-oriented design, logging, profiling, and unit testing.

---

## Project Structure

- `app/` - Main application code
  - `models/` - Domain entities (`User`, `Task`)
  - `schemas/` - Pydantic data contract & validation schemas (`UserSchema`, `TaskSchema`)
  - `services/` - Core business logic and custom iterators (`UserService`, `TaskService`)
  - `utils/` - Shared utilities:
    - `logger.py` - Centralized standard library logging
    - `decorators.py` - Action timing and execution logging decorators (`@log_action`)
    - `context_managers.py` - Block execution timer (`OperationTimer`)
    - `exceptions.py` - Custom exception hierarchy (`UserNotFoundError`, `TaskNotFoundError`, `ValidationError`, etc.)
    - `validation.py` - Schema validation helpers
    - `helpers.py` - ID generation helper
  - `main.py` - Application entry point
- `scripts/` - Utilities and performance profiling (`profile_app.py`)
- `tests/` - Comprehensive unit test suite (`unittest`)

---

## Setup & Running

1. **Activate Virtual Environment**:
   ```bash
   venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Application**:
   ```bash
   python -m app.main
   ```

---

## Advanced Python Features Implemented

1. **Iterators**:
   `UserService` and `TaskService` implement Python's iterator protocol (`__iter__` and `__next__`) via `UserIterator` and `TaskIterator`, allowing direct iteration over services:
   ```python
   for task in task_service:
       print(task)
   ```

2. **Type Hints & Pydantic**:
   - Comprehensive Python type hints applied across all parameters, return types, and class attributes.
   - `UserSchema` and `TaskSchema` inherit from `pydantic.BaseModel` for validation of required fields, email format, status, and priority values.

3. **Decorators & Context Managers**:
   - `@log_action`: Custom decorator measuring method execution time, logging call parameters, and capturing errors.
   - `OperationTimer`: Context manager measuring and logging execution duration of code blocks.

4. **Exceptions**:
   Replaced error string returns with custom exception hierarchy extending `TaskManagementError`:
   - `UserNotFoundError`
   - `TaskNotFoundError`
   - `ValidationError`
   - `InvalidStatusError`
   - `InvalidPriorityError`

5. **Logging**:
   Centralized logging configured in `app/utils/logger.py` using Python's built-in `logging` module. All application events use appropriate log levels (`INFO`, `WARNING`, `ERROR`, `DEBUG`) instead of `print()`.

6. **SOLID Refactor**:
   - **Single Responsibility Principle (SRP)**: Models store data state, Schemas enforce contracts, Services execute business operations, Utils isolate cross-cutting concerns.
   - **Open/Closed Principle (OCP)**: Decorators extend service functionality without altering inner core logic; custom exceptions extend base classes cleanly.
   - **Liskov Substitution Principle (LSP)**: All specialized exception types (`UserNotFoundError`, `ValidationError`) safely substitute for `TaskManagementError`.
   - **Interface Segregation Principle (ISP)**: Modular utils and interfaces contain only focused, relevant functions.
   - **Dependency Inversion Principle (DIP)**: Services depend on abstract validation helpers and schemas rather than hardcoded logic.

7. **Profiling & Debugging**:
   - Run performance profiling via `cProfile`:
     ```bash
     python scripts/profile_app.py
     ```
   - **Debugging in VS Code / Antigravity**:
     Run or debug `app/main.py` directly using Python Debugger (F5 or Debug File configuration).

---

## Testing

Run all unit tests using Python's `unittest`:

```bash
python -m unittest discover tests
```