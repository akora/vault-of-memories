"""
Priority-based metadata conflict resolution.

Applies configurable priority rules to resolve conflicts when multiple sources
provide different values for the same metadata field.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.consolidated_metadata import MetadataSource, MetadataField


logger = logging.getLogger(__name__)


class PriorityResolver:
    """
    Resolve metadata conflicts using priority rules.

    Applies configurable priority ordering to select the most reliable value
    when multiple sources provide conflicting information.
    """

    # Default priority order (highest to lowest)
    DEFAULT_PRIORITY = [
        MetadataSource.EXIF,
        MetadataSource.EMBEDDED,
        MetadataSource.FILENAME,
        MetadataSource.FILESYSTEM,
        MetadataSource.INFERRED,
        MetadataSource.DEFAULT
    ]

    # Source reliability weights for confidence scoring
    SOURCE_WEIGHTS = {
        MetadataSource.EXIF: 1.0,
        MetadataSource.EMBEDDED: 0.9,
        MetadataSource.FILENAME: 0.6,
        MetadataSource.FILESYSTEM: 0.4,
        MetadataSource.INFERRED: 0.3,
        MetadataSource.DEFAULT: 0.2
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize priority resolver.

        Args:
            config_path: Optional path to priority configuration file
        """
        self.field_priorities = {}  # Field-specific priority overrides
        self.default_priority = self.DEFAULT_PRIORITY.copy()

        if config_path and config_path.exists():
            self._load_config(config_path)

    def resolve_field(self, field_name: str, sources: Dict[MetadataSource, Any]) -> MetadataField:
        """
        Resolve conflicts for a specific metadata field.

        Selects the value from the highest-priority source that has a non-None value.

        Args:
            field_name: Name of the metadata field
            sources: Dictionary mapping source to value

        Returns:
            MetadataField with resolved value and source

        Raises:
            ValueError: If no valid sources provided
        """
        if not sources:
            raise ValueError(f"No sources provided for field '{field_name}'")

        # Filter out None values
        valid_sources = {source: value for source, value in sources.items() if value is not None}

        if not valid_sources:
            raise ValueError(f"All sources have None values for field '{field_name}'")

        # Get priority order for this field
        priority_order = self.get_priority_order(field_name)

        # Find highest priority source with a value
        selected_source = None
        selected_value = None

        for source in priority_order:
            if source in valid_sources:
                selected_source = source
                selected_value = valid_sources[source]
                break

        # If no source in priority order, use first available (should not happen)
        if selected_source is None:
            selected_source = next(iter(valid_sources.keys()))
            selected_value = valid_sources[selected_source]
            logger.warning(
                f"No priority match for field '{field_name}', "
                f"using source: {selected_source.value}"
            )

        # Log conflicts if multiple sources provided values
        if len(valid_sources) > 1:
            conflict_sources = [s.value for s in valid_sources.keys() if s != selected_source]
            logger.debug(
                f"Resolved conflict for '{field_name}': "
                f"selected {selected_source.value} over {conflict_sources}"
            )

        # Calculate confidence based on source reliability
        confidence = self.SOURCE_WEIGHTS.get(selected_source, 0.5)

        return MetadataField(
            value=selected_value,
            source=selected_source,
            confidence=confidence,
            notes=f"Resolved from {len(valid_sources)} source(s)" if len(valid_sources) > 1 else None
        )

    def get_priority_order(self, field_name: str) -> List[MetadataSource]:
        """
        Get priority order for a specific field.

        Checks for field-specific overrides first, falls back to default priority.

        Args:
            field_name: Name of the metadata field

        Returns:
            List of MetadataSource in priority order (highest to lowest)
        """
        # Check for field-specific priority override
        if field_name in self.field_priorities:
            return self.field_priorities[field_name]

        # Return default priority
        return self.default_priority

    def set_field_priority(self, field_name: str, priority_order: List[MetadataSource]) -> None:
        """
        Set custom priority order for a specific field.

        Args:
            field_name: Name of the metadata field
            priority_order: List of MetadataSource in desired priority order
        """
        self.field_priorities[field_name] = priority_order
        logger.info(f"Set custom priority for field '{field_name}': {[s.value for s in priority_order]}")

    def _load_config(self, config_path: Path) -> None:
        """
        Load priority configuration from JSON file.

        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Load default priority if specified
            if "default_priority" in config:
                self.default_priority = [
                    MetadataSource(source) for source in config["default_priority"]
                ]
                logger.info(f"Loaded default priority from config: {[s.value for s in self.default_priority]}")

            # Load field-specific priorities
            if "field_priorities" in config:
                for field_name, source_list in config["field_priorities"].items():
                    priority_order = [MetadataSource(source) for source in source_list]
                    self.field_priorities[field_name] = priority_order
                    logger.debug(f"Loaded priority for '{field_name}': {[s.value for s in priority_order]}")

        except Exception as e:
            logger.error(f"Failed to load priority config from {config_path}: {e}")
            raise

    def detect_conflicts(self, sources: Dict[MetadataSource, Any]) -> bool:
        """
        Check if there are conflicting values from different sources.

        Args:
            sources: Dictionary mapping source to value

        Returns:
            True if multiple sources have different non-None values
        """
        valid_values = [v for v in sources.values() if v is not None]
        if len(valid_values) <= 1:
            return False

        # Check if all values are equal
        first_value = valid_values[0]
        return not all(v == first_value for v in valid_values)
