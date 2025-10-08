"""
DuplicateHandler service.
Manages duplicate file detection and storage using the existing DuplicateDatabase.
"""

import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class DuplicateRecord:
    """Record of a duplicate file"""
    duplicate_id: str
    original_file_id: str
    duplicate_path: Path
    original_path: Path
    file_hash: str
    detected_at: datetime
    duplicate_size: int
    metadata_diff: dict
    source_path: Path


class DuplicateHandler:
    """Manages duplicate file detection and storage"""

    def __init__(self, duplicate_database, vault_root: Path):
        self.duplicate_db = duplicate_database
        self.vault_root = vault_root
        self.duplicates_root = vault_root / "duplicates"
        self.duplicates_root.mkdir(parents=True, exist_ok=True)

    def check_duplicate(
        self,
        file_hash: str,
        metadata: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if file is a duplicate of existing vault file.

        Args:
            file_hash: SHA256 hash of file
            metadata: File metadata for comparison

        Returns:
            Tuple of (is_duplicate, original_file_id)
        """
        try:
            # Query DuplicateDatabase by hash
            existing_record = self.duplicate_db.find_by_checksum(file_hash)

            if existing_record:
                # File with same hash exists - it's a duplicate
                return (True, str(existing_record.id) if hasattr(existing_record, 'id') else file_hash)
            else:
                return (False, None)

        except Exception:
            # On error, assume not duplicate
            return (False, None)

    def handle_duplicate(
        self,
        source_path: Path,
        file_hash: str,
        original_file_id: str,
        metadata: dict
    ) -> DuplicateRecord:
        """
        Handle a duplicate file by moving to duplicates folder.

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
        # Get duplicate path
        duplicate_path = self.get_duplicate_path(file_hash, source_path.name)

        # Ensure duplicate directory exists
        duplicate_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file to duplicates folder
        try:
            shutil.move(str(source_path), str(duplicate_path))
        except Exception:
            # If move fails, try copy
            shutil.copy2(str(source_path), str(duplicate_path))

        # Get original file path (simplified - would query database)
        original_path = self.vault_root / "original" / "file.jpg"  # Placeholder

        # Create duplicate record
        duplicate_id = str(uuid.uuid4())
        record = DuplicateRecord(
            duplicate_id=duplicate_id,
            original_file_id=original_file_id,
            duplicate_path=duplicate_path,
            original_path=original_path,
            file_hash=file_hash,
            detected_at=datetime.now(),
            duplicate_size=duplicate_path.stat().st_size if duplicate_path.exists() else 0,
            metadata_diff=self._calculate_metadata_diff(metadata, {}),
            source_path=source_path
        )

        return record

    def get_duplicate_path(self, file_hash: str, original_filename: str) -> Path:
        """
        Calculate path for storing duplicate file.

        Args:
            file_hash: SHA256 hash of file
            original_filename: Original filename

        Returns:
            Path where duplicate should be stored
        """
        # Use current date for folder structure
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")

        # Use first 4 characters of hash for prefix
        hash_prefix = file_hash[:4]

        # Build path: duplicates/YYYY-MM-DD/hash_prefix/filename
        duplicate_dir = self.duplicates_root / date_str / hash_prefix
        duplicate_path = duplicate_dir / original_filename

        # Handle filename collisions with timestamp
        if duplicate_path.exists():
            stem = duplicate_path.stem
            suffix = duplicate_path.suffix
            timestamp = today.strftime("%H%M%S")
            safe_filename = f"{stem}_{timestamp}{suffix}"
            duplicate_path = duplicate_dir / safe_filename

        return duplicate_path

    def _calculate_metadata_diff(self, metadata1: dict, metadata2: dict) -> dict:
        """Calculate differences between two metadata dictionaries"""
        diff = {}
        all_keys = set(metadata1.keys()) | set(metadata2.keys())

        for key in all_keys:
            val1 = metadata1.get(key)
            val2 = metadata2.get(key)
            if val1 != val2:
                diff[key] = {
                    'duplicate': val1,
                    'original': val2
                }

        return diff
