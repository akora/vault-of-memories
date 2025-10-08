"""
Metadata sanitizer for safe filename generation.

Removes or replaces invalid filename characters to ensure cross-platform
compatibility and filesystem safety.
"""

import logging
import re
from typing import List


logger = logging.getLogger(__name__)


class MetadataSanitizer:
    """
    Sanitize metadata values for safe filename use.

    Handles:
    - Invalid filename characters (platform-specific)
    - Whitespace normalization
    - Unicode character handling
    - Consecutive separator cleanup
    """

    # Characters that are invalid in filenames (strictest common set - Windows)
    INVALID_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

    # Additional characters to replace for cleaner filenames
    REPLACE_CHARS = {
        ' ': '-',  # Spaces to hyphens
        '_': '-',  # Underscores to hyphens for consistency
        '.': '-',  # Dots to hyphens (except in extension)
    }

    # Characters to remove entirely
    REMOVE_CHARS = ['\t', '\n', '\r', '\x00']

    def sanitize(self, value: str, component_name: str = None) -> str:
        """
        Sanitize a metadata value for safe filename use.

        Args:
            value: Metadata value to sanitize
            component_name: Optional component name for context-specific rules

        Returns:
            Sanitized string safe for filename use

        Raises:
            ValueError: If value cannot be sanitized (empty after cleaning)
        """
        if not value:
            raise ValueError("Value cannot be empty")

        result = str(value)

        # Remove control characters and null bytes
        for char in self.REMOVE_CHARS:
            result = result.replace(char, '')

        # Remove invalid filename characters
        for char in self.INVALID_CHARS:
            result = result.replace(char, '')

        # Replace problematic characters
        for old_char, new_char in self.REPLACE_CHARS.items():
            result = result.replace(old_char, new_char)

        # Normalize consecutive separators
        result = re.sub(r'-{2,}', '-', result)

        # Remove leading/trailing separators
        result = result.strip('-_.')

        # Handle Unicode: normalize and remove problematic characters
        # Keep most Unicode but normalize forms
        result = self._normalize_unicode(result)

        if not result:
            raise ValueError(f"Value '{value}' resulted in empty string after sanitization")

        return result

    def get_invalid_characters(self) -> List[str]:
        """
        Get list of characters that are invalid in filenames.

        Returns:
            List of invalid characters
        """
        return self.INVALID_CHARS.copy()

    def _normalize_unicode(self, value: str) -> str:
        """
        Normalize Unicode characters for safe filename use.

        Args:
            value: String possibly containing Unicode

        Returns:
            Normalized string
        """
        # For now, allow most Unicode characters
        # Could add more aggressive normalization if needed
        return value

    def sanitize_extension(self, ext: str) -> str:
        """
        Sanitize file extension.

        Args:
            ext: File extension (with or without leading dot)

        Returns:
            Sanitized extension with leading dot
        """
        if not ext:
            return ""

        # Ensure leading dot
        if not ext.startswith('.'):
            ext = '.' + ext

        # Remove invalid characters from extension
        result = ext.lower()
        for char in self.INVALID_CHARS:
            result = result.replace(char, '')

        # Extensions shouldn't have spaces or hyphens
        result = result.replace(' ', '').replace('-', '').replace('_', '')

        return result

    def is_safe_filename(self, filename: str) -> bool:
        """
        Check if a filename is safe (no invalid characters).

        Args:
            filename: Filename to check

        Returns:
            True if safe, False otherwise
        """
        for char in self.INVALID_CHARS:
            if char in filename:
                return False

        for char in self.REMOVE_CHARS:
            if char in filename:
                return False

        return True

    def get_sanitized_char_count(self, original: str, sanitized: str) -> int:
        """
        Count how many characters were changed during sanitization.

        Args:
            original: Original string
            sanitized: Sanitized string

        Returns:
            Number of characters that were modified/removed
        """
        if len(original) == len(sanitized):
            # Same length, count character differences
            return sum(1 for a, b in zip(original, sanitized) if a != b)
        else:
            # Different lengths, characters were removed
            return abs(len(original) - len(sanitized))
