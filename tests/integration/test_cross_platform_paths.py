"""T021: Integration test - Cross-platform path validation."""
from pathlib import Path
from src.services.folder_creator import FolderCreator

def test_cross_platform_path_sanitization(tmp_path):
    creator = FolderCreator()

    # Test Windows reserved name
    sanitized = creator.sanitize_folder_name("CON")
    assert sanitized != "CON"

    # Test invalid characters
    sanitized = creator.sanitize_folder_name("file:with:colons")
    assert ":" not in sanitized
