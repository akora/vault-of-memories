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
        "image": "{date_compact}-{time_compact}-{device_make}-{device_model}-ir{resolution}-s{size_kb}",
        "document": "{date}-{time}-{title}-p{page_count}-s{size_kb}",
        "audio": "{date}-{artist}-{title}-br{bitrate}",
        "video": "{date_compact}-{time_compact}-{resolution_label}-{fps}p-{duration_short}-{device_make}-{device_model}",
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

        # Check if filename is insufficient (metadata was mostly missing)
        # Count how many meaningful components we got from the pattern
        import re
        # Count placeholder-like patterns that were filled
        placeholders_in_pattern = len(re.findall(r'\{([^}]+)\}', pattern))
        # Count meaningful words/identifiers in result (not just size/page numbers)
        meaningful_parts = [p for p in re.split(r'[-_\s]+', base_filename)
                          if p and not p.startswith(('s', 'p', 'br', 'ir')) and len(p) > 2]

        # If we have a pattern with many placeholders but got very few meaningful results,
        # fall back to original filename
        if placeholders_in_pattern >= 3 and len(meaningful_parts) == 0:
            # Fallback to original filename when metadata is insufficient
            logger.warning(f"Pattern resulted in insufficient filename ('{base_filename}'), using original")
            base_filename = original_path.stem
        elif not base_filename:
            # Complete fallback for empty results
            logger.warning("Pattern resulted in empty filename, using original")
            base_filename = original_path.stem

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
        prepared = {}

        # Extract values from MetadataField objects/dicts
        # The pattern engine expects raw values, not MetadataField wrappers
        for key, value in metadata.items():
            # Handle MetadataField objects
            if hasattr(value, 'value'):
                prepared[key] = value.value
            # Handle MetadataField dicts (from asdict conversion)
            elif isinstance(value, dict) and 'value' in value:
                prepared[key] = value['value']
            else:
                prepared[key] = value

        # Format dates for pattern engine's COMPONENT_FORMATTERS
        # The pattern engine's "date" formatter looks for creation_date/capture_date/modification_date
        # and expects them to be datetime objects that it can format
        for date_field in ["creation_date", "capture_date", "modification_date"]:
            if date_field in prepared and prepared[date_field]:
                dt_value = prepared[date_field]
                # If it's already a datetime, the ComponentFormatter will handle it
                # Just make sure it's not still wrapped
                if hasattr(dt_value, 'value'):
                    prepared[date_field] = dt_value.value
                elif isinstance(dt_value, dict) and 'value' in dt_value:
                    prepared[date_field] = dt_value['value']

        # Apply special formatting for video-specific components
        if 'duration' in prepared and prepared['duration']:
            prepared['duration_short'] = self.formatter.format_duration_short(prepared['duration'])

        if 'fps' in prepared and prepared['fps']:
            prepared['fps'] = self.formatter.format_fps(prepared['fps'])

        if 'resolution_label' in prepared and prepared['resolution_label']:
            prepared['resolution_label'] = self.formatter.format_resolution_label(prepared['resolution_label'])

        # Format compact date/time from the date fields
        for date_field in ["creation_date", "capture_date", "modification_date"]:
            if date_field in prepared and prepared[date_field]:
                if 'date_compact' not in prepared or not prepared['date_compact']:
                    prepared['date_compact'] = self.formatter.format_date(prepared[date_field])
                if 'time_compact' not in prepared or not prepared['time_compact']:
                    prepared['time_compact'] = self.formatter.format_time(prepared[date_field])

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
