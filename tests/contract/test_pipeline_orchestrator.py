"""
Contract tests for PipelineOrchestrator service.
Tests the main pipeline orchestration logic.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

from src.models import ProcessingContext, ProcessingResult, ProgressState


class TestPipelineOrchestrator:
    """Contract tests for PipelineOrchestrator."""

    def test_execute_contract(self, tmp_path):
        """Test that execute() follows the contract specification."""
        from src.services.pipeline_orchestrator import PipelineOrchestrator

        # Setup
        source = tmp_path / "source.txt"
        source.write_text("test content")
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        context = ProcessingContext(
            source_path=source,
            vault_root=vault_root,
            config={},
            dry_run=False
        )

        # Create orchestrator (will fail until implemented)
        orchestrator = PipelineOrchestrator(
            database_manager=Mock(),
            file_ingestor=Mock(),
            metadata_consolidator=Mock(),
            organization_manager=Mock(),
            file_mover=Mock()
        )

        # Track progress updates
        progress_updates = []
        def progress_callback(state: ProgressState):
            progress_updates.append(state)

        # Execute
        result = orchestrator.execute(context, progress_callback)

        # Assert contract requirements
        assert isinstance(result, ProcessingResult), "Must return ProcessingResult"
        assert result.context == context, "Must include original context"
        assert isinstance(result.final_state, ProgressState), "Must include final state"
        assert result.success is not None, "Must have success status"
        assert len(progress_updates) > 0, "Must call progress callback"

    def test_validate_context_contract(self, tmp_path):
        """Test that validate_context() follows the contract specification."""
        from src.services.pipeline_orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(
            database_manager=Mock(),
            file_ingestor=Mock(),
            metadata_consolidator=Mock(),
            organization_manager=Mock(),
            file_mover=Mock()
        )

        # Valid context
        valid_context = ProcessingContext(
            source_path=tmp_path / "source.txt",
            vault_root=tmp_path / "vault",
            config={}
        )
        (tmp_path / "source.txt").write_text("test")
        (tmp_path / "vault").mkdir()

        errors = orchestrator.validate_context(valid_context)
        assert isinstance(errors, list), "Must return list of errors"
        assert len(errors) == 0, "Valid context should have no errors"

        # Invalid context (non-existent source)
        invalid_context = ProcessingContext(
            source_path=tmp_path / "nonexistent.txt",
            vault_root=tmp_path / "vault",
            config={}
        )

        errors = orchestrator.validate_context(invalid_context)
        assert len(errors) > 0, "Invalid context should have errors"
        assert all(isinstance(e, str) for e in errors), "Errors must be strings"

    def test_discover_files_contract(self, tmp_path):
        """Test that discover_files() follows the contract specification."""
        from src.services.pipeline_orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(
            database_manager=Mock(),
            file_ingestor=Mock(),
            metadata_consolidator=Mock(),
            organization_manager=Mock(),
            file_mover=Mock()
        )

        # Create test files
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("test1")
        (source_dir / "file2.txt").write_text("test2")
        (source_dir / ".DS_Store").write_text("system")  # Should be filtered

        files = orchestrator.discover_files(source_dir)

        assert isinstance(files, list), "Must return list of paths"
        assert all(isinstance(f, Path) for f in files), "Must return Path objects"
        assert all(f.is_absolute() for f in files), "Must return absolute paths"
        assert len(files) == 2, "Should find 2 files (excluding .DS_Store)"

    def test_process_file_contract(self, tmp_path):
        """Test that process_file() follows the contract specification."""
        from src.services.pipeline_orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(
            database_manager=Mock(),
            file_ingestor=Mock(),
            metadata_consolidator=Mock(),
            organization_manager=Mock(),
            file_mover=Mock()
        )

        source = tmp_path / "test.txt"
        source.write_text("test content")

        context = ProcessingContext(
            source_path=source,
            vault_root=tmp_path / "vault",
            config={}
        )

        progress = ProgressState(total_files=1)

        success, error = orchestrator.process_file(source, context, progress)

        assert isinstance(success, bool), "Must return bool for success"
        assert error is None or isinstance(error, str), "Error must be None or string"
        assert progress.current_file == source, "Must update progress.current_file"

    def test_handle_interruption_contract(self, tmp_path):
        """Test that handle_interruption() follows the contract specification."""
        from src.services.pipeline_orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(
            database_manager=Mock(),
            file_ingestor=Mock(),
            metadata_consolidator=Mock(),
            organization_manager=Mock(),
            file_mover=Mock()
        )

        result = orchestrator.handle_interruption()

        assert isinstance(result, ProcessingResult), "Must return ProcessingResult"
        assert not result.success, "Interrupted result should not be success"
        assert isinstance(result.final_state, ProgressState), "Must include state"
