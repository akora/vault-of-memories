"""
Integration tests for the complete configuration system.
Tests the interaction between all configuration components.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.services.configuration_manager import ConfigurationManagerImpl


@pytest.mark.integration
class TestConfigurationSystemIntegration:
    """Integration tests for complete configuration system workflows."""

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

    def create_complete_configuration(self):
        """Create a complete test configuration."""
        # Core settings
        core_config = {
            "core": {
                "database": {
                    "path": "vault.db",
                    "timeout": 30,
                    "backup_frequency": "daily"
                },
                "logging": {
                    "level": "INFO",
                    "file": "vault.log",
                    "max_size": "10MB",
                    "backup_count": 5
                },
                "temp_directory": "/tmp/vault",
                "max_file_size": "100MB",
                "concurrent_processing": 4
            }
        }

        # Filename rules
        filename_rules = {
            "filename_rules": {
                "default_pattern": (
                    "{date}-{time}-{device}-s{size}-{checksum}"
                ),
                "patterns": {
                    "image": (
                        "{date}-{time}-{camera}-{model}-ir{width}x{height}-"
                        "s{size}-{checksum}"
                    ),
                    "document": "{date}-{title}-{author}-p{pages}-s{size}-{checksum}",
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
        }

        # Classification rules
        classification_rules = {
            "classification_rules": {
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
                            "office": [
                                "doc", "docx", "ppt", "pptx", "xls", "xlsx"
                            ],
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
                    }
                },
                "folder_structure": (
                    "{category}/{subcategory}/{year}/{year}-{month}/"
                    "{year}-{month}-{day}"
                )
            }
        }

        # Processing rules
        processing_rules = {
            "processing_rules": {
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
        }

        # Manufacturer mappings
        manufacturer_mappings = {
            "manufacturer_mappings": {
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
        }

        # Write all configuration files
        configs = [
            ("core.json", core_config),
            ("filename-rules.json", filename_rules),
            ("classification-rules.json", classification_rules),
            ("processing-rules.json", processing_rules),
            ("manufacturer-mappings.json", manufacturer_mappings)
        ]

        for filename, config in configs:
            with open(self.config_path / filename, "w") as f:
                json.dump(config, f, indent=2)

    def test_complete_configuration_workflow(self):
        """Test complete configuration loading and access workflow."""
        self.create_complete_configuration()

        # Load configuration
        assert self.manager.load_configuration(self.config_path) is True

        # Validate configuration
        assert self.manager.validate_configuration().name == "VALID"

        # Get settings repository
        settings = self.manager.get_settings_repository()
        assert settings is not None

        # Test core settings access
        core_settings = settings.get_core_settings()
        assert core_settings.get_database_path().name == "vault.db"
        assert core_settings.get_log_level() == "INFO"

        # Test filename rules access
        filename_rules = settings.get_filename_rules()
        image_pattern = filename_rules.get_pattern_for_type("image")
        assert "camera" in image_pattern
        assert "checksum" in image_pattern

        # Test classification rules access
        classification_rules = settings.get_classification_rules()
        category = classification_rules.classify_file(
            Path("test.jpg"), "image/jpeg"
        )
        assert category == "photos"

        # Test manufacturer mappings access
        manufacturer_mappings = settings.get_manufacturer_mappings()
        manufacturer = manufacturer_mappings.identify_manufacturer(
            {"Make": "Canon", "Model": "EOS 5D Mark IV"}
        )
        assert manufacturer == "Canon"

    def test_configuration_hot_reload(self):
        """Test configuration hot reload without application restart."""
        self.create_complete_configuration()
        self.manager.load_configuration(self.config_path)

        # Get initial settings
        initial_settings = self.manager.get_settings_repository()
        initial_db_path = initial_settings.get_core_settings().get_database_path()

        # Modify core configuration
        modified_core = {
            "core": {
                "database": {
                    "path": "modified-vault.db",
                    "timeout": 60
                },
                "logging": {
                    "level": "DEBUG",
                    "file": "modified-vault.log"
                },
                "temp_directory": "/tmp/modified-vault"
            }
        }

        with open(self.config_path / "core.json", "w") as f:
            json.dump(modified_core, f, indent=2)

        # Reload configuration
        assert self.manager.reload_configuration() is True

        # Verify changes are reflected
        updated_settings = self.manager.get_settings_repository()
        updated_db_path = updated_settings.get_core_settings().get_database_path()

        assert initial_db_path.name == "vault.db"
        assert updated_db_path.name == "modified-vault.db"

    def test_configuration_validation_with_errors(self):
        """Test configuration validation with various error conditions."""
        # Create configuration with multiple issues
        invalid_core = {
            "core": {
                "database": {
                    # Missing required 'path' field
                    "timeout": "invalid_type"  # Should be int
                },
                "logging": {
                    "level": "INVALID_LEVEL",  # Invalid log level
                    "file": ""  # Empty filename
                }
            }
        }

        incomplete_filename_rules = {
            "filename_rules": {
                "patterns": {
                    # Missing default_pattern
                    "image": "{invalid_field}"  # Invalid field
                }
            }
        }

        with open(self.config_path / "core.json", "w") as f:
            json.dump(invalid_core, f, indent=2)

        with open(self.config_path / "filename-rules.json", "w") as f:
            json.dump(incomplete_filename_rules, f, indent=2)

        # Load configuration (should succeed even with invalid content)
        assert self.manager.load_configuration(self.config_path) is True

        # Validation should fail
        result = self.manager.validate_configuration()
        assert result.name in ["INVALID", "WARNING"]

        # Should have detailed error messages
        errors = self.manager.get_validation_errors()
        assert len(errors) > 0

        # Check for specific error types
        error_messages = [error.message.lower() for error in errors]
        assert any("path" in msg for msg in error_messages)
        assert any("integer" in msg or "type" in msg for msg in error_messages)

    def test_default_configuration_fallback(self):
        """Test fallback to default values for missing configuration."""
        # Create minimal configuration (only core settings)
        minimal_config = {
            "core": {
                "database": {"path": "test.db", "timeout": 30},
                "logging": {"level": "INFO", "file": "test.log"}
            }
        }

        with open(self.config_path / "core.json", "w") as f:
            json.dump(minimal_config, f, indent=2)

        # Load minimal configuration
        assert self.manager.load_configuration(self.config_path) is True

        # Should still validate (using defaults for missing sections)
        result = self.manager.validate_configuration()
        assert result.name in ["VALID", "WARNING"]

        # Should provide access to all configuration types with defaults
        settings = self.manager.get_settings_repository()

        # Core settings should use provided values
        core_settings = settings.get_core_settings()
        assert core_settings.get_database_path().name == "test.db"

        # Other settings should use defaults
        filename_rules = settings.get_filename_rules()
        default_pattern = filename_rules.get_default_pattern()
        assert default_pattern is not None
        assert len(default_pattern) > 0

    def test_concurrent_configuration_access(self):
        """Test thread-safe access to configuration settings."""
        import threading
        import time as time_module

        self.create_complete_configuration()
        self.manager.load_configuration(self.config_path)

        results = []
        errors = []

        def access_configuration(thread_id):
            """Access configuration from multiple threads."""
            try:
                for _ in range(10):
                    settings = self.manager.get_settings_repository()
                    core_settings = settings.get_core_settings()
                    db_path = core_settings.get_database_path()
                    results.append((thread_id, db_path.name))
                    time_module.sleep(0.001)  # Small delay to increase contention
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=access_configuration, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in concurrent access: {errors}"

        # Verify all accesses returned consistent results
        assert len(results) == 50  # 5 threads × 10 accesses each
        db_names = [result[1] for result in results]
        assert all(name == "vault.db" for name in db_names)
