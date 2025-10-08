"""T019: Integration test - Batch organization with preview."""
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_batch_preview_no_side_effects(tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manager = OrganizationManager(vault_root=vault_root)

    files = [Path(f"/inbox/file{i}.jpg") for i in range(4)]
    metadata = {f: {'mime_type': 'image/jpeg'} for f in files}

    result = manager.preview_organization(files, metadata)

    assert len(result) == 4
    # Verify no dirs created
    assert list(vault_root.iterdir()) == []
