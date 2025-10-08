"""
T030: DateHierarchyBuilder - Builds date-based folder paths (YYYY/YYYY-MM/YYYY-MM-DD).
"""

from pathlib import Path
from datetime import date, datetime


class DateHierarchyBuilder:
    """Constructs date-based folder hierarchy paths."""

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
        """
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()

        # Validate date is reasonable (1900-2100)
        if not (1900 <= date_obj.year <= 2100):
            raise ValueError(f"Date year must be between 1900-2100, got {date_obj.year}")

        # Get formatted components
        year, month, day = self.get_date_components(date_obj)

        # Build hierarchy: base/YYYY/YYYY-MM/YYYY-MM-DD
        return base_path / year / month / day

    def parse_date_path(self, path: Path) -> date | None:
        """
        Parse date from existing date hierarchy path.

        Args:
            path: Path potentially containing date hierarchy

        Returns:
            Extracted date if found, None otherwise
        """
        import re

        path_str = str(path)

        # Match YYYY/YYYY-MM/YYYY-MM-DD pattern
        pattern = r'(\d{4})/(\d{4})-(\d{2})/(\d{4})-(\d{2})-(\d{2})'
        match = re.search(pattern, path_str)

        if match:
            year1, year2, month, year3, month2, day = match.groups()

            # Validate consistency
            if year1 == year2 == year3 and month == month2:
                try:
                    return date(int(year1), int(month), int(day))
                except ValueError:
                    pass

        return None

    def get_date_components(self, date_obj: date | datetime) -> tuple[str, str, str]:
        """
        Get formatted date components for hierarchy.

        Args:
            date_obj: Date to format

        Returns:
            Tuple of (year, month, day) as strings:
            - year: "YYYY" (e.g., "2024")
            - month: "YYYY-MM" (e.g., "2024-01")
            - day: "YYYY-MM-DD" (e.g., "2024-01-15")
        """
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()

        year = f"{date_obj.year:04d}"
        month = f"{date_obj.year:04d}-{date_obj.month:02d}"
        day = f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d}"

        return year, month, day
