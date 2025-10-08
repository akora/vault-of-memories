"""
Integration test: CLI commands (status, validate).

Tests status and validate commands which don't require full pipeline.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.cli.main import main


class TestCLICommands:
    """Test CLI commands that don't require pipeline orchestration."""

    def test_status_command_empty_vault(self, tmp_path):
        """Test status command on non-existent vault."""
        vault_root = tmp_path / "vault"

        # Execute status command
        exit_code = main([
            '--vault-root', str(vault_root),
            'status'
        ])

        # Should succeed even if vault doesn't exist
        assert exit_code == 0, "Status should handle non-existent vault gracefully"

    def test_status_command_with_verbose(self, tmp_path):
        """Test status command with verbose flag."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir(parents=True)

        # Execute status command with verbose
        exit_code = main([
            '--vault-root', str(vault_root),
            'status',
            '--verbose'
        ])

        assert exit_code == 0

    def test_validate_command_single_file(self, tmp_path):
        """Test validate command on a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Execute validate command
        exit_code = main([
            'validate',
            str(test_file)
        ])

        assert exit_code == 0, "Validate should succeed on valid file"

    def test_validate_command_missing_file(self, tmp_path):
        """Test validate command on missing file."""
        test_file = tmp_path / "nonexistent.txt"

        # Execute validate command
        exit_code = main([
            'validate',
            str(test_file)
        ])

        # Should return error code (65 for not found)
        assert exit_code == 65, f"Should fail on missing file, got {exit_code}"

    def test_validate_command_verbose(self, tmp_path):
        """Test validate command with verbose output."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Execute validate with verbose
        exit_code = main([
            'validate',
            str(test_file),
            '--verbose'
        ])

        assert exit_code == 0

    def test_help_command(self):
        """Test help command."""
        # Execute help command
        exit_code = main(['help'])

        assert exit_code == 0, "Help should always succeed"

    def test_no_command_shows_help(self):
        """Test that running with no command shows help."""
        # Execute with no command
        exit_code = main([])

        assert exit_code == 0, "No command should show help"

    def test_recover_command_no_quarantine(self, tmp_path):
        """Test recover command when there's no quarantine."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir(parents=True)

        with patch('src.cli.service_factory.ServiceFactory.create_pipeline_orchestrator'):
            # Execute recover command
            exit_code = main([
                '--vault-root', str(vault_root),
                'recover'
            ])

            # Should succeed with message about no quarantine
            assert exit_code == 0, "Should handle no quarantine gracefully"
