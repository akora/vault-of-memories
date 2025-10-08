"""
Data models for vault processing.
"""

# Video processor models
from .video_metadata import VideoMetadata, CategoryResult

# Metadata consolidator models
from .consolidated_metadata import (
    MetadataSource,
    MetadataField,
    ConsolidatedMetadata,
    MetadataQuality
)

# File renamer models
from .generated_filename import GeneratedFilename

# Organization manager models
from .enums import PrimaryCategory, DateSource, ExecutionStatus, DetectionMethod
from .vault_path import VaultPath
from .classification import Classification
from .date_info import DateInfo
from .organization_decision import OrganizationDecision
from .classification_rule import ClassificationRule
from .folder_structure import FolderStructure
from .creation_result import CreationResult

__all__ = [
    # Video processor
    "VideoMetadata",
    "CategoryResult",
    # Metadata consolidator
    "MetadataSource",
    "MetadataField",
    "ConsolidatedMetadata",
    "MetadataQuality",
    # File renamer
    "GeneratedFilename",
    # Organization manager
    'PrimaryCategory',
    'DateSource',
    'ExecutionStatus',
    'DetectionMethod',
    'VaultPath',
    'Classification',
    'DateInfo',
    'OrganizationDecision',
    'ClassificationRule',
    'FolderStructure',
    'CreationResult',
]
