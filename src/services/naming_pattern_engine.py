"""
Naming pattern engine for template-based filename generation.

Parses and applies pattern templates with metadata placeholders like
{date}, {device}, {size}, {resolution}, etc.
"""

import logging
import re
from typing import Dict, Any, List
from datetime import datetime


logger = logging.getLogger(__name__)


class NamingPatternEngine:
    """
    Parse and apply naming pattern templates.

    Supports placeholders like {date}, {time}, {device}, {size}, {resolution}
    with automatic metadata substitution and missing component handling.
    """

    # Available pattern components with formatting rules
    COMPONENT_FORMATTERS = {
        # Date/Time components
        "date": lambda m: m.get("date_compact"),  # Use pre-formatted compact date (YYYYMMDD)
        "date_compact": lambda m: m.get("date_compact"),  # Pre-formatted by FilenameGenerator
        "time": lambda m: m.get("time_compact"),  # Use pre-formatted compact time (HHMMSS)
        "time_compact": lambda m: m.get("time_compact"),  # Pre-formatted by FilenameGenerator
        "year": lambda m: m.get("year"),
        "month": lambda m: m.get("month"),
        "day": lambda m: m.get("day"),

        # Device components
        "device_make": lambda m: m.get("device_make"),
        "device_model": lambda m: m.get("device_model"),
        "device": lambda m: m.get("device_make") or m.get("device_model"),

        # Technical components
        "width": lambda m: m.get("width"),
        "height": lambda m: m.get("height"),
        "resolution": lambda m: f"{m.get('width')}x{m.get('height')}" if m.get("width") and m.get("height") else None,
        "resolution_label": lambda m: m.get("resolution_label"),

        # Size components
        "size_bytes": lambda m: m.get("file_size"),
        "size_kb": lambda m: max(1, int(m.get("file_size", 0) / 1024)) if m.get("file_size") else None,
        "size_mb": lambda m: int(m.get("file_size", 0) / (1024 * 1024)) if m.get("file_size") else None,

        # Content components
        "title": lambda m: m.get("title"),
        "category": lambda m: m.get("category", m.get("primary_category")),
        "author": lambda m: m.get("author"),

        # Audio/Video components
        "duration": lambda m: int(m.get("duration", 0)) if m.get("duration") else None,
        "duration_short": lambda m: m.get("duration_short"),  # Pre-formatted by FilenameGenerator
        "bitrate": lambda m: m.get("bitrate"),
        "fps": lambda m: m.get("fps"),  # Pre-formatted by FilenameGenerator (already an integer)
        "page_count": lambda m: m.get("page_count"),

        # Checksum
        "checksum_short": lambda m: m.get("checksum", "")[:8],
    }

    def apply_pattern(self, pattern: str, metadata: Dict[str, Any]) -> str:
        """
        Apply naming pattern with metadata substitution.

        Args:
            pattern: Pattern template (e.g., "{date}-{time}-{device}-{size_kb}")
            metadata: Metadata values for substitution

        Returns:
            Filename with placeholders substituted

        Raises:
            ValueError: If pattern is invalid
        """
        if not pattern:
            raise ValueError("Pattern cannot be empty")

        # Find all placeholders in pattern
        placeholders = re.findall(r'\{([^}]+)\}', pattern)

        result = pattern
        components_used = {}

        for placeholder in placeholders:
            # Get formatter for this component
            formatter = self.COMPONENT_FORMATTERS.get(placeholder)

            if formatter is None:
                logger.warning(f"Unknown placeholder: {{{placeholder}}}")
                # Remove unknown placeholders
                result = result.replace(f"{{{placeholder}}}", "")
                continue

            # Get value from metadata
            value = formatter(metadata)

            # Treat 0 as missing for certain optional fields
            # Note: size_kb now has min value of 1, so 0 won't occur
            if value == 0 and placeholder in ['page_count']:
                value = None

            if value is None:
                # Remove placeholder if no value available
                result = result.replace(f"{{{placeholder}}}", "")
                logger.debug(f"No value for placeholder: {{{placeholder}}}")
            else:
                # Format and substitute value
                formatted_value = str(value)
                result = result.replace(f"{{{placeholder}}}", formatted_value)
                components_used[placeholder] = formatted_value

        # Clean up multiple consecutive separators
        result = re.sub(r'[-_]{2,}', '-', result)

        # Remove orphaned prefixes (e.g., "p-" when page_count is missing, "ir-" when resolution is missing)
        # Match: single letter or two-letter prefix followed by hyphen or at end
        result = re.sub(r'-([a-z]{1,2})-', r'-', result)  # Middle: "-p-" or "-br-"
        result = re.sub(r'-([a-z]{1,2})$', r'', result)   # End: "-p" or "-br"

        # Remove leading/trailing separators
        result = result.strip('-_')

        return result

    def get_available_components(self) -> List[str]:
        """
        Get list of available pattern components.

        Returns:
            List of component names that can be used in patterns
        """
        return list(self.COMPONENT_FORMATTERS.keys())

    def validate_pattern(self, pattern: str) -> bool:
        """
        Validate that a pattern is syntactically correct.

        Args:
            pattern: Pattern template to validate

        Returns:
            True if valid, False otherwise
        """
        if not pattern:
            return False

        # Check for balanced braces
        if pattern.count('{') != pattern.count('}'):
            return False

        # Check that all placeholders are known
        placeholders = re.findall(r'\{([^}]+)\}', pattern)
        for placeholder in placeholders:
            if placeholder not in self.COMPONENT_FORMATTERS:
                logger.warning(f"Unknown component in pattern: {{{placeholder}}}")
                # Allow unknown components (they'll be removed during application)
                pass

        return True

    def format_date(self, dt: Any) -> str:
        """
        Format a date for filename use.

        Args:
            dt: Date/datetime object or string

        Returns:
            Formatted date string (YYYYMMDD)
        """
        if isinstance(dt, datetime):
            return dt.strftime("%Y%m%d")
        elif isinstance(dt, str):
            # Try to parse and reformat
            try:
                parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                return parsed.strftime("%Y%m%d")
            except:
                # Return as-is if can't parse
                return dt.replace('-', '').replace(':', '').replace(' ', '')[:8]
        return str(dt)

    def format_time(self, dt: Any) -> str:
        """
        Format a time for filename use.

        Args:
            dt: Time/datetime object or string

        Returns:
            Formatted time string (HHMMSS)
        """
        if isinstance(dt, datetime):
            return dt.strftime("%H%M%S")
        elif isinstance(dt, str):
            # Try to parse and reformat
            try:
                parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                return parsed.strftime("%H%M%S")
            except:
                # Return as-is if can't parse
                return dt.replace(':', '')[-6:]
        return str(dt)
