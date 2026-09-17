"""Unit tests for task_analytics.config module (Day 4).

Tests:
- Dataclass auto-generated methods (__init__, __repr__, __eq__) and lack of runtime validation
- Generic container usage
- Pydantic PipelineConfig valid initialization and default value assignments
- Pydantic validation errors for:
  - Wrong type for numeric fields
  - Out of range batch_size (<= 0)
  - Out of range threshold (< 0 or > 1)
  - Invalid Enum choices
  - Missing required field (data_path)
  - Non-existent data_path
"""

from pathlib import Path
import unittest

from pydantic import ValidationError

from task_analytics.config import (
    Device,
    GenericConfigContainer,
    PipelineConfig,
    PipelineMode,
    SimplePipelineConfig,
)


class TestSimplePipelineConfigDataclass(unittest.TestCase):
    """Tests for the SimplePipelineConfig dataclass example."""

    def test_dataclass_auto_methods(self):
        """Verifies __init__, __repr__, and __eq__ work on dataclass."""
        path = Path("data")
        config1 = SimplePipelineConfig(data_path=path, batch_size=32, mode="train")
        config2 = SimplePipelineConfig(data_path=path, batch_size=32, mode="train")
        config3 = SimplePipelineConfig(data_path=path, batch_size=64, mode="train")

        # __repr__ check
        self.assertIn("SimplePipelineConfig", repr(config1))
        self.assertIn("batch_size=32", repr(config1))

        # __eq__ equality check
        self.assertEqual(config1, config2)
        self.assertNotEqual(config1, config3)

    def test_dataclass_does_not_validate_types_or_values(self):
        """Verifies dataclass does not raise validation errors for bad input."""
        # Dataclass allows invalid batch size and non-existent path without raising errors
        bad_config = SimplePipelineConfig(
            data_path=Path("non_existent_dir_12345"),
            batch_size=-999,
            mode="invalid_mode",
        )
        self.assertEqual(bad_config.batch_size, -999)


class TestGenericConfigContainer(unittest.TestCase):
    """Tests for GenericConfigContainer type hint example."""

    def test_generic_container(self):
        """Verifies GenericConfigContainer stores typed items correctly."""
        container = GenericConfigContainer[str](item="test_item", metadata={"key": "val"})
        self.assertEqual(container.get_item(), "test_item")
        self.assertEqual(container.metadata, {"key": "val"})


class TestPipelineConfigValidation(unittest.TestCase):
    """Tests for Pydantic PipelineConfig validation and default values."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_data_path = Path("data")

    def test_valid_configuration_defaults(self):
        """Verifies instantiation with valid data_path uses correct defaults."""
        config = PipelineConfig(data_path=self.valid_data_path)

        self.assertEqual(config.data_path, self.valid_data_path)
        self.assertEqual(config.batch_size, 32)
        self.assertEqual(config.feature_columns, [])
        self.assertEqual(config.mode, PipelineMode.TRAIN)
        self.assertEqual(config.device, Device.CPU)
        self.assertEqual(config.threshold, 0.5)
        self.assertIsNone(config.options)

    def test_valid_custom_configuration(self):
        """Verifies instantiation with valid custom field values."""
        config = PipelineConfig(
            data_path=self.valid_data_path,
            batch_size=128,
            feature_columns=["col1", "col2"],
            mode=PipelineMode.INFERENCE,
            device=Device.GPU,
            threshold=0.9,
            options={"lr": 0.001},
        )

        self.assertEqual(config.batch_size, 128)
        self.assertEqual(config.feature_columns, ["col1", "col2"])
        self.assertEqual(config.mode, PipelineMode.INFERENCE)
        self.assertEqual(config.device, Device.GPU)
        self.assertEqual(config.threshold, 0.9)

    def test_wrong_type_validation_error(self):
        """Verifies Pydantic raises ValidationError when given un-coercible wrong type."""
        with self.assertRaises(ValidationError) as ctx:
            PipelineConfig(
                data_path=self.valid_data_path,
                batch_size="invalid_not_an_int",
            )
        self.assertIn("batch_size", str(ctx.exception))

    def test_invalid_batch_size_zero_or_negative(self):
        """Verifies Pydantic raises ValidationError for batch_size <= 0."""
        with self.assertRaises(ValidationError) as ctx_zero:
            PipelineConfig(data_path=self.valid_data_path, batch_size=0)
        self.assertIn("batch_size must be greater than 0", str(ctx_zero.exception))

        with self.assertRaises(ValidationError) as ctx_neg:
            PipelineConfig(data_path=self.valid_data_path, batch_size=-10)
        self.assertIn("batch_size must be greater than 0", str(ctx_neg.exception))

    def test_invalid_threshold_out_of_range(self):
        """Verifies Pydantic raises ValidationError for threshold outside [0.0, 1.0]."""
        with self.assertRaises(ValidationError) as ctx_high:
            PipelineConfig(data_path=self.valid_data_path, threshold=1.5)
        self.assertIn("threshold must be between 0.0 and 1.0", str(ctx_high.exception))

        with self.assertRaises(ValidationError) as ctx_low:
            PipelineConfig(data_path=self.valid_data_path, threshold=-0.1)
        self.assertIn("threshold must be between 0.0 and 1.0", str(ctx_low.exception))

    def test_invalid_enum_value(self):
        """Verifies Pydantic raises ValidationError for invalid Enum choices."""
        with self.assertRaises(ValidationError) as ctx_mode:
            PipelineConfig(data_path=self.valid_data_path, mode="invalid_mode")  # type: ignore
        self.assertIn("mode", str(ctx_mode.exception))

        with self.assertRaises(ValidationError) as ctx_dev:
            PipelineConfig(data_path=self.valid_data_path, device="tpu")  # type: ignore
        self.assertIn("device", str(ctx_dev.exception))

    def test_missing_required_field_data_path(self):
        """Verifies Pydantic raises ValidationError when required field data_path is omitted."""
        with self.assertRaises(ValidationError) as ctx:
            PipelineConfig(batch_size=32)  # type: ignore
        self.assertIn("data_path", str(ctx.exception))

    def test_non_existent_data_path(self):
        """Verifies Pydantic raises ValidationError when data_path does not exist on disk."""
        non_existent_path = Path("non_existent_directory_abc_xyz_987")
        self.assertFalse(non_existent_path.exists())

        with self.assertRaises(ValidationError) as ctx:
            PipelineConfig(data_path=non_existent_path)

        self.assertIn("data_path must point to an existing path on disk", str(ctx.exception))
        # Ensure validator did not create missing directory
        self.assertFalse(non_existent_path.exists())


if __name__ == "__main__":
    unittest.main()
