"""
T023: Classification data model.
"""

from dataclasses import dataclass


@dataclass
class Classification:
    """Result of content classification determining file category and subcategory."""

    primary_category: str
    subcategory: str | None
    confidence: float
    reasoning: str
    mime_type: str
    detection_method: str

    def __post_init__(self):
        """Validate classification after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

        valid_categories = {"photos", "documents", "videos", "audio", "archives", "other"}
        if self.primary_category not in valid_categories:
            raise ValueError(f"Invalid primary_category: {self.primary_category}")

        valid_methods = {"libmagic", "extension", "header_inspection", "fallback", "metadata"}
        if self.detection_method not in valid_methods:
            raise ValueError(f"Invalid detection_method: {self.detection_method}")
