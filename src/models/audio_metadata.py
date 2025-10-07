"""
Audio metadata model.

This module defines the data structure for audio file metadata.
"""

from dataclasses import dataclass, field
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
    duration: Optional[float] = None  # Duration in seconds
    bitrate: Optional[int] = None  # Bitrate in kbps
    sample_rate: Optional[int] = None  # Sample rate in Hz
    channels: Optional[int] = None  # Number of audio channels
    bit_depth: Optional[int] = None  # Bit depth (for lossless formats)

    # Tag metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    disc_number: Optional[int] = None
    total_discs: Optional[int] = None
    year: Optional[int] = None
    date: Optional[str] = None  # ISO format date
    genre: Optional[str] = None
    comment: Optional[str] = None
    composer: Optional[str] = None

    # Quality classification
    is_lossless: bool = False
    quality_level: str = "unknown"  # "high", "medium", "low", "unknown"
    compression_type: str = "unknown"  # "lossless", "lossy", "unknown"

    # Processing metadata
    has_cover_art: bool = False
    tag_format: Optional[str] = None  # ID3v2.4, Vorbis, MP4, etc.
    processing_errors: list[str] = field(default_factory=list)
