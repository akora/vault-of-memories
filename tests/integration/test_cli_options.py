"""
Integration test: CLI options and argument parsing.

Tests various CLI option combinations and edge cases.
"""

import pytest
from pathlib import Path
from datetime import timedelta
from unittest.mock import Mock, patch

from src.cli.main import main
from src.models import ProcessingResult, ProgressState


class TestCLIOptions:
    """Test CLI option parsing and handling."""

    def _create_mock_result(self, test_file: Path) -> ProcessingResult:
        """Helper to create a mock processing result."""
        return ProcessingResult(
            context=Mock(),
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

    def test_dry_run_flag(self, tmp_path):
        """Test --dry-run flag creates context with dry_run=True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        vault_root = tmp_path / "vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file),
                '--dry-run'
            ])

            assert exit_code == 0
            # Verify dry_run was set
            call_args = mock_orch.execute.call_args
            context = call_args[0][0]
            assert context.dry_run is True

    def test_verbose_flag(self, tmp_path):
        """Test --verbose flag creates context with verbose=True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        vault_root = tmp_path / "vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file),
                '--verbose'
            ])

            assert exit_code == 0
            call_args = mock_orch.execute.call_args
            context = call_args[0][0]
            assert context.verbose is True

    def test_quiet_flag(self, tmp_path):
        """Test --quiet flag suppresses output."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        vault_root = tmp_path / "vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(vault_root),
                'process',
                str(test_file),
                '--quiet'
            ])

            assert exit_code == 0

    def test_custom_vault_root(self, tmp_path):
        """Test --vault-root option sets correct vault location."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        custom_vault = tmp_path / "custom_vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(custom_vault),
                'process',
                str(test_file)
            ])

            assert exit_code == 0
            # Verify vault_root was passed to factory
            mock_factory.assert_called_once()
            called_vault_root = mock_factory.call_args[0][0]
            assert called_vault_root == custom_vault

    def test_workers_option(self, tmp_path):
        """Test --workers option sets parallel workers."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        vault_root = tmp_path / "vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(vault_root),
                '--workers', '4',
                'process',
                str(test_file)
            ])

            assert exit_code == 0
            call_args = mock_orch.execute.call_args
            context = call_args[0][0]
            assert context.max_workers == 4

    def test_batch_size_option(self, tmp_path):
        """Test --batch-size option sets batch size."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        vault_root = tmp_path / "vault"

        mock_result = self._create_mock_result(test_file)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator') as mock_factory:
            mock_orch = Mock()
            mock_orch.execute.return_value = mock_result
            mock_factory.return_value = mock_orch

            exit_code = main([
                '--vault-root', str(vault_root),
                '--batch-size', '50',
                'process',
                str(test_file)
            ])

            assert exit_code == 0
            call_args = mock_orch.execute.call_args
            context = call_args[0][0]
            assert context.batch_size == 50
