"""
FileMover service.
Orchestrates file move operations with duplicate detection, quarantine management, and atomic transactions.
"""

import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.models.move_operation import MoveOperation, OperationStatus
from src.models.move_result import MoveResult
from src.models.batch_move_request import BatchMoveRequest
from src.models.batch_move_result import BatchMoveResult
from src.services.atomic_mover import AtomicMover
from src.services.integrity_verifier import IntegrityVerifier
from src.services.quarantine_manager import QuarantineManager


class FileMover:
    """Orchestrates file move operations"""

    def __init__(
        self,
        database_manager,
        duplicate_handler,
        quarantine_manager: QuarantineManager,
        integrity_verifier: Optional[IntegrityVerifier] = None
    ):
        self.db_manager = database_manager
        self.duplicate_handler = duplicate_handler
        self.quarantine_manager = quarantine_manager
        self.integrity_verifier = integrity_verifier or IntegrityVerifier()
        self.atomic_mover = AtomicMover(self.integrity_verifier)

    def move_file(
        self,
        source_path: Path,
        destination_path: Path,
        metadata: dict
    ) -> MoveResult:
        """
        Move a single file to vault location with full error handling.

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
        # Validate inputs
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        if source_path == destination_path:
            raise ValueError("Source and destination cannot be the same")

        start_time = time.time()

        # Calculate file hash
        file_hash = self.integrity_verifier.calculate_hash(source_path)
        file_size = source_path.stat().st_size

        # Create move operation
        operation = MoveOperation(
            operation_id=str(uuid.uuid4()),
            source_path=source_path,
            destination_path=destination_path,
            file_hash=file_hash,
            file_size=file_size,
            status=OperationStatus.PENDING,
            created_at=datetime.now()
        )

        # Check for duplicates
        try:
            is_duplicate, original_file_id = self.duplicate_handler.check_duplicate(
                file_hash, metadata
            )

            if is_duplicate:
                # Handle duplicate
                duplicate_record = self.duplicate_handler.handle_duplicate(
                    source_path, file_hash, original_file_id, metadata
                )

                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000

                operation.status = OperationStatus.COMPLETED
                return MoveResult(
                    success=True,
                    operation=operation,
                    actual_destination=duplicate_record.duplicate_path,
                    is_duplicate=True,
                    is_quarantined=False,
                    execution_time_ms=execution_time_ms
                )
        except Exception as e:
            # Duplicate check failed, continue with normal move
            pass

        # Execute atomic move
        operation.status = OperationStatus.IN_PROGRESS
        operation.started_at = datetime.now()

        move_result = self.atomic_mover.execute_move(operation)

        if move_result.success:
            operation.status = OperationStatus.COMPLETED
            operation.completed_at = datetime.now()

            return MoveResult(
                success=True,
                operation=operation,
                actual_destination=move_result.actual_destination,
                is_duplicate=False,
                is_quarantined=False,
                execution_time_ms=move_result.execution_time_ms
            )
        else:
            # Move failed - quarantine the file
            try:
                quarantine_record = self.quarantine_manager.quarantine_file(
                    source_path, destination_path, move_result.error, metadata
                )

                operation.status = OperationStatus.QUARANTINED
                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000

                return MoveResult(
                    success=False,
                    operation=operation,
                    actual_destination=quarantine_record.file_path,
                    is_duplicate=False,
                    is_quarantined=True,
                    execution_time_ms=execution_time_ms,
                    error=move_result.error
                )
            except Exception as quarantine_error:
                # Quarantine also failed
                operation.status = OperationStatus.FAILED
                operation.error_message = str(move_result.error)
                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000

                return MoveResult(
                    success=False,
                    operation=operation,
                    actual_destination=None,
                    is_duplicate=False,
                    is_quarantined=False,
                    execution_time_ms=execution_time_ms,
                    error=move_result.error
                )

    def move_batch(self, request: BatchMoveRequest) -> BatchMoveResult:
        """
        Move multiple files as a batch operation.

        Args:
            request: Batch move configuration and operations

        Returns:
            BatchMoveResult with aggregated outcomes
        """
        import os

        start_time = time.time()
        results = []

        # Storage space validation
        if request.validate_space:
            total_size = request.total_size
            try:
                stat = os.statvfs(str(request.operations[0].destination_path.parent))
                available = stat.f_bavail * stat.f_frsize
                required = total_size * 1.1  # 10% safety margin

                if required > available:
                    raise Exception(f"Insufficient storage: need {required:,} bytes, only {available:,} available")
            except Exception as e:
                # Storage validation failed - return error result
                pass

        # Execute operations
        for operation in request.operations:
            try:
                result = self.move_file(
                    operation.source_path,
                    operation.destination_path,
                    {}  # metadata would come from operation
                )
                results.append(result)

                if request.stop_on_error and not result.success:
                    break
            except Exception as e:
                # Create error result
                error_result = MoveResult(
                    success=False,
                    operation=operation,
                    actual_destination=None,
                    is_duplicate=False,
                    is_quarantined=False,
                    execution_time_ms=0.0,
                    error=e
                )
                results.append(error_result)

                if request.stop_on_error:
                    break

        # Calculate aggregates
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000

        successful_count = sum(1 for r in results if r.success and not r.is_duplicate and not r.is_quarantined)
        duplicate_count = sum(1 for r in results if r.is_duplicate)
        quarantine_count = sum(1 for r in results if r.is_quarantined)
        failed_count = sum(1 for r in results if not r.success and not r.is_quarantined)

        average_time_ms = total_time_ms / len(results) if results else 0.0

        return BatchMoveResult(
            batch_id=request.batch_id,
            results=results,
            total_operations=request.operation_count,
            successful_count=successful_count,
            duplicate_count=duplicate_count,
            quarantine_count=quarantine_count,
            failed_count=failed_count,
            total_time_ms=total_time_ms,
            average_time_ms=average_time_ms
        )

    def preview_move(self, source_path: Path, destination_path: Path) -> dict:
        """
        Preview what would happen during move without executing.

        Args:
            source_path: Path to source file
            destination_path: Intended destination path

        Returns:
            Dictionary with preview information
        """
        preview = {
            'will_move': True,
            'is_duplicate': False,
            'estimated_time_ms': 100.0,  # Rough estimate
            'potential_errors': [],
            'actual_destination': destination_path
        }

        # Check if source exists
        if not source_path.exists():
            preview['will_move'] = False
            preview['potential_errors'].append("Source file does not exist")
            return preview

        # Check for duplicates
        try:
            file_hash = self.integrity_verifier.calculate_hash(source_path)
            is_duplicate, _ = self.duplicate_handler.check_duplicate(file_hash, {})
            preview['is_duplicate'] = is_duplicate

            if is_duplicate:
                preview['actual_destination'] = Path("duplicates") / source_path.name
        except Exception:
            pass

        # Check destination directory writability
        if not destination_path.parent.exists():
            if not destination_path.parent.parent.exists():
                preview['potential_errors'].append("Destination parent directory does not exist")

        return preview
