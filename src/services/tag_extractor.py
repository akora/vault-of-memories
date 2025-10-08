"""
Tag extraction service using mutagen.

Extracts metadata tags from various audio formats (ID3, Vorbis, MP4, etc.)
"""

from pathlib import Path
from typing import Optional, Dict, Any
import mutagen
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from mutagen.asf import ASF  # For WMA files


class TagExtractor:
    """Extract metadata tags from audio files using mutagen."""

    def extract_tags(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract all available tags from an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary with extracted tag data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
            RuntimeError: If file is corrupted or unreadable
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        try:
            audio = mutagen.File(str(file_path))
            if audio is None:
                raise ValueError(f"Unsupported or invalid audio format: {file_path}")

            # Extract technical specifications
            tags = {
                "duration": getattr(audio.info, "length", None),
                "bitrate": self._get_bitrate(audio),
                "sample_rate": getattr(audio.info, "sample_rate", None),
                "channels": getattr(audio.info, "channels", None),
                "bit_depth": getattr(audio.info, "bits_per_sample", None),
            }

            # Extract tag metadata based on format
            if isinstance(audio, mutagen.id3.ID3FileType):
                tags.update(self._extract_id3_tags(audio))
            elif isinstance(audio, (FLAC, OggVorbis)):
                tags.update(self._extract_vorbis_tags(audio))
            elif isinstance(audio, MP4):
                tags.update(self._extract_mp4_tags(audio))
            elif isinstance(audio, ASF):
                tags.update(self._extract_asf_tags(audio))

            # Check for cover art
            tags["has_cover_art"] = self._has_cover_art(audio)

            # Determine tag format
            tags["tag_format"] = self._get_tag_format(audio)

            return tags

        except Exception as e:
            raise RuntimeError(f"Error reading audio file {file_path}: {str(e)}")

    def _get_bitrate(self, audio) -> Optional[int]:
        """Extract bitrate in kbps."""
        if hasattr(audio.info, "bitrate") and audio.info.bitrate:
            return audio.info.bitrate // 1000  # Convert to kbps
        return None

    def _extract_id3_tags(self, audio) -> Dict[str, Any]:
        """Extract ID3 tags (MP3, etc.)."""
        tags = {}

        if audio.tags is None:
            return tags

        # Title
        if "TIT2" in audio.tags:
            tags["title"] = str(audio.tags["TIT2"])

        # Artist
        if "TPE1" in audio.tags:
            tags["artist"] = str(audio.tags["TPE1"])

        # Album
        if "TALB" in audio.tags:
            tags["album"] = str(audio.tags["TALB"])

        # Album artist
        if "TPE2" in audio.tags:
            tags["album_artist"] = str(audio.tags["TPE2"])

        # Year/Date
        if "TDRC" in audio.tags:
            date_str = str(audio.tags["TDRC"])
            tags["date"] = date_str
            try:
                tags["year"] = int(date_str[:4]) if len(date_str) >= 4 else None
            except ValueError:
                pass

        # Track number
        if "TRCK" in audio.tags:
            track_str = str(audio.tags["TRCK"])
            try:
                if "/" in track_str:
                    track, total = track_str.split("/")
                    tags["track_number"] = int(track)
                    tags["total_tracks"] = int(total)
                else:
                    tags["track_number"] = int(track_str)
            except ValueError:
                pass

        # Disc number
        if "TPOS" in audio.tags:
            disc_str = str(audio.tags["TPOS"])
            try:
                if "/" in disc_str:
                    disc, total = disc_str.split("/")
                    tags["disc_number"] = int(disc)
                    tags["total_discs"] = int(total)
                else:
                    tags["disc_number"] = int(disc_str)
            except ValueError:
                pass

        # Genre
        if "TCON" in audio.tags:
            tags["genre"] = str(audio.tags["TCON"])

        # Comment
        if "COMM" in audio.tags:
            tags["comment"] = str(audio.tags["COMM"])

        # Composer
        if "TCOM" in audio.tags:
            tags["composer"] = str(audio.tags["TCOM"])

        return tags

    def _extract_vorbis_tags(self, audio) -> Dict[str, Any]:
        """Extract Vorbis comments (FLAC, OGG)."""
        tags = {}

        if not audio.tags:
            return tags

        tags["title"] = self._get_vorbis_tag(audio, "title")
        tags["artist"] = self._get_vorbis_tag(audio, "artist")
        tags["album"] = self._get_vorbis_tag(audio, "album")
        tags["album_artist"] = self._get_vorbis_tag(audio, "albumartist")
        tags["date"] = self._get_vorbis_tag(audio, "date")
        tags["genre"] = self._get_vorbis_tag(audio, "genre")
        tags["comment"] = self._get_vorbis_tag(audio, "comment")
        tags["composer"] = self._get_vorbis_tag(audio, "composer")

        # Parse date for year
        if tags.get("date"):
            try:
                tags["year"] = int(tags["date"][:4])
            except (ValueError, IndexError):
                pass

        # Track number
        track_num = self._get_vorbis_tag(audio, "tracknumber")
        if track_num:
            try:
                tags["track_number"] = int(track_num)
            except ValueError:
                pass

        total_tracks = self._get_vorbis_tag(audio, "tracktotal")
        if total_tracks:
            try:
                tags["total_tracks"] = int(total_tracks)
            except ValueError:
                pass

        # Disc number
        disc_num = self._get_vorbis_tag(audio, "discnumber")
        if disc_num:
            try:
                tags["disc_number"] = int(disc_num)
            except ValueError:
                pass

        total_discs = self._get_vorbis_tag(audio, "disctotal")
        if total_discs:
            try:
                tags["total_discs"] = int(total_discs)
            except ValueError:
                pass

        return tags

    def _extract_mp4_tags(self, audio) -> Dict[str, Any]:
        """Extract MP4/M4A tags."""
        tags = {}

        if not audio.tags:
            return tags

        # MP4 uses different tag keys
        tags["title"] = self._get_mp4_tag(audio, "\xa9nam")
        tags["artist"] = self._get_mp4_tag(audio, "\xa9ART")
        tags["album"] = self._get_mp4_tag(audio, "\xa9alb")
        tags["album_artist"] = self._get_mp4_tag(audio, "aART")
        tags["date"] = self._get_mp4_tag(audio, "\xa9day")
        tags["genre"] = self._get_mp4_tag(audio, "\xa9gen")
        tags["comment"] = self._get_mp4_tag(audio, "\xa9cmt")
        tags["composer"] = self._get_mp4_tag(audio, "\xa9wrt")

        # Parse date for year
        if tags.get("date"):
            try:
                tags["year"] = int(tags["date"][:4])
            except (ValueError, IndexError):
                pass

        # Track number (stored as tuple)
        if "trkn" in audio.tags:
            track_info = audio.tags["trkn"][0]
            if isinstance(track_info, tuple):
                tags["track_number"] = track_info[0]
                if len(track_info) > 1 and track_info[1]:
                    tags["total_tracks"] = track_info[1]

        # Disc number (stored as tuple)
        if "disk" in audio.tags:
            disc_info = audio.tags["disk"][0]
            if isinstance(disc_info, tuple):
                tags["disc_number"] = disc_info[0]
                if len(disc_info) > 1 and disc_info[1]:
                    tags["total_discs"] = disc_info[1]

        return tags

    def _extract_asf_tags(self, audio) -> Dict[str, Any]:
        """Extract ASF/WMA tags."""
        tags = {}

        if not audio.tags:
            return tags

        tags["title"] = self._get_asf_tag(audio, "Title")
        tags["artist"] = self._get_asf_tag(audio, "Author")
        tags["album"] = self._get_asf_tag(audio, "WM/AlbumTitle")
        tags["album_artist"] = self._get_asf_tag(audio, "WM/AlbumArtist")
        tags["date"] = self._get_asf_tag(audio, "WM/Year")
        tags["genre"] = self._get_asf_tag(audio, "WM/Genre")
        tags["comment"] = self._get_asf_tag(audio, "Description")
        tags["composer"] = self._get_asf_tag(audio, "WM/Composer")

        # Parse date for year
        if tags.get("date"):
            try:
                tags["year"] = int(tags["date"])
            except (ValueError, TypeError):
                pass

        # Track number
        track_num = self._get_asf_tag(audio, "WM/TrackNumber")
        if track_num:
            try:
                tags["track_number"] = int(track_num)
            except (ValueError, TypeError):
                pass

        return tags

    def _get_vorbis_tag(self, audio, key: str) -> Optional[str]:
        """Get a Vorbis comment tag value."""
        if key in audio.tags:
            value = audio.tags[key]
            if isinstance(value, list) and len(value) > 0:
                return str(value[0])
            return str(value) if value else None
        return None

    def _get_mp4_tag(self, audio, key: str) -> Optional[str]:
        """Get an MP4 tag value."""
        if key in audio.tags:
            value = audio.tags[key]
            if isinstance(value, list) and len(value) > 0:
                return str(value[0])
            return str(value) if value else None
        return None

    def _get_asf_tag(self, audio, key: str) -> Optional[str]:
        """Get an ASF/WMA tag value."""
        if key in audio.tags:
            value = audio.tags[key]
            if isinstance(value, list) and len(value) > 0:
                val = value[0]
                return str(val.value) if hasattr(val, "value") else str(val)
            return str(value) if value else None
        return None

    def _has_cover_art(self, audio) -> bool:
        """Check if audio file has embedded cover art."""
        try:
            if isinstance(audio, mutagen.id3.ID3FileType):
                return "APIC" in audio.tags if audio.tags else False
            elif isinstance(audio, FLAC):
                return len(audio.pictures) > 0 if hasattr(audio, "pictures") else False
            elif isinstance(audio, MP4):
                return "covr" in audio.tags if audio.tags else False
            elif isinstance(audio, ASF):
                return "WM/Picture" in audio.tags if audio.tags else False
        except Exception:
            pass
        return False

    def _get_tag_format(self, audio) -> Optional[str]:
        """Determine the tag format used."""
        if isinstance(audio, mutagen.id3.ID3FileType):
            if audio.tags and hasattr(audio.tags, "version"):
                version = audio.tags.version
                return f"ID3v{version[0]}.{version[1]}"
            return "ID3"
        elif isinstance(audio, (FLAC, OggVorbis)):
            return "Vorbis Comments"
        elif isinstance(audio, MP4):
            return "MP4/iTunes"
        elif isinstance(audio, ASF):
            return "ASF/WMA"
        return None
