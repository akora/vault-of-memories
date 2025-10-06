"""
Duplicate Database Implementation
Handles database operations for duplicate detection and file tracking.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from ..models.file_record import FileRecord, ProcessingStatus
from .database_manager import DatabaseManager


class DuplicateDatabaseImpl:
    """Implementation of duplicate detection database operations."""

    def __init__(self):
        """Initialize duplicate database."""
        self.db_manager = DatabaseManager()

    def initialize(self, db_path: Path) -> None:
        """
        Initialize the database connection and schema.

        Args:
            db_path: Path to SQLite database file

        Raises:
            DatabaseError: If database cannot be initialized
        """
        self.db_manager.initialize(db_path)

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
        if record is None:
            raise ValueError("Record cannot be None")

        # Validate record data
        self._validate_record(record)

        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO file_records
                (file_path, checksum, file_size, modification_time, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(record.file_path),
                record.checksum,
                record.file_size,
                record.modification_time,
                record.created_at,
                record.status.value
            ))

            record_id = cursor.lastrowid
            conn.commit()
            return record_id

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise Exception(f"Duplicate file path: {record.file_path}")
            raise
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def find_by_checksum(self, checksum: str) -> Optional[FileRecord]:
        """
        Find a file record by its checksum.

        Args:
            checksum: SHA-256 hash to search for

        Returns:
            FileRecord if found, None otherwise

        Raises:
            ValueError: If checksum is empty
            TypeError: If checksum is None
        """
        # Handle None input
        if checksum is None:
            raise TypeError("Checksum cannot be None")

        # Handle empty string
        if checksum == "":
            raise ValueError("Checksum cannot be empty")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Case-insensitive search, return the first match
        cursor.execute("""
            SELECT id, file_path, checksum, file_size, modification_time,
                   created_at, status
            FROM file_records
            WHERE LOWER(checksum) = LOWER(?)
            ORDER BY created_at
            LIMIT 1
        """, (checksum,))

        row = cursor.fetchone()
        if row is None:
            return None

        return FileRecord(
            id=row[0],
            file_path=Path(row[1]),
            checksum=row[2],
            file_size=row[3],
            modification_time=row[4],
            created_at=row[5],
            status=ProcessingStatus(row[6])
        )

    def get_all_duplicates(self) -> List[List[FileRecord]]:
        """
        Get all groups of duplicate files.

        Returns:
            List of groups, where each group contains FileRecords
            with the same checksum
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Find checksums with multiple files
        cursor.execute("""
            SELECT checksum
            FROM file_records
            GROUP BY checksum
            HAVING COUNT(*) > 1
        """)

        duplicate_checksums = [row[0] for row in cursor.fetchall()]
        duplicate_groups = []

        for checksum in duplicate_checksums:
            cursor.execute("""
                SELECT id, file_path, checksum, file_size, modification_time,
                       created_at, status
                FROM file_records
                WHERE checksum = ?
                ORDER BY created_at
            """, (checksum,))

            group = []
            for row in cursor.fetchall():
                record = FileRecord(
                    id=row[0],
                    file_path=Path(row[1]),
                    checksum=row[2],
                    file_size=row[3],
                    modification_time=row[4],
                    created_at=row[5],
                    status=ProcessingStatus(row[6])
                )
                group.append(record)

            duplicate_groups.append(group)

        return duplicate_groups

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
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE file_records
            SET status = ?
            WHERE id = ?
        """, (status, record_id))

        if cursor.rowcount == 0:
            raise ValueError(f"Record with ID {record_id} not found")

        conn.commit()

    def get_stats_by_status(self) -> dict:
        """
        Get file counts grouped by processing status.

        Returns:
            Dictionary mapping status to count
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM file_records
            GROUP BY status
        """)

        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]

        return stats

    def close(self) -> None:
        """Close the database connection."""
        self.db_manager.close()

    def _validate_record(self, record: FileRecord) -> None:
        """
        Validate file record data.

        Args:
            record: FileRecord to validate

        Raises:
            ValueError: If record data is invalid
        """
        # Validate checksum (SHA-256 should be 64 hex characters)
        if not isinstance(record.checksum, str) or len(record.checksum) != 64:
            raise ValueError("Checksum must be a 64-character hex string")

        try:
            int(record.checksum, 16)  # Verify it's valid hex
        except ValueError:
            raise ValueError("Checksum must be a valid hexadecimal string")

        # Validate file size
        if not isinstance(record.file_size, int) or record.file_size < 0:
            raise ValueError("File size must be a non-negative integer")

        # Validate timestamps
        if (not isinstance(record.modification_time, (int, float)) or
                record.modification_time < 0):
            raise ValueError("Modification time must be a non-negative number")

        if not isinstance(record.created_at, (int, float)) or record.created_at < 0:
            raise ValueError("Created at time must be a non-negative number")

        # Validate file path
        if not isinstance(record.file_path, Path):
            raise ValueError("File path must be a Path object")

        # Validate status
        if not isinstance(record.status, ProcessingStatus):
            raise ValueError("Status must be a ProcessingStatus enum value")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
