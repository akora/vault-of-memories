"""
Duplicate Database Contract
Defines the interface for duplicate detection database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from .file_ingestor import FileRecord


class DuplicateDatabase(ABC):
    """Abstract interface for duplicate detection database."""

    @abstractmethod
    def initialize(self, db_path: Path) -> None:
        """
        Initialize the database connection and schema.

        Args:
            db_path: Path to SQLite database file

        Raises:
            DatabaseError: If database cannot be initialized
        """
        pass

    @abstractmethod
    def add_file_record(self, record: FileRecord) -> int:
        """
        Add a new file record to the database.

        Args:
            record: FileRecord to add

        Returns:
            ID of the inserted record

        Raises:
            DatabaseError: If record cannot be inserted
            ValueError: If record data is invalid
        """
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[FileRecord]:
        """
        Find a file record by its checksum.

        Args:
            checksum: SHA-256 hash to search for

        Returns:
            FileRecord if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_duplicates(self) -> List[List[FileRecord]]:
        """
        Get all groups of duplicate files.

        Returns:
            List of groups, where each group contains FileRecords
            with the same checksum
        """
        pass

    @abstractmethod
    def update_status(self, record_id: int, status: str) -> None:
        """
        Update the processing status of a file record.

        Args:
            record_id: Database ID of the record
            status: New status value

        Raises:
            DatabaseError: If update fails
            ValueError: If record_id doesn't exist
        """
        pass

    @abstractmethod
    def get_stats_by_status(self) -> dict:
        """
        Get file counts grouped by processing status.

        Returns:
            Dictionary mapping status to count
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass