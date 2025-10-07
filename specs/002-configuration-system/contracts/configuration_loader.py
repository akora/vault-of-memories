"""
Configuration Loader Interface Contract
Defines contracts for loading and validating configuration files.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from .configuration_manager import ValidationError, ValidationResult


class ConfigurationLoader(ABC):
    """
    Contract for loading configuration from JSON files.

    Responsibilities:
    - Parse JSON configuration files
    - Handle file system operations
    - Merge multiple configuration sources
    - Provide structured access to loaded data
    """

    @abstractmethod
    def load_from_directory(self, config_dir: Path) -> Dict[str, Any]:
        """
        Load all configuration files from a directory.

        Args:
            config_dir: Directory containing configuration files

        Returns:
            Dictionary containing merged configuration data

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If files cannot be read
            ValueError: If JSON files are malformed
        """
        pass

    @abstractmethod
    def load_from_file(self, config_file: Path) -> Dict[str, Any]:
        """
        Load configuration from a single file.

        Args:
            config_file: Path to JSON configuration file

        Returns:
            Dictionary containing configuration data

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            ValueError: If JSON is malformed
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported configuration file extensions.

        Returns:
            List of file extensions (e.g., ['.json', '.jsonc'])
        """
        pass

    @abstractmethod
    def merge_configurations(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Args:
            configs: List of configuration dictionaries to merge

        Returns:
            Single merged configuration dictionary

        Note:
            Later configurations override earlier ones for conflicting keys
        """
        pass


class ConfigurationValidator(ABC):
    """
    Contract for validating configuration data.

    Responsibilities:
    - Validate configuration against schema
    - Check data integrity and consistency
    - Provide detailed error reporting
    - Support custom validation rules
    """

    @abstractmethod
    def validate(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration data against schema.

        Args:
            config_data: Configuration dictionary to validate

        Returns:
            ValidationResult indicating success, failure, or warnings
        """
        pass

    @abstractmethod
    def validate_section(self, section_name: str, section_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a specific configuration section.

        Args:
            section_name: Name of the configuration section
            section_data: Section data to validate

        Returns:
            ValidationResult for the specific section
        """
        pass

    @abstractmethod
    def get_validation_errors(self) -> List[ValidationError]:
        """
        Get detailed validation errors from last validation.

        Returns:
            List of ValidationError objects
        """
        pass

    @abstractmethod
    def get_schema_for_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Get validation schema for a specific section.

        Args:
            section_name: Name of configuration section

        Returns:
            Schema dictionary or None if section not found
        """
        pass

    @abstractmethod
    def is_required_section(self, section_name: str) -> bool:
        """
        Check if a configuration section is required.

        Args:
            section_name: Name of configuration section

        Returns:
            True if section is required, False otherwise
        """
        pass


class ConfigurationSchema(ABC):
    """
    Contract for configuration schema definition and management.

    Responsibilities:
    - Define structure and validation rules
    - Provide schema for different configuration types
    - Support schema evolution and versioning
    - Define default values and constraints
    """

    @abstractmethod
    def get_core_schema(self) -> Dict[str, Any]:
        """Get schema for core application settings."""
        pass

    @abstractmethod
    def get_filename_rules_schema(self) -> Dict[str, Any]:
        """Get schema for filename generation rules."""
        pass

    @abstractmethod
    def get_classification_rules_schema(self) -> Dict[str, Any]:
        """Get schema for file classification rules."""
        pass

    @abstractmethod
    def get_processing_rules_schema(self) -> Dict[str, Any]:
        """Get schema for file processing rules."""
        pass

    @abstractmethod
    def get_manufacturer_mappings_schema(self) -> Dict[str, Any]:
        """Get schema for manufacturer mappings."""
        pass

    @abstractmethod
    def get_complete_schema(self) -> Dict[str, Any]:
        """Get complete schema for all configuration types."""
        pass

    @abstractmethod
    def get_default_values(self) -> Dict[str, Any]:
        """Get default configuration values."""
        pass

    @abstractmethod
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate that a schema definition is correct.

        Args:
            schema: Schema dictionary to validate

        Returns:
            True if schema is valid, False otherwise
        """
        pass


class ConfigurationWatcher(ABC):
    """
    Contract for watching configuration files for changes.

    Responsibilities:
    - Monitor configuration files for changes
    - Trigger reload when files are modified
    - Handle file system events gracefully
    - Support enabling/disabling watching
    """

    @abstractmethod
    def start_watching(self, config_path: Path) -> bool:
        """
        Start watching configuration files for changes.

        Args:
            config_path: Path to configuration directory or file

        Returns:
            True if watching started successfully, False otherwise
        """
        pass

    @abstractmethod
    def stop_watching(self) -> bool:
        """
        Stop watching configuration files.

        Returns:
            True if watching stopped successfully, False otherwise
        """
        pass

    @abstractmethod
    def is_watching(self) -> bool:
        """
        Check if currently watching for file changes.

        Returns:
            True if watching is active, False otherwise
        """
        pass

    @abstractmethod
    def set_change_callback(self, callback) -> None:
        """
        Set callback function to invoke when configuration changes.

        Args:
            callback: Function to call when changes are detected
        """
        pass


class DefaultConfigurationProvider(ABC):
    """
    Contract for providing default configuration values.

    Responsibilities:
    - Generate default configurations for new installations
    - Provide fallback values for missing settings
    - Create example configuration files
    - Support configuration migration
    """

    @abstractmethod
    def get_default_core_settings(self) -> Dict[str, Any]:
        """Get default core application settings."""
        pass

    @abstractmethod
    def get_default_filename_rules(self) -> Dict[str, Any]:
        """Get default filename generation rules."""
        pass

    @abstractmethod
    def get_default_classification_rules(self) -> Dict[str, Any]:
        """Get default file classification rules."""
        pass

    @abstractmethod
    def get_default_processing_rules(self) -> Dict[str, Any]:
        """Get default file processing rules."""
        pass

    @abstractmethod
    def get_default_manufacturer_mappings(self) -> Dict[str, Any]:
        """Get default manufacturer mappings."""
        pass

    @abstractmethod
    def create_default_configuration(self, output_path: Path) -> bool:
        """
        Create default configuration files at the specified path.

        Args:
            output_path: Directory where default configuration should be created

        Returns:
            True if default configuration created successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_example_configuration(self) -> Dict[str, Any]:
        """Get example configuration with documentation."""
        pass