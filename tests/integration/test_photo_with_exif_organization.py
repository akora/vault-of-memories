"""T015: Integration test for Scenario 1 - Family photo with EXIF organization."""
import pytest
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_family_photo_with_exif_organization(tmp_path):
    """Test complete flow: Photo with EXIF → Classified → Organized"""
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    manager = OrganizationManager(vault_root=vault_root)

    metadata = {
        'datetime_original': '2024:01:15 14:30:22',
        'offset_time_original': '+05:30',
        'mime_type': 'image/x-canon-cr2',
        'make': 'Canon',
        'model': 'EOS R5'
    }

    vault_path = manager.determine_path(Path("/inbox/IMG_2024.CR2"), metadata)

    assert vault_path.primary_category == "photos"
    assert vault_path.subcategory in ["raw", None]
    assert vault_path.year == "2024"
    assert vault_path.day == "2024-01-15"
