"""
Processing services for vault operations.
"""

# Video processor services
from .video_processor import VideoProcessor, VideoProcessorImpl
from .media_info_extractor import MediaInfoExtractor
from .resolution_detector import ResolutionDetector
from .content_categorizer import ContentCategorizer

# Metadata consolidator services
from .metadata_consolidator import MetadataConsolidator
from .priority_resolver import PriorityResolver
from .timezone_preserver import TimezonePreserver
from .manufacturer_standardizer import ManufacturerStandardizer
from .metadata_quality_assessor import MetadataQualityAssessor

# File renamer services
from .filename_generator import FilenameGenerator
from .naming_pattern_engine import NamingPatternEngine
from .component_formatter import ComponentFormatter
from .metadata_sanitizer import MetadataSanitizer
from .collision_detector import CollisionDetector
from .length_limiter import LengthLimiter

# Organization manager services
from .date_hierarchy_builder import DateHierarchyBuilder
from .folder_creator import FolderCreator
from .date_extractor import DateExtractor
from .filename_date_parser import FilenameDateParser
from .classification_engine import ClassificationEngine
from .mime_detector import MimeDetector
from .organization_manager import OrganizationManager

__all__ = [
    # Video processor
    "VideoProcessor",
    "VideoProcessorImpl",
    "MediaInfoExtractor",
    "ResolutionDetector",
    "ContentCategorizer",
    # Metadata consolidator
    "MetadataConsolidator",
    "PriorityResolver",
    "TimezonePreserver",
    "ManufacturerStandardizer",
    "MetadataQualityAssessor",
    # File renamer
    "FilenameGenerator",
    "NamingPatternEngine",
    "ComponentFormatter",
    "MetadataSanitizer",
    "CollisionDetector",
    "LengthLimiter",
    # Organization manager
    'DateHierarchyBuilder',
    'FolderCreator',
    'DateExtractor',
    'FilenameDateParser',
    'ClassificationEngine',
    'MimeDetector',
    'OrganizationManager',
]
