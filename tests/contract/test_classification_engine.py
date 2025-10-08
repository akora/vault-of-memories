"""
Contract tests for ClassificationEngine (T006-T007).
"""

import pytest
from pathlib import Path
from src.services.classification_engine import ClassificationEngine
from src.models.classification import Classification


def test_classify_returns_valid_classification():
    """T006: Contract test for ClassificationEngine.classify"""
    engine = ClassificationEngine()
    file_path = Path("/test/photo.jpg")
    metadata = {'mime_type': 'image/jpeg'}

    result = engine.classify(file_path, metadata)

    assert isinstance(result, Classification)
    assert result.primary_category in ["photos", "documents", "videos", "audio", "archives", "other"]
    assert 0.0 <= result.confidence <= 1.0


def test_classify_batch_processes_multiple_files():
    """T007: Contract test for ClassificationEngine.classify_batch"""
    engine = ClassificationEngine()
    file_paths = [Path(f"/test/file{i}.jpg") for i in range(5)]
    metadata_dict = {fp: {'mime_type': 'image/jpeg'} for fp in file_paths}

    result = engine.classify_batch(file_paths, metadata_dict)

    assert len(result) == 5
    assert all(isinstance(c, Classification) for c in result.values())
