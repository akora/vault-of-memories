"""
Contract: QuarantineManager

The QuarantineManager service handles quarantine operations for problematic files.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# Input/Output Types
class QuarantineReason(Enum):
    """See data-model.md for full specification"""
    CHECKSUM_MISMATCH = "checksum_mismatch"
    PERMISSION_ERROR = "permission_error"
    DISK_SPACE_ERROR = "disk_space_error"
    PATH_TOO_LONG = "path_too_long"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class QuarantineRecord:
    """See data-model.md for full specification"""
    quarantine_id: str
    file_path: Path
    original_path: Path
    intended_destination: Path
    error_type: QuarantineReason
    error_message: str
    quarantined_at: datetime
    recovery_attempts: int


# Contract Interface
class QuarantineManager:
    """
    Manages quarantine operations for problematic files.
    """

    def quarantine_file(
        self,
        source_path: Path,
        intended_destination: Path,
        error: Exception,
        metadata: dict
    ) -> QuarantineRecord:
        """
        Move file to quarantine with error classification.

        Contract:
        - MUST classify error into QuarantineReason
        - MUST move file to quarantine/{error_type}/
        - MUST create metadata JSON alongside file
        - MUST record in quarantine database table
        - MUST preserve original file (don't delete)
        - MUST capture error traceback
        - MUST return QuarantineRecord with full details

        Args:
            source_path: Path to problematic file
            intended_destination: Where file was supposed to go
            error: Exception that caused quarantine
            metadata: File metadata

        Returns:
            QuarantineRecord with quarantine information

        Raises:
            PermissionError: If cannot access quarantine folder
        """
        raise NotImplementedError

    def classify_error(
        self,
        error: Exception
    ) -> QuarantineReason:
        """
        Classify exception into quarantine reason.

        Contract:
        - MUST map standard exceptions to QuarantineReason
        - MUST return UNKNOWN_ERROR for unrecognized exceptions
        - MUST handle None/empty exceptions

        Args:
            error: Exception to classify

        Returns:
            Appropriate QuarantineReason
        """
        raise NotImplementedError

    def get_quarantine_path(
        self,
        error_type: QuarantineReason,
        filename: str
    ) -> Path:
        """
        Calculate path for quarantined file.

        Contract:
        - MUST return path in format: quarantine/{error_type}/{filename}
        - MUST append timestamp if filename collision
        - MUST sanitize filename for cross-platform compatibility

        Args:
            error_type: Reason for quarantine
            filename: Original filename

        Returns:
            Path where file should be quarantined
        """
        raise NotImplementedError

    def list_quarantined_files(
        self,
        error_type: QuarantineReason | None = None
    ) -> list[QuarantineRecord]:
        """
        List files in quarantine, optionally filtered by error type.

        Contract:
        - MUST query quarantine database
        - MUST filter by error_type if provided
        - MUST return empty list if no files
        - MUST order by quarantine_date descending

        Args:
            error_type: Optional filter by error type

        Returns:
            List of QuarantineRecord
        """
        raise NotImplementedError
