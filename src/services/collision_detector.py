"""
Collision detector for filename uniqueness.

Ensures filename uniqueness across the vault using 8-digit zero-padded counters.
"""

import logging
from typing import Set, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class CollisionDetector:
    """
    Detect and resolve filename collisions.

    Tracks existing filenames and generates unique names using 8-digit
    zero-padded counters when collisions occur.
    """

    def __init__(self):
        """Initialize collision detector with empty registry."""
        self.registry: Set[str] = set()
        logger.info("CollisionDetector initialized")

    def check_collision(self, filename: str) -> bool:
        """
        Check if filename already exists.

        Args:
            filename: Filename to check (should include extension)

        Returns:
            True if collision detected, False otherwise
        """
        # Normalize to lowercase for case-insensitive comparison
        normalized = filename.lower()
        return normalized in self.registry

    def resolve_collision(self, filename: str) -> str:
        """
        Resolve filename collision by adding counter.

        Generates filenames with pattern: {base}-{counter}.{ext}
        where counter is 8-digit zero-padded (00000001, 00000002, etc.)

        Args:
            filename: Base filename that has collision

        Returns:
            Unique filename with counter appended

        Raises:
            RuntimeError: If collision cannot be resolved (counter overflow)
        """
        # Split filename into base and extension
        path = Path(filename)
        base = path.stem
        ext = path.suffix

        # Try counters from 1 to 99999999
        for counter in range(1, 100000000):
            counter_str = f"{counter:08d}"
            candidate = f"{base}-{counter_str}{ext}"

            if not self.check_collision(candidate):
                logger.info(f"Resolved collision: {filename} → {candidate}")
                return candidate

        raise RuntimeError(f"Could not resolve collision for {filename} (counter overflow)")

    def register_filename(self, filename: str) -> None:
        """
        Register filename to prevent future collisions.

        Args:
            filename: Filename to register (case-insensitive)
        """
        # Normalize to lowercase for case-insensitive registry
        normalized = filename.lower()
        self.registry.add(normalized)
        logger.debug(f"Registered filename: {filename}")

    def clear_registry(self) -> None:
        """Clear the filename registry (useful for testing)."""
        count = len(self.registry)
        self.registry.clear()
        logger.info(f"Cleared {count} filenames from registry")

    def get_registry_size(self) -> int:
        """
        Get the number of registered filenames.

        Returns:
            Count of filenames in registry
        """
        return len(self.registry)

    def load_existing_filenames(self, directory: Path) -> int:
        """
        Load existing filenames from a directory into the registry.

        Args:
            directory: Directory to scan for existing files

        Returns:
            Number of filenames loaded

        Raises:
            ValueError: If directory doesn't exist
        """
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        count = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                self.register_filename(file_path.name)
                count += 1

        logger.info(f"Loaded {count} existing filenames from {directory}")
        return count

    def extract_counter(self, filename: str) -> Optional[int]:
        """
        Extract counter from a filename if present.

        Looks for pattern: {base}-{counter}.{ext} where counter is 8 digits.

        Args:
            filename: Filename to examine

        Returns:
            Counter value if found, None otherwise
        """
        path = Path(filename)
        base = path.stem

        # Look for 8-digit counter at end of base name
        if len(base) >= 9 and base[-9] == '-' and base[-8:].isdigit():
            return int(base[-8:])

        return None
