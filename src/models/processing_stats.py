"""
Processing Statistics Data Model
Aggregated statistics for batch processing operations.
"""

from dataclasses import dataclass


@dataclass
class ProcessingStats:
    """
    Statistics for batch processing operations.

    Attributes:
        total_files: Total files encountered during processing
        processed_files: Successfully processed files
        duplicate_files: Files identified as duplicates
        error_files: Files that failed processing
        system_files_removed: System/hidden files filtered out
        total_size: Total bytes processed
        processing_time: Time taken for operation in seconds
    """
    total_files: int = 0
    processed_files: int = 0
    duplicate_files: int = 0
    error_files: int = 0
    system_files_removed: int = 0
    total_size: int = 0
    processing_time: float = 0.0

    def __post_init__(self):
        """Validate statistics after initialization."""
        self._validate_counts()
        self._validate_totals()

    def _validate_counts(self):
        """Validate all counts are non-negative."""
        counts = [
            self.total_files,
            self.processed_files,
            self.duplicate_files,
            self.error_files,
            self.system_files_removed
        ]

        for count in counts:
            if not isinstance(count, int) or count < 0:
                raise ValueError("All file counts must be non-negative integers")

    def _validate_totals(self):
        """Validate total size and processing time."""
        if not isinstance(self.total_size, int) or self.total_size < 0:
            raise ValueError("Total size must be a non-negative integer")

        if not isinstance(self.processing_time, (int, float)) or self.processing_time < 0:
            raise ValueError("Processing time must be a non-negative number")

    def add_processed_file(self, file_size: int):
        """Add a successfully processed file to statistics."""
        self.total_files += 1
        self.processed_files += 1
        self.total_size += file_size

    def add_duplicate_file(self, file_size: int):
        """Add a duplicate file to statistics."""
        self.total_files += 1
        self.duplicate_files += 1
        self.total_size += file_size

    def add_error_file(self):
        """Add a failed file to statistics."""
        self.total_files += 1
        self.error_files += 1

    def add_system_file_removed(self):
        """Add a system file that was filtered out."""
        self.system_files_removed += 1

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage of processed files."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    def get_duplicate_rate(self) -> float:
        """Calculate duplicate rate as percentage of total files."""
        if self.total_files == 0:
            return 0.0
        return (self.duplicate_files / self.total_files) * 100

    def get_error_rate(self) -> float:
        """Calculate error rate as percentage of total files."""
        if self.total_files == 0:
            return 0.0
        return (self.error_files / self.total_files) * 100

    def get_processing_speed(self) -> float:
        """Calculate processing speed in files per second."""
        if self.processing_time == 0:
            return 0.0
        return self.total_files / self.processing_time

    def get_throughput(self) -> float:
        """Calculate throughput in bytes per second."""
        if self.processing_time == 0:
            return 0.0
        return self.total_size / self.processing_time

    def to_dict(self) -> dict:
        """Convert statistics to dictionary for serialization."""
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "duplicate_files": self.duplicate_files,
            "error_files": self.error_files,
            "system_files_removed": self.system_files_removed,
            "total_size": self.total_size,
            "processing_time": self.processing_time,
            "success_rate": self.get_success_rate(),
            "duplicate_rate": self.get_duplicate_rate(),
            "error_rate": self.get_error_rate(),
            "processing_speed": self.get_processing_speed(),
            "throughput": self.get_throughput()
        }

    def merge(self, other: "ProcessingStats") -> "ProcessingStats":
        """
        Merge this statistics with another set of statistics.

        Args:
            other: Another ProcessingStats to merge

        Returns:
            New ProcessingStats with combined values
        """
        return ProcessingStats(
            total_files=self.total_files + other.total_files,
            processed_files=self.processed_files + other.processed_files,
            duplicate_files=self.duplicate_files + other.duplicate_files,
            error_files=self.error_files + other.error_files,
            system_files_removed=self.system_files_removed + other.system_files_removed,
            total_size=self.total_size + other.total_size,
            processing_time=max(self.processing_time, other.processing_time)  # Use max for concurrent operations
        )

    def __str__(self) -> str:
        """String representation of processing statistics."""
        return (
            f"ProcessingStats(total={self.total_files}, "
            f"processed={self.processed_files}, "
            f"duplicates={self.duplicate_files}, "
            f"errors={self.error_files}, "
            f"system_removed={self.system_files_removed})"
        )