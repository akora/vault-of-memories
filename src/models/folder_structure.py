"""
T027: FolderStructure data model.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FolderStructure:
    """Definition of vault organization hierarchy and naming rules."""

    vault_root: Path
    category_folders: dict[str, str]
    date_hierarchy_format: str = "YYYY/YYYY-MM/YYYY-MM-DD"
    max_path_length: int = 260
    use_subcategories: bool = True
    folder_permissions: int = 0o755

    def __post_init__(self):
        """Validate folder structure after initialization."""
        if not self.vault_root.is_absolute():
            raise ValueError("vault_root must be absolute path")

        if self.max_path_length < 100:
            raise ValueError("max_path_length must be at least 100")

        if not 0 <= self.folder_permissions <= 0o777:
            raise ValueError("folder_permissions must be valid Unix mode (0o000-0o777)")
