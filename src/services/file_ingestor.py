"""
File Ingestor Implementation
Handles file ingestion operations with duplicate detection and system file filtering.
"""

import hashlib
import os
import time
from pathlib import Path
from typing import List

from ..models.file_record import FileRecord, ProcessingStatus
from ..models.processing_stats import ProcessingStats
from .database_manager import DatabaseManager


class FileIngestorImpl:
    """Implementation of file ingestion operations."""

    def __init__(self, db_path: Path = None):
        """
        Initialize file ingestor with database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        self.db_manager = DatabaseManager()
        if db_path is None:
            db_path = Path(":memory:")
        self.db_manager.initialize(db_path)

        self.stats = ProcessingStats()
        self.start_time = time.time()

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
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a regular file: {file_path}")

        try:
            # Calculate file metadata
            file_size = file_path.stat().st_size
            modification_time = file_path.stat().st_mtime
            created_at = time.time()

            # Calculate SHA-256 checksum
            checksum = self._calculate_checksum(file_path)

            # Check for duplicates
            status = ProcessingStatus.DUPLICATE if self.is_duplicate(checksum) else ProcessingStatus.PROCESSED

            # Create file record
            record = FileRecord(
                id=None,
                file_path=file_path,
                checksum=checksum,
                file_size=file_size,
                modification_time=modification_time,
                created_at=created_at,
                status=status
            )

            # Add to database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_records
                (file_path, checksum, file_size, modification_time, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(file_path), checksum, file_size, modification_time, created_at, status.value
            ))
            record.id = cursor.lastrowid
            conn.commit()

            # Update statistics
            if status == ProcessingStatus.PROCESSED:
                self.stats.add_processed_file(file_size)
            elif status == ProcessingStatus.DUPLICATE:
                self.stats.add_duplicate_file(file_size)

            return record

        except PermissionError:
            self.stats.add_error_file()
            raise
        except Exception as e:
            self.stats.add_error_file()
            raise

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
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")

        records = []

        try:
            # Get all files in directory
            if recursive:
                files = [f for f in dir_path.rglob("*") if f.is_file()]
            else:
                files = [f for f in dir_path.iterdir() if f.is_file()]

            for file_path in files:
                try:
                    # Skip system files
                    if self.is_system_file(file_path):
                        self.stats.add_system_file_removed()
                        continue

                    record = self.ingest_file(file_path)
                    records.append(record)

                except (PermissionError, ValueError) as e:
                    # Log error but continue processing other files
                    continue

            return records

        except PermissionError:
            raise

    def is_duplicate(self, checksum: str) -> bool:
        """
        Check if a file with given checksum already exists.

        Args:
            checksum: SHA-256 hash to check

        Returns:
            True if duplicate exists, False otherwise

        Raises:
            ValueError: If checksum is None or empty
            TypeError: If checksum is not a string
        """
        # Handle None input
        if checksum is None:
            raise TypeError("Checksum cannot be None")

        # Handle empty string
        if checksum == "":
            raise ValueError("Checksum cannot be empty")

        # Normalize to lowercase for case-insensitive comparison
        checksum_lower = checksum.lower()

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM file_records WHERE LOWER(checksum) = ?", (checksum_lower,))
        return cursor.fetchone() is not None

    def get_processing_stats(self) -> ProcessingStats:
        """
        Get statistics for the current processing session.

        Returns:
            ProcessingStats object with current metrics
        """
        # Update processing time
        self.stats.processing_time = time.time() - self.start_time
        return self.stats

    def is_system_file(self, file_path: Path) -> bool:
        """
        Check if file should be filtered as system/hidden file.

        Args:
            file_path: Path to check

        Returns:
            True if file should be filtered, False otherwise
        """
        filename = file_path.name

        # System files to filter
        system_files = {
            '.DS_Store',      # macOS metadata
            'Thumbs.db',      # Windows thumbnails
            'desktop.ini',    # Windows folder config
            'Icon\r',         # macOS custom icons
        }

        # Check exact matches
        if filename in system_files:
            return True

        # Check patterns
        if filename.startswith('.'):  # Hidden files (Unix convention)
            return True

        if filename.endswith('.tmp'):  # Temporary files
            return True

        return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(65536), b""):  # 64KB chunks
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    def close(self):
        """Close database connection."""
        self.db_manager.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()