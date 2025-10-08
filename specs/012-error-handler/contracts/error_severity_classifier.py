"""
Contract: Error Severity Classifier

Defines how exceptions are mapped to severity levels.
"""

from typing import Optional
from src.models.error_severity import ErrorSeverity
from src.models.quarantine_record import QuarantineReason


class ErrorSeverityClassifierContract:
    """
    Contract for classifying error severity.

    All implementations must follow these rules for consistency across
    the error handling system.
    """

    def classify_by_exception(self, error: Optional[Exception]) -> ErrorSeverity:
        """
        Classify exception into severity level.

        Classification Rules:
        - PermissionError, OSError (disk space) -> CRITICAL
        - File corruption, checksum failures -> ERROR
        - Path validation issues -> WARNING
        - Duplicate files, retryable errors -> INFO
        - Unknown/None errors -> ERROR (safe default)

        Args:
            error: Exception to classify (may be None)

        Returns:
            Appropriate ErrorSeverity

        Contract Requirements:
        1. MUST handle None input (return ERROR)
        2. MUST return ERROR for unknown exception types
        3. MUST be deterministic (same input -> same output)
        4. MUST complete in < 1ms
        5. MUST NOT raise exceptions
        """
        raise NotImplementedError

    def classify_by_quarantine_reason(self, reason: QuarantineReason) -> ErrorSeverity:
        """
        Classify quarantine reason into severity level.

        Severity Mapping:
        - CRITICAL: PERMISSION_ERROR, DISK_SPACE_ERROR
        - ERROR: CORRUPTION_DETECTED, CHECKSUM_MISMATCH, UNKNOWN_ERROR
        - WARNING: PATH_TOO_LONG, INVALID_CHARACTERS
        - INFO: DESTINATION_EXISTS, NETWORK_ERROR

        Args:
            reason: QuarantineReason to classify

        Returns:
            Appropriate ErrorSeverity

        Contract Requirements:
        1. MUST handle all QuarantineReason enum values
        2. MUST be deterministic
        3. MUST complete in < 1ms
        4. MUST NOT raise exceptions
        """
        raise NotImplementedError

    def can_severity_be_escalated(self, current: ErrorSeverity) -> bool:
        """
        Check if severity can be escalated further.

        Args:
            current: Current severity level

        Returns:
            True if escalation possible (not already CRITICAL)

        Contract Requirements:
        1. CRITICAL cannot be escalated
        2. ERROR, WARNING, INFO can be escalated
        """
        raise NotImplementedError

    def escalate_severity(self, current: ErrorSeverity) -> ErrorSeverity:
        """
        Escalate severity to next level.

        Escalation Path:
        - INFO -> WARNING
        - WARNING -> ERROR
        - ERROR -> CRITICAL
        - CRITICAL -> CRITICAL (no change)

        Args:
            current: Current severity level

        Returns:
            Escalated severity level

        Contract Requirements:
        1. MUST follow escalation path above
        2. MUST be idempotent for CRITICAL
        3. MUST NOT raise exceptions
        """
        raise NotImplementedError


# Default Severity Mappings (Reference Implementation)

DEFAULT_QUARANTINE_REASON_TO_SEVERITY = {
    # CRITICAL: System-level failures
    QuarantineReason.PERMISSION_ERROR: ErrorSeverity.CRITICAL,
    QuarantineReason.DISK_SPACE_ERROR: ErrorSeverity.CRITICAL,

    # ERROR: Processing failures
    QuarantineReason.CORRUPTION_DETECTED: ErrorSeverity.ERROR,
    QuarantineReason.CHECKSUM_MISMATCH: ErrorSeverity.ERROR,
    QuarantineReason.UNKNOWN_ERROR: ErrorSeverity.ERROR,

    # WARNING: Recoverable issues
    QuarantineReason.PATH_TOO_LONG: ErrorSeverity.WARNING,
    QuarantineReason.INVALID_CHARACTERS: ErrorSeverity.WARNING,

    # INFO: Expected edge cases
    QuarantineReason.DESTINATION_EXISTS: ErrorSeverity.INFO,
    QuarantineReason.NETWORK_ERROR: ErrorSeverity.INFO,
}


def get_default_severity_for_reason(reason: QuarantineReason) -> ErrorSeverity:
    """
    Get default severity for quarantine reason.

    Args:
        reason: QuarantineReason

    Returns:
        Default ErrorSeverity for this reason
    """
    return DEFAULT_QUARANTINE_REASON_TO_SEVERITY.get(reason, ErrorSeverity.ERROR)
