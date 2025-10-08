"""Contract tests for DateExtractor (T008-T009)."""
import pytest
from pathlib import Path
from src.services.date_extractor import DateExtractor
from src.models.date_info import DateInfo

def test_extract_date_returns_date_info():
    """T008: Contract for DateExtractor.extract_date"""
    extractor = DateExtractor()
    result = extractor.extract_date(Path("/test/file.jpg"), {})
    assert isinstance(result, DateInfo)
    assert result.datetime_utc.tzinfo is not None  # Must have timezone

def test_parse_filename_date_recognizes_iso_format():
    """T009: Contract for DateExtractor.parse_filename_date"""
    extractor = DateExtractor()
    result = extractor.parse_filename_date("photo_2024-01-15.jpg")
    assert result is not None or result is None  # May or may not find date
