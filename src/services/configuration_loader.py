"""
Configuration Loader Implementation
Handles loading and parsing of JSON configuration files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from ..models.configuration import ValidationError


class ConfigurationLoaderImpl:
    """
    Implementation of configuration loading from JSON files.

    Handles file system operations, JSON parsing, and configuration merging.
    """

    def __init__(self):
        """Initialize configuration loader."""
        self.logger = logging.getLogger(__name__)
        self._supported_extensions = ['.json', '.jsonc']

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
        if not config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")

        if not config_dir.is_dir():
            raise ValueError(f"Path is not a directory: {config_dir}")

        self.logger.info(f"Loading configuration from directory: {config_dir}")

        config_files = []
        for extension in self._supported_extensions:
            config_files.extend(config_dir.glob(f"*{extension}"))

        if not config_files:
            self.logger.warning(f"No configuration files found in {config_dir}")
            return {}

        # Load all configuration files
        configurations = []
        for config_file in sorted(config_files):  # Sort for consistent loading order
            try:
                config_data = self.load_from_file(config_file)
                configurations.append(config_data)
                self.logger.debug(f"Loaded configuration from {config_file}")
            except Exception as e:
                self.logger.error(f"Failed to load {config_file}: {e}")
                raise

        # Merge all configurations
        merged_config = self.merge_configurations(configurations)
        self.logger.info(
            f"Successfully merged {len(configurations)} configuration files"
        )

        return merged_config

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
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Handle JSON with comments (JSONC)
            if config_file.suffix.lower() == '.jsonc':
                content = self._strip_json_comments(content)

            config_data = json.loads(content)

            if not isinstance(config_data, dict):
                raise ValueError(
                    f"Configuration file must contain a JSON object, "
                    f"got {type(config_data).__name__}"
                )

            return config_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_file}: {e}")
        except PermissionError:
            raise PermissionError(f"Cannot read configuration file: {config_file}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_file}: {e}")

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported configuration file extensions.

        Returns:
            List of file extensions (e.g., ['.json', '.jsonc'])
        """
        return self._supported_extensions.copy()

    def merge_configurations(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Args:
            configs: List of configuration dictionaries to merge

        Returns:
            Single merged configuration dictionary

        Note:
            Later configurations override earlier ones for conflicting keys.
            Nested dictionaries are merged recursively.
        """
        if not configs:
            return {}

        if len(configs) == 1:
            return configs[0].copy()

        merged = {}
        for config in configs:
            merged = self._deep_merge(merged, config)

        return merged

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Dictionary to merge into base

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if (key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def _strip_json_comments(self, content: str) -> str:
        """
        Strip comments from JSONC (JSON with Comments) content.

        Args:
            content: JSONC content string

        Returns:
            JSON content with comments removed
        """
        import re

        # Remove single-line comments (//...)
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

        # Remove multi-line comments (/* ... */)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        return content

    def validate_file_structure(self, config_file: Path) -> List[ValidationError]:
        """
        Validate the basic structure of a configuration file.

        Args:
            config_file: Path to configuration file to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Check file existence and readability
            if not config_file.exists():
                errors.append(ValidationError(
                    path=str(config_file),
                    message="Configuration file does not exist",
                    severity="error"
                ))
                return errors

            if not config_file.is_file():
                errors.append(ValidationError(
                    path=str(config_file),
                    message="Path is not a regular file",
                    severity="error"
                ))
                return errors

            # Check file extension
            if config_file.suffix.lower() not in self._supported_extensions:
                errors.append(ValidationError(
                    path=str(config_file),
                    message=(
                        f"Unsupported file extension. "
                        f"Supported: {self._supported_extensions}"
                    ),
                    severity="warning"
                ))

            # Try to parse JSON
            try:
                self.load_from_file(config_file)
            except ValueError as e:
                errors.append(ValidationError(
                    path=str(config_file),
                    message=f"JSON parsing error: {e}",
                    severity="error"
                ))

        except Exception as e:
            errors.append(ValidationError(
                path=str(config_file),
                message=f"Unexpected error during validation: {e}",
                severity="error"
            ))

        return errors

    def get_configuration_sections(self, config_data: Dict[str, Any]) -> List[str]:
        """
        Get list of top-level configuration sections.

        Args:
            config_data: Configuration dictionary

        Returns:
            List of section names
        """
        return list(config_data.keys())

    def extract_section(
        self, config_data: Dict[str, Any], section_name: str
    ) -> Dict[str, Any]:
        """
        Extract a specific section from configuration data.

        Args:
            config_data: Full configuration dictionary
            section_name: Name of section to extract

        Returns:
            Section data or empty dict if not found
        """
        return config_data.get(section_name, {})
