"""
AtomicMover service.
Handles low-level atomic file move operations with integrity verification and rollback.
"""

import shutil
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from src.services.integrity_verifier import IntegrityVerifier
from src.models.move_operation import MoveOperation


@dataclass
class AtomicMoveResult:
    """Result of an atomic move operation"""
    success: bool
    actual_destination: Optional[Path]
    execution_time_ms: float
    error: Optional[Exception] = None


class AtomicMover:
    """Executes atomic file move operations with verification and rollback"""

    def __init__(self, integrity_verifier: IntegrityVerifier):
        self.integrity_verifier = integrity_verifier

    def execute_move(self, operation: MoveOperation) -> AtomicMoveResult:
        """
        Execute atomic file move with integrity verification.

        Args:
            operation: Move operation to execute

        Returns:
            AtomicMoveResult with operation outcome

        Raises:
            FileNotFoundError: If source doesn't exist
            PermissionError: If insufficient permissions
        """
        start_time = time.time()

        try:
            # Ensure source exists
            if not operation.source_path.exists():
                raise FileNotFoundError(f"Source file not found: {operation.source_path}")

            # Ensure destination directory exists
            operation.destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Execute move using shutil (handles cross-device)
            shutil.move(str(operation.source_path), str(operation.destination_path))

            # Verify integrity
            verification = self.integrity_verifier.verify_integrity(
                operation.destination_path,
                operation.file_hash
            )

            if not verification.match:
                # Integrity check failed - attempt rollback
                self.rollback_move(operation.destination_path, operation.source_path)
                raise ValueError(f"Integrity verification failed for {operation.destination_path}")

            # Preserve timestamps
            try:
                import os
                stat = operation.destination_path.stat()
                os.utime(operation.destination_path, (stat.st_atime, stat.st_mtime))
            except Exception:
                pass  # Non-critical, continue

            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            return AtomicMoveResult(
                success=True,
                actual_destination=operation.destination_path,
                execution_time_ms=execution_time_ms,
                error=None
            )

        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            return AtomicMoveResult(
                success=False,
                actual_destination=None,
                execution_time_ms=execution_time_ms,
                error=e
            )

    def rollback_move(self, destination_path: Path, source_path: Path) -> bool:
        """
        Rollback a completed move operation.

        Args:
            destination_path: Current file location
            source_path: Original file location

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if destination_path.exists():
                # Check if source location is now occupied
                if source_path.exists():
                    # Cannot rollback - source already exists
                    return False

                # Move file back
                shutil.move(str(destination_path), str(source_path))

                # Verify rollback
                return source_path.exists()

            return False

        except Exception:
            return False

    def verify_move(self, source_hash: str, destination_path: Path) -> bool:
        """
        Verify file integrity after move.

        Args:
            source_hash: SHA256 hash of source file
            destination_path: Path to destination file

        Returns:
            True if integrity verified, False otherwise
        """
        try:
            verification = self.integrity_verifier.verify_integrity(
                destination_path,
                source_hash
            )
            return verification.match
        except Exception:
            return False
