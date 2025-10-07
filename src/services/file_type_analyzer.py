"""
File Type Analyzer Implementation
Analyzes file content to determine true file type using python-magic.
"""

import logging
import magic
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from abc import ABC, abstractmethod
from ..models.file_type_analysis import AnalysisResult, ConfidenceLevel


class FileTypeAnalyzer(ABC):
    """Abstract interface for file type analysis."""

    @abstractmethod
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a file to determine its content type."""
        pass

    @abstractmethod
    def analyze_content(self, content: bytes, filename: str = None) -> AnalysisResult:
        """Analyze file content directly."""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get list of MIME types this analyzer can detect."""
        pass


class FileTypeAnalyzerImpl(FileTypeAnalyzer):
    """
    Implementation of file type analysis using python-magic.

    Uses libmagic to analyze file content and determine MIME types
    with confidence levels based on detection certainty.
    """

    def __init__(self):
        """Initialize the file type analyzer."""
        self.logger = logging.getLogger(__name__)
        self._magic_mime = magic.Magic(mime=True)
        self._magic_description = magic.Magic()
        self._magic_encoding = magic.Magic(mime_encoding=True)

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """
        Analyze a file to determine its content type.

        Args:
            file_path: Path to the file to analyze

        Returns:
            AnalysisResult with detected type and confidence

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            ValueError: If file cannot be analyzed
        """
        start_time = time.time()

        # Validate file exists and is readable
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            # Get file size
            file_size = file_path.stat().st_size

            # Read file content for analysis (limit to first 1MB for performance)
            max_read_size = 1024 * 1024  # 1MB
            with open(file_path, 'rb') as f:
                content = f.read(max_read_size)

            # Perform analysis on content
            result = self.analyze_content(content, str(file_path))

            # Update with actual file path and size
            result.file_path = file_path
            result.file_size = file_size
            result.analysis_time_ms = (time.time() - start_time) * 1000

            return result

        except PermissionError:
            self.logger.error(f"Permission denied reading file: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            # Return error result instead of raising
            return AnalysisResult(
                file_path=file_path,
                detected_mime_type="application/octet-stream",
                confidence_level=ConfidenceLevel.UNKNOWN,
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                magic_description="Error during analysis",
                analysis_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

    def analyze_content(self, content: bytes, filename: str = None) -> AnalysisResult:
        """
        Analyze file content directly.

        Args:
            content: File content as bytes
            filename: Optional filename for context

        Returns:
            AnalysisResult with detected type and confidence
        """
        start_time = time.time()

        try:
            # Get MIME type
            detected_mime = self._magic_mime.from_buffer(content)

            # Get human-readable description
            description = self._magic_description.from_buffer(content)

            # Get encoding for text files
            encoding = None
            if detected_mime.startswith('text/'):
                try:
                    encoding = self._magic_encoding.from_buffer(content)
                except:
                    encoding = None

            # Determine confidence level
            confidence = self._determine_confidence(detected_mime, content, description)

            # Extract additional metadata
            metadata = self._extract_metadata(detected_mime, content, description)

            return AnalysisResult(
                file_path=Path(filename) if filename else Path("unknown"),
                detected_mime_type=detected_mime,
                confidence_level=confidence,
                file_size=len(content),
                magic_description=description,
                encoding=encoding,
                metadata=metadata,
                analysis_time_ms=(time.time() - start_time) * 1000
            )

        except Exception as e:
            self.logger.error(f"Error analyzing content: {e}")
            return AnalysisResult(
                file_path=Path(filename) if filename else Path("unknown"),
                detected_mime_type="application/octet-stream",
                confidence_level=ConfidenceLevel.UNKNOWN,
                file_size=len(content),
                magic_description="Error during content analysis",
                analysis_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

    def get_supported_types(self) -> List[str]:
        """
        Get list of MIME types this analyzer can detect.

        Returns:
            List of supported MIME type strings
        """
        # Common MIME types that libmagic can reliably detect
        return [
            # Images
            "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
            "image/webp", "image/svg+xml",

            # Documents
            "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",

            # Text
            "text/plain", "text/html", "text/css", "text/javascript",
            "text/csv", "text/xml", "application/json",

            # Audio
            "audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "audio/flac",

            # Video
            "video/mp4", "video/avi", "video/mov", "video/mkv", "video/webm",

            # Archives
            "application/zip", "application/x-rar-compressed",
            "application/x-tar", "application/gzip",

            # Executables
            "application/x-executable", "application/x-mach-binary",

            # Generic
            "application/octet-stream"
        ]

    def _determine_confidence(self, mime_type: str, content: bytes, description: str) -> ConfidenceLevel:
        """
        Determine confidence level for the detected MIME type.

        Args:
            mime_type: Detected MIME type
            content: File content
            description: Magic description

        Returns:
            ConfidenceLevel indicating detection certainty
        """
        # High confidence for files with clear magic signatures
        high_confidence_types = [
            "image/jpeg", "image/png", "image/gif", "application/pdf",
            "video/mp4", "audio/mpeg", "application/zip"
        ]

        if mime_type in high_confidence_types:
            return ConfidenceLevel.HIGH

        # Medium confidence for well-structured content types
        if mime_type.startswith(('image/', 'video/', 'audio/')) and len(content) > 100:
            return ConfidenceLevel.MEDIUM

        # Low confidence for generic types or small files
        if mime_type == "application/octet-stream" or len(content) < 50:
            return ConfidenceLevel.LOW

        # Check for specific patterns that indicate certainty
        if "data" in description.lower() or "empty" in description.lower():
            return ConfidenceLevel.LOW

        # Default to medium confidence
        return ConfidenceLevel.MEDIUM

    def _extract_metadata(self, mime_type: str, content: bytes, description: str) -> Dict[str, Any]:
        """
        Extract additional metadata from file content.

        Args:
            mime_type: Detected MIME type
            content: File content
            description: Magic description

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            "content_length": len(content),
            "has_magic_signature": self._has_magic_signature(content),
            "description_keywords": self._extract_description_keywords(description)
        }

        # Extract format-specific metadata
        if mime_type.startswith('image/'):
            metadata.update(self._extract_image_metadata(content, description))
        elif mime_type.startswith('text/'):
            metadata.update(self._extract_text_metadata(content))

        return metadata

    def _has_magic_signature(self, content: bytes) -> bool:
        """Check if content has a recognizable magic signature."""
        if len(content) < 4:
            return False

        # Common magic signatures
        magic_signatures = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG',       # PNG
            b'GIF8',          # GIF
            b'%PDF',          # PDF
            b'PK\x03\x04',    # ZIP
            b'\x00\x00\x01\x00',  # ICO
        ]

        return any(content.startswith(sig) for sig in magic_signatures)

    def _extract_description_keywords(self, description: str) -> List[str]:
        """Extract meaningful keywords from magic description."""
        # Split and filter description for meaningful terms
        words = description.lower().split()
        keywords = []

        # Filter out common stop words and keep meaningful terms
        stop_words = {'data', 'file', 'format', 'with', 'and', 'or', 'the'}
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)

        return keywords[:5]  # Limit to top 5 keywords

    def _extract_image_metadata(self, content: bytes, description: str) -> Dict[str, Any]:
        """Extract metadata specific to image files."""
        metadata = {}

        # Basic image information from description
        if 'x' in description and any(char.isdigit() for char in description):
            # Try to extract dimensions from description
            words = description.split()
            for word in words:
                if 'x' in word and any(char.isdigit() for char in word):
                    try:
                        dimensions = word.split('x')
                        if len(dimensions) == 2:
                            metadata['estimated_width'] = int(dimensions[0])
                            metadata['estimated_height'] = int(dimensions[1])
                            break
                    except ValueError:
                        pass

        return metadata

    def _extract_text_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract metadata specific to text files."""
        try:
            text_content = content.decode('utf-8', errors='ignore')
            return {
                "line_count": text_content.count('\n') + 1,
                "char_count": len(text_content),
                "estimated_encoding": "utf-8" if content == text_content.encode('utf-8') else "mixed"
            }
        except:
            return {"encoding_error": True}