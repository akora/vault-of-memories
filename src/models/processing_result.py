"""
Processing result model.

Summary of completed pipeline execution.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .processing_context import ProcessingContext
    from .progress_state import ProgressState


@dataclass
class ProcessingResult:
    """
    Summary of completed processing pipeline execution.

    Attributes:
        context: Original ProcessingContext
        final_state: Final ProgressState
        success: Whether processing completed successfully
        total_duration: Total processing time
        files_processed: Total files processed
        successful_files: List of successfully processed file paths
        duplicate_files: List of duplicate file paths
        quarantined_files: List of quarantined file paths
        failed_files: List of failed file paths with errors
        warnings: List of warning messages
        completed_at: Timestamp when processing completed
    """

    context: "ProcessingContext"
    final_state: "ProgressState"
    success: bool
    total_duration: timedelta
    files_processed: int
    successful_files: list[Path]
    duplicate_files: list[Path]
    quarantined_files: list[Path]
    failed_files: list[tuple[Path, str]]  # (path, error_message)
    warnings: list[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Calculate percentage of successfully processed files."""
        if self.files_processed == 0:
            return 0.0
        return (len(self.successful_files) / self.files_processed) * 100

    @property
    def had_errors(self) -> bool:
        """Check if any errors occurred during processing."""
        return len(self.failed_files) > 0 or len(self.quarantined_files) > 0

    @property
    def summary_stats(self) -> dict:
        """Generate summary statistics dictionary."""
        avg_time = self.total_duration.total_seconds() / max(self.files_processed, 1)
        return {
            'total_files': self.files_processed,
            'successful': len(self.successful_files),
            'duplicates': len(self.duplicate_files),
            'quarantined': len(self.quarantined_files),
            'failed': len(self.failed_files),
            'success_rate': f"{self.success_rate:.1f}%",
            'duration': str(self.total_duration),
            'avg_time_per_file': f"{avg_time:.2f}s"
        }
