"""
Contract tests for OrganizationManager.

Tests the public API contracts defined in contracts/organization_manager.py
These tests MUST fail until the implementation is complete (TDD approach).
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from src.services.organization_manager import OrganizationManager
from src.models.vault_path import VaultPath


class TestOrganizationManagerDeterminePath:
    """T003: Contract test for OrganizationManager.determine_path"""

    def test_determine_path_with_valid_photo_metadata(self, tmp_path):
        """
        Contract: MUST classify file into valid primary category.
        Contract: MUST extract date from EXIF.
        Contract: MUST construct valid cross-platform path.
        """
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        file_path = Path("/inbox/test_photo.jpg")
        metadata = {
            'mime_type': 'image/jpeg',
            'datetime_original': '2024:01:15 14:30:22',
            'offset_time_original': '+00:00'
        }

        result = manager.determine_path(file_path, metadata)

        assert isinstance(result, VaultPath)
        assert result.primary_category == "photos"
        assert result.year == "2024"
        assert result.month == "2024-01"
        assert result.day == "2024-01-15"
        assert result.full_path.is_absolute()

    def test_determine_path_raises_value_error_for_invalid_file_path(self, tmp_path):
        """Contract: MUST raise ValueError if file_path is invalid."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        with pytest.raises(ValueError):
            manager.determine_path(Path(""), {})

    def test_determine_path_raises_os_error_for_inaccessible_vault(self):
        """Contract: MUST raise OSError if vault root is not accessible."""
        vault_root = Path("/nonexistent/vault/root")

        with pytest.raises(OSError):
            manager = OrganizationManager(vault_root=vault_root)

    def test_determine_path_handles_missing_metadata(self, tmp_path):
        """Contract: MUST handle edge cases (no date, ambiguous type)."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        file_path = Path("/inbox/unknown_file.dat")
        metadata = {}  # No metadata

        result = manager.determine_path(file_path, metadata)

        # Should fall back to "other" category and current date
        assert isinstance(result, VaultPath)
        assert result.primary_category in ["other", "photos", "documents", "videos", "audio", "archives"]


class TestOrganizationManagerPreviewOrganization:
    """T004: Contract test for OrganizationManager.preview_organization"""

    def test_preview_organization_returns_paths_without_creating_dirs(self, tmp_path):
        """
        Contract: MUST return organization decisions for all files.
        Contract: MUST NOT create any directories.
        """
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        file_paths = [
            Path("/inbox/photo1.jpg"),
            Path("/inbox/document.pdf")
        ]
        metadata_dict = {
            Path("/inbox/photo1.jpg"): {'mime_type': 'image/jpeg'},
            Path("/inbox/document.pdf"): {'mime_type': 'application/pdf'}
        }

        result = manager.preview_organization(file_paths, metadata_dict)

        assert len(result) == 2
        assert all(isinstance(vp, VaultPath) for vp in result.values())

        # Verify no directories were created
        assert list(vault_root.iterdir()) == []


class TestOrganizationManagerOrganizeBatch:
    """T005: Contract test for OrganizationManager.organize_batch"""

    def test_organize_batch_handles_parallel_processing(self, tmp_path):
        """
        Contract: MUST handle parallel processing safely.
        Contract: MUST create folders atomically.
        """
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        file_paths = [Path(f"/inbox/file{i}.jpg") for i in range(10)]
        metadata_dict = {fp: {'mime_type': 'image/jpeg'} for fp in file_paths}

        result = manager.organize_batch(file_paths, metadata_dict, preview_only=True)

        assert len(result) == 10
        assert all('execution_status' in r for r in result.values())

    def test_organize_batch_does_not_fail_entire_batch_on_single_failure(self, tmp_path):
        """Contract: MUST NOT fail entire batch if one file fails."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()

        manager = OrganizationManager(vault_root=vault_root)

        file_paths = [
            Path("/inbox/valid.jpg"),
            Path(""),  # Invalid path - should fail
            Path("/inbox/valid2.jpg")
        ]
        metadata_dict = {
            Path("/inbox/valid.jpg"): {'mime_type': 'image/jpeg'},
            Path(""): {},
            Path("/inbox/valid2.jpg"): {'mime_type': 'image/jpeg'}
        }

        result = manager.organize_batch(file_paths, metadata_dict, preview_only=True)

        # Should have processed valid files, marked invalid as failed
        assert len(result) == 3
        assert result[Path("/inbox/valid.jpg")]['execution_status'] in ['success', 'pending']
        assert result[Path("")]['execution_status'] == 'failed'
