"""
File Type Analyzer Contracts
Abstract interfaces defining the behavior of file type analysis components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for file type detection."""
    HIGH = "high"        # >95% confidence
    MEDIUM = "medium"    # 80-95% confidence
    LOW = "low"          # 50-80% confidence
    UNKNOWN = "unknown"  # <50% confidence


class ValidationSeverity(Enum):
    """Severity levels for extension validation issues."""
    ERROR = "error"      # Critical mismatch that could cause processing failures
    WARNING = "warning"  # Minor mismatch but processing can continue
    INFO = "info"        # Informational notice about extension


@dataclass
class AnalysisResult:
    """Result of file type analysis."""
    file_path: Path
    detected_mime_type: str
    confidence_level: ConfidenceLevel
    file_size: int
    magic_description: str
    encoding: Optional[str] = None
    metadata: Dict[str, Any] = None
    analysis_time_ms: float = 0.0
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize metadata dictionary if None."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationResult:
    """Result of extension validation against detected content."""
    file_path: Path
    extension: str
    detected_mime_type: str
    is_valid: bool
    severity: ValidationSeverity
    message: str
    suggested_extension: Optional[str] = None
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN


@dataclass
class RoutingDecision:
    """Decision about which processor to route file to."""
    file_path: Path
    detected_mime_type: str
    target_processor: str
    processor_category: str  # e.g., "image", "document", "audio", etc.
    routing_confidence: ConfidenceLevel
    routing_reason: str
    fallback_processor: Optional[str] = None


class FileTypeAnalyzer(ABC):
    """
    Abstract interface for file type analysis.

    Analyzes file content to determine true file type regardless of extension.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def analyze_content(self, content: bytes, filename: str = None) -> AnalysisResult:
        """
        Analyze file content directly.

        Args:
            content: File content as bytes
            filename: Optional filename for context

        Returns:
            AnalysisResult with detected type and confidence
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """
        Get list of MIME types this analyzer can detect.

        Returns:
            List of supported MIME type strings
        """
        pass


class ExtensionValidator(ABC):
    """
    Abstract interface for validating file extensions against content.

    Compares file extensions with detected content types to identify mismatches.
    """

    @abstractmethod
    def validate_extension(self, file_path: Path, detected_mime_type: str) -> ValidationResult:
        """
        Validate file extension against detected content type.

        Args:
            file_path: Path to file (for extension extraction)
            detected_mime_type: MIME type detected from content analysis

        Returns:
            ValidationResult indicating if extension matches content
        """
        pass

    @abstractmethod
    def get_expected_extensions(self, mime_type: str) -> List[str]:
        """
        Get expected file extensions for a MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            List of common extensions for this MIME type
        """
        pass

    @abstractmethod
    def suggest_extension(self, mime_type: str) -> Optional[str]:
        """
        Suggest the most appropriate extension for a MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            Suggested file extension (without dot) or None if unknown
        """
        pass


class ProcessorRouter(ABC):
    """
    Abstract interface for routing files to appropriate processors.

    Routes files to specialized processors based on detected content type.
    """

    @abstractmethod
    def route_file(self, analysis_result: AnalysisResult) -> RoutingDecision:
        """
        Determine which processor should handle this file.

        Args:
            analysis_result: Result from file type analysis

        Returns:
            RoutingDecision with target processor and reasoning
        """
        pass

    @abstractmethod
    def get_processor_for_type(self, mime_type: str) -> Optional[str]:
        """
        Get the processor name for a specific MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            Processor name or None if no specific processor available
        """
        pass

    @abstractmethod
    def get_supported_processors(self) -> Dict[str, List[str]]:
        """
        Get mapping of processors to their supported MIME types.

        Returns:
            Dictionary mapping processor names to lists of MIME types
        """
        pass


class ContentTypeRegistry(ABC):
    """
    Abstract interface for managing content type mappings.

    Maintains relationships between MIME types, extensions, and processors.
    """

    @abstractmethod
    def get_mime_for_extension(self, extension: str) -> Optional[str]:
        """
        Get expected MIME type for file extension.

        Args:
            extension: File extension (with or without dot)

        Returns:
            Expected MIME type or None if unknown
        """
        pass

    @abstractmethod
    def get_extensions_for_mime(self, mime_type: str) -> List[str]:
        """
        Get file extensions associated with MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            List of associated extensions (without dots)
        """
        pass

    @abstractmethod
    def register_type_mapping(self, mime_type: str, extensions: List[str], processor: str) -> None:
        """
        Register a new content type mapping.

        Args:
            mime_type: MIME type string
            extensions: List of file extensions
            processor: Target processor name
        """
        pass

    @abstractmethod
    def is_known_type(self, mime_type: str) -> bool:
        """
        Check if MIME type is known/supported.

        Args:
            mime_type: MIME type string

        Returns:
            True if type is known, False otherwise
        """
        pass