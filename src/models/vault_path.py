"""
T022: VaultPath data model.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VaultPath:
    """Represents the complete target path for organizing a file in the vault."""

    base_path: Path
    primary_category: str
    subcategory: str | None
    year: str
    month: str
    day: str
    full_path: Path

    def __post_init__(self):
        """Validate vault path after initialization."""
        # Validate primary category
        valid_categories = {"photos", "documents", "videos", "audio", "archives", "other"}
        if self.primary_category not in valid_categories:
            raise ValueError(f"Invalid primary_category: {self.primary_category}")

        # Validate date format
        if not self.year.isdigit() or len(self.year) != 4:
            raise ValueError(f"Invalid year format: {self.year}")

        # Ensure full_path is absolute
        if not self.full_path.is_absolute():
            raise ValueError("full_path must be absolute")
