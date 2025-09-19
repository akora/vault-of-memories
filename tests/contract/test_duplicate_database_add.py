"""
Contract test for DuplicateDatabase.add_file_record method
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
import time
from src.services.duplicate_database import DuplicateDatabaseImpl
from src.models.file_record import FileRecord, ProcessingStatus


@pytest.mark.contract
class TestDuplicateDatabaseAdd:
    """Contract tests for DuplicateDatabase.add_file_record method."""

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

    def test_add_file_record_success(self):
        """Test successful addition of file record."""
        # Create test record
        record = FileRecord(
            id=None,
            file_path=Path("/test/file.txt"),
            checksum="a" * 64,  # Valid SHA-256 hex
            file_size=1024,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PENDING
        )

        # Add record
        record_id = self.database.add_file_record(record)

        # Verify contract requirements
        assert isinstance(record_id, int)
        assert record_id > 0

    def test_add_file_record_returns_unique_ids(self):
        """Test that each record gets a unique ID."""
        records = []
        for i in range(3):
            record = FileRecord(
                id=None,
                file_path=Path(f"/test/file{i}.txt"),
                checksum=f"{'a' * 63}{i}",  # Unique checksums
                file_size=1024,
                modification_time=time.time(),
                created_at=time.time(),
                status=ProcessingStatus.PENDING
            )
            records.append(record)

        # Add all records
        ids = [self.database.add_file_record(record) for record in records]

        # All IDs should be unique
        assert len(set(ids)) == len(ids)

    def test_add_file_record_invalid_data(self):
        """Test adding record with invalid data raises ValueError."""
        invalid_records = [
            # Invalid checksum (too short)
            FileRecord(None, Path("/test.txt"), "abc", 100, time.time(), time.time(), ProcessingStatus.PENDING),
            # Invalid file size (negative)
            FileRecord(None, Path("/test.txt"), "a" * 64, -1, time.time(), time.time(), ProcessingStatus.PENDING),
            # Invalid timestamps
            FileRecord(None, Path("/test.txt"), "a" * 64, 100, -1, time.time(), ProcessingStatus.PENDING),
        ]

        for invalid_record in invalid_records:
            with pytest.raises(ValueError):
                self.database.add_file_record(invalid_record)

    def test_add_file_record_duplicate_path(self):
        """Test adding record with duplicate file path."""
        # Create first record
        record1 = FileRecord(
            id=None,
            file_path=Path("/test/duplicate_path.txt"),
            checksum="a" * 64,
            file_size=1024,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PENDING
        )

        # Add first record successfully
        self.database.add_file_record(record1)

        # Create second record with same path but different checksum
        record2 = FileRecord(
            id=None,
            file_path=Path("/test/duplicate_path.txt"),
            checksum="b" * 64,
            file_size=2048,
            modification_time=time.time(),
            created_at=time.time(),
            status=ProcessingStatus.PENDING
        )

        # Should fail due to unique constraint on file_path
        with pytest.raises(Exception):  # Could be DatabaseError or IntegrityError
            self.database.add_file_record(record2)

    def test_add_file_record_with_none_record(self):
        """Test adding None record raises appropriate error."""
        with pytest.raises((ValueError, TypeError)):
            self.database.add_file_record(None)