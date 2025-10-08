"""
T029: Enumerations for Organization Manager.
"""

from enum import Enum


class PrimaryCategory(Enum):
    """Primary content categories for vault organization."""
    PHOTOS = "photos"
    DOCUMENTS = "documents"
    VIDEOS = "videos"
    AUDIO = "audio"
    ARCHIVES = "archives"
    OTHER = "other"


class DateSource(Enum):
    """Sources for date extraction."""
    EXIF_DATETIME_ORIGINAL = "exif_datetime_original"
    FILE_CREATION_TIME = "file_creation_time"
    FILE_MODIFICATION_TIME = "file_modification_time"
    FILENAME_PARSING = "filename_parsing"
    FALLBACK_CURRENT_TIME = "fallback_current_time"


class ExecutionStatus(Enum):
    """Status of organization execution."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class DetectionMethod(Enum):
    """Methods for MIME type detection."""
    LIBMAGIC = "libmagic"
    EXTENSION = "extension"
    HEADER_INSPECTION = "header_inspection"
    FALLBACK = "fallback"
