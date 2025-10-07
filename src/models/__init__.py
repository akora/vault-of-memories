"""
Data models for vault processing.
"""

from .video_metadata import VideoMetadata, CategoryResult
from .consolidated_metadata import (
    MetadataSource,
    MetadataField,
    ConsolidatedMetadata,
    MetadataQuality
)
from .generated_filename import GeneratedFilename

__all__ = [
    "VideoMetadata",
    "CategoryResult",
    "MetadataSource",
    "MetadataField",
    "ConsolidatedMetadata",
    "MetadataQuality",
    "GeneratedFilename",
]
