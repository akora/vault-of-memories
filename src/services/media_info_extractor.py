"""
Media info extraction service for video files.

Uses pymediainfo to extract technical metadata from video files.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pymediainfo import MediaInfo


logger = logging.getLogger(__name__)


class MediaInfoExtractor:
    """
    Extract technical metadata from video files using pymediainfo.

    Extracts:
    - Container format and codec information
    - Duration, resolution, framerate, bitrate
    - Audio stream information
    - Multiple video/audio/subtitle streams
    - Embedded metadata (creation dates, camera info, GPS)
    """

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from video file.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary containing extracted metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If MediaInfo fails to parse file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        try:
            media_info = MediaInfo.parse(str(file_path))
        except Exception as e:
            raise RuntimeError(f"Failed to parse video file {file_path}: {e}")

        metadata = {
            "file_path": file_path,
            "file_size": file_path.stat().st_size,
            "format": None,
            "container": None,
            "duration": None,
            "width": None,
            "height": None,
            "fps": None,
            "bitrate": None,
            "video_codec": None,
            "audio_codec": None,
            "video_streams": 0,
            "audio_streams": 0,
            "subtitle_streams": 0,
            "camera_make": None,
            "camera_model": None,
            "recording_device": None,
            "gps_latitude": None,
            "gps_longitude": None,
            "gps_altitude": None,
            "creation_date": None,
            "recording_date": None,
            "modification_date": None,
            "processing_errors": []
        }

        # Extract general/container information
        for track in media_info.tracks:
            if track.track_type == "General":
                metadata.update(self._extract_general_info(track))
            elif track.track_type == "Video":
                metadata["video_streams"] += 1
                if metadata["video_streams"] == 1:  # Use first video stream
                    metadata.update(self._extract_video_info(track))
            elif track.track_type == "Audio":
                metadata["audio_streams"] += 1
                if metadata["audio_streams"] == 1:  # Use first audio stream
                    metadata.update(self._extract_audio_info(track))
            elif track.track_type == "Text":
                metadata["subtitle_streams"] += 1

        return metadata

    def _extract_general_info(self, track) -> Dict[str, Any]:
        """Extract general container information."""
        info = {}

        # Container format
        if hasattr(track, "format"):
            info["container"] = track.format
            info["format"] = track.format

        # Duration in seconds
        if hasattr(track, "duration") and track.duration:
            info["duration"] = float(track.duration) / 1000.0  # Convert ms to seconds

        # Overall bitrate
        if hasattr(track, "overall_bit_rate") and track.overall_bit_rate:
            info["bitrate"] = int(track.overall_bit_rate) // 1000  # Convert to kbps

        # Timestamps
        if hasattr(track, "encoded_date") and track.encoded_date:
            info["creation_date"] = self._parse_timestamp(track.encoded_date)
        if hasattr(track, "tagged_date") and track.tagged_date:
            if not info.get("creation_date"):
                info["creation_date"] = self._parse_timestamp(track.tagged_date)

        # File modification date
        if hasattr(track, "file_last_modification_date") and track.file_last_modification_date:
            info["modification_date"] = self._parse_timestamp(track.file_last_modification_date)

        # Recording device/camera
        if hasattr(track, "recorded_by") and track.recorded_by:
            info["recording_device"] = track.recorded_by
        if hasattr(track, "writing_application") and track.writing_application:
            if not info.get("recording_device"):
                info["recording_device"] = track.writing_application

        return info

    def _extract_video_info(self, track) -> Dict[str, Any]:
        """Extract video stream information."""
        info = {}

        # Codec
        if hasattr(track, "format"):
            info["video_codec"] = track.format

        # Resolution
        if hasattr(track, "width") and track.width:
            info["width"] = int(track.width)
        if hasattr(track, "height") and track.height:
            info["height"] = int(track.height)

        # Frame rate
        if hasattr(track, "frame_rate") and track.frame_rate:
            info["fps"] = float(track.frame_rate)

        # Bitrate (video stream specific)
        if hasattr(track, "bit_rate") and track.bit_rate:
            info["bitrate"] = int(track.bit_rate) // 1000  # Convert to kbps

        # Camera information (some cameras embed this in video stream)
        if hasattr(track, "make") and track.make:
            info["camera_make"] = track.make
        if hasattr(track, "model") and track.model:
            info["camera_model"] = track.model

        # Recording date from video stream
        if hasattr(track, "encoded_date") and track.encoded_date:
            info["recording_date"] = self._parse_timestamp(track.encoded_date)

        return info

    def _extract_audio_info(self, track) -> Dict[str, Any]:
        """Extract audio stream information."""
        info = {}

        # Audio codec
        if hasattr(track, "format"):
            info["audio_codec"] = track.format

        return info

    def _parse_timestamp(self, timestamp_str: str) -> Optional[str]:
        """
        Parse timestamp string to ISO format.

        MediaInfo returns timestamps in various formats. This attempts to
        normalize them to ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

        Args:
            timestamp_str: Timestamp string from MediaInfo

        Returns:
            ISO formatted timestamp string, or original if parsing fails
        """
        if not timestamp_str:
            return None

        # MediaInfo typically returns UTC timestamps like:
        # "UTC 2023-12-25 14:30:22"
        # "2023-12-25 14:30:22.000"

        timestamp_str = timestamp_str.strip()

        # Remove "UTC " prefix if present
        if timestamp_str.startswith("UTC "):
            timestamp_str = timestamp_str[4:]

        # Split on space to separate date and time
        parts = timestamp_str.split()
        if len(parts) >= 2:
            date_part = parts[0]
            time_part = parts[1]

            # Remove milliseconds if present
            if "." in time_part:
                time_part = time_part.split(".")[0]

            # Return ISO format
            return f"{date_part}T{time_part}"

        return timestamp_str  # Return as-is if we can't parse it

    def extract_gps_coordinates(self, file_path: Path) -> Optional[Dict[str, float]]:
        """
        Extract GPS coordinates from video metadata.

        Some video formats (particularly from smartphones and cameras) embed
        GPS location data. This is typically found in the General track.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary with latitude, longitude, altitude or None
        """
        try:
            media_info = MediaInfo.parse(str(file_path))
        except Exception as e:
            logger.warning(f"Failed to parse GPS from {file_path}: {e}")
            return None

        for track in media_info.tracks:
            if track.track_type != "General":
                continue

            gps_data = {}

            # Check for GPS coordinates (various possible field names)
            if hasattr(track, "xyz") and track.xyz:
                # Some formats store as "xyz" field: "+12.345+98.765/"
                coords = self._parse_xyz_coords(track.xyz)
                if coords:
                    return coords

            # Individual coordinate fields
            if hasattr(track, "latitude") and track.latitude:
                gps_data["latitude"] = self._parse_coordinate(track.latitude)
            if hasattr(track, "longitude") and track.longitude:
                gps_data["longitude"] = self._parse_coordinate(track.longitude)
            if hasattr(track, "altitude") and track.altitude:
                gps_data["altitude"] = self._parse_altitude(track.altitude)

            if gps_data:
                return gps_data

        return None

    def _parse_xyz_coords(self, xyz_str: str) -> Optional[Dict[str, float]]:
        """Parse XYZ coordinate string like '+12.345+98.765+100.5/'."""
        try:
            # Remove trailing slash
            xyz_str = xyz_str.rstrip("/")

            # Split by + or - while keeping the sign
            parts = []
            current = ""
            for char in xyz_str:
                if char in "+-" and current:
                    parts.append(current)
                    current = char
                else:
                    current += char
            if current:
                parts.append(current)

            if len(parts) >= 2:
                coords = {
                    "latitude": float(parts[0]),
                    "longitude": float(parts[1])
                }
                if len(parts) >= 3:
                    coords["altitude"] = float(parts[2])
                return coords
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse XYZ coords '{xyz_str}': {e}")

        return None

    def _parse_coordinate(self, coord_str: str) -> Optional[float]:
        """Parse coordinate string to decimal degrees."""
        try:
            # Remove direction indicators (N, S, E, W)
            coord_str = coord_str.upper().rstrip("NSEW").strip()
            return float(coord_str)
        except ValueError:
            return None

    def _parse_altitude(self, alt_str: str) -> Optional[float]:
        """Parse altitude string to meters."""
        try:
            # Remove units (m, meters, ft, feet)
            alt_str = alt_str.lower()
            for unit in [" m", " meters", " ft", " feet"]:
                alt_str = alt_str.replace(unit, "")
            return float(alt_str.strip())
        except ValueError:
            return None
