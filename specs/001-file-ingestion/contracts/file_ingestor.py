"""
File Ingestor Contract
Defines the interface for file ingestion operations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class ProcessingStatus(Enum):
    """File processing status enumeration."""
    PENDING = "pending"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    ERROR = "error"


@dataclass
class FileRecord:
    """Represents a processed file with metadata."""
    id: Optional[int]
    file_path: Path
    checksum: str
    file_size: int
    modification_time: float
    created_at: float
    status: ProcessingStatus


@dataclass
class ProcessingStats:
    """Statistics for batch processing operations."""
    total_files: int
    processed_files: int
    duplicate_files: int
    error_files: int
    system_files_removed: int
    total_size: int
    processing_time: float


class FileIngestor(ABC):
    """Abstract interface for file ingestion operations."""

    @abstractmethod
    def ingest_file(self, file_path: Path) -> FileRecord:
        """
        Ingest a single file.

        Args:
            file_path: Path to the file to ingest

        Returns:
            FileRecord with processing results

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            ValueError: If file is not a regular file
        """
        pass

    @abstractmethod
    def ingest_directory(self, dir_path: Path, recursive: bool = True) -> List[FileRecord]:
        """
        Ingest all files in a directory.

        Args:
            dir_path: Path to directory to process
            recursive: Whether to process subdirectories

        Returns:
            List of FileRecord objects for all processed files

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If directory cannot be accessed
        """
        pass

    @abstractmethod
    def is_duplicate(self, checksum: str) -> bool:
        """
        Check if a file with given checksum already exists.

        Args:
            checksum: SHA-256 hash to check

        Returns:
            True if duplicate exists, False otherwise
        """
        pass

    @abstractmethod
    def get_processing_stats(self) -> ProcessingStats:
        """
        Get statistics for the current processing session.

        Returns:
            ProcessingStats object with current metrics
        """
        pass

    @abstractmethod
    def is_system_file(self, file_path: Path) -> bool:
        """
        Check if file should be filtered as system/hidden file.

        Args:
            file_path: Path to check

        Returns:
            True if file should be filtered, False otherwise
        """
        pass