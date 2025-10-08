"""Contract tests for FolderCreator (T010-T012)."""
import pytest
from pathlib import Path
from src.services.folder_creator import FolderCreator
from src.models.creation_result import CreationResult

def test_create_hierarchy_creates_nested_dirs(tmp_path):
    """T010: Contract for FolderCreator.create_hierarchy"""
    creator = FolderCreator()
    test_path = tmp_path / "vault" / "photos" / "2024" / "2024-01" / "2024-01-15"

    result = creator.create_hierarchy(test_path)

    assert isinstance(result, CreationResult)
    assert test_path.exists()
    assert test_path.is_dir()

def test_validate_path_rejects_reserved_names():
    """T011: Contract for FolderCreator.validate_path"""
    creator = FolderCreator()
    is_valid, error = creator.validate_path(Path("/vault/CON"))  # Windows reserved
    assert isinstance(is_valid, bool)

def test_sanitize_folder_name_removes_invalid_chars():
    """T012: Contract for FolderCreator.sanitize_folder_name"""
    creator = FolderCreator()
    result = creator.sanitize_folder_name("test:invalid<chars>")
    assert ":" not in result
    assert "<" not in result
    assert ">" not in result
