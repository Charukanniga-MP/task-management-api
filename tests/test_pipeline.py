"""Unit test suite for task_analytics.pipeline module (Day 3).

Tests abstract Step ABC, concrete steps, Pipeline execution, runtime step swapping,
encapsulation conventions, and standalone helper functions.
"""

import unittest
from abc import ABC

from task_analytics import (
    CleanDataStep,
    EncapsulationDemo,
    FilterDataStep,
    NormalizeDataStep,
    Pipeline,
    PriorityFilterStep,
    Step,
    clean_text,
)


class DummyStep(Step):
    """Concrete dummy step for testing purposes."""

    def __init__(self, prefix: str = "test"):
        self.prefix = prefix

    def execute(self, data: str) -> str:
        return f"{self.prefix}:{data}"


class TestStepAbstractClass(unittest.TestCase):
    """Tests for the abstract Step base class and interface enforcement."""

    def test_cannot_instantiate_step_directly(self):
        """Verifies that Step cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            Step()  # type: ignore

    def test_subclass_without_execute_raises_error(self):
        """Verifies that a subclass missing execute() cannot be instantiated."""
        class IncompleteStep(Step):
            pass

        with self.assertRaises(TypeError):
            IncompleteStep()  # type: ignore

    def test_valid_subclass_instantiates(self):
        """Verifies that a valid Step subclass can be instantiated and executed."""
        step = DummyStep()
        self.assertIsInstance(step, Step)
        self.assertEqual(step.execute("hello"), "test:hello")


class TestConcreteSteps(unittest.TestCase):
    """Tests for CleanDataStep, NormalizeDataStep, FilterDataStep, and PriorityFilterStep."""

    def test_clean_data_step_list(self):
        """Verifies CleanDataStep removes None, empty dicts, and invalid records."""
        step = CleanDataStep(required_keys=["title"])
        raw_data = [
            {"title": "Task 1", "status": "open"},
            None,
            {},
            {"title": "", "status": "open"},
            {"title": "Task 2"},
            "   valid string   ",
        ]
        result = step.execute(raw_data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {"title": "Task 1", "status": "open"})
        self.assertEqual(result[1], {"title": "Task 2"})
        self.assertEqual(result[2], "valid string")

    def test_clean_data_step_dict(self):
        """Verifies CleanDataStep cleans single dictionary attributes."""
        step = CleanDataStep()
        data = {"title": "Task 1", "desc": None, "priority": "high"}
        result = step.execute(data)
        self.assertEqual(result, {"title": "Task 1", "priority": "high"})

    def test_normalize_data_step(self):
        """Verifies NormalizeDataStep lowercases and trims targeted string fields."""
        step = NormalizeDataStep(target_fields=["status", "priority"])
        data = [
            {"title": " Fix Bug ", "status": " IN_PROGRESS ", "priority": " HIGH "},
            {"title": " Write Docs ", "status": " COMPLETED ", "priority": " LOW "},
        ]
        result = step.execute(data)
        self.assertEqual(result[0]["status"], "in_progress")
        self.assertEqual(result[0]["priority"], "high")
        self.assertEqual(result[0]["title"], " Fix Bug ")  # Not in target_fields

    def test_normalize_data_step_all_fields(self):
        """Verifies NormalizeDataStep normalizes all fields when target_fields is None."""
        step = NormalizeDataStep(target_fields=None)
        data = {"title": " Fix Bug ", "status": " IN_PROGRESS "}
        result = step.execute(data)
        self.assertEqual(result["title"], "fix bug")
        self.assertEqual(result["status"], "in_progress")

    def test_filter_data_step_field_value(self):
        """Verifies FilterDataStep filters by key-value equality."""
        step = FilterDataStep(field="status", value="completed")
        data = [
            {"title": "Task 1", "status": "completed"},
            {"title": "Task 2", "status": "in_progress"},
            {"title": "Task 3", "status": "completed"},
        ]
        result = step.execute(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Task 1")
        self.assertEqual(result[1]["title"], "Task 3")

    def test_filter_data_step_predicate(self):
        """Verifies FilterDataStep filters by custom predicate function."""
        step = FilterDataStep(predicate=lambda x: isinstance(x, dict) and x.get("score", 0) > 50)
        data = [
            {"name": "A", "score": 80},
            {"name": "B", "score": 30},
            {"name": "C", "score": 90},
        ]
        result = step.execute(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "A")
        self.assertEqual(result[1]["name"], "C")

    def test_priority_filter_step(self):
        """Verifies PriorityFilterStep filters tasks by priority level."""
        step = PriorityFilterStep(priority="HIGH")
        data = [
            {"title": "T1", "priority": "high"},
            {"title": "T2", "priority": "medium"},
            {"title": "T3", "priority": " HIGH "},
        ]
        result = step.execute(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "T1")
        self.assertEqual(result[1]["title"], "T3")


class TestPipeline(unittest.TestCase):
    """Tests for Pipeline composition, execution, and runtime swapping."""

    def test_pipeline_initialization_and_validation(self):
        """Verifies pipeline rejects non-Step objects on initialization."""
        with self.assertRaises(TypeError):
            Pipeline([DummyStep(), "invalid_step"])  # type: ignore

    def test_pipeline_sequential_execution(self):
        """Verifies pipeline runs steps sequentially in order."""
        step1 = DummyStep("s1")
        step2 = DummyStep("s2")
        pipeline = Pipeline([step1, step2])
        self.assertEqual(pipeline.run("init"), "s2:s1:init")

    def test_pipeline_add_step(self):
        """Verifies add_step appends steps and supports method chaining."""
        pipeline = Pipeline()
        pipeline.add_step(DummyStep("a")).add_step(DummyStep("b"))
        self.assertEqual(len(pipeline.steps), 2)
        self.assertEqual(pipeline.run("start"), "b:a:start")

        with self.assertRaises(TypeError):
            pipeline.add_step("not_a_step")  # type: ignore

    def test_runtime_step_swapping(self):
        """Verifies replacing a step at runtime alters pipeline output without changing Pipeline class."""
        data = [
            {"title": "Task 1", "status": "in_progress", "priority": "high"},
            {"title": "Task 2", "status": "completed", "priority": "high"},
            {"title": "Task 3", "status": "in_progress", "priority": "low"},
        ]

        # Initial pipeline: Clean -> Normalize -> Filter by status=='in_progress'
        pipeline = Pipeline([
            CleanDataStep(),
            NormalizeDataStep(target_fields=["status", "priority"]),
            FilterDataStep(field="status", value="in_progress"),
        ])
        result1 = pipeline.run(data)
        self.assertEqual(len(result1), 2)
        self.assertEqual(result1[0]["title"], "Task 1")
        self.assertEqual(result1[1]["title"], "Task 3")

        # SWAP STEP AT RUNTIME: Replace FilterDataStep with PriorityFilterStep(priority="high")
        pipeline.replace_step(2, PriorityFilterStep(priority="high"))
        result2 = pipeline.run(data)

        # Output changes dynamically
        self.assertEqual(len(result2), 2)
        self.assertEqual(result2[0]["title"], "Task 1")
        self.assertEqual(result2[1]["title"], "Task 2")

    def test_replace_step_invalid_index_or_type(self):
        """Verifies replace_step raises appropriate exceptions for out-of-bounds or invalid step."""
        pipeline = Pipeline([DummyStep("a")])
        with self.assertRaises(IndexError):
            pipeline.replace_step(5, DummyStep("b"))
        with self.assertRaises(TypeError):
            pipeline.replace_step(0, "not_a_step")  # type: ignore

    def test_pipeline_repr(self):
        """Verifies Pipeline string representation."""
        pipeline = Pipeline([CleanDataStep(), NormalizeDataStep()])
        self.assertEqual(repr(pipeline), "Pipeline(steps=['CleanDataStep', 'NormalizeDataStep'])")


class TestEncapsulationAndFunctions(unittest.TestCase):
    """Tests EncapsulationDemo and clean_text helper function."""

    def test_encapsulation_demo(self):
        """Verifies public, protected, and private attribute access and mangling."""
        demo = EncapsulationDemo(name="Pub", protected_val="Prot", private_val="Priv")
        self.assertEqual(demo.name, "Pub")
        self.assertEqual(demo._protected_val, "Prot")
        self.assertEqual(demo.get_private_val(), "Priv")

        # Direct access to private attribute raises AttributeError
        with self.assertRaises(AttributeError):
            _ = demo.__private_val  # type: ignore

        # Accessing via name mangling works
        mangled_attr = "_EncapsulationDemo__private_val"
        self.assertEqual(getattr(demo, mangled_attr), "Priv")

        # Setter updates private attribute
        demo.set_private_val("NewPriv")
        self.assertEqual(demo.get_private_val(), "NewPriv")

        with self.assertRaises(ValueError):
            demo.set_private_val("")

    def test_clean_text_function(self):
        """Verifies clean_text standalone helper function."""
        self.assertEqual(clean_text("   Hello World  "), "hello world")
        with self.assertRaises(TypeError):
            clean_text(123)  # type: ignore


if __name__ == "__main__":
    unittest.main()
