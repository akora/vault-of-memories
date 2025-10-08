"""T017: Integration test - Video with unclear classification."""
from pathlib import Path
from src.services.organization_manager import OrganizationManager

def test_video_classification_fallback(tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manager = OrganizationManager(vault_root=vault_root)
    vault_path = manager.determine_path(
        Path("/inbox/video.mp4"),
        {'mime_type': 'video/mp4', 'bitrate': 3500000}
    )
    assert vault_path.primary_category in ["videos", "other"]
