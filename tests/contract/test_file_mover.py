"""
Contract tests for FileMover service.
Tests the main file mover orchestration logic.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import shutil


class TestFileMover:
    """Contract tests for FileMover"""

    def test_move_file_contract(self, tmp_path):
        """Test that move_file follows the contract specification"""
        from src.services.file_mover import FileMover
        from src.models.move_result import MoveResult
        from src.services.integrity_verifier import IntegrityVerifier
        from src.services.atomic_mover import AtomicMover

        # Setup
        source = tmp_path / "source.txt"
        source.write_text("test content")
        destination = tmp_path / "vault" / "dest.txt"
        metadata = {"file_type": "text/plain"}

        # Create mocks for dependencies
        mock_db = Mock()
        mock_duplicate_handler = Mock()
        mock_duplicate_handler.check_duplicate.return_value = (False, None)  # Not a duplicate

        quarantine_root = tmp_path / "quarantine"
        quarantine_root.mkdir()

        from src.services.quarantine_manager import QuarantineManager
        quarantine_manager = QuarantineManager(quarantine_root)

        # Use real IntegrityVerifier for this test
        integrity_verifier = IntegrityVerifier()

        file_mover = FileMover(
            mock_db,
            mock_duplicate_handler,
            quarantine_manager,
            integrity_verifier
        )

        # Execute
        result = file_mover.move_file(source, destination, metadata)

        # Assert contract requirements
        assert isinstance(result, MoveResult)
        assert result.success is not None
        assert result.operation is not None
        assert hasattr(result, 'actual_destination')
        assert hasattr(result, 'is_duplicate')
        assert hasattr(result, 'is_quarantined')
        assert hasattr(result, 'execution_time_ms')

        # Verify file was actually moved
        if result.success:
            assert result.actual_destination.exists()
            assert not source.exists()  # Source should be moved

    def test_move_batch_contract(self, tmp_path):
        """Test that move_batch follows the contract specification"""
        from src.services.file_mover import FileMover
        from src.models.batch_move_request import BatchMoveRequest
        from src.models.batch_move_result import BatchMoveResult
        from src.models.move_operation import MoveOperation, OperationStatus
        from src.services.integrity_verifier import IntegrityVerifier
        from src.services.quarantine_manager import QuarantineManager
        from datetime import datetime
        import uuid

        # Setup test file
        source = tmp_path / "test.txt"
        source.write_text("test content")
        destination = tmp_path / "vault" / "test.txt"

        mock_db = Mock()
        mock_duplicate_handler = Mock()
        mock_duplicate_handler.check_duplicate.return_value = (False, None)

        quarantine_manager = QuarantineManager(tmp_path / "quarantine")
        integrity_verifier = IntegrityVerifier()

        file_mover = FileMover(mock_db, mock_duplicate_handler, quarantine_manager, integrity_verifier)

        # Create operation
        file_hash = integrity_verifier.calculate_hash(source)
        operation = MoveOperation(
            operation_id=str(uuid.uuid4()),
            source_path=source,
            destination_path=destination,
            file_hash=file_hash,
            file_size=source.stat().st_size,
            status=OperationStatus.PENDING,
            created_at=datetime.now()
        )

        batch_request = BatchMoveRequest(
            batch_id="test-batch",
            operations=[operation],
            validate_space=False,
            parallel=False,
            max_workers=1,
            stop_on_error=False
        )

        result = file_mover.move_batch(batch_request)

        # Assert contract
        assert isinstance(result, BatchMoveResult)
        assert result.batch_id == "test-batch"
        assert hasattr(result, 'total_operations')
        assert hasattr(result, 'successful_count')
        assert result.total_operations == 1

    def test_preview_move_contract(self, tmp_path):
        """Test that preview_move follows the contract specification"""
        from src.services.file_mover import FileMover
        from src.services.integrity_verifier import IntegrityVerifier
        from src.services.quarantine_manager import QuarantineManager

        source = tmp_path / "test.txt"
        source.write_text("content")
        destination = tmp_path / "vault" / "test.txt"

        mock_db = Mock()
        mock_duplicate_handler = Mock()
        mock_duplicate_handler.check_duplicate.return_value = (False, None)

        quarantine_manager = QuarantineManager(tmp_path / "quarantine")
        integrity_verifier = IntegrityVerifier()

        file_mover = FileMover(mock_db, mock_duplicate_handler, quarantine_manager, integrity_verifier)
        preview = file_mover.preview_move(source, destination)

        # Assert contract
        assert isinstance(preview, dict)
        assert 'will_move' in preview
        assert 'is_duplicate' in preview
        assert 'estimated_time_ms' in preview
        assert 'potential_errors' in preview
        assert 'actual_destination' in preview

        # Preview must not modify files
        assert source.exists()
        assert not destination.exists()
