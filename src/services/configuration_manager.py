"""
Configuration Manager Implementation
Central coordinator for all configuration operations.
"""

import logging
import threading
from pathlib import Path
from typing import List, Optional
from ..models.configuration import ValidationResult, ValidationError
from .configuration_loader import ConfigurationLoaderImpl
from .configuration_validator import ConfigurationValidatorImpl
from .settings_repository import SettingsRepositoryImpl


class ConfigurationManagerImpl:
    """
    Implementation of central configuration management.

    Coordinates loading, validation, and access to all configuration settings.
    Provides thread-safe access and supports hot reloading.
    """

    def __init__(self):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        self._loader = ConfigurationLoaderImpl()
        self._validator = ConfigurationValidatorImpl()
        self._settings_repository: Optional[SettingsRepositoryImpl] = None
        self._config_path: Optional[Path] = None
        self._is_loaded = False
        self._lock = threading.RLock()  # Reentrant lock for thread safety

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
        with self._lock:
            try:
                self.logger.info(f"Loading configuration from: {config_path}")

                # Load configuration data
                if config_path.is_dir():
                    config_data = self._loader.load_from_directory(config_path)
                elif config_path.is_file():
                    config_data = self._loader.load_from_file(config_path)
                else:
                    raise FileNotFoundError(
                        f"Configuration path not found: {config_path}"
                    )

                # Apply defaults for missing sections
                config_data = self._apply_defaults(config_data)

                # Create settings repository
                self._settings_repository = SettingsRepositoryImpl(config_data)

                # Store configuration state
                self._config_path = config_path
                self._is_loaded = True

                self.logger.info("Configuration loaded successfully")
                return True

            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                # Don't clear existing configuration on failure
                raise

    def validate_configuration(self) -> ValidationResult:
        """
        Validate the currently loaded configuration.

        Returns:
            ValidationResult indicating success, failure, or warnings

        Raises:
            RuntimeError: If no configuration is loaded
        """
        with self._lock:
            if not self._is_loaded or self._settings_repository is None:
                raise RuntimeError(
                    "No configuration loaded. Call load_configuration() first."
                )

            try:
                config_data = self._settings_repository.get_raw_configuration()
                result = self._validator.validate(config_data)

                if result == ValidationResult.VALID:
                    self.logger.info("Configuration validation passed")
                elif result == ValidationResult.WARNING:
                    self.logger.warning("Configuration validation passed with warnings")
                    for error in self._validator.get_validation_errors():
                        self.logger.warning(f"Validation warning: {error}")
                else:
                    self.logger.error("Configuration validation failed")
                    for error in self._validator.get_validation_errors():
                        self.logger.error(f"Validation error: {error}")

                return result

            except Exception as e:
                self.logger.error(
                    f"Configuration validation failed with exception: {e}"
                )
                return ValidationResult.INVALID

    def get_settings_repository(self) -> 'SettingsRepositoryImpl':
        """
        Get the central settings repository.

        Returns:
            SettingsRepository instance for accessing configuration values

        Raises:
            RuntimeError: If no configuration is loaded
        """
        with self._lock:
            if not self._is_loaded or self._settings_repository is None:
                raise RuntimeError(
                    "No configuration loaded. Call load_configuration() first."
                )

            return self._settings_repository

    def reload_configuration(self) -> bool:
        """
        Reload configuration without application restart.

        Returns:
            True if reload successful, False otherwise

        Note:
            Preserves existing configuration if reload fails
        """
        with self._lock:
            if not self._config_path:
                self.logger.error("Cannot reload: no configuration path available")
                return False

            # Store current state for rollback
            previous_repository = self._settings_repository
            previous_loaded = self._is_loaded

            try:
                self.logger.info("Reloading configuration")

                # Load new configuration
                if self._config_path.is_dir():
                    config_data = self._loader.load_from_directory(self._config_path)
                else:
                    config_data = self._loader.load_from_file(self._config_path)

                # Apply defaults
                config_data = self._apply_defaults(config_data)

                # Validate new configuration
                temp_validator = ConfigurationValidatorImpl()
                validation_result = temp_validator.validate(config_data)

                if validation_result == ValidationResult.INVALID:
                    self.logger.error("Reload failed: new configuration is invalid")
                    return False

                # Update settings repository
                self._settings_repository = SettingsRepositoryImpl(config_data)
                self._is_loaded = True

                self.logger.info("Configuration reloaded successfully")
                return True

            except Exception as e:
                self.logger.error(f"Configuration reload failed: {e}")

                # Restore previous state
                self._settings_repository = previous_repository
                self._is_loaded = previous_loaded

                return False

    def get_validation_errors(self) -> List[ValidationError]:
        """
        Get detailed validation errors from last validation attempt.

        Returns:
            List of ValidationError objects describing any issues
        """
        return self._validator.get_validation_errors()

    def is_configuration_loaded(self) -> bool:
        """
        Check if configuration is currently loaded.

        Returns:
            True if configuration is loaded, False otherwise
        """
        with self._lock:
            return self._is_loaded

    def get_configuration_path(self) -> Optional[Path]:
        """
        Get the path to the currently loaded configuration.

        Returns:
            Path to configuration directory, or None if not loaded
        """
        with self._lock:
            return self._config_path

    def _apply_defaults(self, config_data: dict) -> dict:
        """
        Apply default values for missing configuration sections.

        Args:
            config_data: Raw configuration data

        Returns:
            Configuration data with defaults applied
        """
        # Default core settings
        if "core" not in config_data:
            config_data["core"] = {}

        core_defaults = {
            "temp_directory": "/tmp/vault",
            "max_file_size": "100MB",
            "concurrent_processing": 4
        }

        for key, value in core_defaults.items():
            if key not in config_data["core"]:
                config_data["core"][key] = value

        # Default database settings
        if "database" not in config_data["core"]:
            config_data["core"]["database"] = {}

        db_defaults = {
            "timeout": 30,
            "backup_frequency": "daily"
        }

        for key, value in db_defaults.items():
            if key not in config_data["core"]["database"]:
                config_data["core"]["database"][key] = value

        # Default logging settings
        if "logging" not in config_data["core"]:
            config_data["core"]["logging"] = {}

        logging_defaults = {
            "max_size": "10MB",
            "backup_count": 5
        }

        for key, value in logging_defaults.items():
            if key not in config_data["core"]["logging"]:
                config_data["core"]["logging"][key] = value

        # Default filename rules
        if "filename_rules" not in config_data:
            config_data["filename_rules"] = {
                "default_pattern": "{date}-{time}-{device}-s{size}-{checksum}",
                "patterns": {
                    "image": (
                        "{date}-{time}-{camera}-{model}-ir{width}x{height}-"
                        "s{size}-{checksum}"
                    ),
                    "document": (
                        "{date}-{title}-{author}-p{pages}-s{size}-{checksum}"
                    ),
                    "video": (
                        "{date}-{time}-{device}-d{duration}-ir{width}x{height}-"
                        "s{size}-{checksum}"
                    ),
                    "audio": (
                        "{date}-{time}-{artist}-{title}-d{duration}-s{size}-{checksum}"
                    )
                },
                "field_mappings": {
                    "camera": ["Make", "Camera Make"],
                    "model": ["Model", "Camera Model"],
                    "artist": ["Artist", "AlbumArtist", "Author"],
                    "title": ["Title", "DocumentTitle", "Subject"]
                }
            }

        # Default classification rules
        if "classification_rules" not in config_data:
            config_data["classification_rules"] = {
                "categories": {
                    "photos": {
                        "folder": "photos",
                        "file_types": [
                            "jpg", "jpeg", "png", "tiff", "raw", "nef", "cr2"
                        ],
                        "subcategories": {
                            "raw": ["raw", "nef", "cr2", "dng"],
                            "processed": ["jpg", "jpeg", "png", "tiff"]
                        }
                    },
                    "documents": {
                        "folder": "documents",
                        "file_types": ["pdf", "doc", "docx", "txt", "md"],
                        "subcategories": {
                            "office": ["doc", "docx", "ppt", "pptx", "xls", "xlsx"],
                            "pdf": ["pdf"],
                            "text": ["txt", "md", "rtf"]
                        }
                    },
                    "videos": {
                        "folder": "videos",
                        "file_types": ["mp4", "avi", "mov", "mkv", "wmv"],
                        "subcategories": {
                            "family": ["keywords:family", "keywords:personal"],
                            "work": ["keywords:work", "keywords:business"]
                        }
                    },
                    "audio": {
                        "folder": "audio",
                        "file_types": ["mp3", "flac", "wav", "aac", "m4a"],
                        "subcategories": {
                            "music": ["mp3", "flac", "m4a"],
                            "voice": ["wav", "aac"]
                        }
                    }
                },
                "folder_structure": (
                    "{category}/{subcategory}/{year}/{year}-{month}/"
                    "{year}-{month}-{day}"
                )
            }

        # Default processing rules
        if "processing_rules" not in config_data:
            config_data["processing_rules"] = {
                "extractors": {
                    "image": {
                        "enabled": True,
                        "extract_exif": True,
                        "extract_iptc": True,
                        "extract_xmp": True,
                        "thumbnail_size": [200, 200]
                    },
                    "document": {
                        "enabled": True,
                        "extract_properties": True,
                        "extract_text": False,
                        "max_text_length": 1000
                    },
                    "video": {
                        "enabled": True,
                        "extract_metadata": True,
                        "generate_thumbnail": True,
                        "thumbnail_time": 5
                    },
                    "audio": {
                        "enabled": True,
                        "extract_id3": True,
                        "extract_duration": True,
                        "extract_bitrate": True
                    }
                },
                "processors": {
                    "duplicate_detection": {
                        "enabled": True,
                        "algorithm": "sha256",
                        "chunk_size": 65536
                    },
                    "virus_scanning": {
                        "enabled": False,
                        "engine": "clamav"
                    }
                }
            }

        # Default manufacturer mappings
        if "manufacturer_mappings" not in config_data:
            config_data["manufacturer_mappings"] = {
                "cameras": {
                    "Canon": {
                        "patterns": ["Canon", "CANON"],
                        "models": {
                            "Canon EOS 5D Mark IV": [
                                "5D Mark IV", "5D4", "EOS 5D Mark IV"
                            ],
                            "Canon EOS R5": ["EOS R5", "R5"]
                        }
                    },
                    "Nikon": {
                        "patterns": ["Nikon", "NIKON CORPORATION"],
                        "models": {
                            "Nikon D850": ["D850", "NIKON D850"],
                            "Nikon Z9": ["Z9", "NIKON Z9"]
                        }
                    }
                },
                "phones": {
                    "Apple": {
                        "patterns": ["Apple", "iPhone"],
                        "models": {
                            "iPhone 15 Pro": ["iPhone15,2", "iPhone 15 Pro"],
                            "iPhone 14": ["iPhone14,7", "iPhone 14"]
                        }
                    },
                    "Samsung": {
                        "patterns": ["samsung", "SAMSUNG"],
                        "models": {
                            "Galaxy S24": ["SM-S921", "Galaxy S24"],
                            "Galaxy Note20": ["SM-N981", "Galaxy Note20"]
                        }
                    }
                }
            }

        return config_data
