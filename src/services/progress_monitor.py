"""
Progress monitor service.

Tracks and reports processing progress with real-time updates.
"""

import logging
import time
from typing import Callable, Optional
from pathlib import Path

from src.models import ProgressState

logger = logging.getLogger(__name__)


class ProgressMonitor:
    """
    Monitors and reports processing progress in real-time.

    Maintains progress state and notifies subscribers when progress changes.
    Throttles updates to avoid spam (minimum 100ms between notifications).
    """

    def __init__(self):
        """Initialize progress monitor."""
        self._state: Optional[ProgressState] = None
        self._callbacks: list[Callable[[ProgressState], None]] = []
        self._last_update_time = 0.0
        self._min_update_interval = 0.1  # 100ms

    def subscribe(self, callback: Callable[[ProgressState], None]) -> None:
        """
        Subscribe to progress updates.

        Args:
            callback: Function to call on progress update
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

            # Call immediately with current state
            if self._state:
                callback(self._state)

    def unsubscribe(self, callback: Callable[[ProgressState], None]) -> None:
        """
        Unsubscribe from progress updates.

        Args:
            callback: Function to remove from subscribers
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def update(
        self,
        files_processed: Optional[int] = None,
        current_file: Optional[str | Path] = None,
        current_stage: Optional[str] = None,
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
        """
        if not self._state:
            logger.warning("Cannot update progress - not initialized")
            return

        # Update state
        if files_processed is not None:
            self._state.processed_files = files_processed

        if current_file is not None:
            self._state.current_file = Path(current_file) if isinstance(current_file, str) else current_file

        if current_stage is not None:
            self._state.current_stage = current_stage

        # Increment counters
        if increment_success:
            self._state.successful_count += 1

        if increment_duplicate:
            self._state.duplicate_count += 1

        if increment_quarantine:
            self._state.quarantine_count += 1

        if increment_failed:
            self._state.failed_count += 1

        # Update estimates and timestamp
        self._state.update_estimates()

        # Notify subscribers (with throttling)
        self._notify_subscribers()

    def get_state(self) -> ProgressState:
        """
        Get current progress state.

        Returns:
            Current ProgressState snapshot
        """
        if not self._state:
            # Return empty state if not initialized
            return ProgressState(total_files=0)

        # Return a copy to ensure immutability
        return ProgressState(
            total_files=self._state.total_files,
            processed_files=self._state.processed_files,
            current_file=self._state.current_file,
            current_stage=self._state.current_stage,
            successful_count=self._state.successful_count,
            duplicate_count=self._state.duplicate_count,
            quarantine_count=self._state.quarantine_count,
            failed_count=self._state.failed_count,
            started_at=self._state.started_at,
            last_update=self._state.last_update,
            estimated_completion=self._state.estimated_completion
        )

    def reset(self, total_files: int) -> None:
        """
        Reset progress state for new processing run.

        Args:
            total_files: Total number of files to process
        """
        self._state = ProgressState(total_files=total_files)
        logger.debug(f"Progress monitor reset: {total_files} files")

        # Notify all subscribers of reset
        self._notify_subscribers(force=True)

    def _notify_subscribers(self, force: bool = False) -> None:
        """
        Notify all subscribers of state change.

        Args:
            force: Force notification even if throttled
        """
        current_time = time.time()

        # Throttle updates (except when forced)
        if not force:
            if current_time - self._last_update_time < self._min_update_interval:
                return

        self._last_update_time = current_time

        # Notify all callbacks
        for callback in self._callbacks:
            try:
                callback(self.get_state())
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
