"""
T026: ClassificationRule data model.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClassificationRule:
    """Configurable rule for determining file category/subcategory."""

    name: str
    priority: int
    primary_category: str
    subcategory: str | None
    mime_patterns: list[str]
    extension_patterns: list[str]
    metadata_conditions: dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self):
        """Validate classification rule after initialization."""
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")

        if not self.mime_patterns and not self.extension_patterns:
            raise ValueError("Either mime_patterns or extension_patterns must be non-empty")

        valid_categories = {"photos", "documents", "videos", "audio", "archives", "other"}
        if self.primary_category not in valid_categories:
            raise ValueError(f"Invalid primary_category: {self.primary_category}")
