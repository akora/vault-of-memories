"""
Contract: AtomicMover

The AtomicMover service handles low-level atomic file move operations
with integrity verification and rollback capability.
"""

from pathlib import Path
from dataclasses import dataclass


# Input/Output Types
@dataclass
class MoveOperation:
    """See data-model.md for full specification"""
    operation_id: str
    source_path: Path
    destination_path: Path
    file_hash: str


@dataclass
class MoveResult:
    """See data-model.md for full specification"""
    success: bool
    actual_destination: Path | None
    execution_time_ms: float
    error: Exception | None


# Contract Interface
class AtomicMover:
    """
    Executes atomic file move operations with verification and rollback.
    """

    def execute_move(
        self,
        operation: MoveOperation
    ) -> MoveResult:
        """
        Execute atomic file move with integrity verification.

        Contract:
        - MUST ensure destination directory exists (create if needed)
        - MUST use shutil.move() for cross-device compatibility
        - MUST preserve file timestamps and permissions
        - MUST verify destination file hash matches source
        - MUST attempt rollback if verification fails
        - MUST NOT delete source until destination verified
        - MUST track operation timing
        - MUST handle cross-platform path differences

        Args:
            operation: Move operation to execute

        Returns:
            MoveResult with operation outcome

        Raises:
            FileNotFoundError: If source doesn't exist
            PermissionError: If insufficient permissions
        """
        raise NotImplementedError

    def rollback_move(
        self,
        destination_path: Path,
        source_path: Path
    ) -> bool:
        """
        Rollback a completed move operation.

        Contract:
        - MUST move file from destination back to source
        - MUST verify source file after rollback
        - MUST handle case where source location is now occupied
        - MUST log rollback operation
        - MUST return success/failure status

        Args:
            destination_path: Current file location
            source_path: Original file location

        Returns:
            True if rollback successful, False otherwise
        """
        raise NotImplementedError

    def verify_move(
        self,
        source_hash: str,
        destination_path: Path
    ) -> bool:
        """
        Verify file integrity after move.

        Contract:
        - MUST calculate destination file hash
        - MUST compare with source hash
        - MUST handle missing destination file
        - MUST return True only if hashes match exactly

        Args:
            source_hash: SHA256 hash of source file
            destination_path: Path to destination file

        Returns:
            True if integrity verified, False otherwise
        """
        raise NotImplementedError
