"""
T033: FilenameDateParser - Parse dates from filenames using multiple formats.
"""

import re
from datetime import datetime, timezone
import logging


logger = logging.getLogger(__name__)


class FilenameDateParser:
    """Parse dates from filenames using multiple patterns."""

    # Date patterns in priority order
    PATTERNS = [
        # ISO 8601: YYYY-MM-DD
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'iso8601', lambda m: (int(m[0]), int(m[1]), int(m[2]))),
        # Compact: YYYYMMDD
        (r'(\d{4})(\d{2})(\d{2})', 'compact', lambda m: (int(m[0]), int(m[1]), int(m[2]))),
        # Underscore: YYYY_MM_DD
        (r'(\d{4})_(\d{2})_(\d{2})', 'underscore', lambda m: (int(m[0]), int(m[1]), int(m[2]))),
    ]

    def parse(self, filename: str) -> datetime | None:
        """
        Parse date from filename.

        Args:
            filename: Filename to parse (without path)

        Returns:
            Datetime if pattern matched, None otherwise
        """
        for pattern, name, extractor in self.PATTERNS:
            match = re.search(pattern, filename)
            if match:
                try:
                    groups = match.groups()
                    year, month, day = extractor(groups)

                    dt = datetime(year, month, day, tzinfo=timezone.utc)
                    logger.debug(f"Parsed date from filename '{filename}': {dt} (pattern: {name})")
                    return dt

                except (ValueError, IndexError) as e:
                    logger.debug(f"Pattern {name} matched but invalid date: {e}")
                    continue

        return None
