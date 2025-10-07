"""
Helper utilities for creating test audio files.

Uses mutagen to create minimal valid audio files for testing.
"""

import struct
import wave
from pathlib import Path
from typing import Optional
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4


def create_wav_file(file_path: Path, duration_seconds: float = 1.0,
                    sample_rate: int = 44100, channels: int = 2) -> Path:
    """Create a minimal WAV file for testing."""
    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate silence
        num_frames = int(duration_seconds * sample_rate)
        for _ in range(num_frames):
            for _ in range(channels):
                wav_file.writeframes(struct.pack('h', 0))

    return file_path


def create_mp3_file(file_path: Path, title: Optional[str] = None,
                    artist: Optional[str] = None, album: Optional[str] = None,
                    year: Optional[int] = None, track_number: Optional[int] = None,
                    genre: Optional[str] = None) -> Path:
    """
    Create a minimal MP3 file with ID3 tags for testing.

    Note: This creates a WAV file and adds ID3 tags. It's not a real MP3,
    but mutagen can read the tags. For real MP3 testing, use actual MP3 files.
    """
    # Create a minimal WAV first
    create_wav_file(file_path, duration_seconds=0.1)

    # Add ID3 tags
    try:
        audio = ID3(str(file_path))
    except mutagen.id3.ID3NoHeaderError:
        audio = ID3()

    if title:
        audio.add(TIT2(encoding=3, text=title))
    if artist:
        audio.add(TPE1(encoding=3, text=artist))
    if album:
        audio.add(TALB(encoding=3, text=album))
    if year:
        audio.add(TDRC(encoding=3, text=str(year)))
    if track_number:
        audio.add(TRCK(encoding=3, text=str(track_number)))
    if genre:
        audio.add(TCON(encoding=3, text=genre))

    audio.save(str(file_path))
    return file_path


def add_metadata_to_audio_file(file_path: Path, **metadata) -> None:
    """
    Add metadata to an existing audio file.

    Supported metadata keys:
    - title, artist, album, album_artist, date, genre, comment
    - track_number, total_tracks, disc_number, total_discs
    """
    audio = mutagen.File(str(file_path))

    if audio is None:
        raise ValueError(f"Could not open audio file: {file_path}")

    # Handle different tag formats
    if isinstance(audio, mutagen.id3.ID3FileType):
        _add_id3_tags(audio, **metadata)
    elif isinstance(audio, (FLAC, OggVorbis)):
        _add_vorbis_comments(audio, **metadata)
    elif isinstance(audio, MP4):
        _add_mp4_tags(audio, **metadata)

    audio.save()


def _add_id3_tags(audio, **metadata):
    """Add ID3 tags to audio file."""
    if 'title' in metadata:
        audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    if 'artist' in metadata:
        audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
    if 'album' in metadata:
        audio.tags.add(TALB(encoding=3, text=metadata['album']))
    if 'date' in metadata or 'year' in metadata:
        year = metadata.get('date') or metadata.get('year')
        audio.tags.add(TDRC(encoding=3, text=str(year)))
    if 'track_number' in metadata:
        audio.tags.add(TRCK(encoding=3, text=str(metadata['track_number'])))
    if 'genre' in metadata:
        audio.tags.add(TCON(encoding=3, text=metadata['genre']))


def _add_vorbis_comments(audio, **metadata):
    """Add Vorbis comments to FLAC/OGG file."""
    if 'title' in metadata:
        audio['title'] = metadata['title']
    if 'artist' in metadata:
        audio['artist'] = metadata['artist']
    if 'album' in metadata:
        audio['album'] = metadata['album']
    if 'album_artist' in metadata:
        audio['albumartist'] = metadata['album_artist']
    if 'date' in metadata:
        audio['date'] = str(metadata['date'])
    if 'genre' in metadata:
        audio['genre'] = metadata['genre']
    if 'track_number' in metadata:
        audio['tracknumber'] = str(metadata['track_number'])


def _add_mp4_tags(audio, **metadata):
    """Add MP4 tags to M4A file."""
    if 'title' in metadata:
        audio['\xa9nam'] = metadata['title']
    if 'artist' in metadata:
        audio['\xa9ART'] = metadata['artist']
    if 'album' in metadata:
        audio['\xa9alb'] = metadata['album']
    if 'date' in metadata:
        audio['\xa9day'] = str(metadata['date'])
    if 'genre' in metadata:
        audio['\xa9gen'] = metadata['genre']
    if 'track_number' in metadata:
        audio['trkn'] = [(metadata['track_number'], 0)]
