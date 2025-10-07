"""
Audio processor implementation.

Main service for processing audio files and extracting comprehensive metadata.
"""

from pathlib import Path
from typing import Optional
import logging

from src.models.audio_metadata import AudioMetadata
from src.services.tag_extractor import TagExtractor
from src.services.audio_quality_classifier import AudioQualityClassifier


logger = logging.getLogger(__name__)


class AudioProcessorImpl:
    """
    Implementation of audio file processor.

    Extracts metadata, tags, and classifies audio quality for various formats.
    """

    SUPPORTED_FORMATS = {
        ".mp3", ".flac", ".m4a", ".mp4", ".aac",
        ".ogg", ".oga", ".opus", ".wma", ".wav", ".wave"
    }

    def __init__(
        self,
        tag_extractor: Optional[TagExtractor] = None,
        quality_classifier: Optional[AudioQualityClassifier] = None
    ):
        """
        Initialize audio processor.

        Args:
            tag_extractor: Tag extraction service (creates default if None)
            quality_classifier: Quality classification service (creates default if None)
        """
        self.tag_extractor = tag_extractor or TagExtractor()
        self.quality_classifier = quality_classifier or AudioQualityClassifier()

    def process_audio(self, file_path: Path) -> AudioMetadata:
        """
        Process an audio file and extract comprehensive metadata.

        Args:
            file_path: Path to the audio file

        Returns:
            AudioMetadata object with all extracted information

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If file is not a supported audio format
            RuntimeError: If audio file is corrupted or unreadable
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(
                f"Unsupported audio format: {file_path.suffix}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

        logger.info(f"Processing audio file: {file_path}")

        processing_errors = []

        try:
            # Extract tags and technical metadata
            tags = self.tag_extractor.extract_tags(file_path)

            # Get file info
            file_size = file_path.stat().st_size
            format_str = self._get_format_name(file_path)

            # Classify quality
            is_lossless, quality_level, compression_type = self.quality_classifier.classify(
                format=format_str,
                bitrate=tags.get("bitrate"),
                bit_depth=tags.get("bit_depth"),
                sample_rate=tags.get("sample_rate")
            )

            # Build metadata object
            metadata = AudioMetadata(
                # File information
                file_path=file_path,
                file_size=file_size,
                format=format_str,
                # Technical specifications
                duration=tags.get("duration"),
                bitrate=tags.get("bitrate"),
                sample_rate=tags.get("sample_rate"),
                channels=tags.get("channels"),
                bit_depth=tags.get("bit_depth"),
                # Tag metadata
                title=tags.get("title"),
                artist=tags.get("artist"),
                album=tags.get("album"),
                album_artist=tags.get("album_artist"),
                track_number=tags.get("track_number"),
                total_tracks=tags.get("total_tracks"),
                disc_number=tags.get("disc_number"),
                total_discs=tags.get("total_discs"),
                year=tags.get("year"),
                date=tags.get("date"),
                genre=tags.get("genre"),
                comment=tags.get("comment"),
                composer=tags.get("composer"),
                # Quality classification
                is_lossless=is_lossless,
                quality_level=quality_level,
                compression_type=compression_type,
                # Processing metadata
                has_cover_art=tags.get("has_cover_art", False),
                tag_format=tags.get("tag_format"),
                processing_errors=processing_errors
            )

            logger.info(
                f"Successfully processed {file_path.name}: "
                f"{format_str}, {quality_level} quality, "
                f"{metadata.duration:.2f}s" if metadata.duration else f"{format_str}, {quality_level} quality"
            )

            return metadata

        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            error_msg = f"Error processing audio file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def supports_format(self, file_path: Path) -> bool:
        """
        Check if the processor supports the audio file format.

        Args:
            file_path: Path to the audio file

        Returns:
            True if format is supported, False otherwise
        """
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS

    def _get_format_name(self, file_path: Path) -> str:
        """
        Get human-readable format name from file extension.

        Args:
            file_path: Path to the audio file

        Returns:
            Format name (e.g., "MP3", "FLAC", "M4A")
        """
        ext = file_path.suffix.lower().lstrip(".")

        # Map extensions to standard format names
        format_map = {
            "mp3": "MP3",
            "flac": "FLAC",
            "m4a": "M4A",
            "mp4": "M4A",
            "aac": "AAC",
            "ogg": "OGG",
            "oga": "OGG",
            "opus": "Opus",
            "wma": "WMA",
            "wav": "WAV",
            "wave": "WAV"
        }

        return format_map.get(ext, ext.upper())
