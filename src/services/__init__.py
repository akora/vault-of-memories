"""
Services package for Vault of Memories.

Contains business logic and processing services.
"""

# Configuration services
from .configuration_manager import ConfigurationManager

# File type analysis services
from .file_type_analyzer import FileTypeAnalyzer

# Image processing services
from .image_processor import ImageProcessor

# Document processing services
from .document_processor import DocumentProcessor

# Audio processing services
from .audio_processor import AudioProcessor

# Video processing services
from .video_processor import VideoProcessor
from .media_metadata_extractor import MediaMetadataExtractor
from .resolution_detector import ResolutionDetector
from .video_categorizer import VideoCategorizer

# Metadata consolidation services
from .metadata_consolidator import MetadataConsolidator
from .priority_resolver import PriorityResolver
from .timezone_preserver import TimezonePreserver
from .manufacturer_standardizer import ManufacturerStandardizer

# Filename generation services
from .filename_generator import FilenameGenerator
from .naming_pattern_engine import NamingPatternEngine
from .component_formatter import ComponentFormatter
from .metadata_sanitizer import MetadataSanitizer
from .collision_detector import CollisionDetector
from .length_limiter import LengthLimiter

__all__ = [
    # Configuration
    "ConfigurationManager",
    # File type
    "FileTypeAnalyzer",
    # Image
    "ImageProcessor",
    # Document
    "DocumentProcessor",
    # Audio
    "AudioProcessor",
    # Video
    "VideoProcessor",
    "MediaMetadataExtractor",
    "ResolutionDetector",
    "VideoCategorizer",
    # Metadata
    "MetadataConsolidator",
    "PriorityResolver",
    "TimezonePreserver",
    "ManufacturerStandardizer",
    # Filename
    "FilenameGenerator",
    "NamingPatternEngine",
    "ComponentFormatter",
    "MetadataSanitizer",
    "CollisionDetector",
    "LengthLimiter",
]
