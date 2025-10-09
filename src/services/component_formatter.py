"""
Component formatter for metadata values.

Formats metadata values for safe and consistent filename use.
"""

import logging
from typing import Any
from datetime import datetime


logger = logging.getLogger(__name__)


class ComponentFormatter:
    """
    Format metadata values for filename components.

    Handles type conversion, truncation, and formatting rules for
    different types of metadata.
    """

    def format_date(self, value: Any) -> str:
        """
        Format a date for filename use (YYYYMMDD).

        Args:
            value: Date/datetime object or string

        Returns:
            Formatted date string
        """
        if isinstance(value, datetime):
            return value.strftime("%Y%m%d")
        elif isinstance(value, str):
            # Try to parse ISO format
            try:
                # Handle both naive and timezone-aware datetimes
                dt_str = value.replace('Z', '+00:00')
                if 'T' in dt_str:
                    parsed = datetime.fromisoformat(dt_str)
                    return parsed.strftime("%Y%m%d")
                else:
                    # Already in simple format, clean it up
                    return value.replace('-', '').replace(':', '').replace(' ', '')[:8]
            except Exception as e:
                logger.debug(f"Could not parse date '{value}': {e}")
                # Clean up whatever we have
                cleaned = ''.join(c for c in value if c.isdigit())
                return cleaned[:8] if cleaned else "00000000"
        return str(value)

    def format_time(self, value: Any) -> str:
        """
        Format a time for filename use (HHMMSS).

        Args:
            value: Time/datetime object or string

        Returns:
            Formatted time string
        """
        if isinstance(value, datetime):
            return value.strftime("%H%M%S")
        elif isinstance(value, str):
            # Try to parse ISO format
            try:
                dt_str = value.replace('Z', '+00:00')
                if 'T' in dt_str:
                    parsed = datetime.fromisoformat(dt_str)
                    return parsed.strftime("%H%M%S")
                else:
                    # Clean up time string
                    return value.replace(':', '')[-6:]
            except Exception as e:
                logger.debug(f"Could not parse time '{value}': {e}")
                # Clean up whatever we have
                cleaned = ''.join(c for c in value if c.isdigit())
                return cleaned[-6:] if len(cleaned) >= 6 else "000000"
        return str(value)

    def format_size_kb(self, size_bytes: int) -> int:
        """
        Format file size in kilobytes.

        Args:
            size_bytes: Size in bytes

        Returns:
            Size in KB (rounded)
        """
        return int(size_bytes / 1024) if size_bytes else 0

    def format_size_mb(self, size_bytes: int) -> int:
        """
        Format file size in megabytes.

        Args:
            size_bytes: Size in bytes

        Returns:
            Size in MB (rounded)
        """
        return int(size_bytes / (1024 * 1024)) if size_bytes else 0

    def format_resolution(self, width: int, height: int) -> str:
        """
        Format resolution as widthxheight.

        Args:
            width: Image/video width
            height: Image/video height

        Returns:
            Resolution string (e.g., "1920x1080")
        """
        return f"{width}x{height}" if width and height else ""

    def format_device_name(self, name: str, max_length: int = 20) -> str:
        """
        Format device/camera name for filename use.

        Args:
            name: Device or camera name
            max_length: Maximum length for device name

        Returns:
            Formatted and truncated device name
        """
        if not name:
            return ""

        # Remove common suffixes
        cleaned = name.strip()
        for suffix in [" Corporation", " Inc.", " Ltd."]:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)]

        # Truncate if too long
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned.strip()

    def format_counter(self, counter: int) -> str:
        """
        Format collision counter with 8-digit zero-padding.

        Args:
            counter: Counter value (1-based)

        Returns:
            Zero-padded counter string (e.g., "00000001")
        """
        return f"{counter:08d}"

    def truncate_middle(self, value: str, max_length: int) -> str:
        """
        Truncate string in the middle, keeping start and end.

        Args:
            value: String to truncate
            max_length: Maximum length

        Returns:
            Truncated string with "..." in middle
        """
        if len(value) <= max_length:
            return value

        if max_length < 5:
            return value[:max_length]

        # Keep more of the start than end
        ellipsis = "..."
        remaining = max_length - len(ellipsis)
        start_len = remaining * 2 // 3
        end_len = remaining - start_len

        return value[:start_len] + ellipsis + value[-end_len:] if end_len > 0 else value[:start_len] + ellipsis

    def format_duration_short(self, duration_seconds: float) -> str:
        """
        Format duration for compact filename use (e.g., "45s", "2m30s").

        Args:
            duration_seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if not duration_seconds:
            return ""

        duration = int(duration_seconds)

        if duration < 60:
            return f"{duration}s"
        elif duration < 3600:
            minutes = duration // 60
            seconds = duration % 60
            return f"{minutes}m{seconds}s" if seconds > 0 else f"{minutes}m"
        else:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            return f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h"

    def format_resolution_label(self, label: str) -> str:
        """
        Clean up resolution label for compact filename use.

        Converts "Custom 4096x2160" → "4K"
        Converts "1080p" → "1080p" (unchanged)

        Args:
            label: Resolution label from video processor

        Returns:
            Clean resolution label
        """
        if not label:
            return ""

        # Remove "Custom " prefix
        if label.startswith("Custom "):
            label = label[7:]

        # Convert specific resolutions to standard labels
        resolution_map = {
            "3840x2160": "4K",
            "4096x2160": "4K",
            "1920x1080": "1080p",
            "1280x720": "720p",
            "2560x1440": "1440p",
            "7680x4320": "8K"
        }

        return resolution_map.get(label, label)

    def format_fps(self, fps: float) -> str:
        """
        Format frame rate for filename use (e.g., "60", "30", "24").

        Args:
            fps: Frames per second

        Returns:
            Integer fps string
        """
        if not fps:
            return ""
        return str(int(round(fps)))
