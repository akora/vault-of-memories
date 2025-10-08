"""
Contract: DuplicateHandler

The DuplicateHandler service manages duplicate file detection and storage.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


# Input/Output Types
@dataclass
class DuplicateRecord:
    """See data-model.md for full specification"""
    duplicate_id: str
    original_file_id: str
    duplicate_path: Path
    original_path: Path
    file_hash: str
    detected_at: datetime


# Contract Interface
class DuplicateHandler:
    """
    Manages duplicate file detection and storage.
    """

    def check_duplicate(
        self,
        file_hash: str,
        metadata: dict
    ) -> tuple[bool, str | None]:
        """
        Check if file is a duplicate of existing vault file.

        Contract:
        - MUST query DuplicateDatabase by file hash
        - MUST return (True, original_file_id) if duplicate found
        - MUST return (False, None) if not a duplicate
        - MUST handle database query errors gracefully

        Args:
            file_hash: SHA256 hash of file
            metadata: File metadata for comparison

        Returns:
            Tuple of (is_duplicate, original_file_id)
        """
        raise NotImplementedError

    def handle_duplicate(
        self,
        source_path: Path,
        file_hash: str,
        original_file_id: str,
        metadata: dict
    ) -> DuplicateRecord:
        """
        Handle a duplicate file by moving to duplicates folder.

        Contract:
        - MUST move file to duplicates/{YYYY-MM-DD}/{hash_prefix}/
        - MUST create unique filename to avoid collisions
        - MUST record relationship in DuplicateDatabase
        - MUST store metadata differences
        - MUST preserve original file (don't delete)
        - MUST return DuplicateRecord with full details

        Args:
            source_path: Path to duplicate file
            file_hash: File content hash
            original_file_id: ID of original file in vault
            metadata: Duplicate file metadata

        Returns:
            DuplicateRecord with duplicate information

        Raises:
            PermissionError: If cannot access duplicates folder
        """
        raise NotImplementedError

    def get_duplicate_path(
        self,
        file_hash: str,
        original_filename: str
    ) -> Path:
        """
        Calculate path for storing duplicate file.

        Contract:
        - MUST return path in format: duplicates/{YYYY-MM-DD}/{hash_prefix}/{filename}
        - MUST use current date for YYYY-MM-DD
        - MUST use first 4 characters of hash for prefix
        - MUST append timestamp if filename collision

        Args:
            file_hash: SHA256 hash of file
            original_filename: Original filename

        Returns:
            Path where duplicate should be stored
        """
        raise NotImplementedError
