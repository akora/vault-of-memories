"""
Service Contract: SummaryFormatter

Generates human-readable processing summaries and reports.
Formats ProcessingResult for terminal and file output.
"""

from typing import Protocol
from pathlib import Path
from src.models import ProcessingResult, ProgressState


class SummaryFormatter(Protocol):
    """
    Formats processing results and summaries for display.

    The formatter converts ProcessingResult into human-readable
    text with appropriate formatting, colors, and structure.

    Responsibilities:
    - Format processing results
    - Generate error reports
    - Create summary statistics
    - Support multiple output formats
    - Handle terminal capabilities
    """

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

        Contract:
            - MUST include summary statistics
            - MUST highlight errors/warnings
            - MUST show success rate
            - MUST include duration
            - SHOULD list quarantined/failed files if verbose
            - SHOULD use colors if use_colors and terminal supports it
        """
        ...

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

        Contract:
            - MUST list all failed/quarantined files
            - MUST include error messages
            - MUST group by error type if requested
            - MUST suggest recovery steps
            - SHOULD include file paths and error details
        """
        ...

    def format_statistics(self, result: ProcessingResult) -> str:
        """
        Format summary statistics table.

        Args:
            result: Processing result

        Returns:
            Formatted statistics table

        Contract:
            - MUST include total files
            - MUST include counts by status (success/duplicate/quarantine/failed)
            - MUST include success rate percentage
            - MUST include processing duration
            - MUST include average time per file
            - SHOULD format as aligned table
        """
        ...

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

        Contract:
            - MUST include title
            - MUST show file paths
            - MUST truncate if exceeds max_items
            - MUST show count of truncated items
            - SHOULD use relative paths if possible
        """
        ...


class ProgressDisplay(Protocol):
    """
    Real-time progress display for terminal.

    Responsibilities:
    - Display progress bar
    - Show current file/stage
    - Update in-place (overwrite line)
    - Handle terminal resize
    """

    def display(self, state: ProgressState) -> None:
        """
        Display current progress state.

        Args:
            state: Current progress state

        Contract:
            - MUST display on single line (overwrite previous)
            - MUST include progress bar
            - MUST show percentage
            - MUST show current file (truncated if needed)
            - SHOULD show ETA if available
            - SHOULD clear line before writing
        """
        ...

    def display_final(self, state: ProgressState) -> None:
        """
        Display final progress state (no overwrite).

        Args:
            state: Final progress state

        Contract:
            - MUST write newline after display
            - MUST show final statistics
            - MUST not overwrite previous output
        """
        ...

    def clear(self) -> None:
        """
        Clear progress display line.

        Contract:
            - MUST clear current line
            - MUST reset cursor position
        """
        ...


class ColorFormatter(Protocol):
    """
    ANSI color formatting utilities.

    Responsibilities:
    - Apply ANSI color codes
    - Detect terminal capabilities
    - Disable colors for non-TTY
    """

    def colorize(self, text: str, color: str) -> str:
        """
        Apply color to text.

        Args:
            text: Text to colorize
            color: Color name (green, yellow, red, blue, etc.)

        Returns:
            Text with ANSI color codes

        Contract:
            - MUST return unmodified text if colors disabled
            - MUST use standard ANSI color codes
            - MUST reset color after text
            - SHOULD support: green, yellow, red, blue, cyan, magenta
        """
        ...

    def success(self, text: str) -> str:
        """Colorize text as success (green)."""
        ...

    def warning(self, text: str) -> str:
        """Colorize text as warning (yellow)."""
        ...

    def error(self, text: str) -> str:
        """Colorize text as error (red)."""
        ...

    def info(self, text: str) -> str:
        """Colorize text as info (blue)."""
        ...

    def is_terminal(self) -> bool:
        """
        Check if output is a terminal (supports colors).

        Returns:
            True if TTY, False otherwise

        Contract:
            - MUST detect TTY using sys.stdout.isatty()
            - MUST return False if NO_COLOR env var set
        """
        ...


# Example Usage
"""
from src.cli.formatters import SummaryFormatter, ProgressDisplay, ColorFormatter

# Create formatters
summary_formatter = SummaryFormatter()
progress_display = ProgressDisplay()
colors = ColorFormatter()

# Display progress
def on_progress(state: ProgressState):
    progress_display.display(state)

# Format result
result_text = summary_formatter.format_result(result, verbose=True)
print(result_text)

# Format errors if any
if result.had_errors:
    error_report = summary_formatter.format_error_report(result)
    print(colors.error("\\nERROR REPORT:"))
    print(error_report)

# Format statistics
stats = summary_formatter.format_statistics(result)
print(stats)
"""
