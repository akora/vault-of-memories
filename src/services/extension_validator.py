"""
Extension Validator Implementation
Validates file extensions against detected content types.
"""

import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional

from abc import ABC, abstractmethod
from ..models.file_type_analysis import ValidationResult, ValidationSeverity, ConfidenceLevel


class ExtensionValidator(ABC):
    """Abstract interface for validating file extensions against content."""

    @abstractmethod
    def validate_extension(self, file_path: Path, detected_mime_type: str) -> ValidationResult:
        """Validate file extension against detected content type."""
        pass

    @abstractmethod
    def get_expected_extensions(self, mime_type: str) -> List[str]:
        """Get expected file extensions for a MIME type."""
        pass

    @abstractmethod
    def suggest_extension(self, mime_type: str) -> Optional[str]:
        """Suggest the most appropriate extension for a MIME type."""
        pass


class ExtensionValidatorImpl(ExtensionValidator):
    """
    Implementation of extension validation against content types.

    Compares file extensions with detected MIME types and provides
    validation results with severity levels and suggestions.
    """

    def __init__(self, registry=None):
        """
        Initialize the extension validator.

        Args:
            registry: Optional ContentTypeRegistry for shared type mappings.
                     If not provided, will use internal mappings only.
        """
        self.logger = logging.getLogger(__name__)
        self._registry = registry

        # Initialize mimetypes for system mappings
        mimetypes.init()

        # Enhanced MIME type to extension mappings (fallback)
        self._mime_to_extensions = self._build_mime_extension_mappings()

        # Extension to MIME type mappings (reverse lookup, fallback)
        self._extension_to_mime = self._build_extension_mime_mappings()

    def validate_extension(self, file_path: Path, detected_mime_type: str) -> ValidationResult:
        """
        Validate file extension against detected content type.

        Args:
            file_path: Path to file (for extension extraction)
            detected_mime_type: MIME type detected from content analysis

        Returns:
            ValidationResult indicating if extension matches content
        """
        # Extract extension from file path
        extension = file_path.suffix.lstrip('.').lower() if file_path.suffix else ""

        # Get expected extensions for the detected MIME type
        expected_extensions = self.get_expected_extensions(detected_mime_type)

        # Check if current extension is valid
        is_valid = extension in expected_extensions if extension else False

        # Determine severity and message
        severity, message = self._determine_validation_severity(
            extension, detected_mime_type, expected_extensions
        )

        # Get suggested extension if needed
        suggested_extension = None
        if not is_valid:
            suggested_extension = self.suggest_extension(detected_mime_type)

        # Determine confidence level based on MIME type certainty
        confidence_level = self._determine_validation_confidence(detected_mime_type)

        return ValidationResult(
            file_path=file_path,
            extension=extension,
            detected_mime_type=detected_mime_type,
            is_valid=is_valid,
            severity=severity,
            message=message,
            suggested_extension=suggested_extension,
            confidence_level=confidence_level
        )

    def get_expected_extensions(self, mime_type: str) -> List[str]:
        """
        Get expected file extensions for a MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            List of common extensions for this MIME type
        """
        # Try registry first (includes custom registrations)
        if self._registry:
            extensions = self._registry.get_extensions_for_mime(mime_type)
            if extensions:
                return extensions

        # Try our enhanced mappings
        extensions = self._mime_to_extensions.get(mime_type.lower(), [])

        # Fall back to system mimetypes
        if not extensions:
            system_extensions = mimetypes.guess_all_extensions(mime_type)
            extensions = [ext.lstrip('.') for ext in system_extensions]

        return list(set(extensions))  # Remove duplicates

    def suggest_extension(self, mime_type: str) -> Optional[str]:
        """
        Suggest the most appropriate extension for a MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            Suggested file extension (without dot) or None if unknown
        """
        expected_extensions = self.get_expected_extensions(mime_type)

        if not expected_extensions:
            return None

        # Return the most common/preferred extension for each type
        preferred_extensions = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/bmp': 'bmp',
            'image/tiff': 'tiff',
            'image/webp': 'webp',
            'image/svg+xml': 'svg',

            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'application/vnd.ms-powerpoint': 'ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',

            'text/plain': 'txt',
            'text/html': 'html',
            'text/css': 'css',
            'text/javascript': 'js',
            'text/csv': 'csv',
            'application/json': 'json',
            'text/xml': 'xml',

            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/mp4': 'm4a',
            'audio/flac': 'flac',

            'video/mp4': 'mp4',
            'video/avi': 'avi',
            'video/quicktime': 'mov',
            'video/x-msvideo': 'avi',
            'video/webm': 'webm',

            'application/zip': 'zip',
            'application/x-rar-compressed': 'rar',
            'application/x-tar': 'tar',
            'application/gzip': 'gz'
        }

        # Return preferred extension if available
        preferred = preferred_extensions.get(mime_type.lower())
        if preferred and preferred in expected_extensions:
            return preferred

        # Otherwise return the first available extension
        return expected_extensions[0]

    def _build_mime_extension_mappings(self) -> Dict[str, List[str]]:
        """Build comprehensive MIME type to extensions mapping."""
        return {
            # Images
            'image/jpeg': ['jpg', 'jpeg', 'jpe'],
            'image/png': ['png'],
            'image/gif': ['gif'],
            'image/bmp': ['bmp'],
            'image/tiff': ['tiff', 'tif'],
            'image/webp': ['webp'],
            'image/svg+xml': ['svg'],
            'image/x-icon': ['ico'],
            'image/vnd.microsoft.icon': ['ico'],

            # Documents
            'application/pdf': ['pdf'],
            'application/msword': ['doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
            'application/vnd.ms-excel': ['xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['xlsx'],
            'application/vnd.ms-powerpoint': ['ppt'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['pptx'],
            'application/rtf': ['rtf'],
            'application/vnd.oasis.opendocument.text': ['odt'],
            'application/vnd.oasis.opendocument.spreadsheet': ['ods'],
            'application/vnd.oasis.opendocument.presentation': ['odp'],

            # Text
            'text/plain': ['txt', 'text'],
            'text/html': ['html', 'htm'],
            'text/css': ['css'],
            'text/javascript': ['js'],
            'text/csv': ['csv'],
            'application/json': ['json'],
            'text/xml': ['xml'],
            'application/xml': ['xml'],
            'text/markdown': ['md', 'markdown'],
            'text/yaml': ['yaml', 'yml'],

            # Audio
            'audio/mpeg': ['mp3'],
            'audio/wav': ['wav'],
            'audio/ogg': ['ogg'],
            'audio/mp4': ['m4a'],
            'audio/flac': ['flac'],
            'audio/aac': ['aac'],
            'audio/x-ms-wma': ['wma'],

            # Video
            'video/mp4': ['mp4'],
            'video/avi': ['avi'],
            'video/quicktime': ['mov'],
            'video/x-msvideo': ['avi'],
            'video/webm': ['webm'],
            'video/x-matroska': ['mkv'],
            'video/x-ms-wmv': ['wmv'],
            'video/x-flv': ['flv'],

            # Archives
            'application/zip': ['zip'],
            'application/x-rar-compressed': ['rar'],
            'application/x-tar': ['tar'],
            'application/gzip': ['gz'],
            'application/x-bzip2': ['bz2'],
            'application/x-7z-compressed': ['7z'],

            # Executables
            'application/x-executable': ['exe'],
            'application/x-mach-binary': ['bin'],
            'application/x-dosexec': ['exe'],

            # Others
            'application/octet-stream': []  # Generic binary - no specific extension
        }

    def _build_extension_mime_mappings(self) -> Dict[str, str]:
        """Build extension to MIME type mapping (reverse lookup)."""
        extension_to_mime = {}

        for mime_type, extensions in self._mime_to_extensions.items():
            for ext in extensions:
                # Use the first occurrence (most common) for conflicts
                if ext not in extension_to_mime:
                    extension_to_mime[ext] = mime_type

        return extension_to_mime

    def _determine_validation_severity(
        self,
        extension: str,
        detected_mime_type: str,
        expected_extensions: List[str]
    ) -> tuple[ValidationSeverity, str]:
        """
        Determine validation severity and message.

        Args:
            extension: Current file extension
            detected_mime_type: Detected MIME type
            expected_extensions: List of expected extensions

        Returns:
            Tuple of (severity, message)
        """
        if not extension:
            if detected_mime_type == "application/octet-stream":
                return ValidationSeverity.INFO, "File has no extension and unknown content type"
            else:
                return ValidationSeverity.WARNING, f"File has no extension but appears to be {detected_mime_type}"

        if not expected_extensions:
            if detected_mime_type == "application/octet-stream":
                return ValidationSeverity.INFO, f"Extension '{extension}' with unknown content type"
            else:
                return ValidationSeverity.WARNING, f"Extension '{extension}' but detected type {detected_mime_type} has no known extensions"

        if extension in expected_extensions:
            return ValidationSeverity.INFO, f"Extension '{extension}' matches detected type {detected_mime_type}"

        # Check if it's a related but different extension (e.g., jpg vs jpeg)
        if self._is_related_extension(extension, expected_extensions):
            return ValidationSeverity.INFO, f"Extension '{extension}' is acceptable for {detected_mime_type}"

        # Check severity based on content type importance
        if detected_mime_type.startswith('image/') or detected_mime_type.startswith('video/'):
            return ValidationSeverity.WARNING, f"Extension '{extension}' doesn't match {detected_mime_type} content"
        elif detected_mime_type.startswith('application/'):
            return ValidationSeverity.ERROR, f"Extension '{extension}' conflicts with {detected_mime_type} - may cause processing errors"
        else:
            return ValidationSeverity.WARNING, f"Extension '{extension}' doesn't match detected type {detected_mime_type}"

    def _is_related_extension(self, extension: str, expected_extensions: List[str]) -> bool:
        """Check if extension is a related variant of expected extensions."""
        # Handle common variants
        variants = {
            'jpg': ['jpeg', 'jpe'],
            'jpeg': ['jpg', 'jpe'],
            'tiff': ['tif'],
            'tif': ['tiff'],
            'htm': ['html'],
            'html': ['htm']
        }

        related = variants.get(extension, [])
        return any(rel in expected_extensions for rel in related)

    def _determine_validation_confidence(self, detected_mime_type: str) -> ConfidenceLevel:
        """Determine confidence level for validation based on MIME type."""
        # High confidence for well-defined types
        high_confidence_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf', 'video/mp4', 'audio/mpeg'
        ]

        if detected_mime_type in high_confidence_types:
            return ConfidenceLevel.HIGH

        # Medium confidence for specific types
        if any(detected_mime_type.startswith(prefix) for prefix in ['image/', 'video/', 'audio/']):
            return ConfidenceLevel.MEDIUM

        # Low confidence for generic types
        if detected_mime_type in ['application/octet-stream', 'text/plain']:
            return ConfidenceLevel.LOW

        return ConfidenceLevel.MEDIUM