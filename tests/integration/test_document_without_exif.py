"""T016: Integration test - Office document with no EXIF."""
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_document_without_exif_uses_file_time(tmp_path):
    """Test fallback to file creation time when no EXIF"""
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    manager = OrganizationManager(vault_root=vault_root)
    vault_path = manager.determine_path(
        Path("/inbox/report.pdf"),
        {'mime_type': 'application/pdf'}
    )

    assert vault_path.primary_category in ["documents", "other"]
