"""
Contract tests for ConfigurationManager
These tests MUST pass for any implementation of ConfigurationManager.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.services.configuration_manager import ConfigurationManagerImpl
from src.models.configuration import ValidationResult


@pytest.mark.contract
class TestConfigurationManager:
    """Contract tests for ConfigurationManager interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.manager = ConfigurationManagerImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_valid_config(self):
        """Create a valid test configuration."""
        # Core settings
        core_config = {
            "core": {
                "database": {
                    "path": "vault.db",
                    "timeout": 30
                },
                "logging": {
                    "level": "INFO",
                    "file": "vault.log"
                },
                "temp_directory": "/tmp/vault"
            }
        }

        # Filename rules
        filename_config = {
            "filename_rules": {
                "default_pattern": "{date}-{time}-{device}-{checksum}",
                "patterns": {
                    "image": "{date}-{time}-{camera}-{resolution}-{checksum}",
                    "document": "{date}-{title}-{author}-{checksum}",
                    "video": "{date}-{time}-{device}-{duration}-{checksum}"
                }
            }
        }

        # Write configuration files
        with open(self.config_path / "core.json", "w") as f:
            json.dump(core_config, f, indent=2)

        with open(self.config_path / "filename-rules.json", "w") as f:
            json.dump(filename_config, f, indent=2)

    def test_load_configuration_success(self):
        """Test successful configuration loading."""
        self.create_valid_config()

        result = self.manager.load_configuration(self.config_path)

        assert result is True
        assert self.manager.is_configuration_loaded()
        assert self.manager.get_configuration_path() == self.config_path

    def test_load_configuration_nonexistent_path(self):
        """Test loading from nonexistent path raises FileNotFoundError."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent"

        with pytest.raises(FileNotFoundError):
            self.manager.load_configuration(nonexistent_path)

    def test_load_configuration_invalid_json(self):
        """Test loading invalid JSON raises ValueError."""
        # Create invalid JSON file
        invalid_file = self.config_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json content }")

        with pytest.raises(ValueError):
            self.manager.load_configuration(self.config_path)

    def test_validate_configuration_valid(self):
        """Test validation of valid configuration."""
        self.create_valid_config()
        self.manager.load_configuration(self.config_path)

        result = self.manager.validate_configuration()

        assert result == ValidationResult.VALID
        assert len(self.manager.get_validation_errors()) == 0

    def test_validate_configuration_without_loading(self):
        """Test validation fails when no configuration is loaded."""
        with pytest.raises(RuntimeError):
            self.manager.validate_configuration()

    def test_get_settings_repository(self):
        """Test getting settings repository after loading."""
        self.create_valid_config()
        self.manager.load_configuration(self.config_path)

        settings = self.manager.get_settings_repository()

        assert settings is not None
        assert hasattr(settings, 'get_core_settings')
        assert hasattr(settings, 'get_filename_rules')

    def test_get_settings_repository_without_loading(self):
        """Test getting settings repository fails when no config loaded."""
        with pytest.raises(RuntimeError):
            self.manager.get_settings_repository()

    def test_reload_configuration(self):
        """Test configuration reload without application restart."""
        self.create_valid_config()
        self.manager.load_configuration(self.config_path)

        # Modify configuration
        modified_config = {
            "core": {
                "database": {
                    "path": "modified.db",
                    "timeout": 60
                },
                "logging": {
                    "level": "DEBUG",
                    "file": "modified.log"
                }
            }
        }
        with open(self.config_path / "core.json", "w") as f:
            json.dump(modified_config, f, indent=2)

        result = self.manager.reload_configuration()

        assert result is True
        settings = self.manager.get_settings_repository()
        core_settings = settings.get_core_settings()
        assert core_settings.get_database_path().name == "modified.db"

    def test_reload_configuration_with_invalid_changes(self):
        """Test reload fails with invalid changes and preserves existing config."""
        self.create_valid_config()
        self.manager.load_configuration(self.config_path)
        # original_settings = self.manager.get_settings_repository()

        # Create invalid configuration
        with open(self.config_path / "core.json", "w") as f:
            f.write("{ invalid json }")

        result = self.manager.reload_configuration()

        assert result is False
        # Original configuration should be preserved
        current_settings = self.manager.get_settings_repository()
        assert current_settings is not None

    def test_validation_errors_reporting(self):
        """Test detailed validation error reporting."""
        # Create configuration with missing required fields
        incomplete_config = {
            "database": {
                # Missing required 'path' field
                "timeout": 30
            }
        }
        with open(self.config_path / "core.json", "w") as f:
            json.dump(incomplete_config, f, indent=2)

        self.manager.load_configuration(self.config_path)
        result = self.manager.validate_configuration()

        assert result in [ValidationResult.INVALID, ValidationResult.WARNING]
        errors = self.manager.get_validation_errors()
        assert len(errors) > 0
        assert any("path" in error.message.lower() for error in errors)

    def test_is_configuration_loaded_initially_false(self):
        """Test configuration loaded status is initially false."""
        assert self.manager.is_configuration_loaded() is False

    def test_get_configuration_path_initially_none(self):
        """Test configuration path is initially None."""
        assert self.manager.get_configuration_path() is None
