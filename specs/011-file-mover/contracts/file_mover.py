"""
Contract: FileMover

The FileMover service orchestrates file move operations, coordinating with
duplicate detection, quarantine management, and transaction management.
"""

from pathlib import Path
from typing import List
from dataclasses import dataclass


# Input/Output Types
@dataclass
class MoveOperation:
    """See data-model.md for full specification"""
    operation_id: str
    source_path: Path
    destination_path: Path
    file_hash: str
    file_size: int


@dataclass
class MoveResult:
    """See data-model.md for full specification"""
    success: bool
    operation: MoveOperation
    actual_destination: Path | None
    is_duplicate: bool
    is_quarantined: bool
    execution_time_ms: float


@dataclass
class BatchMoveRequest:
    """See data-model.md for full specification"""
    batch_id: str
    operations: List[MoveOperation]
    validate_space: bool
    parallel: bool


@dataclass
class BatchMoveResult:
    """See data-model.md for full specification"""
    batch_id: str
    results: List[MoveResult]
    total_operations: int
    successful_count: int


# Contract Interface
class FileMover:
    """
    Orchestrates file move operations with duplicate detection,
    quarantine management, and atomic transactions.
    """

    def move_file(
        self,
        source_path: Path,
        destination_path: Path,
        metadata: dict
    ) -> MoveResult:
        """
        Move a single file to vault location with full error handling.

        Contract:
        - MUST calculate file hash before move
        - MUST check for duplicates using DuplicateHandler
        - MUST use AtomicMover for actual file operation
        - MUST verify integrity after move
        - MUST update database records atomically with file move
        - MUST quarantine file if any verification fails
        - MUST preserve file timestamps and permissions
        - MUST return MoveResult with complete operation details

        Args:
            source_path: Path to source file (must exist)
            destination_path: Intended destination path in vault
            metadata: File metadata from MetadataConsolidator

        Returns:
            MoveResult with operation outcome

        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If destination equals source
        """
        raise NotImplementedError

    def move_batch(
        self,
        request: BatchMoveRequest
    ) -> BatchMoveResult:
        """
        Move multiple files as a batch operation.

        Contract:
        - MUST validate storage space if request.validate_space=True
        - MUST execute operations in parallel if request.parallel=True
        - MUST stop on first error if request.stop_on_error=True
        - MUST track progress of all operations
        - MUST handle partial failures gracefully
        - MUST aggregate individual results into batch summary
        - MUST log batch operation details

        Args:
            request: Batch move configuration and operations

        Returns:
            BatchMoveResult with aggregated outcomes

        Raises:
            InsufficientStorageError: If storage validation fails
        """
        raise NotImplementedError

    def preview_move(
        self,
        source_path: Path,
        destination_path: Path
    ) -> dict:
        """
        Preview what would happen during move without executing.

        Contract:
        - MUST NOT modify any files
        - MUST check for duplicates
        - MUST validate destination path
        - MUST estimate operation time
        - MUST identify potential errors

        Args:
            source_path: Path to source file
            destination_path: Intended destination path

        Returns:
            Dictionary with preview information:
            {
                'will_move': bool,
                'is_duplicate': bool,
                'estimated_time_ms': float,
                'potential_errors': List[str],
                'actual_destination': Path
            }
        """
        raise NotImplementedError
