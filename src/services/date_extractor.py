"""
T032: DateExtractor - Extract dates with fallback cascade (EXIF → creation → modification → filename).
"""

from pathlib import Path
from datetime import datetime, date, timezone, timedelta
import platform
import logging
from typing import Any
from ..models.date_info import DateInfo
from .filename_date_parser import FilenameDateParser


logger = logging.getLogger(__name__)


class DateExtractor:
    """Extracts dates from files using cascading fallback strategy."""

    def __init__(self):
        self.filename_parser = FilenameDateParser()

    def extract_date(self, file_path: Path, metadata: dict[str, Any]) -> DateInfo:
        """
        Extract date using fallback cascade.

        Fallback order:
        1. EXIF DateTimeOriginal (photos/videos)
        2. Embedded document metadata (PDF/Office creation date)
        3. Embedded capture date (videos)
        4. File creation time
        5. File modification time
        6. Filename date parsing
        7. Current time (last resort)

        Args:
            file_path: Path to file
            metadata: File metadata including EXIF data

        Returns:
            DateInfo with UTC datetime and source information
        """
        # Level 1: EXIF DateTimeOriginal
        date_info = self._extract_exif_datetime(metadata)
        if date_info:
            return date_info

        # Level 2: Embedded document metadata (PDF, Office documents)
        date_info = self._extract_embedded_creation_date(metadata)
        if date_info:
            return date_info

        # Level 3: Embedded capture date (videos)
        date_info = self._extract_capture_date(metadata)
        if date_info:
            return date_info

        # Level 4: File creation time
        date_info = self._extract_creation_time(file_path)
        if date_info:
            return date_info

        # Level 3: File modification time
        date_info = self._extract_modification_time(file_path)
        if date_info:
            return date_info

        # Level 4: Filename date parsing
        date_info = self._parse_filename_date(file_path)
        if date_info:
            return date_info

        # Level 5: Fallback to current time
        logger.warning(f"No date found for {file_path}, using current time")
        now = datetime.now(timezone.utc)
        return DateInfo(
            datetime_utc=now,
            source="fallback_current_time",
            timezone_info=None,
            original_local_date=now.date(),
            confidence=0.0
        )

    def _extract_exif_datetime(self, metadata: dict[str, Any]) -> DateInfo | None:
        """Level 1: Extract EXIF DateTimeOriginal."""
        datetime_str = metadata.get('datetime_original')
        if not datetime_str:
            return None

        try:
            # EXIF format: "YYYY:MM:DD HH:MM:SS"
            dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')

            # Check for OffsetTimeOriginal (timezone info)
            offset_str = metadata.get('offset_time_original')
            if offset_str:
                dt = self._apply_timezone_offset(dt, offset_str)
            else:
                dt = dt.replace(tzinfo=timezone.utc)

            logger.debug(f"Extracted EXIF DateTimeOriginal: {dt}")
            return DateInfo(
                datetime_utc=dt.astimezone(timezone.utc),
                source="exif_datetime_original",
                timezone_info=f"offset_{offset_str}" if offset_str else "assumed_utc",
                original_local_date=dt.date(),
                confidence=0.95
            )

        except (ValueError, AttributeError) as e:
            logger.debug(f"Failed to parse EXIF datetime '{datetime_str}': {e}")
            return None

    def _extract_embedded_creation_date(self, metadata: dict[str, Any]) -> DateInfo | None:
        """Level 2: Extract embedded creation date from document/media metadata."""
        # Check for consolidated metadata creation_date field
        creation_date = metadata.get('creation_date')
        if not creation_date:
            return None

        try:
            # Handle MetadataField objects (from consolidated metadata)
            if hasattr(creation_date, 'value'):
                dt = creation_date.value
                source = creation_date.source
            # Handle dict format
            elif isinstance(creation_date, dict) and 'value' in creation_date:
                dt = creation_date['value']
                source = creation_date.get('source', 'embedded')
            else:
                dt = creation_date
                source = 'embedded'

            # Convert to datetime if needed
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            elif isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time()).replace(tzinfo=timezone.utc)

            # Ensure timezone aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Only use if source is embedded (not filesystem)
            source_str = str(source).lower()
            if 'filesystem' in source_str or 'file_' in source_str:
                return None

            logger.debug(f"Extracted embedded creation date: {dt}")
            return DateInfo(
                datetime_utc=dt.astimezone(timezone.utc),
                source="embedded_creation_date",
                timezone_info="from_metadata",
                original_local_date=dt.date(),
                confidence=0.9
            )

        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse embedded creation date: {e}")
            return None

    def _extract_capture_date(self, metadata: dict[str, Any]) -> DateInfo | None:
        """Level 3: Extract capture/recording date from video metadata."""
        # Check for capture_date or recording_date
        capture_date = metadata.get('capture_date') or metadata.get('recording_date')
        if not capture_date:
            return None

        try:
            # Handle MetadataField objects
            if hasattr(capture_date, 'value'):
                dt = capture_date.value
            elif isinstance(capture_date, dict) and 'value' in capture_date:
                dt = capture_date['value']
            else:
                dt = capture_date

            # Convert to datetime if needed
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            elif isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time()).replace(tzinfo=timezone.utc)

            # Ensure timezone aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            logger.debug(f"Extracted capture date: {dt}")
            return DateInfo(
                datetime_utc=dt.astimezone(timezone.utc),
                source="capture_date",
                timezone_info="from_metadata",
                original_local_date=dt.date(),
                confidence=0.9
            )

        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse capture date: {e}")
            return None

    def _extract_creation_time(self, file_path: Path) -> DateInfo | None:
        """Level 2: Extract file creation time."""
        if not file_path.exists():
            return None

        try:
            stat_info = file_path.stat()

            # Platform-specific creation time
            if platform.system() == 'Windows':
                timestamp = stat_info.st_ctime
            elif platform.system() == 'Darwin':  # macOS
                timestamp = stat_info.st_birthtime
            else:  # Linux
                return None  # st_ctime is metadata change time on Linux

            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            logger.debug(f"Extracted file creation time: {dt}")
            return DateInfo(
                datetime_utc=dt,
                source="file_creation_time",
                timezone_info="system_local_to_utc",
                original_local_date=dt.date(),
                confidence=0.8
            )

        except (AttributeError, OSError) as e:
            logger.debug(f"Failed to get creation time for {file_path}: {e}")
            return None

    def _extract_modification_time(self, file_path: Path) -> DateInfo | None:
        """Level 3: Extract file modification time."""
        if not file_path.exists():
            return None

        try:
            stat_info = file_path.stat()
            timestamp = stat_info.st_mtime

            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            logger.debug(f"Extracted file modification time: {dt}")
            return DateInfo(
                datetime_utc=dt,
                source="file_modification_time",
                timezone_info="system_local_to_utc",
                original_local_date=dt.date(),
                confidence=0.6
            )

        except OSError as e:
            logger.debug(f"Failed to get modification time for {file_path}: {e}")
            return None

    def _parse_filename_date(self, file_path: Path) -> DateInfo | None:
        """Level 4: Parse date from filename."""
        dt = self.filename_parser.parse(file_path.stem)
        if dt:
            return DateInfo(
                datetime_utc=dt,
                source="filename_parsing",
                timezone_info="assumed_utc",
                original_local_date=dt.date(),
                confidence=0.7
            )
        return None

    def _apply_timezone_offset(self, dt: datetime, offset_str: str) -> datetime:
        """Apply timezone offset to naive datetime."""
        try:
            # Parse offset like "+05:30" or "-08:00"
            sign = 1 if offset_str[0] == '+' else -1
            hours, minutes = map(int, offset_str[1:].split(':'))

            offset = timedelta(hours=sign * hours, minutes=sign * minutes)
            tz = timezone(offset)
            return dt.replace(tzinfo=tz)

        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse timezone offset '{offset_str}': {e}")
            return dt.replace(tzinfo=timezone.utc)

    def parse_filename_date(self, filename: str) -> datetime | None:
        """Public method for parsing filename dates."""
        return self.filename_parser.parse(filename)

    def extract_batch(
        self,
        file_paths: list[Path],
        metadata_dict: dict[Path, dict[str, Any]]
    ) -> dict[Path, DateInfo]:
        """Extract dates for multiple files efficiently."""
        results = {}
        for file_path in file_paths:
            metadata = metadata_dict.get(file_path, {})
            results[file_path] = self.extract_date(file_path, metadata)
        return results
