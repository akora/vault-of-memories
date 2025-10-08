"""
Progress formatter.

Formats progress state for display.
"""

from src.models import ProgressState


class ProgressFormatter:
    """Formats progress state for display."""

    def format(self, state: ProgressState, detailed: bool = False) -> str:
        """
        Format progress state for display.

        Args:
            state: Current progress state
            detailed: Include detailed statistics

        Returns:
            Formatted progress string
        """
        if detailed:
            return self._format_detailed(state)
        else:
            return self._format_single_line(state)

    def _format_single_line(self, state: ProgressState) -> str:
        """Format as single line with progress bar."""
        percent = state.percent_complete
        bar = self._create_progress_bar(percent, width=20)

        current_file = ""
        if state.current_file:
            current_file = f" | {state.current_file.name}"

        return f"[{bar}] {percent:.1f}% ({state.processed_files}/{state.total_files}){current_file}"

    def _format_detailed(self, state: ProgressState) -> str:
        """Format with detailed statistics."""
        lines = [
            f"Progress: {state.percent_complete:.1f}%",
            f"Files: {state.processed_files}/{state.total_files}",
            f"Successful: {state.successful_count}",
            f"Duplicates: {state.duplicate_count}",
            f"Quarantined: {state.quarantine_count}",
            f"Failed: {state.failed_count}",
            f"Stage: {state.current_stage}"
        ]

        if state.estimated_completion:
            lines.append(f"ETA: {state.estimated_completion.strftime('%H:%M:%S')}")

        return "\n".join(lines)

    def _create_progress_bar(self, percent: float, width: int = 20) -> str:
        """Create ASCII progress bar."""
        filled = int(width * percent / 100)
        bar = "=" * filled + "-" * (width - filled)
        return bar

    def format_summary(self, state: ProgressState) -> str:
        """
        Format progress summary (final statistics).

        Args:
            state: Final progress state

        Returns:
            Formatted summary string
        """
        lines = [
            "\nProcessing Summary:",
            f"  Total files: {state.total_files}",
            f"  Successful: {state.successful_count}",
            f"  Duplicates: {state.duplicate_count}",
            f"  Quarantined: {state.quarantine_count}",
            f"  Failed: {state.failed_count}",
            f"  Duration: {state.elapsed_time}",
            f"  Avg time/file: {state.avg_time_per_file:.2f}s"
        ]

        return "\n".join(lines)
