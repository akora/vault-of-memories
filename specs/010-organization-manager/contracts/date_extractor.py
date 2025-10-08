"""
Contract: DateExtractor

Date extraction with multiple fallback sources.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class DateInfo:
    """Extracted date information."""
    datetime_utc: datetime
    source: str
    timezone_info: str | None
    original_local_date: date
    confidence: float


class DateExtractor:
    """
    Extracts dates from files using cascading fallback strategy.

    Responsibilities:
    - Extract date from EXIF metadata (photos/videos)
    - Extract date from filesystem (creation/modification time)
    - Parse date from filename
    - Handle timezone conversion to UTC
    - Provide date source and confidence
    """

    def extract_date(self, file_path: Path, metadata: Dict[str, Any]) -> DateInfo:
        """
        Extract date using fallback cascade.

        Fallback order:
        1. EXIF DateTimeOriginal (photos/videos)
        2. File creation time
        3. File modification time
        4. Filename date parsing
        5. Current time (last resort)

        Args:
            file_path: Path to file
            metadata: File metadata including EXIF data

        Returns:
            DateInfo with UTC datetime and source information

        Raises:
            ValueError: If file_path is invalid
            OSError: If file cannot be accessed

        Contract:
            - MUST try all fallback sources in priority order
            - MUST return valid datetime (never None)
            - datetime_utc MUST have UTC timezone
            - original_local_date MUST reflect date in original timezone (for folder names)
            - source MUST be one of: exif_datetime_original, file_creation_time,
              file_modification_time, filename_parsing, fallback_current_time
            - Confidence: EXIF (0.95), creation (0.8), modification (0.6),
              filename (0.7), fallback (0.0)
            - MUST log which source was used
            - MUST handle EXIF OffsetTimeOriginal for timezone-aware dates
        """
        raise NotImplementedError

    def parse_filename_date(self, filename: str) -> datetime | None:
        """
        Parse date from filename using multiple patterns.

        Supported patterns (priority order):
        1. ISO 8601: YYYY-MM-DD
        2. Compact: YYYYMMDD
        3. ISO with time: YYYY-MM-DD_HH-MM-SS
        4. European: DD-MM-YYYY (with warning)
        5. US: MM/DD/YYYY (with warning)

        Args:
            filename: Filename to parse (without path)

        Returns:
            Datetime if pattern matched, None otherwise

        Contract:
            - MUST prefer unambiguous formats (ISO 8601)
            - MUST log warning for ambiguous formats (DD-MM-YYYY vs MM-DD-YYYY)
            - MUST assume UTC timezone for parsed dates
            - MUST return None if no pattern matches
        """
        raise NotImplementedError

    def extract_batch(
        self,
        file_paths: list[Path],
        metadata_dict: Dict[Path, Dict[str, Any]]
    ) -> Dict[Path, DateInfo]:
        """
        Extract dates for multiple files efficiently.

        Args:
            file_paths: List of files
            metadata_dict: Metadata for each file

        Returns:
            Dictionary mapping file paths to date info

        Contract:
            - MUST handle batch processing efficiently
            - MUST NOT fail entire batch if one file fails
            - Failed files MUST return fallback_current_time with confidence 0.0
        """
        raise NotImplementedError
