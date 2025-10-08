"""
Contract: OrganizationManager

Main orchestrator for file organization decisions.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VaultPath:
    """Target path in vault structure."""
    base_path: Path
    primary_category: str
    subcategory: str | None
    year: str
    month: str
    day: str
    full_path: Path


class OrganizationManager:
    """
    Determines final file placement in vault structure.

    Responsibilities:
    - Coordinate classification and date extraction
    - Construct target vault path
    - Apply organization rules and fallbacks
    - Return organization decision with audit trail
    """

    def determine_path(self, file_path: Path, metadata: Dict[str, Any]) -> VaultPath:
        """
        Determine target vault path for a file.

        Args:
            file_path: Source file path
            metadata: Consolidated metadata from MetadataConsolidator

        Returns:
            VaultPath with complete target path information

        Raises:
            ValueError: If file_path is invalid or metadata is missing required fields
            OSError: If vault root is not accessible

        Contract:
            - MUST classify file into valid primary category
            - MUST extract date from available sources (EXIF, filesystem, filename)
            - MUST construct valid cross-platform path
            - MUST handle edge cases (no date, ambiguous type, etc.)
            - MUST log decision reasoning for audit
            - Path MUST be safe for Windows, macOS, Linux
            - Path length MUST not exceed platform limits
        """
        raise NotImplementedError

    def preview_organization(
        self,
        file_paths: list[Path],
        metadata_dict: Dict[Path, Dict[str, Any]]
    ) -> Dict[Path, VaultPath]:
        """
        Preview organization decisions without executing.

        Args:
            file_paths: List of files to preview
            metadata_dict: Metadata for each file

        Returns:
            Dictionary mapping file paths to proposed vault paths

        Contract:
            - MUST NOT create any directories
            - MUST NOT move any files
            - MUST return organization decisions for all files
            - MUST handle batch processing efficiently
        """
        raise NotImplementedError

    def organize_batch(
        self,
        file_paths: list[Path],
        metadata_dict: Dict[Path, Dict[str, Any]],
        preview_only: bool = False
    ) -> Dict[Path, dict]:
        """
        Organize multiple files with parallel-safe operations.

        Args:
            file_paths: Files to organize
            metadata_dict: Metadata for each file
            preview_only: If True, preview without executing

        Returns:
            Dictionary mapping file paths to organization results

        Contract:
            - MUST handle parallel processing safely
            - MUST create folders atomically (no race conditions)
            - MUST maintain consistent folder structure
            - MUST log all decisions
            - MUST NOT fail entire batch if one file fails
            - Individual file failures MUST be reported in results
        """
        raise NotImplementedError
