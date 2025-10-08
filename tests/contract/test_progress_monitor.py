"""
Contract tests for ProgressMonitor service.
Tests progress tracking and notification logic.
"""

import pytest
from pathlib import Path

from src.models import ProgressState


class TestProgressMonitor:
    """Contract tests for ProgressMonitor."""

    def test_subscribe_contract(self):
        """Test that subscribe() follows the contract specification."""
        from src.services.progress_monitor import ProgressMonitor

        monitor = ProgressMonitor()

        callback_called = []
        def callback(state: ProgressState):
            callback_called.append(state)

        monitor.subscribe(callback)

        # Should support multiple subscribers
        callback2_called = []
        def callback2(state: ProgressState):
            callback2_called.append(state)

        monitor.subscribe(callback2)

    def test_update_contract(self):
        """Test that update() follows the contract specification."""
        from src.services.progress_monitor import ProgressMonitor

        monitor = ProgressMonitor()

        updates_received = []
        def callback(state: ProgressState):
            updates_received.append(state)

        monitor.subscribe(callback)
        monitor.reset(total_files=10)

        # Update progress
        monitor.update(
            files_processed=1,
            current_file="/test/file.txt",
            current_stage="extracting",
            increment_success=True
        )

        assert len(updates_received) > 0, "Must notify subscribers"
        latest_state = updates_received[-1]
        assert isinstance(latest_state, ProgressState), "Must pass ProgressState"
        assert latest_state.processed_files == 1, "Must update processed count"
        assert latest_state.successful_count == 1, "Must increment success"

    def test_get_state_contract(self):
        """Test that get_state() follows the contract specification."""
        from src.services.progress_monitor import ProgressMonitor

        monitor = ProgressMonitor()
        monitor.reset(total_files=5)

        state = monitor.get_state()

        assert isinstance(state, ProgressState), "Must return ProgressState"
        assert state.total_files == 5, "Must have correct total"

    def test_reset_contract(self):
        """Test that reset() follows the contract specification."""
        from src.services.progress_monitor import ProgressMonitor

        monitor = ProgressMonitor()

        updates = []
        def callback(state: ProgressState):
            updates.append(state)

        monitor.subscribe(callback)
        monitor.reset(total_files=10)

        assert len(updates) > 0, "Must notify subscribers on reset"
        state = monitor.get_state()
        assert state.total_files == 10, "Must set total_files"
        assert state.processed_files == 0, "Must reset counters"
        assert state.successful_count == 0, "Must reset success count"


class TestProgressFormatter:
    """Contract tests for ProgressFormatter."""

    def test_format_contract(self):
        """Test that format() follows the contract specification."""
        from src.cli.formatters.progress_formatter import ProgressFormatter

        formatter = ProgressFormatter()

        state = ProgressState(
            total_files=10,
            processed_files=5,
            current_file=Path("/test/file.txt"),
            current_stage="extracting"
        )

        # Single-line format
        output = formatter.format(state, detailed=False)
        assert isinstance(output, str), "Must return string"
        assert len(output.split('\n')) <= 1, "Default should be single-line"

        # Detailed format
        detailed_output = formatter.format(state, detailed=True)
        assert isinstance(detailed_output, str), "Must return string"

    def test_format_summary_contract(self):
        """Test that format_summary() follows the contract specification."""
        from src.cli.formatters.progress_formatter import ProgressFormatter

        formatter = ProgressFormatter()

        state = ProgressState(
            total_files=10,
            processed_files=10,
            successful_count=8,
            duplicate_count=1,
            quarantine_count=1
        )

        summary = formatter.format_summary(state)

        assert isinstance(summary, str), "Must return string"
        assert "8" in summary or "80" in summary, "Should include success count/rate"
        assert "10" in summary, "Should include total"
