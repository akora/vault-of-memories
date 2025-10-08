"""
Video processor implementation.

Main orchestration service for video file processing, combining metadata
extraction, resolution detection, and content categorization.
"""

import logging
from pathlib import Path
from typing import Optional

from ..models.video_metadata import VideoMetadata, CategoryResult
from .media_info_extractor import MediaInfoExtractor
from .resolution_detector import ResolutionDetector
from .content_categorizer import ContentCategorizer


logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Process video files and extract comprehensive metadata.

    Integrates:
    - MediaInfoExtractor: Technical metadata extraction
    - ResolutionDetector: Resolution classification and quality scoring
    - ContentCategorizer: Content categorization with confidence

    Supports: MP4, AVI, MOV, MKV, WMV, WebM formats
    """

    # Supported video file extensions
    SUPPORTED_FORMATS = {
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm",
        ".m4v", ".mpg", ".mpeg", ".flv", ".f4v"
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize video processor.

        Args:
            config_path: Optional path to configuration file
        """
        self.media_extractor = MediaInfoExtractor()
        self.resolution_detector = ResolutionDetector()
        self.categorizer = ContentCategorizer(config_path)

        logger.info("VideoProcessor initialized")

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
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(f"Unsupported video format: {file_path.suffix}")

        logger.info(f"Processing video: {file_path}")

        # Extract technical metadata using pymediainfo
        try:
            metadata_dict = self.media_extractor.extract_metadata(file_path)
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            raise RuntimeError(f"Metadata extraction failed: {e}")

        # Detect and classify resolution
        width = metadata_dict.get("width")
        height = metadata_dict.get("height")
        resolution_label, is_hd, is_4k = self.resolution_detector.detect_resolution(width, height)

        # Calculate quality score
        quality_score = self.resolution_detector.calculate_quality_score(
            width=width,
            height=height,
            bitrate=metadata_dict.get("bitrate"),
            fps=metadata_dict.get("fps")
        )

        # Extract GPS coordinates if available
        gps_coords = self.media_extractor.extract_gps_coordinates(file_path)
        if gps_coords:
            metadata_dict.update({
                "gps_latitude": gps_coords.get("latitude"),
                "gps_longitude": gps_coords.get("longitude"),
                "gps_altitude": gps_coords.get("altitude")
            })

        # Categorize content
        try:
            category_result = self.categorizer.categorize(metadata_dict, file_path)
        except Exception as e:
            logger.warning(f"Content categorization failed for {file_path}: {e}")
            # Create default category result
            category_result = CategoryResult(
                primary_category="other",
                confidence=0.5,
                reasoning="Categorization failed, defaulting to 'other'",
                alternative_categories=[]
            )

        # Build VideoMetadata object
        video_metadata = VideoMetadata(
            file_path=file_path,
            file_size=metadata_dict["file_size"],
            format=metadata_dict.get("format", file_path.suffix[1:].upper()),
            container=metadata_dict.get("container"),
            duration=metadata_dict.get("duration"),
            width=width,
            height=height,
            resolution_label=resolution_label,
            fps=metadata_dict.get("fps"),
            bitrate=metadata_dict.get("bitrate"),
            video_codec=metadata_dict.get("video_codec"),
            audio_codec=metadata_dict.get("audio_codec"),
            video_streams=metadata_dict.get("video_streams", 0),
            audio_streams=metadata_dict.get("audio_streams", 0),
            subtitle_streams=metadata_dict.get("subtitle_streams", 0),
            camera_make=metadata_dict.get("camera_make"),
            camera_model=metadata_dict.get("camera_model"),
            recording_device=metadata_dict.get("recording_device"),
            gps_latitude=metadata_dict.get("gps_latitude"),
            gps_longitude=metadata_dict.get("gps_longitude"),
            gps_altitude=metadata_dict.get("gps_altitude"),
            creation_date=metadata_dict.get("creation_date"),
            recording_date=metadata_dict.get("recording_date"),
            modification_date=metadata_dict.get("modification_date"),
            primary_category=category_result.primary_category,
            secondary_category=(
                category_result.alternative_categories[0][0]
                if category_result.alternative_categories else None
            ),
            category_confidence=category_result.confidence,
            category_reasoning=category_result.reasoning,
            is_hd=is_hd,
            is_4k=is_4k,
            quality_score=quality_score,
            processing_errors=metadata_dict.get("processing_errors", [])
        )

        logger.info(
            f"Processed video: {file_path.name} - "
            f"{resolution_label}, {category_result.primary_category} "
            f"(confidence: {category_result.confidence:.2f})"
        )

        return video_metadata

    def supports_format(self, file_path: Path) -> bool:
        """
        Check if the processor supports the video file format.

        Args:
            file_path: Path to the video file

        Returns:
            True if format is supported, False otherwise
        """
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS


class VideoProcessorImpl(VideoProcessor):
    """
    Concrete implementation of VideoProcessor interface.

    This class exists to match the contract interface while maintaining
    backward compatibility with the main VideoProcessor class.
    """
    pass
