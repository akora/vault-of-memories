"""
Models package for Vault of Memories.

Contains data models and domain objects for the application.
"""

# Video processing models
from .video_metadata import VideoMetadata, CategoryResult

# Metadata consolidation models
from .consolidated_metadata import (
    MetadataSource,
    MetadataField,
    ConsolidatedMetadata,
    MetadataQuality
)

# Filename generation models
from .generated_filename import GeneratedFilename

__all__ = [
    # Video
    "VideoMetadata",
    "CategoryResult",
    # Metadata
    "MetadataSource",
    "MetadataField",
    "ConsolidatedMetadata",
    "MetadataQuality",
    # Filename
    "GeneratedFilename",
]
