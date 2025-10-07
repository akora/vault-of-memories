"""
Contract tests for ConfigurationLoader and ConfigurationValidator
These tests MUST pass for any implementation.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.services.configuration_loader import ConfigurationLoaderImpl
from src.services.configuration_validator import ConfigurationValidatorImpl
from src.models.configuration import ValidationResult


@pytest.mark.contract
class TestConfigurationLoader:
    """Contract tests for ConfigurationLoader interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.loader = ConfigurationLoaderImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_from_file_valid_json(self):
        """Test loading valid JSON file."""
        config_data = {"key": "value", "number": 42}
        config_file = self.config_dir / "test.json"

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        result = self.loader.load_from_file(config_file)

        assert result == config_data

    def test_load_from_file_nonexistent(self):
        """Test loading from nonexistent file raises FileNotFoundError."""
        nonexistent_file = self.config_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            self.loader.load_from_file(nonexistent_file)

    def test_load_from_file_invalid_json(self):
        """Test loading invalid JSON raises ValueError."""
        config_file = self.config_dir / "invalid.json"

        with open(config_file, "w") as f:
            f.write("{ invalid json content }")

        with pytest.raises(ValueError):
            self.loader.load_from_file(config_file)

    def test_load_from_directory_multiple_files(self):
        """Test loading multiple configuration files from directory."""
        # Create multiple config files
        config1 = {"section1": {"key1": "value1"}}
        config2 = {"section2": {"key2": "value2"}}

        with open(self.config_dir / "config1.json", "w") as f:
            json.dump(config1, f)
        with open(self.config_dir / "config2.json", "w") as f:
            json.dump(config2, f)

        result = self.loader.load_from_directory(self.config_dir)

        assert "section1" in result
        assert "section2" in result
        assert result["section1"]["key1"] == "value1"
        assert result["section2"]["key2"] == "value2"

    def test_load_from_directory_nonexistent(self):
        """Test loading from nonexistent directory raises FileNotFoundError."""
        nonexistent_dir = Path(self.temp_dir) / "nonexistent"

        with pytest.raises(FileNotFoundError):
            self.loader.load_from_directory(nonexistent_dir)

    def test_get_supported_extensions(self):
        """Test getting supported file extensions."""
        extensions = self.loader.get_supported_extensions()

        assert isinstance(extensions, list)
        assert len(extensions) > 0
        assert ".json" in extensions

    def test_merge_configurations(self):
        """Test merging multiple configuration dictionaries."""
        config1 = {"a": 1, "b": {"x": 10}}
        config2 = {"b": {"y": 20}, "c": 3}
        config3 = {"b": {"x": 30}, "d": 4}

        result = self.loader.merge_configurations([config1, config2, config3])

        assert result["a"] == 1
        assert result["c"] == 3
        assert result["d"] == 4
        assert result["b"]["x"] == 30  # Latest override
        assert result["b"]["y"] == 20

    def test_merge_configurations_empty_list(self):
        """Test merging empty list returns empty dict."""
        result = self.loader.merge_configurations([])
        assert result == {}

    def test_load_from_directory_ignores_non_json_files(self):
        """Test that non-JSON files are ignored during directory loading."""
        # Create JSON config
        config_data = {"valid": "config"}
        with open(self.config_dir / "config.json", "w") as f:
            json.dump(config_data, f)

        # Create non-JSON file
        with open(self.config_dir / "readme.txt", "w") as f:
            f.write("This is not JSON")

        result = self.loader.load_from_directory(self.config_dir)

        assert "valid" in result
        assert result["valid"] == "config"


@pytest.mark.contract
class TestConfigurationValidator:
    """Contract tests for ConfigurationValidator interface."""

    def setup_method(self):
        """Set up test environment."""
        self.validator = ConfigurationValidatorImpl()

    def test_validate_valid_configuration(self):
        """Test validation of valid configuration."""
        valid_config = {
            "core": {
                "database": {"path": "test.db", "timeout": 30},
                "logging": {"level": "INFO", "file": "test.log"}
            },
            "filename_rules": {
                "default_pattern": "{date}-{checksum}",
                "patterns": {"image": "{date}-{device}-{checksum}"}
            }
        }

        result = self.validator.validate(valid_config)

        assert result == ValidationResult.VALID
        assert len(self.validator.get_validation_errors()) == 0

    def test_validate_invalid_configuration(self):
        """Test validation of invalid configuration."""
        invalid_config = {
            "core": {
                "database": {"timeout": "invalid_type"}  # Should be int
                # Missing required 'path' field
            }
        }

        result = self.validator.validate(invalid_config)

        assert result in [ValidationResult.INVALID, ValidationResult.WARNING]
        errors = self.validator.get_validation_errors()
        assert len(errors) > 0

    def test_validate_section_valid(self):
        """Test validation of valid configuration section."""
        valid_core = {
            "database": {"path": "test.db", "timeout": 30},
            "logging": {"level": "INFO", "file": "test.log"}
        }

        result = self.validator.validate_section("core", valid_core)

        assert result == ValidationResult.VALID

    def test_validate_section_invalid(self):
        """Test validation of invalid configuration section."""
        invalid_core = {
            "database": {"timeout": "invalid"}  # Wrong type, missing path
        }

        result = self.validator.validate_section("core", invalid_core)

        assert result in [ValidationResult.INVALID, ValidationResult.WARNING]

    def test_get_schema_for_section_core(self):
        """Test getting schema for core section."""
        schema = self.validator.get_schema_for_section("core")

        assert schema is not None
        assert isinstance(schema, dict)

    def test_get_schema_for_section_nonexistent(self):
        """Test getting schema for nonexistent section returns None."""
        schema = self.validator.get_schema_for_section("nonexistent")

        assert schema is None

    def test_is_required_section_core(self):
        """Test that core section is required."""
        assert self.validator.is_required_section("core") is True

    def test_is_required_section_optional(self):
        """Test that some sections are optional."""
        # manufacturer_mappings should be optional with defaults
        assert self.validator.is_required_section("manufacturer_mappings") is False

    def test_validation_errors_cleared_on_new_validation(self):
        """Test that validation errors are cleared on new validation."""
        # First validation with errors
        invalid_config = {"core": {"database": {}}}
        self.validator.validate(invalid_config)
        assert len(self.validator.get_validation_errors()) > 0

        # Second validation without errors
        valid_config = {
            "core": {
                "database": {"path": "test.db", "timeout": 30},
                "logging": {"level": "INFO", "file": "test.log"}
            }
        }
        result = self.validator.validate(valid_config)

        if result == ValidationResult.VALID:
            assert len(self.validator.get_validation_errors()) == 0
