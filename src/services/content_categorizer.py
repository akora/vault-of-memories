"""
Content categorization service for video files.

Categorizes videos into predefined categories based on metadata patterns,
technical characteristics, and filename analysis.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from ..models.video_metadata import CategoryResult


logger = logging.getLogger(__name__)


class ContentCategorizer:
    """
    Categorize video content based on metadata and analysis.

    Categories:
    - family: Personal/family videos from phones and cameras
    - tutorials: Educational and instructional content
    - work: Work-related videos (meetings, presentations)
    - tech: Technical content (screencasts, coding)
    - entertainment: Downloaded or streamed entertainment
    - other: Uncategorized content

    Uses pattern-based heuristics with confidence scoring.
    """

    # Supported categories
    CATEGORIES = ["family", "tutorials", "work", "tech", "entertainment", "other"]

    # Default categorization rules
    DEFAULT_RULES = {
        "family": {
            "camera_indicators": ["iphone", "android", "samsung", "canon", "nikon", "sony"],
            "device_patterns": ["phone", "camera", "gopro"],
            "filename_patterns": ["family", "vacation", "birthday", "holiday", "kids", "home"],
            "resolution_preferences": ["1080p", "720p"],
            "confidence_boost": 0.2
        },
        "tutorials": {
            "filename_patterns": ["tutorial", "howto", "guide", "lesson", "learn", "course"],
            "device_patterns": ["screen record", "screencast", "obs"],
            "duration_range": (300, 3600),  # 5-60 minutes typical
            "confidence_boost": 0.15
        },
        "work": {
            "filename_patterns": ["meeting", "presentation", "zoom", "teams", "webinar", "conference"],
            "device_patterns": ["screen record", "zoom", "teams"],
            "duration_range": (600, 7200),  # 10 min - 2 hours typical
            "confidence_boost": 0.15
        },
        "tech": {
            "filename_patterns": ["coding", "programming", "developer", "demo", "screencast", "tech"],
            "device_patterns": ["screen record", "obs", "quicktime"],
            "resolution_preferences": ["1080p", "1440p", "4K"],
            "confidence_boost": 0.15
        },
        "entertainment": {
            "filename_patterns": ["movie", "show", "episode", "season", "film"],
            "resolution_preferences": ["1080p", "4K"],
            "duration_range": (1200, 10800),  # 20 min - 3 hours
            "confidence_boost": 0.1
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize categorizer with optional configuration.

        Args:
            config_path: Path to JSON configuration file with custom rules
        """
        self.rules = self.DEFAULT_RULES.copy()

        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    custom_rules = json.load(f)
                    self.rules.update(custom_rules.get("categorization_rules", {}))
                    logger.info(f"Loaded categorization rules from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    def categorize(self, metadata_dict: Dict[str, Any], file_path: Path) -> CategoryResult:
        """
        Categorize video based on metadata and file information.

        Args:
            metadata_dict: Extracted video metadata
            file_path: Path to video file

        Returns:
            CategoryResult with primary category, confidence, and reasoning
        """
        # Calculate confidence scores for each category
        scores = {}
        for category in self.CATEGORIES:
            if category == "other":
                continue  # "other" is fallback only
            scores[category] = self._calculate_category_score(
                category, metadata_dict, file_path
            )

        # Sort by confidence score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Get top category or default to "other"
        if sorted_categories and sorted_categories[0][1] > 0.3:
            primary_category = sorted_categories[0][0]
            confidence = sorted_categories[0][1]
        else:
            primary_category = "other"
            confidence = 0.5

        # Generate reasoning
        reasoning = self._generate_reasoning(primary_category, metadata_dict, file_path)

        # Alternative categories (those with >0.2 confidence)
        alternatives = [
            (cat, score) for cat, score in sorted_categories[1:]
            if score > 0.2
        ]

        return CategoryResult(
            primary_category=primary_category,
            confidence=confidence,
            reasoning=reasoning,
            alternative_categories=alternatives
        )

    def _calculate_category_score(self, category: str, metadata: Dict[str, Any],
                                  file_path: Path) -> float:
        """
        Calculate confidence score for a specific category.

        Args:
            category: Category to score
            metadata: Video metadata
            file_path: Path to video file

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if category not in self.rules:
            return 0.0

        rules = self.rules[category]
        score = 0.0
        matches = []

        # Check camera/device indicators
        camera_make = (metadata.get("camera_make") or "").lower()
        camera_model = (metadata.get("camera_model") or "").lower()
        recording_device = (metadata.get("recording_device") or "").lower()

        if "camera_indicators" in rules:
            for indicator in rules["camera_indicators"]:
                if (indicator in camera_make or indicator in camera_model or
                    indicator in recording_device):
                    score += 0.3
                    matches.append(f"camera/device: {indicator}")
                    break

        # Check device patterns
        if "device_patterns" in rules:
            for pattern in rules["device_patterns"]:
                if pattern in recording_device:
                    score += 0.25
                    matches.append(f"device pattern: {pattern}")
                    break

        # Check filename patterns
        filename_lower = file_path.stem.lower()
        if "filename_patterns" in rules:
            for pattern in rules["filename_patterns"]:
                if pattern in filename_lower:
                    score += 0.2
                    matches.append(f"filename: {pattern}")
                    break

        # Check resolution preferences
        resolution_label = metadata.get("resolution_label")
        if "resolution_preferences" in rules and resolution_label:
            if resolution_label in rules["resolution_preferences"]:
                score += 0.15
                matches.append(f"resolution: {resolution_label}")

        # Check duration range
        duration = metadata.get("duration")
        if "duration_range" in rules and duration:
            min_dur, max_dur = rules["duration_range"]
            if min_dur <= duration <= max_dur:
                score += 0.15
                matches.append(f"duration in range")

        # Apply confidence boost
        if matches and "confidence_boost" in rules:
            score += rules["confidence_boost"]

        # Normalize to 0.0-1.0 range
        return min(score, 1.0)

    def _generate_reasoning(self, category: str, metadata: Dict[str, Any],
                           file_path: Path) -> str:
        """
        Generate human-readable reasoning for categorization.

        Args:
            category: Selected category
            metadata: Video metadata
            file_path: Path to video file

        Returns:
            Reasoning string
        """
        reasons = []

        if category == "family":
            camera_make = metadata.get("camera_make")
            camera_model = metadata.get("camera_model")
            if camera_make or camera_model:
                camera_info = f"{camera_make} {camera_model}".strip()
                reasons.append(f"recorded with {camera_info}")
            if metadata.get("gps_latitude") or metadata.get("gps_longitude"):
                reasons.append("contains GPS location data")

        elif category == "tutorials":
            if "tutorial" in file_path.stem.lower():
                reasons.append("filename indicates tutorial content")
            duration = metadata.get("duration")
            if duration and 300 <= duration <= 3600:
                reasons.append(f"typical tutorial duration ({int(duration/60)} minutes)")

        elif category == "work":
            device = metadata.get("recording_device", "").lower()
            if "zoom" in device or "teams" in device:
                reasons.append(f"recorded with {device}")
            if "meeting" in file_path.stem.lower():
                reasons.append("filename indicates meeting")

        elif category == "tech":
            device = metadata.get("recording_device", "").lower()
            if "screen" in device:
                reasons.append("screen recording detected")
            resolution = metadata.get("resolution_label")
            if resolution in ["1080p", "1440p", "4K"]:
                reasons.append(f"high resolution ({resolution})")

        elif category == "entertainment":
            duration = metadata.get("duration")
            if duration and duration > 1200:
                reasons.append(f"long duration ({int(duration/60)} minutes)")
            resolution = metadata.get("resolution_label")
            if resolution in ["1080p", "4K"]:
                reasons.append(f"high quality ({resolution})")

        elif category == "other":
            return "No strong category indicators found"

        if not reasons:
            return f"Categorized as {category} based on metadata patterns"

        return f"Categorized as {category}: {', '.join(reasons)}"

    def get_supported_categories(self) -> List[str]:
        """
        Get list of supported categories.

        Returns:
            List of category names
        """
        return self.CATEGORIES.copy()
