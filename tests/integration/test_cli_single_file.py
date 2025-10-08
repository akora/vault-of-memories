"""
Integration test: Single file processing.

Tests complete pipeline on a single file.
"""

import pytest
from pathlib import Path
from datetime import timedelta
from unittest.mock import Mock, patch

from src.cli.main import main
from src.models import ProcessingResult, ProcessingContext, ProgressState


class TestSingleFileProcessing:
    """Test single file processing through CLI."""

    def _create_success_result(self, test_file: Path, context: Mock) -> ProcessingResult:
        """Helper to create a successful processing result."""
        return ProcessingResult(
            context=context,
            final_state=ProgressState(
                total_files=1,
                processed_files=1,
                successful_count=1,
                failed_count=0,
                quarantine_count=0
            ),
            success=True,
            total_duration=timedelta(seconds=1),
            files_processed=1,
            successful_files=[test_file],
            duplicate_files=[],
            quarantined_files=[],
            failed_files=[]
        )

    def test_single_file_basic(self, tmp_path):
        """Test processing a single file through the CLI."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        vault_root = tmp_path / "vault"

        # Mock the ServiceFactory to return a mock orchestrator
        mock_result = self._create_success_result(test_file, Mock())

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_create_orch:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_create_orch.return_value = mock_orch

            # Execute (global options come before subcommand)
            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file)
            ])

            # Assert
            assert exit_code == 0, "Should succeed"
            assert mock_orch.execute.called, "Should call orchestrator.execute()"

    def test_single_file_with_verbose(self, tmp_path):
        """Test processing with verbose output."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        vault_root = tmp_path / "vault"

        mock_result = self._create_success_result(test_file, Mock())

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_create_orch:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_create_orch.return_value = mock_orch

            # Execute with --verbose
            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file),
                '--verbose'
            ])

            assert exit_code == 0

    def test_single_file_dry_run(self, tmp_path):
        """Test dry-run mode doesn't modify files."""
        test_file = tmp_path / "test.txt"
        original_content = "test content"
        test_file.write_text(original_content)

        vault_root = tmp_path / "vault"

        mock_result = self._create_success_result(test_file, Mock())

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_create_orch:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_create_orch.return_value = mock_orch

            # Execute with --dry-run
            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file),
                '--dry-run'
            ])

            assert exit_code == 0

            # Verify context was created with dry_run=True
            call_args = mock_orch.execute.call_args
            context = call_args[0][0]
            assert context.dry_run is True, "Context should have dry_run=True"

    def test_single_file_not_found(self, tmp_path):
        """Test error handling when source file doesn't exist."""
        test_file = tmp_path / "nonexistent.txt"
        vault_root = tmp_path / "vault"

        # Execute
        exit_code = main([
            '--vault-root', str(vault_root),
            'process',
            str(test_file)
        ])

        # Should return error code (2 for invalid arguments or 65 for not found)
        assert exit_code == 2, f"Should fail with validation error, got {exit_code}"

    def test_single_file_with_failure(self, tmp_path):
        """Test handling when file processing fails."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        vault_root = tmp_path / "vault"

        # Mock result with failure
        mock_result = ProcessingResult(
            context=Mock(),
            final_state=ProgressState(
                total_files=1,
                processed_files=1,
                successful_count=0,
                failed_count=1,
                quarantine_count=0
            ),
            success=False,
            total_duration=timedelta(seconds=1),
            files_processed=1,
            successful_files=[],
            duplicate_files=[],
            quarantined_files=[],
            failed_files=[(test_file, "Test error")]
        )

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_create_orch:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_create_orch.return_value = mock_orch

            # Execute
            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file)
            ])

            # Should return 1 for partial failure
            assert exit_code == 1, f"Should return 1 for failure, got {exit_code}"
