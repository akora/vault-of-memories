"""
Summary formatter.

Generates human-readable processing summaries and reports.
"""

from pathlib import Path
from collections import defaultdict

from src.models import ProcessingResult, ErrorSeverity
from .color_formatter import ColorFormatter


class SummaryFormatter:
    """Formats processing results and summaries for display."""

    def __init__(self):
        """Initialize summary formatter."""
        self.colors = ColorFormatter()

    def format_result(
        self,
        result: ProcessingResult,
        verbose: bool = False,
        use_colors: bool = True
    ) -> str:
        """
        Format processing result for display.

        Args:
            result: Processing result to format
            verbose: Include detailed file listings
            use_colors: Use ANSI color codes

        Returns:
            Formatted result string
        """
        lines = []

        # Header
        if result.success:
            header = "✓ Processing Complete"
            if use_colors:
                header = self.colors.success(header)
        else:
            header = "✗ Processing Complete with Errors"
            if use_colors:
                header = self.colors.error(header)

        lines.append(header)
        lines.append("")

        # Statistics
        lines.append(self.format_statistics(result))

        # Detailed file listings if verbose
        if verbose and result.had_errors:
            lines.append("")
            lines.append(self.format_error_report(result))

        return "\n".join(lines)

    def format_error_report(
        self,
        result: ProcessingResult,
        group_by_type: bool = True
    ) -> str:
        """
        Format detailed error report.

        Args:
            result: Processing result with errors
            group_by_type: Group errors by quarantine type

        Returns:
            Formatted error report string
        """
        lines = ["Error Report:"]

        if result.quarantined_files:
            lines.append(f"\nQuarantined Files ({len(result.quarantined_files)}):")
            for file_path in result.quarantined_files:
                lines.append(f"  - {file_path}")

        if result.failed_files:
            lines.append(f"\nFailed Files ({len(result.failed_files)}):")
            for file_path, error in result.failed_files:
                lines.append(f"  - {file_path}")
                lines.append(f"    Error: {error}")

        return "\n".join(lines)

    def format_statistics(self, result: ProcessingResult) -> str:
        """
        Format summary statistics table.

        Args:
            result: Processing result

        Returns:
            Formatted statistics table
        """
        stats = result.summary_stats

        lines = [
            "Statistics:",
            f"  Total files:    {stats['total_files']}",
            f"  Successful:     {stats['successful']}",
            f"  Duplicates:     {stats['duplicates']}",
            f"  Quarantined:    {stats['quarantined']}",
            f"  Failed:         {stats['failed']}",
            f"  Success rate:   {stats['success_rate']}",
            f"  Duration:       {stats['duration']}",
            f"  Avg time/file:  {stats['avg_time_per_file']}"
        ]

        return "\n".join(lines)

    def format_file_list(
        self,
        files: list[Path],
        title: str,
        max_items: int = 10
    ) -> str:
        """
        Format list of file paths for display.

        Args:
            files: List of file paths
            title: Section title
            max_items: Maximum items to show (rest summarized)

        Returns:
            Formatted file list string
        """
        lines = [f"{title} ({len(files)}):"]

        for i, file_path in enumerate(files[:max_items]):
            lines.append(f"  - {file_path}")

        if len(files) > max_items:
            remaining = len(files) - max_items
            lines.append(f"  ... and {remaining} more")

        return "\n".join(lines)
