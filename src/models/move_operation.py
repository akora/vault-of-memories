"""
MoveOperation data model.
Tracks a single file move operation from source to destination.
"""

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum


class OperationStatus(Enum):
    """Status of a move operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    QUARANTINED = "quarantined"


@dataclass
class MoveOperation:
    """Represents a file move operation with full tracking"""
    operation_id: str
    source_path: Path
    destination_path: Path
    file_hash: str
    file_size: int
    status: OperationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_attempted: bool = False
    rollback_success: Optional[bool] = None

    def __post_init__(self):
        """Validate move operation"""
        if not isinstance(self.source_path, Path):
            self.source_path = Path(self.source_path)
        if not isinstance(self.destination_path, Path):
            self.destination_path = Path(self.destination_path)
        if not isinstance(self.status, OperationStatus):
            self.status = OperationStatus(self.status)

        # Validation
        if self.source_path == self.destination_path:
            raise ValueError("Source and destination paths cannot be the same")
        if len(self.file_hash) != 64:  # SHA256
            raise ValueError(f"Invalid SHA256 hash length: {len(self.file_hash)}")
        if self.file_size < 0:
            raise ValueError("File size cannot be negative")
        if self.completed_at and self.started_at:
            if self.completed_at < self.started_at:
                raise ValueError("Completed time cannot be before started time")
