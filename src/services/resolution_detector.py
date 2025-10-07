"""
Resolution detection and classification service.

Classifies video resolution into standard categories (4K, 1080p, 720p, etc.)
and determines quality indicators.
"""

import logging
from typing import Tuple, Optional


logger = logging.getLogger(__name__)


class ResolutionDetector:
    """
    Detect and classify video resolution.

    Provides:
    - Standard resolution labels (4K, 1080p, 720p, 480p, etc.)
    - HD/4K quality flags
    - Quality scoring based on resolution
    """

    # Standard resolution definitions (width x height)
    RESOLUTION_STANDARDS = {
        "8K": (7680, 4320),
        "4K": (3840, 2160),
        "2K": (2560, 1440),
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "480p": (720, 480),
        "360p": (640, 360),
        "240p": (426, 240)
    }

    # Tolerance for matching standard resolutions (pixels)
    RESOLUTION_TOLERANCE = 100

    def detect_resolution(self, width: Optional[int], height: Optional[int]) -> Tuple[Optional[str], bool, bool]:
        """
        Detect resolution label and quality indicators.

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            Tuple of (resolution_label, is_hd, is_4k)
            - resolution_label: "4K", "1080p", "720p", etc., or None
            - is_hd: True if resolution is 720p or higher
            - is_4k: True if resolution is 4K or higher
        """
        if width is None or height is None:
            return None, False, False

        # Find matching standard resolution
        resolution_label = self._classify_resolution(width, height)

        # Determine quality flags
        is_hd = self._is_hd_resolution(width, height)
        is_4k = self._is_4k_resolution(width, height)

        return resolution_label, is_hd, is_4k

    def _classify_resolution(self, width: int, height: int) -> Optional[str]:
        """
        Classify resolution into standard label.

        Matches against known standards with tolerance for slight variations
        (e.g., 1918x1080 still counts as 1080p).

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            Resolution label or custom label if no match
        """
        # Check each standard resolution
        for label, (std_width, std_height) in self.RESOLUTION_STANDARDS.items():
            if (abs(width - std_width) <= self.RESOLUTION_TOLERANCE and
                abs(height - std_height) <= self.RESOLUTION_TOLERANCE):
                return label

        # If no exact match, create custom label
        return self._create_custom_label(width, height)

    def _create_custom_label(self, width: int, height: int) -> str:
        """
        Create custom resolution label for non-standard resolutions.

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            Custom label like "1280x720" or "Custom 1920x800"
        """
        # For common aspect ratios, use simplified format
        if width >= 1920 and height >= 1080:
            return f"Custom {width}x{height}"
        else:
            return f"{width}x{height}"

    def _is_hd_resolution(self, width: int, height: int) -> bool:
        """
        Check if resolution qualifies as HD (720p or higher).

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            True if HD or higher
        """
        # HD is defined as 720p (1280x720) or higher
        hd_threshold_width = 1280
        hd_threshold_height = 720

        return width >= hd_threshold_width or height >= hd_threshold_height

    def _is_4k_resolution(self, width: int, height: int) -> bool:
        """
        Check if resolution qualifies as 4K or higher.

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            True if 4K or higher
        """
        # 4K is defined as 3840x2160 or higher
        fourk_threshold_width = 3840
        fourk_threshold_height = 2160

        return width >= fourk_threshold_width or height >= fourk_threshold_height

    def calculate_quality_score(self, width: Optional[int], height: Optional[int],
                               bitrate: Optional[int], fps: Optional[float]) -> float:
        """
        Calculate overall video quality score (0.0 to 1.0).

        Considers resolution, bitrate, and frame rate to assess quality.

        Args:
            width: Video width in pixels
            height: Video height in pixels
            bitrate: Video bitrate in kbps
            fps: Frames per second

        Returns:
            Quality score from 0.0 (lowest) to 1.0 (highest)
        """
        if width is None or height is None:
            return 0.0

        score = 0.0

        # Resolution contribution (50% of score)
        resolution_score = self._score_resolution(width, height)
        score += resolution_score * 0.5

        # Bitrate contribution (30% of score)
        if bitrate is not None:
            bitrate_score = self._score_bitrate(bitrate, width, height)
            score += bitrate_score * 0.3
        else:
            # If no bitrate available, weight resolution more heavily
            score += resolution_score * 0.3

        # Frame rate contribution (20% of score)
        if fps is not None:
            fps_score = self._score_fps(fps)
            score += fps_score * 0.2
        else:
            # If no FPS available, weight resolution more heavily
            score += resolution_score * 0.2

        return min(score, 1.0)

    def _score_resolution(self, width: int, height: int) -> float:
        """Score resolution on 0.0 to 1.0 scale."""
        pixel_count = width * height

        # Reference points
        # 8K: 33,177,600 pixels
        # 4K: 8,294,400 pixels
        # 1080p: 2,073,600 pixels
        # 720p: 921,600 pixels
        # 480p: 345,600 pixels

        if pixel_count >= 8294400:  # 4K or higher
            return 1.0
        elif pixel_count >= 2073600:  # 1080p
            return 0.8
        elif pixel_count >= 921600:  # 720p
            return 0.6
        elif pixel_count >= 345600:  # 480p
            return 0.4
        else:
            return 0.2

    def _score_bitrate(self, bitrate: int, width: int, height: int) -> float:
        """
        Score bitrate relative to resolution.

        Higher resolution needs higher bitrate for good quality.
        """
        pixel_count = width * height

        # Calculate expected bitrate for good quality (rough heuristic)
        # ~0.1 bits per pixel at 30fps is decent quality
        expected_bitrate = (pixel_count * 0.1 * 30) / 1000  # Convert to kbps

        # Compare actual vs expected
        ratio = bitrate / expected_bitrate if expected_bitrate > 0 else 0

        if ratio >= 1.5:  # Excellent bitrate
            return 1.0
        elif ratio >= 1.0:  # Good bitrate
            return 0.8
        elif ratio >= 0.5:  # Acceptable bitrate
            return 0.6
        elif ratio >= 0.25:  # Low bitrate
            return 0.4
        else:  # Very low bitrate
            return 0.2

    def _score_fps(self, fps: float) -> float:
        """Score frame rate on 0.0 to 1.0 scale."""
        if fps >= 60:  # High frame rate
            return 1.0
        elif fps >= 30:  # Standard frame rate
            return 0.8
        elif fps >= 24:  # Cinema frame rate
            return 0.6
        else:  # Low frame rate
            return 0.4
