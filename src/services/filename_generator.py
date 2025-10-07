"""
Filename generator service.

Main orchestration service for generating standardized filenames from metadata
using configurable patterns, collision detection, and length limiting.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.generated_filename import GeneratedFilename
from .naming_pattern_engine import NamingPatternEngine
from .component_formatter import ComponentFormatter
from .metadata_sanitizer import MetadataSanitizer
from .collision_detector import CollisionDetector
from .length_limiter import LengthLimiter


logger = logging.getLogger(__name__)


class FilenameGenerator:
    """
    Generate standardized filenames from metadata.

    Orchestrates:
    - Pattern application with metadata
    - Metadata sanitization
    - Collision detection and resolution
    - Length limiting
    """

    # Default naming patterns by file type
    DEFAULT_PATTERNS = {
        "image": "{date}-{time}-{device_make}-{device_model}-ir{resolution}-s{size_kb}",
        "document": "{date}-{title}-p{page_count}-s{size_kb}",
        "audio": "{date}-{artist}-{title}-br{bitrate}",
        "video": "{date}-{time}-{resolution_label}-{category}-s{size_mb}",
        "unknown": "{date}-{checksum_short}-{size_kb}"
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize filename generator.

        Args:
            config_path: Optional path to naming patterns configuration
        """
        self.pattern_engine = NamingPatternEngine()
        self.formatter = ComponentFormatter()
        self.sanitizer = MetadataSanitizer()
        self.collision_detector = CollisionDetector()
        self.length_limiter = LengthLimiter()

        # Load patterns from config or use defaults
        self.patterns = self.DEFAULT_PATTERNS.copy()
        if config_path and config_path.exists():
            self._load_patterns(config_path)

        logger.info("FilenameGenerator initialized")

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
        if not metadata:
            raise ValueError("Metadata cannot be empty")

        if file_type not in self.patterns:
            logger.warning(f"Unknown file type '{file_type}', using 'unknown' pattern")
            file_type = "unknown"

        logger.info(f"Generating filename for {original_filename} (type: {file_type})")

        # Get pattern for this file type
        pattern = self.patterns[file_type]

        # Extract extension from original filename
        original_path = Path(original_filename)
        extension = original_path.suffix

        # Prepare metadata for pattern application
        prepared_metadata = self._prepare_metadata(metadata)

        # Apply pattern to get base filename
        base_filename = self.pattern_engine.apply_pattern(pattern, prepared_metadata)

        if not base_filename:
            # Fallback to checksum-based name
            logger.warning("Pattern resulted in empty filename, using fallback")
            checksum = metadata.get("checksum", "unknown")[:8]
            base_filename = f"{checksum}-{original_path.stem}"

        # Sanitize the base filename
        sanitized_chars = 0
        try:
            original_base = base_filename
            base_filename = self.sanitizer.sanitize(base_filename)
            sanitized_chars = self.sanitizer.get_sanitized_char_count(original_base, base_filename)
        except ValueError as e:
            logger.error(f"Sanitization failed: {e}")
            base_filename = "unnamed"

        # Sanitize extension
        clean_extension = self.sanitizer.sanitize_extension(extension)

        # Combine base and extension
        filename = base_filename + clean_extension

        # Check for collisions and resolve
        collision_counter = None
        if self.collision_detector.check_collision(filename):
            original_filename_attempt = filename
            filename = self.collision_detector.resolve_collision(filename)
            # Extract counter from resolved filename
            collision_counter = self.collision_detector.extract_counter(filename)
            logger.info(f"Collision resolved: {original_filename_attempt} → {filename}")

        # Apply length limiting
        truncated = False
        if self.length_limiter.needs_truncation(filename):
            filename = self.length_limiter.limit_length(filename)
            truncated = True

        # Register filename (unless preview mode)
        if not preview:
            self.collision_detector.register_filename(filename)

        # Build result
        result = GeneratedFilename(
            filename=filename,
            original_filename=original_filename,
            components_used=prepared_metadata,
            pattern_applied=pattern,
            collision_counter=collision_counter,
            truncated=truncated,
            sanitized_chars=sanitized_chars,
            generation_timestamp=datetime.now()
        )

        logger.info(f"Generated filename: {original_filename} → {filename}")

        return result

    def register_filename(self, filename: str) -> None:
        """
        Register a filename to prevent future collisions.

        Args:
            filename: Filename to register

        Raises:
            ValueError: If filename is invalid
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        self.collision_detector.register_filename(filename)

    def check_collision(self, filename: str) -> bool:
        """
        Check if a filename already exists in the vault.

        Args:
            filename: Filename to check

        Returns:
            True if filename already exists, False otherwise
        """
        return self.collision_detector.check_collision(filename)

    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for pattern application.

        Extracts and formats date/time components from metadata fields.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Prepared metadata with formatted components
        """
        prepared = metadata.copy()

        # Extract date/time from datetime fields
        for date_field in ["creation_date", "capture_date", "modification_date"]:
            if date_field in metadata and metadata[date_field]:
                dt_value = metadata[date_field]
                if hasattr(dt_value, 'value'):
                    # MetadataField object
                    dt_value = dt_value.value

                if dt_value:
                    prepared["date"] = self.formatter.format_date(dt_value)
                    prepared["time"] = self.formatter.format_time(dt_value)
                    break

        # Extract device info from MetadataField objects if present
        for field in ["device_make", "device_model", "title", "category", "author"]:
            if field in metadata and metadata[field]:
                value = metadata[field]
                if hasattr(value, 'value'):
                    prepared[field] = value.value
                else:
                    prepared[field] = value

        return prepared

    def _load_patterns(self, config_path: Path) -> None:
        """
        Load naming patterns from configuration file.

        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            if "naming_patterns" in config:
                self.patterns.update(config["naming_patterns"])
                logger.info(f"Loaded naming patterns from {config_path}")

        except Exception as e:
            logger.error(f"Failed to load patterns from {config_path}: {e}")
            # Continue with default patterns
