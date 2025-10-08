"""
T031: FolderCreator - Thread-safe folder creation with cross-platform support.
"""

from pathlib import Path
from datetime import datetime, timezone
import platform
import logging
from pathvalidate import sanitize_filename, is_valid_filename
from ..models.creation_result import CreationResult


logger = logging.getLogger(__name__)


class FolderCreator:
    """Creates vault directory hierarchies safely across platforms."""

    # Windows reserved names
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

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
        """
        try:
            # Resolve to absolute path
            abs_path = vault_path.resolve()

            # Handle Windows long paths (>260 chars)
            if platform.system() == 'Windows' and len(str(abs_path)) > 260:
                # Use extended-length path syntax
                if not str(abs_path).startswith('\\\\?\\'):
                    abs_path = Path(f'\\\\?\\{abs_path}')

            # Check if already exists
            already_existed = abs_path.exists()

            # Create directory with parents, atomic operation
            abs_path.mkdir(parents=True, exist_ok=True, mode=mode)

            # Verify it's actually a directory
            if not abs_path.is_dir():
                raise OSError(f"Path exists but is not a directory: {abs_path}")

            # Get actual permissions (Unix only)
            permissions_set = abs_path.stat().st_mode & 0o777 if platform.system() != 'Windows' else mode

            logger.debug(f"Created/verified directory: {abs_path} (new={not already_existed})")

            return CreationResult(
                path=abs_path,
                created_new=not already_existed,
                already_existed=already_existed,
                permissions_set=permissions_set,
                timestamp=datetime.now(timezone.utc),
                error=None
            )

        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create directory {vault_path}: {e}")
            return CreationResult(
                path=vault_path,
                created_new=False,
                already_existed=False,
                permissions_set=0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )

    def validate_path(self, path: Path) -> tuple[bool, str | None]:
        """
        Validate path for cross-platform compatibility.

        Args:
            path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        path_str = str(path)

        # Check path length (Windows limit)
        if len(path_str) > 260 and platform.system() == 'Windows':
            if not path_str.startswith('\\\\?\\'):
                return False, f"Path exceeds 260 characters (Windows limit): {len(path_str)}"

        # Check each component
        for part in path.parts:
            # Check for reserved names (Windows)
            if part.upper() in self.RESERVED_NAMES:
                return False, f"Contains reserved name: {part}"

            # Check for invalid characters
            if not is_valid_filename(part, platform='universal'):
                return False, f"Contains invalid characters: {part}"

            # Check for leading/trailing spaces or dots (Windows compatibility)
            if part != part.strip('. '):
                return False, f"Name has leading/trailing spaces or dots: {part}"

        return True, None

    def sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name for cross-platform use.

        Args:
            name: Folder name to sanitize

        Returns:
            Sanitized folder name safe for all platforms
        """
        # Use pathvalidate for universal platform compatibility
        sanitized = sanitize_filename(
            name,
            platform='universal',
            replacement_text='_'
        )

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')

        # Handle reserved names by appending suffix
        if sanitized.upper() in self.RESERVED_NAMES:
            sanitized = f"{sanitized}_file"
            logger.warning(f"Sanitized reserved name: {name} → {sanitized}")

        # Ensure non-empty
        if not sanitized:
            sanitized = 'unnamed_folder'

        if sanitized != name:
            logger.info(f"Sanitized folder name: '{name}' → '{sanitized}'")

        return sanitized

    def create_batch(
        self,
        vault_paths: list[Path],
        mode: int = 0o755
    ) -> dict[Path, CreationResult]:
        """
        Create multiple directory hierarchies efficiently.

        Args:
            vault_paths: List of paths to create
            mode: Unix permission mode

        Returns:
            Dictionary mapping paths to creation results
        """
        results = {}

        # Deduplicate paths
        unique_paths = list(set(vault_paths))

        for vault_path in unique_paths:
            results[vault_path] = self.create_hierarchy(vault_path, mode)

        return results
