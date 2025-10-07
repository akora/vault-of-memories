"""
Timezone preservation service.

Handles timezone-aware datetime parsing and preservation without UTC conversion.
Maintains original timezone context from metadata sources.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..models.consolidated_metadata import MetadataSource


logger = logging.getLogger(__name__)


class TimezonePreserver:
    """
    Preserve timezone information without UTC conversion.

    Parses timestamps from various sources and maintains their original timezone
    context. Never converts to UTC to preserve the original time context.
    """

    def preserve_timezone(self, timestamp: Any, source: MetadataSource) -> datetime:
        """
        Preserve timezone information from original timestamp.

        Args:
            timestamp: Original timestamp (may be string, datetime, etc.)
            source: Source of the timestamp

        Returns:
            Timezone-aware datetime with original timezone preserved

        Raises:
            ValueError: If timestamp format is invalid
        """
        if timestamp is None:
            raise ValueError("Timestamp cannot be None")

        # Already a timezone-aware datetime
        if isinstance(timestamp, datetime) and timestamp.tzinfo is not None:
            return timestamp

        # Naive datetime - try to infer timezone
        if isinstance(timestamp, datetime):
            logger.debug(f"Naive datetime from {source.value}, storing without timezone")
            return timestamp  # Return as-is, don't force a timezone

        # String timestamp - parse it
        if isinstance(timestamp, str):
            return self._parse_timestamp_string(timestamp, source)

        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")

    def extract_timezone(self, timestamp: Any) -> Optional[str]:
        """
        Extract timezone information from timestamp.

        Args:
            timestamp: Timestamp to analyze

        Returns:
            Timezone string (e.g., "America/New_York") or None
        """
        if isinstance(timestamp, datetime) and timestamp.tzinfo is not None:
            # Try to get zone name
            tzinfo = timestamp.tzinfo
            if hasattr(tzinfo, "key"):
                return tzinfo.key
            elif hasattr(tzinfo, "zone"):
                return tzinfo.zone
            else:
                # For fixed offset timezones, return offset representation
                return str(tzinfo)

        return None

    def _parse_timestamp_string(self, timestamp_str: str, source: MetadataSource) -> datetime:
        """
        Parse timestamp string with timezone awareness.

        Handles multiple common formats while preserving original timezone.

        Args:
            timestamp_str: Timestamp string to parse
            source: Source of the timestamp

        Returns:
            Parsed datetime with timezone if available

        Raises:
            ValueError: If timestamp format is invalid
        """
        timestamp_str = timestamp_str.strip()

        # Try ISO 8601 format with timezone
        formats_with_tz = [
            "%Y-%m-%dT%H:%M:%S%z",  # 2023-12-25T14:30:22+0100
            "%Y-%m-%d %H:%M:%S%z",  # 2023-12-25 14:30:22+0100
            "%Y:%m:%d %H:%M:%S%z",  # EXIF format with timezone
        ]

        for fmt in formats_with_tz:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                logger.debug(f"Parsed timestamp with timezone from {source.value}: {dt.tzinfo}")
                return dt
            except ValueError:
                continue

        # Try ISO 8601 format without timezone
        formats_no_tz = [
            "%Y-%m-%dT%H:%M:%S",  # 2023-12-25T14:30:22
            "%Y-%m-%d %H:%M:%S",  # 2023-12-25 14:30:22
            "%Y:%m:%d %H:%M:%S",  # EXIF format: 2023:12:25 14:30:22
        ]

        for fmt in formats_no_tz:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                logger.debug(f"Parsed naive timestamp from {source.value}, no timezone info")
                return dt
            except ValueError:
                continue

        # Try with milliseconds
        formats_with_ms = [
            "%Y-%m-%dT%H:%M:%S.%f",  # 2023-12-25T14:30:22.123456
            "%Y-%m-%d %H:%M:%S.%f",  # 2023-12-25 14:30:22.123456
        ]

        for fmt in formats_with_ms:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt
            except ValueError:
                continue

        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

    def apply_timezone(self, naive_dt: datetime, tz_name: str) -> datetime:
        """
        Apply a timezone to a naive datetime.

        Args:
            naive_dt: Naive datetime object
            tz_name: Timezone name (e.g., "America/New_York")

        Returns:
            Timezone-aware datetime

        Raises:
            ValueError: If timezone name is invalid
        """
        if naive_dt.tzinfo is not None:
            logger.warning(f"Datetime already has timezone: {naive_dt.tzinfo}")
            return naive_dt

        try:
            tz = ZoneInfo(tz_name)
            return naive_dt.replace(tzinfo=tz)
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone name: {tz_name}")

    def is_timezone_aware(self, dt: datetime) -> bool:
        """
        Check if datetime object is timezone-aware.

        Args:
            dt: Datetime object to check

        Returns:
            True if timezone-aware, False if naive
        """
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None
