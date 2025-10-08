"""
Contract tests for ErrorSeverity classification.

Tests severity enum, classification logic, and escalation behavior.
"""

import pytest
from src.models.error_severity import ErrorSeverity
from src.models.quarantine_record import QuarantineReason


class TestErrorSeverity:
    """Contract tests for ErrorSeverity enum."""

    def test_severity_enum_values(self):
        """Test that all expected severity levels exist."""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.INFO.value == "info"

    def test_is_critical(self):
        """Test is_critical() method."""
        assert ErrorSeverity.CRITICAL.is_critical() is True
        assert ErrorSeverity.ERROR.is_critical() is False
        assert ErrorSeverity.WARNING.is_critical() is False
        assert ErrorSeverity.INFO.is_critical() is False

    def test_is_error(self):
        """Test is_error() method (ERROR or higher)."""
        assert ErrorSeverity.CRITICAL.is_error() is True
        assert ErrorSeverity.ERROR.is_error() is True
        assert ErrorSeverity.WARNING.is_error() is False
        assert ErrorSeverity.INFO.is_error() is False

    def test_is_warning(self):
        """Test is_warning() method (WARNING or higher)."""
        assert ErrorSeverity.CRITICAL.is_warning() is True
        assert ErrorSeverity.ERROR.is_warning() is True
        assert ErrorSeverity.WARNING.is_warning() is True
        assert ErrorSeverity.INFO.is_warning() is False

    def test_requires_notification(self):
        """Test requires_notification() method."""
        assert ErrorSeverity.CRITICAL.requires_notification() is True
        assert ErrorSeverity.ERROR.requires_notification() is True
        assert ErrorSeverity.WARNING.requires_notification() is False
        assert ErrorSeverity.INFO.requires_notification() is False

    def test_get_priority(self):
        """Test numeric priority values."""
        assert ErrorSeverity.CRITICAL.get_priority() == 3
        assert ErrorSeverity.ERROR.get_priority() == 2
        assert ErrorSeverity.WARNING.get_priority() == 1
        assert ErrorSeverity.INFO.get_priority() == 0

    def test_comparison_operations(self):
        """Test severity comparison operators."""
        # Less than
        assert ErrorSeverity.INFO < ErrorSeverity.WARNING
        assert ErrorSeverity.WARNING < ErrorSeverity.ERROR
        assert ErrorSeverity.ERROR < ErrorSeverity.CRITICAL

        # Greater than
        assert ErrorSeverity.CRITICAL > ErrorSeverity.ERROR
        assert ErrorSeverity.ERROR > ErrorSeverity.WARNING
        assert ErrorSeverity.WARNING > ErrorSeverity.INFO

        # Less than or equal
        assert ErrorSeverity.INFO <= ErrorSeverity.INFO
        assert ErrorSeverity.INFO <= ErrorSeverity.WARNING

        # Greater than or equal
        assert ErrorSeverity.CRITICAL >= ErrorSeverity.CRITICAL
        assert ErrorSeverity.CRITICAL >= ErrorSeverity.ERROR

        # Equal
        assert ErrorSeverity.ERROR == ErrorSeverity.ERROR
        assert not (ErrorSeverity.ERROR == ErrorSeverity.WARNING)

    def test_sorting(self):
        """Test that severities can be sorted correctly."""
        severities = [
            ErrorSeverity.INFO,
            ErrorSeverity.CRITICAL,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR
        ]

        sorted_severities = sorted(severities)

        assert sorted_severities == [
            ErrorSeverity.INFO,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL
        ]

    def test_sorting_reverse(self):
        """Test reverse sorting (most severe first)."""
        severities = [
            ErrorSeverity.INFO,
            ErrorSeverity.CRITICAL,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR
        ]

        sorted_severities = sorted(severities, reverse=True)

        assert sorted_severities == [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO
        ]

    def test_string_representation(self):
        """Test __str__() method."""
        assert str(ErrorSeverity.CRITICAL) == "CRITICAL"
        assert str(ErrorSeverity.ERROR) == "ERROR"
        assert str(ErrorSeverity.WARNING) == "WARNING"
        assert str(ErrorSeverity.INFO) == "INFO"

    def test_repr_representation(self):
        """Test __repr__() method."""
        assert repr(ErrorSeverity.CRITICAL) == "ErrorSeverity.CRITICAL"
        assert repr(ErrorSeverity.ERROR) == "ErrorSeverity.ERROR"
        assert repr(ErrorSeverity.WARNING) == "ErrorSeverity.WARNING"
        assert repr(ErrorSeverity.INFO) == "ErrorSeverity.INFO"


class TestErrorSeverityClassification:
    """Contract tests for severity classification logic."""

    def test_default_quarantine_reason_mappings(self):
        """Test that all QuarantineReason values have default severity mappings."""
        import sys
        from pathlib import Path
        # Add specs directory to path for contract imports
        specs_path = Path(__file__).parent.parent.parent / "specs" / "012-error-handler" / "contracts"
        sys.path.insert(0, str(specs_path))
        from error_severity_classifier import get_default_severity_for_reason

        # CRITICAL severities
        assert get_default_severity_for_reason(
            QuarantineReason.PERMISSION_ERROR
        ) == ErrorSeverity.CRITICAL

        assert get_default_severity_for_reason(
            QuarantineReason.DISK_SPACE_ERROR
        ) == ErrorSeverity.CRITICAL

        # ERROR severities
        assert get_default_severity_for_reason(
            QuarantineReason.CORRUPTION_DETECTED
        ) == ErrorSeverity.ERROR

        assert get_default_severity_for_reason(
            QuarantineReason.CHECKSUM_MISMATCH
        ) == ErrorSeverity.ERROR

        assert get_default_severity_for_reason(
            QuarantineReason.UNKNOWN_ERROR
        ) == ErrorSeverity.ERROR

        # WARNING severities
        assert get_default_severity_for_reason(
            QuarantineReason.PATH_TOO_LONG
        ) == ErrorSeverity.WARNING

        assert get_default_severity_for_reason(
            QuarantineReason.INVALID_CHARACTERS
        ) == ErrorSeverity.WARNING

        # INFO severities
        assert get_default_severity_for_reason(
            QuarantineReason.DESTINATION_EXISTS
        ) == ErrorSeverity.INFO

        assert get_default_severity_for_reason(
            QuarantineReason.NETWORK_ERROR
        ) == ErrorSeverity.INFO

    def test_escalation_path(self):
        """Test severity escalation logic."""
        # INFO -> WARNING
        assert ErrorSeverity.WARNING > ErrorSeverity.INFO

        # WARNING -> ERROR
        assert ErrorSeverity.ERROR > ErrorSeverity.WARNING

        # ERROR -> CRITICAL
        assert ErrorSeverity.CRITICAL > ErrorSeverity.ERROR

    def test_critical_is_highest(self):
        """Test that CRITICAL cannot be escalated further."""
        all_severities = [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO
        ]

        for severity in all_severities:
            assert ErrorSeverity.CRITICAL >= severity
