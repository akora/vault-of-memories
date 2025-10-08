"""
BatchMoveRequest data model.
Represents a batch move operation request.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from src.models.move_operation import MoveOperation


@dataclass
class BatchMoveRequest:
    """Request to move multiple files as a batch"""
    batch_id: str
    operations: List[MoveOperation]
    validate_space: bool
    parallel: bool
    max_workers: int = 1
    stop_on_error: bool = False
    created_at: datetime = None

    def __post_init__(self):
        """Validate batch request"""
        if self.created_at is None:
            self.created_at = datetime.now()

        if not self.operations:
            raise ValueError("Batch must contain at least one operation")
        if self.max_workers < 1:
            raise ValueError("Max workers must be at least 1")
        if self.parallel and self.max_workers < 2:
            raise ValueError("Parallel execution requires max_workers >= 2")

        # Check for duplicate operation IDs
        op_ids = [op.operation_id for op in self.operations]
        if len(op_ids) != len(set(op_ids)):
            raise ValueError("Batch contains duplicate operation IDs")

    @property
    def total_size(self) -> int:
        """Total size of all files in batch"""
        return sum(op.file_size for op in self.operations)

    @property
    def operation_count(self) -> int:
        """Number of operations in batch"""
        return len(self.operations)
