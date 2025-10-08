"""T018: Integration test - File with date in filename."""
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_date_parsed_from_filename(tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manager = OrganizationManager(vault_root=vault_root)
    vault_path = manager.determine_path(
        Path("/inbox/scan_2024-01-15_invoice.pdf"),
        {'mime_type': 'application/pdf'}
    )
    # Should parse date from filename
    assert vault_path.day == "2024-01-15"
