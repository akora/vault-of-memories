"""T020: Integration test - Parallel batch organization."""
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_parallel_batch_processing(tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manager = OrganizationManager(vault_root=vault_root)

    files = [Path(f"/inbox/file{i}.jpg") for i in range(20)]
    metadata = {f: {'mime_type': 'image/jpeg'} for f in files}

    result = manager.organize_batch(files, metadata, preview_only=True)

    assert len(result) == 20
