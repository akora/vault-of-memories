"""
Contract: DateHierarchyBuilder

Builds date-based folder paths (YYYY/YYYY-MM/YYYY-MM-DD).
"""

from datetime import date, datetime
from pathlib import Path


class DateHierarchyBuilder:
    """
    Constructs date-based folder hierarchy paths.

    Responsibilities:
    - Build YYYY/YYYY-MM/YYYY-MM-DD folder structure
    - Handle date formatting consistently
    - Support alternative hierarchy formats if configured
    """

    def build_path(self, base_path: Path, date_obj: date | datetime) -> Path:
        """
        Build date-based folder path.

        Args:
            base_path: Base directory (e.g., /vault/photos/family)
            date_obj: Date to organize by

        Returns:
            Complete path with date hierarchy (e.g., /vault/photos/family/2024/2024-01/2024-01-15)

        Raises:
            ValueError: If date is invalid

        Contract:
            - MUST create YYYY/YYYY-MM/YYYY-MM-DD hierarchy
            - Year MUST be 4 digits (e.g., "2024")
            - Month MUST be YYYY-MM format (e.g., "2024-01")
            - Day MUST be YYYY-MM-DD format (e.g., "2024-01-15")
            - MUST use date_obj.date() if datetime provided
            - MUST validate date is reasonable (1900-2100)
        """
        raise NotImplementedError

    def parse_date_path(self, path: Path) -> date | None:
        """
        Parse date from existing date hierarchy path.

        Args:
            path: Path potentially containing date hierarchy

        Returns:
            Extracted date if found, None otherwise

        Contract:
            - MUST recognize YYYY/YYYY-MM/YYYY-MM-DD pattern
            - MUST return None if pattern not found
            - MUST validate extracted date is valid
        """
        raise NotImplementedError

    def get_date_components(self, date_obj: date | datetime) -> tuple[str, str, str]:
        """
        Get formatted date components for hierarchy.

        Args:
            date_obj: Date to format

        Returns:
            Tuple of (year, month, day) as strings

        Contract:
            - year: "YYYY" (e.g., "2024")
            - month: "YYYY-MM" (e.g., "2024-01")
            - day: "YYYY-MM-DD" (e.g., "2024-01-15")
            - MUST use zero-padding for single-digit months/days
        """
        raise NotImplementedError
