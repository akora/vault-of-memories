"""
Contract: Filename Generator Interface

This contract defines the interface for generating standardized filenames from
consolidated metadata using configurable naming patterns.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class GeneratedFilename:
    """
    Result of filename generation.

    Contains the generated filename, component mapping, and metadata about
    the generation process.
    """
    filename: str  # Generated filename with extension
    original_filename: str  # Original filename
    components_used: Dict[str, Any]  # Metadata components used in generation
    pattern_applied: str  # Pattern template that was used
    collision_counter: Optional[int] = None  # Counter if collision occurred (1-based)
    truncated: bool = False  # Whether filename was truncated
    sanitized_chars: int = 0  # Number of characters sanitized
    generation_timestamp: Optional[datetime] = None  # When generated
    warnings: List[str] = None  # Any warnings during generation

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class FilenameGenerator:
    """
    Interface for generating standardized filenames from metadata.

    Contract:
    - MUST generate human-readable filenames using metadata
    - MUST apply configurable naming patterns
    - MUST ensure filename uniqueness with 8-digit counters
    - MUST handle filesystem length limits (default 255 chars)
    - MUST sanitize metadata for safe filename use
    - MUST preserve file extensions
    - MUST support preview mode (no side effects)
    """

    def generate(
        self,
        metadata: Dict[str, Any],
        file_type: str,
        original_filename: str,
        preview: bool = False
    ) -> GeneratedFilename:
        """
        Generate a standardized filename from metadata.

        Args:
            metadata: Consolidated metadata dictionary
            file_type: File type identifier (image, document, audio, video)
            original_filename: Original filename with extension
            preview: If True, don't register filename (no side effects)

        Returns:
            GeneratedFilename with generated name and metadata

        Raises:
            ValueError: If metadata or file_type is invalid
            RuntimeError: If filename generation fails
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def register_filename(self, filename: str) -> None:
        """
        Register a filename to prevent future collisions.

        Args:
            filename: Filename to register in collision detector

        Raises:
            ValueError: If filename is invalid
        """
        raise NotImplementedError("Subclasses must implement register_filename()")

    def check_collision(self, filename: str) -> bool:
        """
        Check if a filename already exists in the vault.

        Args:
            filename: Filename to check

        Returns:
            True if filename already exists, False otherwise
        """
        raise NotImplementedError("Subclasses must implement check_collision()")


class NamingPatternEngine:
    """
    Interface for applying naming pattern templates.

    Contract:
    - MUST parse pattern templates with placeholders like {date}, {device}, etc.
    - MUST substitute placeholders with metadata values
    - MUST handle missing metadata gracefully
    - MUST support conditional components (omit if metadata missing)
    """

    def apply_pattern(
        self,
        pattern: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Apply naming pattern with metadata substitution.

        Args:
            pattern: Pattern template (e.g., "{date}-{time}-{device}-{size}")
            metadata: Metadata values for substitution

        Returns:
            Filename with placeholders substituted

        Raises:
            ValueError: If pattern is invalid
        """
        raise NotImplementedError("Subclasses must implement apply_pattern()")

    def get_available_components(self) -> List[str]:
        """
        Get list of available pattern components.

        Returns:
            List of component names that can be used in patterns
        """
        raise NotImplementedError("Subclasses must implement get_available_components()")

    def validate_pattern(self, pattern: str) -> bool:
        """
        Validate that a pattern is syntactically correct.

        Args:
            pattern: Pattern template to validate

        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate_pattern()")


class MetadataSanitizer:
    """
    Interface for sanitizing metadata values for filename use.

    Contract:
    - MUST remove or replace invalid filename characters
    - MUST handle platform-specific restrictions (Windows, macOS, Linux)
    - MUST normalize whitespace
    - MUST handle Unicode characters safely
    """

    def sanitize(self, value: str, component_name: str = None) -> str:
        """
        Sanitize a metadata value for safe filename use.

        Args:
            value: Metadata value to sanitize
            component_name: Optional component name for context-specific rules

        Returns:
            Sanitized string safe for filename use

        Raises:
            ValueError: If value cannot be sanitized
        """
        raise NotImplementedError("Subclasses must implement sanitize()")

    def get_invalid_characters(self) -> List[str]:
        """
        Get list of characters that are invalid in filenames.

        Returns:
            List of invalid characters
        """
        raise NotImplementedError("Subclasses must implement get_invalid_characters()")


class CollisionDetector:
    """
    Interface for detecting and resolving filename collisions.

    Contract:
    - MUST track existing filenames in vault
    - MUST generate 8-digit zero-padded counters (00000001, 00000002, etc.)
    - MUST ensure uniqueness across entire vault
    - MUST handle counter overflow gracefully
    """

    def check_collision(self, filename: str) -> bool:
        """
        Check if filename already exists.

        Args:
            filename: Filename to check

        Returns:
            True if collision detected, False otherwise
        """
        raise NotImplementedError("Subclasses must implement check_collision()")

    def resolve_collision(self, filename: str) -> str:
        """
        Resolve filename collision by adding counter.

        Args:
            filename: Base filename that has collision

        Returns:
            Unique filename with counter appended

        Raises:
            RuntimeError: If collision cannot be resolved
        """
        raise NotImplementedError("Subclasses must implement resolve_collision()")

    def register_filename(self, filename: str) -> None:
        """
        Register filename to prevent future collisions.

        Args:
            filename: Filename to register
        """
        raise NotImplementedError("Subclasses must implement register_filename()")


class LengthLimiter:
    """
    Interface for handling filename length limitations.

    Contract:
    - MUST enforce maximum filename length (default 255 characters)
    - MUST intelligently truncate while preserving essential components
    - MUST always preserve file extension
    - MUST prioritize components (date > device > resolution > category)
    """

    def limit_length(
        self,
        filename: str,
        max_length: int = 255
    ) -> str:
        """
        Enforce maximum filename length with intelligent truncation.

        Args:
            filename: Filename to check/truncate
            max_length: Maximum allowed length (default 255)

        Returns:
            Filename within length limit

        Raises:
            ValueError: If filename cannot be truncated to fit
        """
        raise NotImplementedError("Subclasses must implement limit_length()")

    def get_truncation_strategy(self) -> str:
        """
        Get description of truncation strategy used.

        Returns:
            Description of how components are prioritized for truncation
        """
        raise NotImplementedError("Subclasses must implement get_truncation_strategy()")
