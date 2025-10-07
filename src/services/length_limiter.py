"""
Length limiter for filename length constraints.

Handles filesystem filename length limitations (typically 255 characters)
with intelligent truncation strategies.
"""

import logging
from pathlib import Path
from .component_formatter import ComponentFormatter


logger = logging.getLogger(__name__)


class LengthLimiter:
    """
    Enforce maximum filename length with intelligent truncation.

    Preserves essential components (date, extension, counter) while
    truncating or dropping optional components.
    """

    # Default maximum filename length (common filesystem limit)
    DEFAULT_MAX_LENGTH = 255

    # Components that should never be truncated (in priority order)
    PRESERVE_COMPONENTS = ["date", "extension", "counter"]

    # Components that can be dropped first (lowest priority)
    DROPPABLE_COMPONENTS = ["category", "secondary_category", "author"]

    # Components that can be truncated (medium priority)
    TRUNCATABLE_COMPONENTS = ["device_model", "title", "description"]

    def __init__(self):
        """Initialize length limiter."""
        self.formatter = ComponentFormatter()

    def limit_length(self, filename: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
        """
        Enforce maximum filename length with intelligent truncation.

        Args:
            filename: Filename to check/truncate
            max_length: Maximum allowed length (default 255)

        Returns:
            Filename within length limit

        Raises:
            ValueError: If filename cannot be truncated to fit
        """
        if len(filename) <= max_length:
            return filename

        logger.info(f"Filename too long ({len(filename)} > {max_length}), truncating: {filename}")

        # Split into base and extension
        path = Path(filename)
        base = path.stem
        ext = path.suffix

        # Extension must be preserved
        if len(ext) >= max_length:
            raise ValueError(f"Extension alone exceeds max length: {ext}")

        # Calculate available length for base
        available = max_length - len(ext)

        if available < 10:
            raise ValueError(f"Not enough space for base name (available: {available})")

        # Strategy 1: Truncate the middle of the base name
        truncated_base = self._truncate_base(base, available)

        result = truncated_base + ext

        logger.info(f"Truncated filename: {filename} → {result}")

        return result

    def get_truncation_strategy(self) -> str:
        """
        Get description of truncation strategy used.

        Returns:
            Description of how components are prioritized for truncation
        """
        return (
            "Truncation strategy:\n"
            "1. Preserve: date, extension, counter\n"
            "2. Drop first: category, secondary_category, author\n"
            "3. Truncate next: device_model, title, description\n"
            "4. Finally: truncate middle of base name with '...'"
        )

    def _truncate_base(self, base: str, max_length: int) -> str:
        """
        Truncate base filename intelligently.

        Args:
            base: Base filename (without extension)
            max_length: Maximum length for base

        Returns:
            Truncated base name
        """
        if len(base) <= max_length:
            return base

        # Use component formatter's truncate_middle method
        return self.formatter.truncate_middle(base, max_length)

    def calculate_safe_length(self, filename: str, components: dict) -> int:
        """
        Calculate safe length for a filename given its components.

        Args:
            filename: Current filename
            components: Dictionary of components used

        Returns:
            Recommended maximum length to avoid truncation
        """
        # Account for extension
        ext_length = len(Path(filename).suffix)

        # Account for potential counter (9 chars: "-00000001")
        counter_overhead = 9

        # Recommended safe length
        safe_length = self.DEFAULT_MAX_LENGTH - ext_length - counter_overhead

        return safe_length

    def needs_truncation(self, filename: str, max_length: int = DEFAULT_MAX_LENGTH) -> bool:
        """
        Check if filename needs truncation.

        Args:
            filename: Filename to check
            max_length: Maximum allowed length

        Returns:
            True if filename exceeds max_length
        """
        return len(filename) > max_length

    def preview_truncation(self, filename: str, max_length: int = DEFAULT_MAX_LENGTH) -> dict:
        """
        Preview truncation without applying it.

        Args:
            filename: Filename to analyze
            max_length: Maximum allowed length

        Returns:
            Dictionary with truncation analysis
        """
        needs_truncation = self.needs_truncation(filename, max_length)

        if not needs_truncation:
            return {
                "needs_truncation": False,
                "current_length": len(filename),
                "max_length": max_length,
                "truncated_filename": filename,
                "chars_removed": 0
            }

        truncated = self.limit_length(filename, max_length)

        return {
            "needs_truncation": True,
            "current_length": len(filename),
            "max_length": max_length,
            "truncated_filename": truncated,
            "chars_removed": len(filename) - len(truncated)
        }
