"""
T024: DateInfo data model.
"""

from dataclasses import dataclass
from datetime import datetime, date, timezone


@dataclass
class DateInfo:
    """Extracted date information with source and timezone details."""

    datetime_utc: datetime
    source: str
    timezone_info: str | None
    original_local_date: date
    confidence: float

    def __post_init__(self):
        """Validate date info after initialization."""
        # Ensure datetime has UTC timezone
        if self.datetime_utc.tzinfo is None:
            raise ValueError("datetime_utc must have timezone information")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

        valid_sources = {
            "exif_datetime_original",
            "file_creation_time",
            "file_modification_time",
            "filename_parsing",
            "fallback_current_time"
        }
        if self.source not in valid_sources:
            raise ValueError(f"Invalid source: {self.source}")
