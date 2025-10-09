"""
T035: MimeDetector - MIME type detection with fallback strategies.
"""

import mimetypes
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class MimeDetector:
    """Detect MIME types with multiple fallback strategies."""

    # Custom extension to MIME type mappings for formats not in stdlib
    CUSTOM_EXTENSIONS = {
        # Raw photo formats
        '.nef': 'image/x-nikon-nef',
        '.cr2': 'image/x-canon-cr2',
        '.cr3': 'image/x-canon-cr3',
        '.arw': 'image/x-sony-arw',
        '.dng': 'image/x-adobe-dng',
        '.orf': 'image/x-olympus-orf',
        '.rw2': 'image/x-panasonic-rw2',
        '.raf': 'image/x-fuji-raf',
        '.pef': 'image/x-pentax-pef',

        # HEIC/HEIF (may not be in older Python versions)
        '.heic': 'image/heic',
        '.heif': 'image/heif',
    }

    def __init__(self):
        mimetypes.init()

    def detect(self, file_path: Path) -> tuple[str, str, float]:
        """
        Detect MIME type using fallback strategy.

        Returns:
            Tuple of (mime_type, method_used, confidence)
        """
        # Level 1: python-magic/libmagic (most reliable)
        # Note: Skipping libmagic for simplicity, would use in production

        # Level 2: Extension-based detection
        mime_type, confidence = self._detect_from_extension(file_path)
        if mime_type:
            return mime_type, 'extension', confidence

        # Level 3: Default fallback
        return 'application/octet-stream', 'fallback', 0.0

    def _detect_from_extension(self, file_path: Path) -> tuple[str | None, float]:
        """Level 2: Use file extension for MIME detection."""
        # Check custom extensions first (higher confidence for known formats)
        ext = file_path.suffix.lower()
        if ext in self.CUSTOM_EXTENSIONS:
            return self.CUSTOM_EXTENSIONS[ext], 0.9

        # Fall back to stdlib mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type, 0.7
        return None, 0.0
