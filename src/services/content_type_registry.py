"""
Content Type Registry Implementation
Manages relationships between MIME types, extensions, and processors.
"""

import logging
import mimetypes
from typing import Dict, List, Optional

from abc import ABC, abstractmethod


class ContentTypeRegistry(ABC):
    """Abstract interface for managing content type mappings."""

    @abstractmethod
    def get_mime_for_extension(self, extension: str) -> Optional[str]:
        """Get expected MIME type for file extension."""
        pass

    @abstractmethod
    def get_extensions_for_mime(self, mime_type: str) -> List[str]:
        """Get file extensions associated with MIME type."""
        pass

    @abstractmethod
    def register_type_mapping(self, mime_type: str, extensions: List[str], processor: str) -> None:
        """Register a new content type mapping."""
        pass

    @abstractmethod
    def is_known_type(self, mime_type: str) -> bool:
        """Check if MIME type is known/supported."""
        pass


class ContentTypeRegistryImpl(ContentTypeRegistry):
    """
    Implementation of content type registry.

    Maintains comprehensive mappings between MIME types, file extensions,
    and processor assignments with support for custom registrations.
    """

    def __init__(self):
        """Initialize the content type registry."""
        self.logger = logging.getLogger(__name__)

        # Initialize system mimetypes
        mimetypes.init()

        # Custom extension to MIME type mappings
        self._extension_to_mime = self._build_extension_mappings()

        # MIME type to extensions mappings (reverse lookup)
        self._mime_to_extensions = self._build_mime_mappings()

        # MIME type to processor mappings
        self._mime_to_processor = self._build_processor_mappings()

        # Custom registrations
        self._custom_mappings = {}

    def get_mime_for_extension(self, extension: str) -> Optional[str]:
        """
        Get expected MIME type for file extension.

        Args:
            extension: File extension (with or without dot)

        Returns:
            Expected MIME type or None if unknown
        """
        # Clean extension
        clean_ext = extension.lstrip('.').lower()

        # Check custom mappings first
        for mime_type, data in self._custom_mappings.items():
            if clean_ext in data.get('extensions', []):
                return mime_type

        # Check our enhanced mappings
        mime_type = self._extension_to_mime.get(clean_ext)
        if mime_type:
            return mime_type

        # Fall back to system mimetypes
        system_mime = mimetypes.guess_type(f"file.{clean_ext}")[0]
        return system_mime

    def get_extensions_for_mime(self, mime_type: str) -> List[str]:
        """
        Get file extensions associated with MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            List of associated extensions (without dots)
        """
        mime_lower = mime_type.lower()

        # Check custom mappings first
        if mime_lower in self._custom_mappings:
            return self._custom_mappings[mime_lower].get('extensions', [])

        # Check our enhanced mappings
        extensions = self._mime_to_extensions.get(mime_lower, [])

        # Fall back to system mimetypes if no custom mapping
        if not extensions:
            system_extensions = mimetypes.guess_all_extensions(mime_type)
            extensions = [ext.lstrip('.') for ext in system_extensions]

        return list(set(extensions))  # Remove duplicates

    def register_type_mapping(self, mime_type: str, extensions: List[str], processor: str) -> None:
        """
        Register a new content type mapping.

        Args:
            mime_type: MIME type string
            extensions: List of file extensions
            processor: Target processor name
        """
        mime_lower = mime_type.lower()
        clean_extensions = [ext.lstrip('.').lower() for ext in extensions]

        # Store custom mapping
        self._custom_mappings[mime_lower] = {
            'extensions': clean_extensions,
            'processor': processor
        }

        # Update reverse mappings
        for ext in clean_extensions:
            self._extension_to_mime[ext] = mime_lower

        self._mime_to_extensions[mime_lower] = clean_extensions
        self._mime_to_processor[mime_lower] = processor

        self.logger.info(f"Registered custom mapping: {mime_type} -> {extensions} -> {processor}")

    def is_known_type(self, mime_type: str) -> bool:
        """
        Check if MIME type is known/supported.

        Args:
            mime_type: MIME type string

        Returns:
            True if type is known, False otherwise
        """
        mime_lower = mime_type.lower()

        # Check custom mappings
        if mime_lower in self._custom_mappings:
            return True

        # Check our enhanced mappings
        if mime_lower in self._mime_to_extensions:
            return True

        # Check system mimetypes
        extensions = mimetypes.guess_all_extensions(mime_type)
        return len(extensions) > 0

    def get_processor_for_mime(self, mime_type: str) -> Optional[str]:
        """
        Get the processor assigned to handle a MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            Processor name or None if not assigned
        """
        mime_lower = mime_type.lower()

        # Check custom mappings first
        if mime_lower in self._custom_mappings:
            return self._custom_mappings[mime_lower].get('processor')

        # Check built-in mappings
        return self._mime_to_processor.get(mime_lower)

    def get_all_known_types(self) -> List[str]:
        """
        Get all known MIME types.

        Returns:
            List of all known MIME types
        """
        # Combine custom, enhanced, and system types
        all_types = set()

        # Add custom types
        all_types.update(self._custom_mappings.keys())

        # Add enhanced types
        all_types.update(self._mime_to_extensions.keys())

        # Add common system types
        all_types.update(mimetypes.common_types.values())
        all_types.update(mimetypes.types_map.values())

        return sorted(list(all_types))

    def get_registry_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the registry.

        Returns:
            Dictionary with registry statistics
        """
        return {
            'total_mime_types': len(self.get_all_known_types()),
            'custom_mappings': len(self._custom_mappings),
            'enhanced_mappings': len(self._mime_to_extensions),
            'total_extensions': len(self._extension_to_mime),
            'processor_mappings': len(self._mime_to_processor)
        }

    def _build_extension_mappings(self) -> Dict[str, str]:
        """Build comprehensive extension to MIME type mappings."""
        return {
            # Images
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'jpe': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'ico': 'image/x-icon',

            # Documents
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'rtf': 'application/rtf',
            'odt': 'application/vnd.oasis.opendocument.text',
            'ods': 'application/vnd.oasis.opendocument.spreadsheet',
            'odp': 'application/vnd.oasis.opendocument.presentation',

            # Text
            'txt': 'text/plain',
            'text': 'text/plain',
            'html': 'text/html',
            'htm': 'text/html',
            'css': 'text/css',
            'js': 'text/javascript',
            'json': 'application/json',
            'xml': 'text/xml',
            'csv': 'text/csv',
            'md': 'text/markdown',
            'markdown': 'text/markdown',
            'yaml': 'text/yaml',
            'yml': 'text/yaml',

            # Audio
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'wma': 'audio/x-ms-wma',

            # Video
            'mp4': 'video/mp4',
            'avi': 'video/avi',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
            'wmv': 'video/x-ms-wmv',
            'flv': 'video/x-flv',
            'webm': 'video/webm',

            # Archives
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            'tar': 'application/x-tar',
            'gz': 'application/gzip',
            'bz2': 'application/x-bzip2',
            '7z': 'application/x-7z-compressed'
        }

    def _build_mime_mappings(self) -> Dict[str, List[str]]:
        """Build MIME type to extensions mappings."""
        mime_to_ext = {}

        # Reverse the extension mappings
        for ext, mime_type in self._extension_to_mime.items():
            if mime_type not in mime_to_ext:
                mime_to_ext[mime_type] = []
            mime_to_ext[mime_type].append(ext)

        return mime_to_ext

    def _build_processor_mappings(self) -> Dict[str, str]:
        """Build MIME type to processor mappings."""
        return {
            # Images
            'image/jpeg': 'image_processor',
            'image/png': 'image_processor',
            'image/gif': 'image_processor',
            'image/bmp': 'image_processor',
            'image/tiff': 'image_processor',
            'image/webp': 'image_processor',
            'image/svg+xml': 'image_processor',

            # Documents
            'application/pdf': 'document_processor',
            'application/msword': 'document_processor',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document_processor',
            'application/vnd.ms-excel': 'document_processor',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document_processor',
            'application/vnd.ms-powerpoint': 'document_processor',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document_processor',

            # Audio
            'audio/mpeg': 'audio_processor',
            'audio/wav': 'audio_processor',
            'audio/ogg': 'audio_processor',
            'audio/mp4': 'audio_processor',
            'audio/flac': 'audio_processor',

            # Video
            'video/mp4': 'video_processor',
            'video/avi': 'video_processor',
            'video/quicktime': 'video_processor',
            'video/webm': 'video_processor',

            # Text
            'text/plain': 'text_processor',
            'text/html': 'text_processor',
            'application/json': 'text_processor',
            'text/csv': 'text_processor',

            # Archives
            'application/zip': 'archive_processor',
            'application/x-rar-compressed': 'archive_processor',
            'application/x-tar': 'archive_processor'
        }