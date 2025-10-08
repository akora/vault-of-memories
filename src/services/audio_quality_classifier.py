"""
Audio quality classification service.

Classifies audio files based on format type, bitrate, and compression.
"""

from typing import Tuple


class AudioQualityClassifier:
    """Classify audio quality based on format and bitrate."""

    # Lossless format extensions
    LOSSLESS_FORMATS = {
        "flac", "wav", "wave", "aiff", "aif", "ape", "wv", "tta", "alac", "m4a"
    }

    # Default quality thresholds (in kbps)
    # These can be overridden by configuration
    HIGH_QUALITY_THRESHOLD = 256
    MEDIUM_QUALITY_THRESHOLD = 128

    def __init__(
        self,
        high_quality_threshold: int = HIGH_QUALITY_THRESHOLD,
        medium_quality_threshold: int = MEDIUM_QUALITY_THRESHOLD
    ):
        """
        Initialize quality classifier with custom thresholds.

        Args:
            high_quality_threshold: Minimum bitrate for high quality (kbps)
            medium_quality_threshold: Minimum bitrate for medium quality (kbps)
        """
        self.high_quality_threshold = high_quality_threshold
        self.medium_quality_threshold = medium_quality_threshold

    def classify(
        self,
        format: str,
        bitrate: int = None,
        bit_depth: int = None,
        sample_rate: int = None
    ) -> Tuple[bool, str, str]:
        """
        Classify audio quality.

        Args:
            format: Audio format (extension or format name)
            bitrate: Bitrate in kbps (None if unknown)
            bit_depth: Bit depth for lossless formats
            sample_rate: Sample rate in Hz

        Returns:
            Tuple of (is_lossless, quality_level, compression_type)
            - is_lossless: True if lossless format
            - quality_level: "high", "medium", "low", or "unknown"
            - compression_type: "lossless", "lossy", or "unknown"
        """
        format_lower = format.lower()

        # Determine if lossless
        is_lossless = self._is_lossless_format(format_lower)

        # Determine compression type
        if is_lossless:
            compression_type = "lossless"
        elif format_lower in ["mp3", "m4a", "aac", "ogg", "opus", "wma"]:
            compression_type = "lossy"
        else:
            compression_type = "unknown"

        # Determine quality level
        quality_level = self._determine_quality_level(
            is_lossless, format_lower, bitrate, bit_depth, sample_rate
        )

        return is_lossless, quality_level, compression_type

    def _is_lossless_format(self, format: str) -> bool:
        """Check if format is lossless."""
        # Check direct format match
        if format in self.LOSSLESS_FORMATS:
            return True

        # Check format name contains lossless indicators
        if any(indicator in format for indicator in ["flac", "wav", "aiff", "alac"]):
            return True

        return False

    def _determine_quality_level(
        self,
        is_lossless: bool,
        format: str,
        bitrate: int = None,
        bit_depth: int = None,
        sample_rate: int = None
    ) -> str:
        """
        Determine quality level based on format characteristics.

        Args:
            is_lossless: Whether format is lossless
            format: Audio format
            bitrate: Bitrate in kbps
            bit_depth: Bit depth
            sample_rate: Sample rate in Hz

        Returns:
            Quality level: "high", "medium", "low", or "unknown"
        """
        # Lossless formats
        if is_lossless:
            # For lossless, quality depends on bit depth and sample rate
            if bit_depth and sample_rate:
                # High-res audio: 24-bit and/or > 48kHz
                if bit_depth >= 24 or sample_rate > 48000:
                    return "high"
                # Standard CD quality: 16-bit, 44.1kHz
                elif bit_depth >= 16 and sample_rate >= 44100:
                    return "high"
                else:
                    return "medium"
            # If we don't have detailed info, assume high for lossless
            return "high"

        # Lossy formats - use bitrate
        if bitrate is not None:
            if bitrate >= self.high_quality_threshold:
                return "high"
            elif bitrate >= self.medium_quality_threshold:
                return "medium"
            else:
                return "low"

        # Special format considerations when bitrate unknown
        if format in ["opus"]:
            # Opus is efficient, assume at least medium
            return "medium"

        return "unknown"

    def get_quality_description(
        self,
        is_lossless: bool,
        quality_level: str,
        compression_type: str,
        bitrate: int = None
    ) -> str:
        """
        Get human-readable quality description.

        Args:
            is_lossless: Whether audio is lossless
            quality_level: Quality level
            compression_type: Compression type
            bitrate: Bitrate in kbps

        Returns:
            Human-readable quality description
        """
        if is_lossless:
            if quality_level == "high":
                return "Lossless high-resolution audio"
            else:
                return "Lossless audio"

        # Lossy format
        if bitrate:
            if quality_level == "high":
                return f"High quality lossy ({bitrate} kbps)"
            elif quality_level == "medium":
                return f"Medium quality lossy ({bitrate} kbps)"
            elif quality_level == "low":
                return f"Low quality lossy ({bitrate} kbps)"

        return f"{quality_level.capitalize()} quality {compression_type}"
