"""Contract tests for DateHierarchyBuilder (T013-T014)."""
from pathlib import Path
from datetime import date
from src.services.date_hierarchy_builder import DateHierarchyBuilder

def test_build_path_creates_date_hierarchy(tmp_path):
    """T013: Contract for DateHierarchyBuilder.build_path"""
    builder = DateHierarchyBuilder()
    test_date = date(2024, 1, 15)

    result = builder.build_path(tmp_path, test_date)

    assert "2024" in str(result)
    assert "2024-01" in str(result)
    assert "2024-01-15" in str(result)

def test_get_date_components_returns_formatted_strings():
    """T014: Contract for DateHierarchyBuilder.get_date_components"""
    builder = DateHierarchyBuilder()
    test_date = date(2024, 1, 15)

    year, month, day = builder.get_date_components(test_date)

    assert year == "2024"
    assert month == "2024-01"
    assert day == "2024-01-15"
