"""
Consolidated metadata models.

Defines data structures for unified metadata from multiple sources with
priority-based resolution and source tracking.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class MetadataSource(Enum):
    """Sources of metadata information with priority ordering."""
    EXIF = "exif"  # Highest priority
    EMBEDDED = "embedded"  # Document properties, ID3 tags, media info
    FILENAME = "filename"  # Parsed from filename
    FILESYSTEM = "filesystem"  # File system attributes
    INFERRED = "inferred"  # Derived from analysis
    DEFAULT = "default"  # Lowest priority


@dataclass
class MetadataField:
    """
    Individual metadata field with source tracking.

    Tracks the value, where it came from, confidence level, and when extracted.
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

    # File information (always required)
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
    bitrate: Optional[MetadataField] = None  # Bitrate in kbps (audio/video)
    page_count: Optional[MetadataField] = None
    resolution_label: Optional[MetadataField] = None  # "4K", "1080p", "720p", etc.
    fps: Optional[MetadataField] = None  # Frames per second (video)

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
