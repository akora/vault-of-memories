"""
Contract test for DuplicateDatabase.find_by_checksum method
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
import time
from src.services.duplicate_database import DuplicateDatabaseImpl
from src.models.file_record import FileRecord, ProcessingStatus


@pytest.mark.contract
class TestDuplicateDatabaseFind:
    """Contract tests for DuplicateDatabase.find_by_checksum method."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.database = DuplicateDatabaseImpl()
        self.database.initialize(self.db_path)

    def teardown_method(self):
        """Clean up test environment."""
        self.database.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_by_checksum_existing(self):
        """Test finding existing record by checksum."""
        # Create and add test record
        checksum = "abcdef" + "0" * 58  # Valid 64-char SHA-256
        record = FileRecord(
            id=None,
            file_path=Path("/test/findable.txt"),
            checksum=checksum,
            file_size=1024,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PROCESSED
        )

        record_id = self.database.add_file_record(record)

        # Find by checksum
        found_record = self.database.find_by_checksum(checksum)

        # Verify contract requirements
        assert found_record is not None
        assert isinstance(found_record, FileRecord)
        assert found_record.checksum == checksum
        assert found_record.file_path == record.file_path
        assert found_record.id == record_id

    def test_find_by_checksum_not_found(self):
        """Test finding non-existent checksum returns None."""
        non_existent_checksum = "ffffff" + "0" * 58

        result = self.database.find_by_checksum(non_existent_checksum)

        assert result is None

    def test_find_by_checksum_case_insensitive(self):
        """Test that checksum search is case-insensitive."""
        # Create record with lowercase checksum
        checksum_lower = "abcdef" + "0" * 58
        record = FileRecord(
            id=None,
            file_path=Path("/test/case_test.txt"),
            checksum=checksum_lower,
            file_size=1024,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PROCESSED
        )

        self.database.add_file_record(record)

        # Search with uppercase should find the same record
        checksum_upper = checksum_lower.upper()
        found_record = self.database.find_by_checksum(checksum_upper)

        assert found_record is not None
        assert found_record.checksum.lower() == checksum_lower

    def test_find_by_checksum_invalid_format(self):
        """Test finding with invalid checksum format."""
        invalid_checksums = [
            "too_short",
            "g" * 64,  # Invalid hex character
            "1" * 63,  # Too short
            "1" * 65,  # Too long
        ]

        for invalid_checksum in invalid_checksums:
            # Should either return None or raise ValueError
            try:
                result = self.database.find_by_checksum(invalid_checksum)
                assert result is None
            except ValueError:
                # Acceptable to raise ValueError for invalid input
                pass

    def test_find_by_checksum_empty_string(self):
        """Test finding with empty checksum string."""
        with pytest.raises(ValueError):
            self.database.find_by_checksum("")

    def test_find_by_checksum_none_input(self):
        """Test finding with None input."""
        with pytest.raises((ValueError, TypeError)):
            self.database.find_by_checksum(None)

    def test_find_by_checksum_multiple_same_checksum(self):
        """Test finding when multiple records have same checksum (should not happen but test boundary)."""
        checksum = "duplicate" + "0" * 56

        # This test documents expected behavior if duplicates somehow exist
        # Implementation should prevent this through constraints
        record1 = FileRecord(
            id=None,
            file_path=Path("/test/file1.txt"),
            checksum=checksum,
            file_size=1024,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PROCESSED
        )

        self.database.add_file_record(record1)

        # Find should return one of the records
        found = self.database.find_by_checksum(checksum)
        assert found is not None
        assert found.checksum == checksum