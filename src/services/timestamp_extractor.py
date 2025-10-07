"""
Timestamp Extractor Implementation
Extracts and prioritizes timestamps from image metadata.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..models.image_metadata import TimestampCollection


class TimestampExtractorImpl:
    """
    Implementation of timestamp extraction from EXIF and file metadata.

    Handles various timestamp formats and sources, prioritizing based on
    reliability and relevance to the original creation time.
    """

    def __init__(self):
        """Initialize the timestamp extractor."""
        self.logger = logging.getLogger(__name__)

    def extract_timestamps(self, raw_exif: Dict[str, Any]) -> TimestampCollection:
        """
        Extract all timestamps from EXIF data.

        Args:
            raw_exif: Raw EXIF metadata dictionary

        Returns:
            TimestampCollection with all available timestamps
        """
        collection = TimestampCollection()

        # EXIF timestamps (preferred sources)
        collection.date_time_original = self._extract_timestamp(
            raw_exif, ["EXIF:DateTimeOriginal", "DateTimeOriginal"]
        )
        collection.create_date = self._extract_timestamp(
            raw_exif, ["EXIF:CreateDate", "CreateDate", "EXIF:DateTimeDigitized"]
        )
        collection.date_time_digitized = self._extract_timestamp(
            raw_exif, ["EXIF:DateTimeDigitized", "DateTimeDigitized"]
        )
        collection.modify_date = self._extract_timestamp(
            raw_exif, ["EXIF:ModifyDate", "ModifyDate"]
        )

        # File system timestamps (fallback)
        collection.file_create_date = self._extract_timestamp(
            raw_exif, ["File:FileCreateDate", "FileCreateDate"]
        )
        collection.file_modify_date = self._extract_timestamp(
            raw_exif, ["File:FileModifyDate", "FileModifyDate"]
        )
        collection.file_access_date = self._extract_timestamp(
            raw_exif, ["File:FileAccessDate", "FileAccessDate"]
        )

        # GPS timestamp
        collection.gps_date_time = self._extract_timestamp(
            raw_exif, ["EXIF:GPSDateStamp", "Composite:GPSDateTime", "GPSDateTime"]
        )

        # Timezone information
        collection.offset_time = self._extract_string(
            raw_exif, ["EXIF:OffsetTime", "OffsetTime"]
        )
        collection.offset_time_original = self._extract_string(
            raw_exif, ["EXIF:OffsetTimeOriginal", "OffsetTimeOriginal"]
        )

        return collection

    def parse_exif_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse EXIF datetime string to Python datetime.

        Handles various EXIF datetime formats:
        - "YYYY:MM:DD HH:MM:SS"
        - "YYYY:MM:DD HH:MM:SS.fff"
        - "YYYY:MM:DD HH:MM:SS+HH:MM"
        - "YYYY-MM-DD HH:MM:SS"

        Args:
            datetime_str: EXIF datetime string

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not datetime_str or not isinstance(datetime_str, str):
            return None

        # Clean up the string
        datetime_str = datetime_str.strip()

        # Try various EXIF datetime formats
        formats = [
            "%Y:%m:%d %H:%M:%S",  # Standard EXIF format
            "%Y:%m:%d %H:%M:%S.%f",  # With subseconds
            "%Y-%m-%d %H:%M:%S",  # ISO format
            "%Y-%m-%d %H:%M:%S.%f",  # ISO with subseconds
            "%Y:%m:%d %H:%M:%S%z",  # With timezone
            "%Y-%m-%d %H:%M:%S%z",  # ISO with timezone
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        # Try parsing with timezone offset separately
        if '+' in datetime_str or datetime_str.count('-') > 2:
            try:
                # Remove timezone info and parse
                dt_part = datetime_str.split('+')[0].split('-')[0:3]
                dt_str = '-'.join(dt_part) if '-' in datetime_str else datetime_str.split('+')[0]
                return self.parse_exif_datetime(dt_str.strip())
            except Exception:
                pass

        self.logger.warning(f"Failed to parse datetime: {datetime_str}")
        return None

    def get_timestamp_priority_order(self) -> List[str]:
        """
        Get the priority order for timestamp selection.

        Returns:
            List of timestamp field names in priority order
        """
        return [
            "DateTimeOriginal",  # When photo was taken
            "CreateDate",  # When file was created
            "DateTimeDigitized",  # When scanned/digitized
            "ModifyDate",  # When file was modified (EXIF)
            "FileCreateDate",  # File system create date
            "FileModifyDate",  # File system modify date
        ]

    def _extract_timestamp(
        self,
        raw_exif: Dict[str, Any],
        tag_names: List[str]
    ) -> Optional[datetime]:
        """
        Extract timestamp from EXIF trying multiple tag names.

        Args:
            raw_exif: Raw EXIF dictionary
            tag_names: List of possible tag names to try

        Returns:
            Parsed datetime or None
        """
        for tag_name in tag_names:
            value = raw_exif.get(tag_name)
            if value:
                parsed = self.parse_exif_datetime(str(value))
                if parsed:
                    return parsed
        return None

    def _extract_string(
        self,
        raw_exif: Dict[str, Any],
        tag_names: List[str]
    ) -> Optional[str]:
        """
        Extract string value from EXIF trying multiple tag names.

        Args:
            raw_exif: Raw EXIF dictionary
            tag_names: List of possible tag names to try

        Returns:
            String value or None
        """
        for tag_name in tag_names:
            value = raw_exif.get(tag_name)
            if value:
                return str(value)
        return None
