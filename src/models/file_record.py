"""
File Record Data Model
Represents a processed file with metadata for duplicate detection and tracking.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class ProcessingStatus(Enum):
    """File processing status enumeration."""
    PENDING = "pending"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    ERROR = "error"


@dataclass
class FileRecord:
    """
    Represents a processed file with all metadata needed for duplicate detection.

    Attributes:
        id: Database record ID (None for new records)
        file_path: Full path to the original file
        checksum: SHA-256 hash in hexadecimal format
        file_size: File size in bytes
        modification_time: Unix timestamp of file's last modification
        created_at: Unix timestamp when record was created
        status: Current processing status
    """
    id: Optional[int]
    file_path: Path
    checksum: str
    file_size: int
    modification_time: float
    created_at: float
    status: ProcessingStatus

    def __post_init__(self):
        """Validate data after initialization."""
        self._validate_checksum()
        self._validate_file_size()
        self._validate_timestamps()
        self._validate_file_path()

    def _validate_checksum(self):
        """Validate SHA-256 checksum format."""
        if not isinstance(self.checksum, str):
            raise ValueError("Checksum must be a string")

        if len(self.checksum) != 64:
            raise ValueError(
                f"SHA-256 checksum must be 64 characters, "
                f"got {len(self.checksum)}"
            )

        try:
            int(self.checksum, 16)
        except ValueError:
            raise ValueError("Checksum must be valid hexadecimal")

    def _validate_file_size(self):
        """Validate file size is non-negative."""
        if not isinstance(self.file_size, int) or self.file_size < 0:
            raise ValueError("File size must be a non-negative integer")

    def _validate_timestamps(self):
        """Validate timestamps are reasonable."""
        if (not isinstance(self.modification_time, (int, float)) or
                self.modification_time < 0):
            raise ValueError("Modification time must be a non-negative number")

        if (not isinstance(self.created_at, (int, float)) or
                self.created_at < 0):
            raise ValueError(
                "Created at timestamp must be a non-negative number"
            )

    def _validate_file_path(self):
        """Validate file path is absolute."""
        if not isinstance(self.file_path, Path):
            raise ValueError("File path must be a Path object")

        if not self.file_path.is_absolute():
            raise ValueError("File path must be absolute")

    def normalize_checksum(self) -> str:
        """Return checksum in lowercase for consistent comparison."""
        return self.checksum.lower()

    def is_duplicate_of(self, other: "FileRecord") -> bool:
        """
        Check if this record represents a duplicate of another file.

        Args:
            other: Another FileRecord to compare against

        Returns:
            True if files have identical checksums
        """
        return self.normalize_checksum() == other.normalize_checksum()

    def to_dict(self) -> dict:
        """Convert record to dictionary for serialization."""
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "checksum": self.checksum,
            "file_size": self.file_size,
            "modification_time": self.modification_time,
            "created_at": self.created_at,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileRecord":
        """Create FileRecord from dictionary."""
        return cls(
            id=data.get("id"),
            file_path=Path(data["file_path"]),
            checksum=data["checksum"],
            file_size=data["file_size"],
            modification_time=data["modification_time"],
            created_at=data["created_at"],
            status=ProcessingStatus(data["status"])
        )
