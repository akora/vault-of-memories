"""
Contract: Video Processor Interface

This contract defines the interface for processing video files and extracting metadata.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Tuple


@dataclass
class VideoMetadata:
    """Video metadata extracted from video files."""

    # File information
    file_path: Path
    file_size: int
    format: str  # MP4, AVI, MOV, MKV, WMV, WebM, etc.
    container: Optional[str] = None  # Container format

    # Technical specifications
    duration: Optional[float] = None  # Duration in seconds
    width: Optional[int] = None  # Video width in pixels
    height: Optional[int] = None  # Video height in pixels
    resolution_label: Optional[str] = None  # "4K", "1080p", "720p", etc.
    fps: Optional[float] = None  # Frames per second
    bitrate: Optional[int] = None  # Bitrate in kbps

    # Codec information
    video_codec: Optional[str] = None  # H.264, H.265, VP9, etc.
    audio_codec: Optional[str] = None  # AAC, MP3, Opus, etc.

    # Stream information
    video_streams: int = 0
    audio_streams: int = 0
    subtitle_streams: int = 0

    # Camera and device information
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    recording_device: Optional[str] = None

    # Location information
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None

    # Timestamps
    creation_date: Optional[str] = None  # ISO format date
    recording_date: Optional[str] = None  # ISO format date
    modification_date: Optional[str] = None  # ISO format date

    # Content categorization
    primary_category: str = "other"  # "family", "tutorials", "work", "tech", "entertainment", "other"
    secondary_category: Optional[str] = None
    category_confidence: float = 0.0  # 0.0 to 1.0
    category_reasoning: Optional[str] = None

    # Quality indicators
    is_hd: bool = False
    is_4k: bool = False
    quality_score: Optional[float] = None  # 0.0 to 1.0

    # Processing metadata
    processing_errors: List[str] = field(default_factory=list)


@dataclass
class CategoryResult:
    """Result of video content categorization."""

    primary_category: str
    confidence: float
    reasoning: str
    alternative_categories: List[Tuple[str, float]] = field(default_factory=list)  # [(category, confidence), ...]


class VideoProcessor:
    """
    Interface for processing video files and extracting metadata.

    Contract:
    - MUST support MP4, AVI, MOV, MKV, WMV, WebM formats
    - MUST extract technical specifications (duration, resolution, FPS, codec)
    - MUST extract camera and device information when available
    - MUST categorize videos with confidence scores
    - MUST handle videos with multiple streams
    - MUST NOT modify original video files
    """

    def process_video(self, file_path: Path) -> VideoMetadata:
        """
        Process a video file and extract comprehensive metadata.

        Args:
            file_path: Path to the video file

        Returns:
            VideoMetadata object with extracted information

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If file is not a supported video format
            RuntimeError: If video file is corrupted or unreadable
        """
        raise NotImplementedError("Subclasses must implement process_video()")

    def supports_format(self, file_path: Path) -> bool:
        """
        Check if the processor supports the video file format.

        Args:
            file_path: Path to the video file

        Returns:
            True if format is supported, False otherwise
        """
        raise NotImplementedError("Subclasses must implement supports_format()")


class ContentCategorizer:
    """
    Interface for categorizing video content.

    Contract:
    - MUST classify videos into predefined categories
    - MUST provide confidence scores for classifications
    - MUST provide reasoning for category assignments
    - SHOULD suggest alternative categories when ambiguous
    """

    def categorize(self, metadata: VideoMetadata, file_path: Path) -> CategoryResult:
        """
        Categorize video content based on metadata and analysis.

        Args:
            metadata: Extracted video metadata
            file_path: Path to the video file

        Returns:
            CategoryResult with primary category, confidence, and reasoning

        Raises:
            ValueError: If metadata is insufficient for categorization
        """
        raise NotImplementedError("Subclasses must implement categorize()")

    def get_supported_categories(self) -> List[str]:
        """
        Get list of supported video categories.

        Returns:
            List of category names
        """
        raise NotImplementedError("Subclasses must implement get_supported_categories()")
