"""
QuarantineRecord data model.
Tracks files in quarantine with recovery information.
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum


class QuarantineReason(Enum):
    """Reason a file was quarantined"""
    CHECKSUM_MISMATCH = "checksum_mismatch"
    PERMISSION_ERROR = "permission_error"
    DISK_SPACE_ERROR = "disk_space_error"
    PATH_TOO_LONG = "path_too_long"
    INVALID_CHARACTERS = "invalid_characters"
    DESTINATION_EXISTS = "destination_exists"
    NETWORK_ERROR = "network_error"
    CORRUPTION_DETECTED = "corruption_detected"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class QuarantineRecord:
    """Record of a quarantined file"""
    quarantine_id: str
    file_path: Path
    original_path: Path
    intended_destination: Path
    error_type: QuarantineReason
    error_message: str
    quarantined_at: datetime
    recovery_attempts: int
    file_size: int
    error_traceback: Optional[str] = None
    last_recovery_attempt: Optional[datetime] = None
    metadata_snapshot: Optional[dict] = None
    file_hash: Optional[str] = None
    can_retry: bool = False
    # Error handler fields (Feature 012)
    severity: Optional['ErrorSeverity'] = None  # Error severity level
    escalation_level: int = 0  # Number of times error was escalated
    previous_attempts: list[datetime] = field(default_factory=list)  # History of retry timestamps

    def __post_init__(self):
        """Validate quarantine record"""
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)
        if not isinstance(self.original_path, Path):
            self.original_path = Path(self.original_path)
        if not isinstance(self.intended_destination, Path):
            self.intended_destination = Path(self.intended_destination)
        if not isinstance(self.error_type, QuarantineReason):
            self.error_type = QuarantineReason(self.error_type)

        if self.recovery_attempts < 0:
            raise ValueError("Recovery attempts cannot be negative")
        if self.last_recovery_attempt and self.last_recovery_attempt < self.quarantined_at:
            raise ValueError("Last recovery attempt cannot be before quarantine time")
