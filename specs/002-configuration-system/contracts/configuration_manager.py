"""
Configuration Manager Interface Contract
Defines the contract for central configuration coordination.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from enum import Enum


class ValidationResult(Enum):
    """Configuration validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class ValidationError:
    """Represents a configuration validation error."""

    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.path} - {self.message}"


class ConfigurationManager(ABC):
    """
    Contract for central configuration management.

    Responsibilities:
    - Load configuration from hierarchical JSON files
    - Validate configuration integrity
    - Provide centralized access to settings
    - Support configuration updates without restart
    - Handle errors and provide clear feedback
    """

    @abstractmethod
    def load_configuration(self, config_path: Path) -> bool:
        """
        Load configuration from the specified path.

        Args:
            config_path: Path to the configuration directory or file

        Returns:
            True if configuration loaded successfully, False otherwise

        Raises:
            FileNotFoundError: If configuration path doesn't exist
            PermissionError: If configuration files cannot be read
            ValueError: If configuration files are malformed
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> ValidationResult:
        """
        Validate the currently loaded configuration.

        Returns:
            ValidationResult indicating success, failure, or warnings

        Requires:
            Configuration must be loaded first
        """
        pass

    @abstractmethod
    def get_settings_repository(self) -> 'SettingsRepository':
        """
        Get the central settings repository.

        Returns:
            SettingsRepository instance for accessing configuration values

        Requires:
            Configuration must be loaded and validated first
        """
        pass

    @abstractmethod
    def reload_configuration(self) -> bool:
        """
        Reload configuration without application restart.

        Returns:
            True if reload successful, False otherwise

        Note:
            Must preserve existing configuration if reload fails
        """
        pass

    @abstractmethod
    def get_validation_errors(self) -> List[ValidationError]:
        """
        Get detailed validation errors from last validation attempt.

        Returns:
            List of ValidationError objects describing any issues
        """
        pass

    @abstractmethod
    def is_configuration_loaded(self) -> bool:
        """
        Check if configuration is currently loaded.

        Returns:
            True if configuration is loaded, False otherwise
        """
        pass

    @abstractmethod
    def get_configuration_path(self) -> Optional[Path]:
        """
        Get the path to the currently loaded configuration.

        Returns:
            Path to configuration directory, or None if not loaded
        """
        pass


class SettingsRepository(ABC):
    """
    Contract for centralized configuration value access.

    Responsibilities:
    - Provide type-safe access to all configuration values
    - Handle default values when settings are missing
    - Support different configuration categories
    - Ensure thread-safe access
    """

    @abstractmethod
    def get_filename_rules(self) -> 'FilenameRules':
        """Get filename generation rules configuration."""
        pass

    @abstractmethod
    def get_classification_rules(self) -> 'ClassificationRules':
        """Get file classification rules configuration."""
        pass

    @abstractmethod
    def get_processing_rules(self) -> 'ProcessingRules':
        """Get file processing rules configuration."""
        pass

    @abstractmethod
    def get_manufacturer_mappings(self) -> 'ManufacturerMappings':
        """Get device manufacturer mappings configuration."""
        pass

    @abstractmethod
    def get_core_settings(self) -> 'CoreSettings':
        """Get core application settings."""
        pass

    @abstractmethod
    def get_setting(self, path: str, default=None):
        """
        Get a specific setting by path.

        Args:
            path: Dot-separated path to setting (e.g., "core.database.path")
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        pass


# Configuration data classes (contracts for specific configuration types)

class FilenameRules(ABC):
    """Contract for filename generation rules."""

    @abstractmethod
    def get_pattern_for_type(self, file_type: str) -> Optional[str]:
        """Get filename pattern for specific file type."""
        pass

    @abstractmethod
    def get_default_pattern(self) -> str:
        """Get default filename pattern."""
        pass


class ClassificationRules(ABC):
    """Contract for file classification rules."""

    @abstractmethod
    def classify_file(self, file_path: Path, file_type: str) -> str:
        """Classify file into appropriate category."""
        pass

    @abstractmethod
    def get_category_folder(self, category: str) -> str:
        """Get folder name for file category."""
        pass


class ProcessingRules(ABC):
    """Contract for file processing rules."""

    @abstractmethod
    def get_processor_for_type(self, file_type: str) -> Optional[str]:
        """Get processor class name for file type."""
        pass

    @abstractmethod
    def should_extract_metadata(self, file_type: str) -> bool:
        """Check if metadata extraction is enabled for file type."""
        pass


class ManufacturerMappings(ABC):
    """Contract for device manufacturer mappings."""

    @abstractmethod
    def identify_manufacturer(self, metadata: dict) -> Optional[str]:
        """Identify manufacturer from file metadata."""
        pass

    @abstractmethod
    def get_device_model(self, manufacturer: str, model_id: str) -> Optional[str]:
        """Get full device model name."""
        pass


class CoreSettings(ABC):
    """Contract for core application settings."""

    @abstractmethod
    def get_database_path(self) -> Path:
        """Get database file path."""
        pass

    @abstractmethod
    def get_log_level(self) -> str:
        """Get logging level."""
        pass

    @abstractmethod
    def get_temp_directory(self) -> Path:
        """Get temporary files directory."""
        pass