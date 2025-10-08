"""
Error severity classification.

Defines severity levels for errors encountered during vault processing.
"""

from enum import Enum


class ErrorSeverity(Enum):
    """
    Error severity levels.

    Severity impacts notification behavior, error reporting, and escalation logic.
    """

    CRITICAL = "critical"  # System-level failures requiring immediate attention
    ERROR = "error"        # Processing failures that prevent file handling
    WARNING = "warning"    # Issues that may degrade quality but allow processing
    INFO = "info"          # Informational notices about edge cases

    def is_critical(self) -> bool:
        """Check if severity is CRITICAL."""
        return self == ErrorSeverity.CRITICAL

    def is_error(self) -> bool:
        """Check if severity is ERROR or higher."""
        return self in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR)

    def is_warning(self) -> bool:
        """Check if severity is WARNING or higher."""
        return self in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR, ErrorSeverity.WARNING)

    def requires_notification(self) -> bool:
        """
        Check if this severity typically requires notification.

        Returns:
            True for CRITICAL and ERROR, False for WARNING and INFO
        """
        return self.is_error()

    def get_priority(self) -> int:
        """
        Get numeric priority for sorting (higher = more severe).

        Returns:
            Priority value: CRITICAL=3, ERROR=2, WARNING=1, INFO=0
        """
        priority_map = {
            ErrorSeverity.CRITICAL: 3,
            ErrorSeverity.ERROR: 2,
            ErrorSeverity.WARNING: 1,
            ErrorSeverity.INFO: 0
        }
        return priority_map[self]

    def __lt__(self, other):
        """Less than comparison for sorting."""
        if not isinstance(other, ErrorSeverity):
            return NotImplemented
        return self.get_priority() < other.get_priority()

    def __le__(self, other):
        """Less than or equal comparison."""
        if not isinstance(other, ErrorSeverity):
            return NotImplemented
        return self.get_priority() <= other.get_priority()

    def __gt__(self, other):
        """Greater than comparison."""
        if not isinstance(other, ErrorSeverity):
            return NotImplemented
        return self.get_priority() > other.get_priority()

    def __ge__(self, other):
        """Greater than or equal comparison."""
        if not isinstance(other, ErrorSeverity):
            return NotImplemented
        return self.get_priority() >= other.get_priority()

    def __str__(self) -> str:
        """String representation."""
        return self.value.upper()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"ErrorSeverity.{self.name}"
