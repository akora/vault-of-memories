"""
T036: OrganizationManager - Main orchestration logic for file organization.
"""

from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import logging
from ..models.vault_path import VaultPath
from ..models.organization_decision import OrganizationDecision
from .classification_engine import ClassificationEngine
from .date_extractor import DateExtractor
from .date_hierarchy_builder import DateHierarchyBuilder
from .folder_creator import FolderCreator


logger = logging.getLogger(__name__)


class OrganizationManager:
    """
    Determines final file placement in vault structure.

    Orchestrates:
    - Classification (via ClassificationEngine)
    - Date extraction (via DateExtractor)
    - Path construction (via DateHierarchyBuilder)
    - Folder creation (via FolderCreator)
    """

    def __init__(self, vault_root: Path):
        """
        Initialize OrganizationManager.

        Args:
            vault_root: Root directory of the vault

        Raises:
            OSError: If vault_root is not accessible
        """
        if not vault_root.is_absolute():
            vault_root = vault_root.resolve()

        # Create vault root if it doesn't exist
        vault_root.mkdir(parents=True, exist_ok=True)

        if not vault_root.is_dir():
            raise OSError(f"Vault root is not a directory: {vault_root}")

        self.vault_root = vault_root
        self.classification_engine = ClassificationEngine()
        self.date_extractor = DateExtractor()
        self.date_hierarchy_builder = DateHierarchyBuilder()
        self.folder_creator = FolderCreator()

        logger.info(f"OrganizationManager initialized with vault_root: {vault_root}")

    def determine_path(self, file_path: Path, metadata: dict[str, Any]) -> VaultPath:
        """
        Determine target vault path for a file.

        Args:
            file_path: Source file path
            metadata: Consolidated metadata

        Returns:
            VaultPath with complete target path information

        Raises:
            ValueError: If file_path is invalid or metadata is missing required fields
        """
        if not file_path or str(file_path) == "":
            raise ValueError("file_path cannot be empty")

        # Classify file
        classification = self.classification_engine.classify(file_path, metadata)

        # Extract date
        date_info = self.date_extractor.extract_date(file_path, metadata)

        # Build base path: vault_root/category/[subcategory]
        base_path = self.vault_root / classification.primary_category
        if classification.subcategory:
            base_path = base_path / classification.subcategory

        # Build date hierarchy
        full_path = self.date_hierarchy_builder.build_path(base_path, date_info.original_local_date)

        # Get date components
        year, month, day = self.date_hierarchy_builder.get_date_components(date_info.original_local_date)

        vault_path = VaultPath(
            base_path=self.vault_root,
            primary_category=classification.primary_category,
            subcategory=classification.subcategory,
            year=year,
            month=month,
            day=day,
            full_path=full_path
        )

        logger.info(f"Determined path for {file_path}: {vault_path.full_path}")
        return vault_path

    def preview_organization(
        self,
        file_paths: list[Path],
        metadata_dict: dict[Path, dict[str, Any]]
    ) -> dict[Path, VaultPath]:
        """
        Preview organization decisions without executing.

        Args:
            file_paths: List of files to preview
            metadata_dict: Metadata for each file

        Returns:
            Dictionary mapping file paths to proposed vault paths
        """
        results = {}

        for file_path in file_paths:
            metadata = metadata_dict.get(file_path, {})
            try:
                vault_path = self.determine_path(file_path, metadata)
                results[file_path] = vault_path
            except Exception as e:
                logger.error(f"Failed to determine path for {file_path}: {e}")
                # Return a default vault path for failed files
                results[file_path] = VaultPath(
                    base_path=self.vault_root,
                    primary_category='other',
                    subcategory=None,
                    year='0000',
                    month='0000-00',
                    day='0000-00-00',
                    full_path=self.vault_root / 'other'
                )

        logger.info(f"Preview completed for {len(file_paths)} files")
        return results

    def organize_batch(
        self,
        file_paths: list[Path],
        metadata_dict: dict[Path, dict[str, Any]],
        preview_only: bool = False
    ) -> dict[Path, dict]:
        """
        Organize multiple files with parallel-safe operations.

        Args:
            file_paths: Files to organize
            metadata_dict: Metadata for each file
            preview_only: If True, preview without executing

        Returns:
            Dictionary mapping file paths to organization results
        """
        results = {}

        for file_path in file_paths:
            metadata = metadata_dict.get(file_path, {})

            try:
                # Determine path
                vault_path = self.determine_path(file_path, metadata)

                # Get classification and date info for audit
                classification = self.classification_engine.classify(file_path, metadata)
                date_info = self.date_extractor.extract_date(file_path, metadata)

                # Create folders if not preview mode
                if not preview_only:
                    creation_result = self.folder_creator.create_hierarchy(vault_path.full_path)
                    if creation_result.error:
                        execution_status = 'failed'
                        error_message = creation_result.error
                    else:
                        execution_status = 'success'
                        error_message = None
                else:
                    execution_status = 'pending'
                    error_message = None

                # Create organization decision
                decision = OrganizationDecision(
                    file_path=file_path,
                    vault_path=vault_path,
                    classification=classification,
                    date_info=date_info,
                    decision_timestamp=datetime.now(timezone.utc),
                    preview_mode=preview_only,
                    execution_status=execution_status,
                    error_message=error_message
                )

                results[file_path] = {
                    'vault_path': vault_path,
                    'execution_status': execution_status,
                    'error_message': error_message,
                    'classification': classification.primary_category,
                    'confidence': classification.confidence
                }

            except Exception as e:
                logger.error(f"Failed to organize {file_path}: {e}")
                results[file_path] = {
                    'execution_status': 'failed',
                    'error_message': str(e)
                }

        logger.info(f"Batch organization completed: {len(results)} files processed")
        return results
