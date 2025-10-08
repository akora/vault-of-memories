"""
BatchMoveResult data model.
Result of a batch move operation.
"""

from dataclasses import dataclass
from typing import List
from src.models.move_result import MoveResult


@dataclass
class BatchMoveResult:
    """Result of a batch move operation"""
    batch_id: str
    results: List[MoveResult]
    total_operations: int
    successful_count: int
    duplicate_count: int
    quarantine_count: int
    failed_count: int
    total_time_ms: float
    average_time_ms: float
    warnings: List[str] = None

    def __post_init__(self):
        """Validate batch result"""
        if self.warnings is None:
            self.warnings = []

        # Validation
        if self.total_operations != len(self.results):
            raise ValueError("Total operations must equal number of results")

        counts_sum = self.successful_count + self.duplicate_count + self.quarantine_count + self.failed_count
        if counts_sum != self.total_operations:
            raise ValueError(f"Sum of counts ({counts_sum}) must equal total operations ({self.total_operations})")

        if self.total_operations > 0:
            expected_avg = self.total_time_ms / self.total_operations
            if abs(self.average_time_ms - expected_avg) > 0.01:  # Allow small floating point error
                raise ValueError(f"Average time ({self.average_time_ms}) doesn't match calculated ({expected_avg})")

    @property
    def success_rate(self) -> float:
        """Percentage of successful operations"""
        return (self.successful_count / self.total_operations) * 100 if self.total_operations > 0 else 0.0

    @property
    def all_succeeded(self) -> bool:
        """True if all operations succeeded"""
        return self.successful_count == self.total_operations

    @property
    def any_failed(self) -> bool:
        """True if any operations failed"""
        return self.failed_count > 0
