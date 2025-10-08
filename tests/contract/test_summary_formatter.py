"""
Contract tests for SummaryFormatter service.
Tests result formatting and display logic.
"""

import pytest
from pathlib import Path
from datetime import timedelta

from src.models import ProcessingContext, ProcessingResult, ProgressState


class TestSummaryFormatter:
    """Contract tests for SummaryFormatter."""

    def test_format_result_contract(self, tmp_path):
        """Test that format_result() follows the contract specification."""
        from src.cli.formatters.summary_formatter import SummaryFormatter

        formatter = SummaryFormatter()

        # Create test result
        context = ProcessingContext(
            source_path=tmp_path / "source",
            vault_root=tmp_path / "vault",
            config={}
        )

        final_state = ProgressState(
            total_files=10,
            processed_files=10,
            successful_count=8,
            duplicate_count=1,
            quarantine_count=1
        )

        result = ProcessingResult(
            context=context,
            final_state=final_state,
            success=True,
            total_duration=timedelta(seconds=45),
            files_processed=10,
            successful_files=[tmp_path / f"file{i}.txt" for i in range(8)],
            duplicate_files=[tmp_path / "dup.txt"],
            quarantined_files=[tmp_path / "bad.txt"],
            failed_files=[]
        )

        # Test default format
        output = formatter.format_result(result, verbose=False, use_colors=False)
        assert isinstance(output, str), "Must return string"
        assert "10" in output, "Should include total files"
        assert "8" in output or "80" in output, "Should include success info"

        # Test verbose format
        verbose_output = formatter.format_result(result, verbose=True, use_colors=False)
        assert isinstance(verbose_output, str), "Must return string"
        assert len(verbose_output) > len(output), "Verbose should be longer"

    def test_format_error_report_contract(self, tmp_path):
        """Test that format_error_report() follows the contract specification."""
        from src.cli.formatters.summary_formatter import SummaryFormatter

        formatter = SummaryFormatter()

        context = ProcessingContext(
            source_path=tmp_path / "source",
            vault_root=tmp_path / "vault",
            config={}
        )

        final_state = ProgressState(total_files=2, processed_files=2)

        result = ProcessingResult(
            context=context,
            final_state=final_state,
            success=False,
            total_duration=timedelta(seconds=10),
            files_processed=2,
            successful_files=[],
            duplicate_files=[],
            quarantined_files=[tmp_path / "bad1.txt"],
            failed_files=[(tmp_path / "bad2.txt", "Test error")]
        )

        error_report = formatter.format_error_report(result, group_by_type=True)

        assert isinstance(error_report, str), "Must return string"
        assert "bad1.txt" in error_report, "Should list quarantined files"
        assert "bad2.txt" in error_report, "Should list failed files"
        assert "Test error" in error_report, "Should include error message"

    def test_format_statistics_contract(self, tmp_path):
        """Test that format_statistics() follows the contract specification."""
        from src.cli.formatters.summary_formatter import SummaryFormatter

        formatter = SummaryFormatter()

        context = ProcessingContext(
            source_path=tmp_path / "source",
            vault_root=tmp_path / "vault",
            config={}
        )

        final_state = ProgressState(
            total_files=10,
            processed_files=10,
            successful_count=10
        )

        result = ProcessingResult(
            context=context,
            final_state=final_state,
            success=True,
            total_duration=timedelta(seconds=50),
            files_processed=10,
            successful_files=[tmp_path / f"file{i}.txt" for i in range(10)],
            duplicate_files=[],
            quarantined_files=[],
            failed_files=[]
        )

        stats = formatter.format_statistics(result)

        assert isinstance(stats, str), "Must return string"
        assert "10" in stats, "Should include counts"
        assert "100" in stats or "100.0" in stats, "Should include 100% success rate"


class TestColorFormatter:
    """Contract tests for ColorFormatter."""

    def test_colorize_contract(self):
        """Test that colorize() follows the contract specification."""
        from src.cli.formatters.color_formatter import ColorFormatter

        formatter = ColorFormatter()

        # Test with colors enabled
        colored = formatter.colorize("test", "green")
        assert isinstance(colored, str), "Must return string"

        # Test color methods
        assert isinstance(formatter.success("test"), str)
        assert isinstance(formatter.warning("test"), str)
        assert isinstance(formatter.error("test"), str)
        assert isinstance(formatter.info("test"), str)

    def test_is_terminal_contract(self):
        """Test that is_terminal() follows the contract specification."""
        from src.cli.formatters.color_formatter import ColorFormatter

        formatter = ColorFormatter()

        result = formatter.is_terminal()
        assert isinstance(result, bool), "Must return bool"
