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

# File mover models (Feature 011)
from .move_operation import MoveOperation, OperationStatus
from .move_result import MoveResult
from .quarantine_record import QuarantineRecord, QuarantineReason
from .batch_move_request import BatchMoveRequest
from .batch_move_result import BatchMoveResult

# Error handler models (Feature 012)
from .error_severity import ErrorSeverity

# CLI interface models (Feature 013)
from .pipeline_stage import PipelineStage
from .processing_context import ProcessingContext
from .progress_state import ProgressState
from .processing_result import ProcessingResult
from .command_options import CommandOptions

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
    # File mover
    'MoveOperation',
    'OperationStatus',
    'MoveResult',
    'QuarantineRecord',
    'QuarantineReason',
    'BatchMoveRequest',
    'BatchMoveResult',
    # Error handler
    'ErrorSeverity',
    # CLI interface
    'PipelineStage',
    'ProcessingContext',
    'ProgressState',
    'ProcessingResult',
    'CommandOptions',
]
