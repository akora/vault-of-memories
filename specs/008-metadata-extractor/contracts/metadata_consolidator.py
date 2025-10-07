"""
Contract: Metadata Consolidator Interface

This contract defines the interface for consolidating metadata from multiple
specialized processors with priority-based conflict resolution.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class MetadataSource(Enum):
    """Sources of metadata information."""
    EXIF = "exif"
    EMBEDDED = "embedded"  # Document properties, ID3 tags, etc.
    FILENAME = "filename"
    FILESYSTEM = "filesystem"
    INFERRED = "inferred"  # Derived from analysis
    DEFAULT = "default"


@dataclass
class MetadataField:
    """
    Individual metadata field with source tracking.

    Tracks the value, where it came from, and confidence level.
    """
    value: Any
    source: MetadataSource
    confidence: float = 1.0  # 0.0 to 1.0
    timestamp: Optional[datetime] = None  # When extracted
    notes: Optional[str] = None  # Additional context


@dataclass
class ConsolidatedMetadata:
    """
    Unified metadata record from all sources.

    Contains metadata from all specialized processors with source tracking
    and conflict resolution applied.
    """

    # File information
    file_path: Path
    file_size: int
    file_type: str  # MIME type
    checksum: str  # SHA-256

    # Timestamps (timezone-aware when available)
    creation_date: Optional[MetadataField] = None
    modification_date: Optional[MetadataField] = None
    capture_date: Optional[MetadataField] = None  # Original capture/creation

    # Device/Camera information
    device_make: Optional[MetadataField] = None
    device_model: Optional[MetadataField] = None
    software: Optional[MetadataField] = None

    # Location information
    gps_latitude: Optional[MetadataField] = None
    gps_longitude: Optional[MetadataField] = None
    gps_altitude: Optional[MetadataField] = None
    location_name: Optional[MetadataField] = None

    # Content information
    title: Optional[MetadataField] = None
    description: Optional[MetadataField] = None
    keywords: Optional[MetadataField] = None  # List of tags
    category: Optional[MetadataField] = None

    # Creator information
    author: Optional[MetadataField] = None
    copyright: Optional[MetadataField] = None

    # Technical details (varies by file type)
    width: Optional[MetadataField] = None
    height: Optional[MetadataField] = None
    duration: Optional[MetadataField] = None
    page_count: Optional[MetadataField] = None

    # Quality assessment
    quality_score: Optional[float] = None  # Overall metadata quality (0.0-1.0)
    completeness_score: Optional[float] = None  # Percentage of fields populated
    confidence_score: Optional[float] = None  # Average confidence across fields

    # Audit trail
    processors_used: List[str] = field(default_factory=list)  # Which processors ran
    conflicts_detected: List[Dict[str, Any]] = field(default_factory=list)
    extraction_timestamp: Optional[datetime] = None
    processing_errors: List[str] = field(default_factory=list)


@dataclass
class MetadataQuality:
    """Assessment of metadata quality and completeness."""

    completeness_score: float  # 0.0 to 1.0 - percentage of fields populated
    confidence_score: float  # 0.0 to 1.0 - average confidence from sources
    total_fields: int  # Total possible metadata fields
    populated_fields: int  # Number of fields with values
    high_confidence_fields: int  # Fields with confidence > 0.8
    conflicts_count: int  # Number of conflicts detected
    source_breakdown: Dict[MetadataSource, int]  # Count of fields from each source


class MetadataConsolidator:
    """
    Interface for consolidating metadata from multiple processors.

    Contract:
    - MUST coordinate between specialized processors (image, document, audio, video)
    - MUST apply priority-based conflict resolution (EXIF > Filename > Filesystem)
    - MUST preserve original timezone information
    - MUST standardize manufacturer names using configurable mappings
    - MUST track metadata sources for audit trail
    - MUST calculate quality scores for consolidated metadata
    - MUST handle missing or conflicting metadata gracefully
    """

    def consolidate(self, file_path: Path) -> ConsolidatedMetadata:
        """
        Consolidate metadata from all available sources for a file.

        Args:
            file_path: Path to the file to process

        Returns:
            ConsolidatedMetadata with resolved metadata from all sources

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            RuntimeError: If critical metadata extraction fails
        """
        raise NotImplementedError("Subclasses must implement consolidate()")

    def assess_quality(self, metadata: ConsolidatedMetadata) -> MetadataQuality:
        """
        Assess the quality and completeness of consolidated metadata.

        Args:
            metadata: Consolidated metadata to assess

        Returns:
            MetadataQuality with scores and analysis

        Raises:
            ValueError: If metadata is invalid
        """
        raise NotImplementedError("Subclasses must implement assess_quality()")

    def get_supported_file_types(self) -> List[str]:
        """
        Get list of supported file types (MIME types).

        Returns:
            List of MIME type strings
        """
        raise NotImplementedError("Subclasses must implement get_supported_file_types()")


class PriorityResolver:
    """
    Interface for resolving metadata conflicts using priority rules.

    Contract:
    - MUST apply configurable priority rules
    - MUST support default priority: EXIF > Embedded > Filename > Filesystem
    - MUST allow field-specific priority overrides
    - MUST log all conflicts for audit trail
    - MUST handle missing sources gracefully
    """

    def resolve_field(self, field_name: str, sources: Dict[MetadataSource, Any]) -> MetadataField:
        """
        Resolve conflicts for a specific metadata field.

        Args:
            field_name: Name of the metadata field
            sources: Dictionary mapping source to value

        Returns:
            MetadataField with resolved value and source

        Raises:
            ValueError: If no valid sources provided
        """
        raise NotImplementedError("Subclasses must implement resolve_field()")

    def get_priority_order(self, field_name: str) -> List[MetadataSource]:
        """
        Get priority order for a specific field.

        Args:
            field_name: Name of the metadata field

        Returns:
            List of MetadataSource in priority order (highest to lowest)
        """
        raise NotImplementedError("Subclasses must implement get_priority_order()")


class TimezonePreserver:
    """
    Interface for preserving timezone information.

    Contract:
    - MUST preserve original timezone without UTC conversion
    - MUST handle timezone-aware and naive datetimes
    - MUST track timezone source and confidence
    - MUST validate timezone information
    """

    def preserve_timezone(self, timestamp: Any, source: MetadataSource) -> datetime:
        """
        Preserve timezone information from original timestamp.

        Args:
            timestamp: Original timestamp (may be string, datetime, etc.)
            source: Source of the timestamp

        Returns:
            Timezone-aware datetime with original timezone preserved

        Raises:
            ValueError: If timestamp format is invalid
        """
        raise NotImplementedError("Subclasses must implement preserve_timezone()")

    def extract_timezone(self, timestamp: Any) -> Optional[str]:
        """
        Extract timezone information from timestamp.

        Args:
            timestamp: Timestamp to analyze

        Returns:
            Timezone string (e.g., "America/New_York") or None
        """
        raise NotImplementedError("Subclasses must implement extract_timezone()")


class ManufacturerStandardizer:
    """
    Interface for standardizing manufacturer names.

    Contract:
    - MUST apply configurable mapping rules
    - MUST handle case-insensitive matching
    - MUST preserve original name if no mapping found
    - MUST support multiple aliases per manufacturer
    """

    def standardize(self, manufacturer: str) -> str:
        """
        Standardize manufacturer name using mapping rules.

        Args:
            manufacturer: Original manufacturer name

        Returns:
            Standardized manufacturer name

        Raises:
            ValueError: If manufacturer name is invalid
        """
        raise NotImplementedError("Subclasses must implement standardize()")

    def get_mappings(self) -> Dict[str, str]:
        """
        Get all manufacturer mappings.

        Returns:
            Dictionary mapping original names to standardized names
        """
        raise NotImplementedError("Subclasses must implement get_mappings()")
