"""
Contract tests for CommandHandler services.
Tests CLI command implementations.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.models import CommandOptions


class TestProcessCommand:
    """Contract tests for ProcessCommand."""

    def test_execute_contract(self, tmp_path):
        """Test that execute() follows the contract specification."""
        from src.cli.commands.process import ProcessCommand

        # Setup
        source = tmp_path / "test.txt"
        source.write_text("test content")
        vault_root = tmp_path / "vault"

        options = CommandOptions(
            command="process",
            source=source,
            vault_root=vault_root,
            dry_run=False
        )

        # Create command (will need orchestrator, etc.)
        command = ProcessCommand(
            orchestrator=Mock(),
            progress_monitor=Mock(),
            formatter=Mock()
        )

        exit_code = command.execute(options)

        assert isinstance(exit_code, int), "Must return int exit code"
        assert 0 <= exit_code <= 255, "Exit code must be valid"


class TestStatusCommand:
    """Contract tests for StatusCommand."""

    def test_execute_contract(self, tmp_path):
        """Test that execute() follows the contract specification."""
        from src.cli.commands.status import StatusCommand

        options = CommandOptions(
            command="status",
            vault_root=tmp_path / "vault"
        )

        command = StatusCommand(database_manager=Mock())

        exit_code = command.execute(options)

        assert isinstance(exit_code, int), "Must return int exit code"
        assert exit_code in [0, 1], "Status should return 0 (healthy) or 1 (issues)"


class TestRecoverCommand:
    """Contract tests for RecoverCommand."""

    def test_execute_contract(self, tmp_path):
        """Test that execute() follows the contract specification."""
        from src.cli.commands.recover import RecoverCommand

        options = CommandOptions(
            command="recover",
            vault_root=tmp_path / "vault",
            quarantine_type="corruption_detected"
        )

        command = RecoverCommand(
            orchestrator=Mock(),
            quarantine_manager=Mock()
        )

        exit_code = command.execute(options)

        assert isinstance(exit_code, int), "Must return int exit code"


class TestValidateCommand:
    """Contract tests for ValidateCommand."""

    def test_execute_contract(self, tmp_path):
        """Test that execute() follows the contract specification."""
        from src.cli.commands.validate import ValidateCommand

        source = tmp_path / "test.txt"
        source.write_text("test")

        options = CommandOptions(
            command="validate",
            source=source,
            vault_root=tmp_path / "vault"
        )

        command = ValidateCommand()

        exit_code = command.execute(options)

        assert isinstance(exit_code, int), "Must return int exit code"
        assert exit_code in [0, 1], "Validate should return 0 (valid) or 1 (issues)"
