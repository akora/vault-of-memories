"""
T028: CreationResult data model.
"""

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class CreationResult:
    """Result of folder creation operation."""

    path: Path
    created_new: bool
    already_existed: bool
    permissions_set: int
    timestamp: datetime
    error: str | None = None

    def __post_init__(self):
        """Validate creation result after initialization."""
        # Either created_new or already_existed must be True (unless error)
        if self.error is None:
            if not (self.created_new or self.already_existed):
                raise ValueError("Either created_new or already_existed must be True")
