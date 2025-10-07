"""
Configuration data models and supporting classes.
Provides structured representations of configuration data and validation results.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional


class ValidationResult(Enum):
    """Configuration validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationError:
    """Represents a configuration validation error."""
    path: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.path} - {self.message}"


@dataclass
class CoreSettings:
    """Core application settings."""
    database_path: Path
    log_level: str
    log_file: Path
    temp_directory: Path
    max_file_size: str = "100MB"
    concurrent_processing: int = 4
    backup_frequency: str = "daily"

    def __post_init__(self):
        """Validate settings after initialization."""
        if not isinstance(self.database_path, Path):
            self.database_path = Path(self.database_path)
        if not isinstance(self.log_file, Path):
            self.log_file = Path(self.log_file)
        if not isinstance(self.temp_directory, Path):
            self.temp_directory = Path(self.temp_directory)

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")

    def get_database_path(self) -> Path:
        """Get database file path."""
        return self.database_path

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.log_level.upper()

    def get_temp_directory(self) -> Path:
        """Get temporary files directory."""
        return self.temp_directory


@dataclass
class FilenamePattern:
    """Represents a filename generation pattern."""
    pattern: str
    file_types: List[str]
    required_fields: List[str]

    def __post_init__(self):
        """Extract required fields from pattern."""
        import re
        if not self.required_fields:
            # Extract field names from {field} placeholders
            field_matches = re.findall(r'\{([^}]+)\}', self.pattern)
            self.required_fields = list(set(field_matches))

    def is_valid_for_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check if pattern can be applied with given metadata."""
        return all(field in metadata for field in self.required_fields)


@dataclass
class FilenameRulesData:
    """Filename generation rules configuration."""
    default_pattern: str
    patterns: Dict[str, str]
    field_mappings: Dict[str, List[str]]

    def get_pattern_for_type(self, file_type: str) -> str:
        """Get filename pattern for specific file type."""
        return self.patterns.get(file_type, self.default_pattern)

    def get_default_pattern(self) -> str:
        """Get default filename pattern."""
        return self.default_pattern

    def get_field_mapping(self, field_name: str) -> List[str]:
        """Get possible metadata field names for a logical field."""
        return self.field_mappings.get(field_name, [field_name])


@dataclass
class CategoryRule:
    """File classification category rule."""
    folder: str
    file_types: List[str]
    subcategories: Dict[str, List[str]]
    keywords: List[str] = None

    def __post_init__(self):
        """Initialize optional fields."""
        if self.keywords is None:
            self.keywords = []

    def matches_file_type(self, file_extension: str) -> bool:
        """Check if file extension matches this category."""
        return file_extension.lower() in [ft.lower() for ft in self.file_types]

    def get_subcategory(
        self, file_extension: str, metadata: Dict[str, Any] = None
    ) -> str:
        """Determine subcategory for file."""
        file_ext = file_extension.lower()

        # Check subcategories based on file type
        for subcategory, extensions in self.subcategories.items():
            if file_ext in [ext.lower() for ext in extensions]:
                return subcategory

        # Check subcategories based on keywords in metadata
        if metadata:
            for subcategory, rules in self.subcategories.items():
                for rule in rules:
                    if rule.startswith("keywords:"):
                        keyword = rule.split(":", 1)[1]
                        keywords_field = metadata.get("keywords", [])
                        if isinstance(keywords_field, str):
                            keywords_field = [keywords_field]
                        if keyword in keywords_field:
                            return subcategory

        return "general"


@dataclass
class ClassificationRulesData:
    """File classification rules configuration."""
    categories: Dict[str, CategoryRule]
    folder_structure: str

    def __post_init__(self):
        """Convert category dictionaries to CategoryRule objects."""
        for name, rule_data in self.categories.items():
            if isinstance(rule_data, dict):
                self.categories[name] = CategoryRule(**rule_data)

    def classify_file(self, file_path: Path, file_type: str = None) -> str:
        """Classify file into appropriate category."""
        file_extension = file_path.suffix[1:] if file_path.suffix else ""
        # file_type parameter available for future MIME type classification

        for category_name, rule in self.categories.items():
            if rule.matches_file_type(file_extension):
                return category_name

        return "other"

    def get_category_folder(self, category: str) -> str:
        """Get folder name for file category."""
        if category in self.categories:
            return self.categories[category].folder
        return category


@dataclass
class ProcessorRule:
    """Processing rule for a specific file type."""
    enabled: bool
    extractor_settings: Dict[str, Any]

    def is_enabled(self) -> bool:
        """Check if processing is enabled."""
        return self.enabled

    def get_setting(self, setting_name: str, default=None):
        """Get specific processor setting."""
        return self.extractor_settings.get(setting_name, default)


@dataclass
class ProcessingRulesData:
    """File processing rules configuration."""
    extractors: Dict[str, ProcessorRule]
    processors: Dict[str, ProcessorRule]

    def __post_init__(self):
        """Convert rule dictionaries to ProcessorRule objects."""
        for name, rule_data in self.extractors.items():
            if isinstance(rule_data, dict):
                enabled = rule_data.pop("enabled", True)
                self.extractors[name] = ProcessorRule(enabled, rule_data)

        for name, rule_data in self.processors.items():
            if isinstance(rule_data, dict):
                enabled = rule_data.pop("enabled", True)
                self.processors[name] = ProcessorRule(enabled, rule_data)

    def get_processor_for_type(self, file_type: str) -> Optional[ProcessorRule]:
        """Get processor rule for file type."""
        return self.extractors.get(file_type)

    def should_extract_metadata(self, file_type: str) -> bool:
        """Check if metadata extraction is enabled for file type."""
        rule = self.get_processor_for_type(file_type)
        return rule.is_enabled() if rule else False


@dataclass
class ManufacturerInfo:
    """Manufacturer information and patterns."""
    patterns: List[str]
    models: Dict[str, List[str]]

    def matches_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches this manufacturer."""
        make_field = metadata.get("Make", metadata.get("manufacturer", ""))
        if not make_field:
            return False

        make_lower = make_field.lower()
        return any(pattern.lower() in make_lower for pattern in self.patterns)

    def identify_model(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Identify specific model from metadata."""
        model_field = metadata.get("Model", metadata.get("model", ""))
        if not model_field:
            return None

        model_lower = model_field.lower()
        for model_name, patterns in self.models.items():
            if any(pattern.lower() in model_lower for pattern in patterns):
                return model_name

        return model_field  # Return original if no mapping found


@dataclass
class ManufacturerMappingsData:
    """Device manufacturer mappings configuration."""
    cameras: Dict[str, ManufacturerInfo]
    phones: Dict[str, ManufacturerInfo]

    def __post_init__(self):
        """Convert manufacturer dictionaries to ManufacturerInfo objects."""
        for name, info_data in self.cameras.items():
            if isinstance(info_data, dict):
                self.cameras[name] = ManufacturerInfo(**info_data)

        for name, info_data in self.phones.items():
            if isinstance(info_data, dict):
                self.phones[name] = ManufacturerInfo(**info_data)

    def identify_manufacturer(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Identify manufacturer from file metadata."""
        # Check cameras first
        for manufacturer, info in self.cameras.items():
            if info.matches_metadata(metadata):
                return manufacturer

        # Then check phones
        for manufacturer, info in self.phones.items():
            if info.matches_metadata(metadata):
                return manufacturer

        return None

    def get_device_model(
        self, manufacturer: str, metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Get full device model name."""
        # Check in cameras
        if manufacturer in self.cameras:
            return self.cameras[manufacturer].identify_model(metadata)

        # Check in phones
        if manufacturer in self.phones:
            return self.phones[manufacturer].identify_model(metadata)

        return None
