"""
Contract: FolderCreator

Thread-safe folder creation with cross-platform support.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreationResult:
    """Result of folder creation operation."""
    path: Path
    created_new: bool
    already_existed: bool
    permissions_set: int
    timestamp: datetime
    error: str | None


class FolderCreator:
    """
    Creates vault directory hierarchies safely across platforms.

    Responsibilities:
    - Create nested directories atomically
    - Handle race conditions (multiple threads/processes)
    - Ensure cross-platform path compatibility
    - Set appropriate permissions
    - Handle Windows long path limitations
    """

    def create_hierarchy(self, vault_path: Path, mode: int = 0o755) -> CreationResult:
        """
        Create complete vault directory hierarchy.

        Args:
            vault_path: Complete target path to create
            mode: Unix permission mode (ignored on Windows)

        Returns:
            CreationResult with creation status and details

        Raises:
            OSError: If directory creation fails
            PermissionError: If insufficient permissions

        Contract:
            - MUST create all parent directories (like mkdir -p)
            - MUST be thread-safe (no race conditions)
            - MUST use exist_ok=True for idempotent operations
            - MUST handle Windows long paths (>260 chars) with \\?\ prefix
            - MUST validate path for cross-platform compatibility
            - MUST sanitize folder names (no reserved names, invalid chars)
            - MUST set permissions on Unix (mode), accept Windows defaults
            - MUST NOT fail if directory already exists
            - MUST verify created path is actually a directory
        """
        raise NotImplementedError

    def validate_path(self, path: Path) -> tuple[bool, str | None]:
        """
        Validate path for cross-platform compatibility.

        Args:
            path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)

        Contract:
            - MUST check for Windows reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
            - MUST check for invalid characters (\\, /, :, *, ?, ", <, >, |)
            - MUST check path length against platform limits (260 for Windows)
            - MUST check for leading/trailing spaces and dots
            - MUST return detailed error message if invalid
        """
        raise NotImplementedError

    def sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name for cross-platform use.

        Args:
            name: Folder name to sanitize

        Returns:
            Sanitized folder name safe for all platforms

        Contract:
            - MUST replace invalid characters with underscore
            - MUST handle reserved names (append suffix if needed)
            - MUST preserve readability where possible
            - MUST ensure non-empty result
            - MUST log sanitization for audit
        """
        raise NotImplementedError

    def create_batch(
        self,
        vault_paths: list[Path],
        mode: int = 0o755
    ) -> Dict[Path, CreationResult]:
        """
        Create multiple directory hierarchies efficiently.

        Args:
            vault_paths: List of paths to create
            mode: Unix permission mode

        Returns:
            Dictionary mapping paths to creation results

        Contract:
            - MUST handle parallel creation safely
            - MUST NOT fail entire batch if one path fails
            - Failed paths MUST have error in CreationResult
            - MUST deduplicate paths before processing
        """
        raise NotImplementedError
