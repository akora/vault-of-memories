"""
Settings Repository Implementation
Provides centralized, type-safe access to all configuration values.
"""

import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from ..models.configuration import (
    CoreSettings, FilenameRulesData, ClassificationRulesData,
    ProcessingRulesData, ManufacturerMappingsData
)


class SettingsRepositoryImpl:
    """
    Implementation of centralized configuration value access.

    Provides type-safe, thread-safe access to all configuration categories.
    """

    def __init__(self, config_data: Dict[str, Any]):
        """
        Initialize settings repository with configuration data.

        Args:
            config_data: Complete configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self._config_data = config_data
        self._lock = threading.RLock()

        # Lazy-loaded configuration objects
        self._core_settings: Optional[CoreSettings] = None
        self._filename_rules: Optional[FilenameRulesData] = None
        self._classification_rules: Optional[ClassificationRulesData] = None
        self._processing_rules: Optional[ProcessingRulesData] = None
        self._manufacturer_mappings: Optional[ManufacturerMappingsData] = None

    def get_core_settings(self) -> CoreSettings:
        """Get core application settings."""
        with self._lock:
            if self._core_settings is None:
                core_data = self._config_data.get("core", {})
                self._core_settings = self._create_core_settings(core_data)
            return self._core_settings

    def get_filename_rules(self) -> FilenameRulesData:
        """Get filename generation rules configuration."""
        with self._lock:
            if self._filename_rules is None:
                rules_data = self._config_data.get("filename_rules", {})
                self._filename_rules = FilenameRulesData(**rules_data)
            return self._filename_rules

    def get_classification_rules(self) -> ClassificationRulesData:
        """Get file classification rules configuration."""
        with self._lock:
            if self._classification_rules is None:
                rules_data = self._config_data.get("classification_rules", {})
                self._classification_rules = ClassificationRulesData(**rules_data)
            return self._classification_rules

    def get_processing_rules(self) -> ProcessingRulesData:
        """Get file processing rules configuration."""
        with self._lock:
            if self._processing_rules is None:
                rules_data = self._config_data.get("processing_rules", {})
                self._processing_rules = ProcessingRulesData(**rules_data)
            return self._processing_rules

    def get_manufacturer_mappings(self) -> ManufacturerMappingsData:
        """Get device manufacturer mappings configuration."""
        with self._lock:
            if self._manufacturer_mappings is None:
                mappings_data = self._config_data.get("manufacturer_mappings", {})
                self._manufacturer_mappings = ManufacturerMappingsData(**mappings_data)
            return self._manufacturer_mappings

    def get_setting(self, path: str, default=None):
        """
        Get a specific setting by path.

        Args:
            path: Dot-separated path to setting (e.g., "core.database.path")
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        with self._lock:
            try:
                keys = path.split('.')
                value = self._config_data

                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default

                return value

            except Exception as e:
                self.logger.warning(f"Failed to get setting '{path}': {e}")
                return default

    def get_raw_configuration(self) -> Dict[str, Any]:
        """
        Get the raw configuration data.

        Returns:
            Complete configuration dictionary
        """
        with self._lock:
            return self._config_data.copy()

    def _create_core_settings(self, core_data: Dict[str, Any]) -> CoreSettings:
        """
        Create CoreSettings object from configuration data.

        Args:
            core_data: Core configuration section

        Returns:
            CoreSettings instance
        """
        # Extract database settings
        db_data = core_data.get("database", {})
        database_path = Path(db_data.get("path", "vault.db"))

        # Extract logging settings
        log_data = core_data.get("logging", {})
        log_level = log_data.get("level", "INFO")
        log_file = Path(log_data.get("file", "vault.log"))

        # Extract other core settings
        temp_directory = Path(core_data.get("temp_directory", "/tmp/vault"))
        max_file_size = core_data.get("max_file_size", "100MB")
        concurrent_processing = core_data.get("concurrent_processing", 4)
        backup_frequency = db_data.get("backup_frequency", "daily")

        return CoreSettings(
            database_path=database_path,
            log_level=log_level,
            log_file=log_file,
            temp_directory=temp_directory,
            max_file_size=max_file_size,
            concurrent_processing=concurrent_processing,
            backup_frequency=backup_frequency
        )

    def has_section(self, section_name: str) -> bool:
        """
        Check if a configuration section exists.

        Args:
            section_name: Name of configuration section

        Returns:
            True if section exists, False otherwise
        """
        with self._lock:
            return section_name in self._config_data

    def get_section_keys(self, section_name: str) -> list:
        """
        Get all keys in a configuration section.

        Args:
            section_name: Name of configuration section

        Returns:
            List of keys in the section
        """
        with self._lock:
            section = self._config_data.get(section_name, {})
            if isinstance(section, dict):
                return list(section.keys())
            return []

    def get_all_sections(self) -> list:
        """
        Get all configuration section names.

        Returns:
            List of all section names
        """
        with self._lock:
            return list(self._config_data.keys())


# Convenience classes that implement the abstract interfaces from contracts

class FilenameRulesImpl(FilenameRulesData):
    """Implementation of FilenameRules contract."""

    def get_pattern_for_type(self, file_type: str) -> Optional[str]:
        """Get filename pattern for specific file type."""
        return self.patterns.get(file_type, self.default_pattern)

    def get_default_pattern(self) -> str:
        """Get default filename pattern."""
        return self.default_pattern


class ClassificationRulesImpl(ClassificationRulesData):
    """Implementation of ClassificationRules contract."""

    def classify_file(self, file_path: Path, file_type: str = None) -> str:
        """Classify file into appropriate category."""
        return super().classify_file(file_path, file_type)

    def get_category_folder(self, category: str) -> str:
        """Get folder name for file category."""
        return super().get_category_folder(category)


class ProcessingRulesImpl(ProcessingRulesData):
    """Implementation of ProcessingRules contract."""

    def get_processor_for_type(self, file_type: str) -> Optional[str]:
        """Get processor class name for file type."""
        rule = super().get_processor_for_type(file_type)
        return rule.__class__.__name__ if rule else None

    def should_extract_metadata(self, file_type: str) -> bool:
        """Check if metadata extraction is enabled for file type."""
        return super().should_extract_metadata(file_type)


class ManufacturerMappingsImpl(ManufacturerMappingsData):
    """Implementation of ManufacturerMappings contract."""

    def identify_manufacturer(self, metadata: dict) -> Optional[str]:
        """Identify manufacturer from file metadata."""
        return super().identify_manufacturer(metadata)

    def get_device_model(self, manufacturer: str, model_id: str) -> Optional[str]:
        """Get full device model name."""
        # For this implementation, model_id is not used directly
        # Instead, we need the full metadata to identify the model
        return None


class CoreSettingsImpl(CoreSettings):
    """Implementation of CoreSettings contract."""

    def get_database_path(self) -> Path:
        """Get database file path."""
        return self.database_path

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.log_level

    def get_temp_directory(self) -> Path:
        """Get temporary files directory."""
        return self.temp_directory
