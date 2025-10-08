"""
Progress state model.

Real-time tracking of processing progress.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class ProgressState:
    """
    Real-time state of processing progress.

    Attributes:
        total_files: Total number of files to process
        processed_files: Number of files processed so far
        current_file: Path to file currently being processed
        current_stage: Name of current pipeline stage
        successful_count: Number of successfully processed files
        duplicate_count: Number of duplicate files detected
        quarantine_count: Number of files quarantined
        failed_count: Number of files that failed processing
        started_at: Timestamp when processing started
        last_update: Timestamp of last progress update
        estimated_completion: Estimated completion time (calculated)
    """

    total_files: int
    processed_files: int = 0
    current_file: Optional[Path] = None
    current_stage: str = "initializing"
    successful_count: int = 0
    duplicate_count: int = 0
    quarantine_count: int = 0
    failed_count: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.total_files < 0:
            raise ValueError("total_files must be >= 0")
        if self.processed_files > self.total_files:
            raise ValueError("processed_files cannot exceed total_files")

    @property
    def percent_complete(self) -> float:
        """Calculate completion percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time since start."""
        return datetime.now() - self.started_at

    @property
    def avg_time_per_file(self) -> float:
        """Calculate average processing time per file in seconds."""
        if self.processed_files == 0:
            return 0.0
        return self.elapsed_time.total_seconds() / self.processed_files

    def update_estimates(self) -> None:
        """Update estimated completion time based on current progress."""
        if self.processed_files > 0 and self.processed_files < self.total_files:
            remaining_files = self.total_files - self.processed_files
            estimated_seconds = remaining_files * self.avg_time_per_file
            self.estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
        self.last_update = datetime.now()
