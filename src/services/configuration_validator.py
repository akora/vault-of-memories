"""
Configuration Validator Implementation
Validates configuration data against schema and business rules.
"""

import logging
from typing import Dict, Any, List, Optional
from ..models.configuration import ValidationResult, ValidationError


class ConfigurationValidatorImpl:
    """
    Implementation of configuration validation.

    Validates configuration data against predefined schemas and business rules.
    """

    def __init__(self):
        """Initialize configuration validator."""
        self.logger = logging.getLogger(__name__)
        self._validation_errors: List[ValidationError] = []
        self._schemas = self._initialize_schemas()

    def validate(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration data against schema.

        Args:
            config_data: Configuration dictionary to validate

        Returns:
            ValidationResult indicating success, failure, or warnings
        """
        self._validation_errors.clear()

        try:
            # Validate each section
            has_errors = False
            has_warnings = False

            # Check for required sections
            for section_name in self._get_required_sections():
                if section_name not in config_data:
                    self._validation_errors.append(ValidationError(
                        path=section_name,
                        message=(
                            f"Required configuration section "
                            f"'{section_name}' is missing"
                        ),
                        severity="error"
                    ))
                    has_errors = True

            # Validate existing sections
            for section_name, section_data in config_data.items():
                section_result = self.validate_section(section_name, section_data)
                if section_result == ValidationResult.INVALID:
                    has_errors = True
                elif section_result == ValidationResult.WARNING:
                    has_warnings = True

            # Determine overall result
            if has_errors:
                return ValidationResult.INVALID
            elif has_warnings:
                return ValidationResult.WARNING
            else:
                return ValidationResult.VALID

        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            self._validation_errors.append(ValidationError(
                path="<root>",
                message=f"Validation failed with error: {e}",
                severity="error"
            ))
            return ValidationResult.INVALID

    def validate_section(
        self, section_name: str, section_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a specific configuration section.

        Args:
            section_name: Name of the configuration section
            section_data: Section data to validate

        Returns:
            ValidationResult for the specific section
        """
        schema = self.get_schema_for_section(section_name)
        if not schema:
            self._validation_errors.append(ValidationError(
                path=section_name,
                message=f"Unknown configuration section: {section_name}",
                severity="warning"
            ))
            return ValidationResult.WARNING

        return self._validate_against_schema(section_name, section_data, schema)

    def get_validation_errors(self) -> List[ValidationError]:
        """
        Get detailed validation errors from last validation.

        Returns:
            List of ValidationError objects
        """
        return self._validation_errors.copy()

    def get_schema_for_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Get validation schema for a specific section.

        Args:
            section_name: Name of configuration section

        Returns:
            Schema dictionary or None if section not found
        """
        return self._schemas.get(section_name)

    def is_required_section(self, section_name: str) -> bool:
        """
        Check if a configuration section is required.

        Args:
            section_name: Name of configuration section

        Returns:
            True if section is required, False otherwise
        """
        return section_name in self._get_required_sections()

    def _initialize_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation schemas for all configuration sections."""
        return {
            "core": self._get_core_schema(),
            "filename_rules": self._get_filename_rules_schema(),
            "classification_rules": self._get_classification_rules_schema(),
            "processing_rules": self._get_processing_rules_schema(),
            "manufacturer_mappings": self._get_manufacturer_mappings_schema()
        }

    def _get_required_sections(self) -> List[str]:
        """Get list of required configuration sections."""
        return ["core"]

    def _get_core_schema(self) -> Dict[str, Any]:
        """Get schema for core application settings."""
        return {
            "type": "object",
            "required": ["database", "logging"],
            "properties": {
                "database": {
                    "type": "object",
                    "required": ["path", "timeout"],
                    "properties": {
                        "path": {"type": "string", "minLength": 1},
                        "timeout": {
                            "type": "integer", "minimum": 1, "maximum": 300
                        },
                        "backup_frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"]
                        }
                    }
                },
                "logging": {
                    "type": "object",
                    "required": ["level", "file"],
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                        },
                        "file": {"type": "string", "minLength": 1},
                        "max_size": {"type": "string"},
                        "backup_count": {
                            "type": "integer", "minimum": 1, "maximum": 100
                        }
                    }
                },
                "temp_directory": {"type": "string", "minLength": 1},
                "max_file_size": {"type": "string"},
                "concurrent_processing": {
                    "type": "integer", "minimum": 1, "maximum": 32
                }
            }
        }

    def _get_filename_rules_schema(self) -> Dict[str, Any]:
        """Get schema for filename generation rules."""
        return {
            "type": "object",
            "required": ["default_pattern"],
            "properties": {
                "default_pattern": {"type": "string", "minLength": 1},
                "patterns": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {"type": "string", "minLength": 1}
                    }
                },
                "field_mappings": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1
                        }
                    }
                }
            }
        }

    def _get_classification_rules_schema(self) -> Dict[str, Any]:
        """Get schema for file classification rules."""
        return {
            "type": "object",
            "required": ["categories"],
            "properties": {
                "categories": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["folder", "file_types"],
                            "properties": {
                                "folder": {"type": "string", "minLength": 1},
                                "file_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1
                                },
                                "subcategories": {
                                    "type": "object",
                                    "patternProperties": {
                                        ".*": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "folder_structure": {"type": "string", "minLength": 1}
            }
        }

    def _get_processing_rules_schema(self) -> Dict[str, Any]:
        """Get schema for file processing rules."""
        return {
            "type": "object",
            "properties": {
                "extractors": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["enabled"],
                            "properties": {
                                "enabled": {"type": "boolean"}
                            },
                            "additionalProperties": True
                        }
                    }
                },
                "processors": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["enabled"],
                            "properties": {
                                "enabled": {"type": "boolean"}
                            },
                            "additionalProperties": True
                        }
                    }
                }
            }
        }

    def _get_manufacturer_mappings_schema(self) -> Dict[str, Any]:
        """Get schema for manufacturer mappings."""
        return {
            "type": "object",
            "properties": {
                "cameras": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["patterns"],
                            "properties": {
                                "patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1
                                },
                                "models": {
                                    "type": "object",
                                    "patternProperties": {
                                        ".*": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "phones": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["patterns"],
                            "properties": {
                                "patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1
                                },
                                "models": {
                                    "type": "object",
                                    "patternProperties": {
                                        ".*": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def _validate_against_schema(
        self, path: str, data: Any, schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate data against a JSON schema.

        Args:
            path: Configuration path for error reporting
            data: Data to validate
            schema: JSON schema to validate against

        Returns:
            ValidationResult for the validation
        """
        try:
            # Basic type checking
            schema_type = schema.get("type")
            if schema_type == "object" and not isinstance(data, dict):
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Expected object, got {type(data).__name__}",
                    severity="error"
                ))
                return ValidationResult.INVALID

            if schema_type == "array" and not isinstance(data, list):
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Expected array, got {type(data).__name__}",
                    severity="error"
                ))
                return ValidationResult.INVALID

            # For objects, validate properties and required fields
            if schema_type == "object" and isinstance(data, dict):
                return self._validate_object(path, data, schema)

            # For arrays, validate items
            if schema_type == "array" and isinstance(data, list):
                return self._validate_array(path, data, schema)

            # Basic value validation
            return self._validate_value(path, data, schema)

        except Exception as e:
            self._validation_errors.append(ValidationError(
                path=path,
                message=f"Schema validation error: {e}",
                severity="error"
            ))
            return ValidationResult.INVALID

    def _validate_object(
        self, path: str, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> ValidationResult:
        """Validate object against schema."""
        has_errors = False
        has_warnings = False

        # Check required properties
        required_props = schema.get("required", [])
        for prop in required_props:
            if prop not in data:
                self._validation_errors.append(ValidationError(
                    path=f"{path}.{prop}",
                    message=f"Required property '{prop}' is missing",
                    severity="error"
                ))
                has_errors = True

        # Validate existing properties
        properties = schema.get("properties", {})
        pattern_properties = schema.get("patternProperties", {})

        for key, value in data.items():
            key_path = f"{path}.{key}"

            # Check specific properties first
            if key in properties:
                result = self._validate_against_schema(
                    key_path, value, properties[key]
                )
                if result == ValidationResult.INVALID:
                    has_errors = True
                elif result == ValidationResult.WARNING:
                    has_warnings = True
            # Check pattern properties
            elif pattern_properties:
                import re
                matched = False
                for pattern, prop_schema in pattern_properties.items():
                    if re.match(pattern, key):
                        matched = True
                        result = self._validate_against_schema(
                            key_path, value, prop_schema
                        )
                        if result == ValidationResult.INVALID:
                            has_errors = True
                        elif result == ValidationResult.WARNING:
                            has_warnings = True
                        break

                if not matched and not schema.get("additionalProperties", True):
                    self._validation_errors.append(ValidationError(
                        path=key_path,
                        message=f"Unknown property '{key}'",
                        severity="warning"
                    ))
                    has_warnings = True

        if has_errors:
            return ValidationResult.INVALID
        elif has_warnings:
            return ValidationResult.WARNING
        else:
            return ValidationResult.VALID

    def _validate_array(
        self, path: str, data: List[Any], schema: Dict[str, Any]
    ) -> ValidationResult:
        """Validate array against schema."""
        has_errors = False
        has_warnings = False

        # Check minimum items
        min_items = schema.get("minItems", 0)
        if len(data) < min_items:
            self._validation_errors.append(ValidationError(
                path=path,
                message=(
                    f"Array must have at least {min_items} items, "
                    f"got {len(data)}"
                ),
                severity="error"
            ))
            has_errors = True

        # Check maximum items
        max_items = schema.get("maxItems")
        if max_items and len(data) > max_items:
            self._validation_errors.append(ValidationError(
                path=path,
                message=(
                    f"Array must have at most {max_items} items, "
                    f"got {len(data)}"
                ),
                severity="error"
            ))
            has_errors = True

        # Validate items
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                result = self._validate_against_schema(item_path, item, items_schema)
                if result == ValidationResult.INVALID:
                    has_errors = True
                elif result == ValidationResult.WARNING:
                    has_warnings = True

        if has_errors:
            return ValidationResult.INVALID
        elif has_warnings:
            return ValidationResult.WARNING
        else:
            return ValidationResult.VALID

    def _validate_value(
        self, path: str, data: Any, schema: Dict[str, Any]
    ) -> ValidationResult:
        """Validate primitive value against schema."""
        has_errors = False

        # Type validation
        expected_type = schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(data, str):
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Expected string, got {type(data).__name__}",
                    severity="error"
                ))
                has_errors = True
            elif expected_type == "integer" and not isinstance(data, int):
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Expected integer, got {type(data).__name__}",
                    severity="error"
                ))
                has_errors = True
            elif expected_type == "boolean" and not isinstance(data, bool):
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Expected boolean, got {type(data).__name__}",
                    severity="error"
                ))
                has_errors = True

        # String validations
        if isinstance(data, str):
            min_length = schema.get("minLength")
            if min_length and len(data) < min_length:
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=(
                        f"String must be at least {min_length} characters, "
                        f"got {len(data)}"
                    ),
                    severity="error"
                ))
                has_errors = True

            enum_values = schema.get("enum")
            if enum_values and data not in enum_values:
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Value must be one of {enum_values}, got '{data}'",
                    severity="error"
                ))
                has_errors = True

        # Integer validations
        if isinstance(data, int):
            minimum = schema.get("minimum")
            if minimum is not None and data < minimum:
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Value must be at least {minimum}, got {data}",
                    severity="error"
                ))
                has_errors = True

            maximum = schema.get("maximum")
            if maximum is not None and data > maximum:
                self._validation_errors.append(ValidationError(
                    path=path,
                    message=f"Value must be at most {maximum}, got {data}",
                    severity="error"
                ))
                has_errors = True

        return ValidationResult.INVALID if has_errors else ValidationResult.VALID
