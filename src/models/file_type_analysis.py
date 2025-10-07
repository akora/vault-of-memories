"""
File Type Analysis Models
Data models for file type analysis results and metadata.
"""

from dataclasses import dataclass, field
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_time_ms: float = 0.0
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate and process analysis result data."""
        # Ensure metadata is not None
        if self.metadata is None:
            self.metadata = {}

        # Validate confidence level
        if not isinstance(self.confidence_level, ConfidenceLevel):
            raise ValueError(f"Invalid confidence level: {self.confidence_level}")

        # Validate file size
        if self.file_size < 0:
            raise ValueError(f"File size cannot be negative: {self.file_size}")

        # Validate analysis time
        if self.analysis_time_ms < 0:
            raise ValueError(f"Analysis time cannot be negative: {self.analysis_time_ms}")

    def is_successful(self) -> bool:
        """Check if analysis completed successfully."""
        return self.error_message is None

    def is_high_confidence(self) -> bool:
        """Check if analysis has high confidence."""
        return self.confidence_level == ConfidenceLevel.HIGH

    def get_file_category(self) -> str:
        """Get general file category from MIME type."""
        mime_parts = self.detected_mime_type.split('/')
        if len(mime_parts) >= 2:
            return mime_parts[0]
        return "unknown"

    def get_file_subtype(self) -> str:
        """Get specific file subtype from MIME type."""
        mime_parts = self.detected_mime_type.split('/')
        if len(mime_parts) >= 2:
            return mime_parts[1]
        return "unknown"


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

    def __post_init__(self):
        """Validate extension validation result."""
        # Clean extension (remove dot if present)
        if self.extension.startswith('.'):
            self.extension = self.extension[1:]

        # Validate severity
        if not isinstance(self.severity, ValidationSeverity):
            raise ValueError(f"Invalid severity: {self.severity}")

        # Validate confidence level
        if not isinstance(self.confidence_level, ConfidenceLevel):
            raise ValueError(f"Invalid confidence level: {self.confidence_level}")

    def requires_attention(self) -> bool:
        """Check if validation result requires user attention."""
        return not self.is_valid and self.severity in [
            ValidationSeverity.ERROR, ValidationSeverity.WARNING
        ]

    def get_recommendation(self) -> str:
        """Get human-readable recommendation based on validation."""
        if self.is_valid:
            return "Extension matches content type."

        if self.suggested_extension:
            return f"Consider renaming to .{self.suggested_extension}"

        return "Extension does not match detected content type."


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

    def __post_init__(self):
        """Validate routing decision."""
        # Validate confidence level
        if not isinstance(self.routing_confidence, ConfidenceLevel):
            raise ValueError(f"Invalid routing confidence: {self.routing_confidence}")

        # Ensure processor and category are not empty
        if not self.target_processor:
            raise ValueError("Target processor cannot be empty")

        if not self.processor_category:
            raise ValueError("Processor category cannot be empty")

    def has_fallback(self) -> bool:
        """Check if routing decision has a fallback processor."""
        return self.fallback_processor is not None

    def is_confident_routing(self) -> bool:
        """Check if routing decision has high confidence."""
        return self.routing_confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]

    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information as dictionary."""
        info = {
            "primary": self.target_processor,
            "category": self.processor_category,
            "reason": self.routing_reason
        }

        if self.fallback_processor:
            info["fallback"] = self.fallback_processor

        return info


@dataclass
class ContentTypeMapping:
    """Mapping between MIME types, extensions, and processors."""
    mime_type: str
    extensions: List[str]
    processor: str
    category: str
    confidence_threshold: float = 0.8
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate content type mapping."""
        # Validate MIME type format
        if '/' not in self.mime_type:
            raise ValueError(f"Invalid MIME type format: {self.mime_type}")

        # Clean extensions (remove dots)
        self.extensions = [ext.lstrip('.') for ext in self.extensions]

        # Validate confidence threshold
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(f"Confidence threshold must be 0.0-1.0: {self.confidence_threshold}")

        # Ensure aliases is not None
        if self.aliases is None:
            self.aliases = []

    def matches_extension(self, extension: str) -> bool:
        """Check if extension matches this mapping."""
        clean_ext = extension.lstrip('.')
        return clean_ext.lower() in [ext.lower() for ext in self.extensions]

    def matches_mime_type(self, mime_type: str) -> bool:
        """Check if MIME type matches this mapping."""
        return (mime_type.lower() == self.mime_type.lower() or
                mime_type.lower() in [alias.lower() for alias in self.aliases])

    def get_primary_extension(self) -> str:
        """Get the primary/preferred extension for this mapping."""
        return self.extensions[0] if self.extensions else ""


@dataclass
class FileTypeStatistics:
    """Statistics about file type analysis operations."""
    total_files_analyzed: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0
    extension_mismatches: int = 0
    high_confidence_detections: int = 0
    unknown_types_detected: int = 0
    average_analysis_time_ms: float = 0.0
    type_distribution: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize statistics."""
        if self.type_distribution is None:
            self.type_distribution = {}

    def add_analysis(self, result: AnalysisResult, validation: Optional[ValidationResult] = None):
        """Add analysis result to statistics."""
        self.total_files_analyzed += 1

        if result.is_successful():
            self.successful_analyses += 1
        else:
            self.failed_analyses += 1

        if result.is_high_confidence():
            self.high_confidence_detections += 1

        if result.detected_mime_type == "application/octet-stream":
            self.unknown_types_detected += 1

        if validation and not validation.is_valid:
            self.extension_mismatches += 1

        # Update type distribution
        category = result.get_file_category()
        self.type_distribution[category] = self.type_distribution.get(category, 0) + 1

        # Update average analysis time
        total_time = self.average_analysis_time_ms * (self.total_files_analyzed - 1)
        self.average_analysis_time_ms = (total_time + result.analysis_time_ms) / self.total_files_analyzed

    def get_success_rate(self) -> float:
        """Get analysis success rate as percentage."""
        if self.total_files_analyzed == 0:
            return 0.0
        return (self.successful_analyses / self.total_files_analyzed) * 100

    def get_confidence_rate(self) -> float:
        """Get high confidence detection rate as percentage."""
        if self.successful_analyses == 0:
            return 0.0
        return (self.high_confidence_detections / self.successful_analyses) * 100

    def get_mismatch_rate(self) -> float:
        """Get extension mismatch rate as percentage."""
        if self.total_files_analyzed == 0:
            return 0.0
        return (self.extension_mismatches / self.total_files_analyzed) * 100