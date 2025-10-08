"""
Service Contract: ProgressMonitor

Tracks and reports processing progress with real-time updates.
Manages progress state and notifies subscribers of changes.
"""

from typing import Protocol, Callable
from src.models import ProgressState


class ProgressMonitor(Protocol):
    """
    Monitors and reports processing progress in real-time.

    The monitor maintains progress state and notifies subscribers
    when progress changes. Supports multiple output formats and
    update strategies.

    Responsibilities:
    - Track current progress state
    - Notify subscribers on updates
    - Calculate progress metrics (ETA, rate)
    - Format progress for display
    - Throttle updates to avoid spam
    """

    def subscribe(self, callback: Callable[[ProgressState], None]) -> None:
        """
        Subscribe to progress updates.

        Args:
            callback: Function to call on progress update

        Contract:
            - MUST store callback for future notifications
            - MUST support multiple subscribers
            - SHOULD call callback immediately with current state
        """
        ...

    def unsubscribe(self, callback: Callable[[ProgressState], None]) -> None:
        """
        Unsubscribe from progress updates.

        Args:
            callback: Function to remove from subscribers

        Contract:
            - MUST remove callback if present
            - MUST not error if callback not found
        """
        ...

    def update(
        self,
        files_processed: int | None = None,
        current_file: str | None = None,
        current_stage: str | None = None,
        increment_success: bool = False,
        increment_duplicate: bool = False,
        increment_quarantine: bool = False,
        increment_failed: bool = False
    ) -> None:
        """
        Update progress state and notify subscribers.

        Args:
            files_processed: Total files processed (if changed)
            current_file: Currently processing file path
            current_stage: Current pipeline stage
            increment_success: Increment successful count
            increment_duplicate: Increment duplicate count
            increment_quarantine: Increment quarantine count
            increment_failed: Increment failed count

        Contract:
            - MUST update state with provided values
            - MUST increment counters if flags set
            - MUST update last_update timestamp
            - MUST recalculate estimates
            - MUST notify all subscribers
            - SHOULD throttle notifications (min 100ms between updates)
        """
        ...

    def get_state(self) -> ProgressState:
        """
        Get current progress state.

        Returns:
            Current ProgressState snapshot

        Contract:
            - MUST return immutable snapshot
            - MUST not block on notification
        """
        ...

    def reset(self, total_files: int) -> None:
        """
        Reset progress state for new processing run.

        Args:
            total_files: Total number of files to process

        Contract:
            - MUST create new ProgressState
            - MUST reset all counters to 0
            - MUST set total_files
            - MUST notify subscribers of reset
        """
        ...


class ProgressFormatter(Protocol):
    """
    Formats progress state for display.

    Responsibilities:
    - Convert ProgressState to human-readable format
    - Support multiple output formats (text, JSON)
    - Handle terminal width and color support
    """

    def format(self, state: ProgressState, detailed: bool = False) -> str:
        """
        Format progress state for display.

        Args:
            state: Current progress state
            detailed: Include detailed statistics

        Returns:
            Formatted progress string

        Contract:
            - MUST return single-line format by default
            - MUST use multi-line format if detailed=True
            - MUST handle zero total_files gracefully
            - SHOULD include progress bar
            - SHOULD colorize output if terminal supports it
        """
        ...

    def format_summary(self, state: ProgressState) -> str:
        """
        Format progress summary (final statistics).

        Args:
            state: Final progress state

        Returns:
            Formatted summary string

        Contract:
            - MUST include all counters
            - MUST include success rate
            - MUST include duration
            - MUST include avg time per file
            - SHOULD highlight errors/warnings
        """
        ...


class ProgressBar(Protocol):
    """
    ASCII progress bar renderer.

    Responsibilities:
    - Render progress bar with percentage
    - Auto-detect terminal width
    - Support custom symbols
    """

    def render(
        self,
        current: int,
        total: int,
        width: int | None = None,
        prefix: str = "",
        suffix: str = ""
    ) -> str:
        """
        Render progress bar.

        Args:
            current: Current progress value
            total: Total target value
            width: Bar width in characters (auto-detect if None)
            prefix: Text before bar
            suffix: Text after bar

        Returns:
            Formatted progress bar string

        Contract:
            - MUST handle current > total gracefully (cap at 100%)
            - MUST handle total = 0 gracefully
            - MUST auto-detect terminal width if not provided
            - MUST fit within specified width
            - SHOULD use Unicode box characters if supported
        """
        ...


# Example Usage
"""
from src.services import ProgressMonitor, ProgressFormatter

# Create monitor
monitor = ProgressMonitor()
formatter = ProgressFormatter()

# Subscribe to updates
def print_progress(state: ProgressState):
    output = formatter.format(state)
    print(f"\\r{output}", end="", flush=True)

monitor.subscribe(print_progress)

# Start processing
monitor.reset(total_files=100)

# Update during processing
for i in range(100):
    monitor.update(
        files_processed=i+1,
        current_file=f"/source/file_{i}.jpg",
        current_stage="extracting",
        increment_success=True
    )
    # ... process file ...

# Final summary
final_state = monitor.get_state()
print(f"\\n{formatter.format_summary(final_state)}")
"""
