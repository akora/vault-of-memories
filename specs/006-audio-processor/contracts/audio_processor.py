"""
Contract: Audio Processor Interface

This contract defines the interface for processing audio files and extracting metadata.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AudioMetadata:
    """Audio metadata extracted from audio files."""

    # File information
    file_path: Path
    file_size: int
    format: str  # MP3, FLAC, M4A, OGG, WMA, etc.

    # Technical specifications
    duration: Optional[float]  # Duration in seconds
    bitrate: Optional[int]  # Bitrate in kbps
    sample_rate: Optional[int]  # Sample rate in Hz
    channels: Optional[int]  # Number of audio channels
    bit_depth: Optional[int]  # Bit depth (for lossless formats)

    # Tag metadata
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    album_artist: Optional[str]
    track_number: Optional[int]
    total_tracks: Optional[int]
    disc_number: Optional[int]
    total_discs: Optional[int]
    year: Optional[int]
    date: Optional[str]  # ISO format date
    genre: Optional[str]
    comment: Optional[str]
    composer: Optional[str]

    # Quality classification
    is_lossless: bool
    quality_level: str  # "high", "medium", "low"
    compression_type: str  # "lossless", "lossy"

    # Processing metadata
    has_cover_art: bool
    tag_format: Optional[str]  # ID3v2.4, Vorbis, MP4, etc.
    processing_errors: list[str]


class AudioProcessor:
    """
    Interface for processing audio files and extracting metadata.

    Contract:
    - MUST support MP3, FLAC, M4A, OGG, WMA formats
    - MUST extract technical specifications (duration, bitrate, sample rate)
    - MUST extract ID3/Vorbis/MP4 tags
    - MUST classify audio quality
    - MUST handle missing metadata gracefully
    - MUST NOT modify original audio files
    """

    def process_audio(self, file_path: Path) -> AudioMetadata:
        """
        Process an audio file and extract metadata.

        Args:
            file_path: Path to the audio file

        Returns:
            AudioMetadata object with extracted information

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If file is not a supported audio format
            RuntimeError: If audio file is corrupted or unreadable
        """
        raise NotImplementedError("Subclasses must implement process_audio()")

    def supports_format(self, file_path: Path) -> bool:
        """
        Check if the processor supports the audio format.

        Args:
            file_path: Path to the audio file

        Returns:
            True if format is supported, False otherwise
        """
        raise NotImplementedError("Subclasses must implement supports_format()")
