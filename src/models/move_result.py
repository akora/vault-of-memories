"""
MoveResult data model.
Result of a move operation, returned to caller.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from src.models.move_operation import MoveOperation


@dataclass
class MoveResult:
    """Result of a file move operation"""
    success: bool
    operation: MoveOperation
    actual_destination: Optional[Path]
    is_duplicate: bool
    is_quarantined: bool
    execution_time_ms: float
    error: Optional[Exception] = None
    warnings: list[str] = None

    def __post_init__(self):
        """Initialize defaults and validate"""
        if self.warnings is None:
            self.warnings = []

        # Validation
        if self.success and not self.actual_destination:
            raise ValueError("Successful operation must have actual_destination")
        if not self.success and not self.error:
            raise ValueError("Failed operation must have error")
        if self.is_duplicate and self.is_quarantined:
            raise ValueError("Operation cannot be both duplicate and quarantined")
        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative")

    @property
    def moved_to_vault(self) -> bool:
        """True if file successfully moved to intended vault location"""
        return self.success and not self.is_duplicate and not self.is_quarantined

    @property
    def needs_attention(self) -> bool:
        """True if operation requires user attention"""
        return self.is_quarantined or (not self.success) or len(self.warnings) > 0
