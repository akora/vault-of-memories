"""
Contract test for FileIngestor.ingest_file method
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
import os
from src.services.file_ingestor import FileIngestorImpl
from src.models.file_record import ProcessingStatus


@pytest.mark.contract
class TestFileIngestorIngestFile:
    """Contract tests for FileIngestor.ingest_file method."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ingest_file_success(self):
        """Test successful ingestion of a single file."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Test file content for ingestion"
        test_file.write_text(test_content)

        # Test ingestion
        result = self.ingestor.ingest_file(test_file)

        # Verify contract requirements
        assert isinstance(result.file_path, Path)
        assert result.file_path == test_file
        assert isinstance(result.checksum, str)
        assert len(result.checksum) == 64  # SHA-256 hex length
        assert result.file_size == len(test_content.encode())
        assert isinstance(result.modification_time, float)
        assert isinstance(result.created_at, float)
        assert result.status in [ProcessingStatus.PROCESSED, ProcessingStatus.DUPLICATE]

    def test_ingest_file_not_found(self):
        """Test ingestion fails for non-existent file."""
        non_existent = Path(self.temp_dir) / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError):
            self.ingestor.ingest_file(non_existent)

    def test_ingest_file_permission_error(self):
        """Test ingestion handles permission denied."""
        # Create file and remove read permissions
        test_file = Path(self.temp_dir) / "no_permission.txt"
        test_file.write_text("test")

        # This test may not work on all systems
        try:
            os.chmod(test_file, 0o000)
            with pytest.raises(PermissionError):
                self.ingestor.ingest_file(test_file)
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_ingest_file_not_regular_file(self):
        """Test ingestion rejects directories."""
        test_dir = Path(self.temp_dir) / "test_directory"
        test_dir.mkdir()

        with pytest.raises(ValueError, match="not a regular file"):
            self.ingestor.ingest_file(test_dir)

    def test_ingest_file_checksum_consistency(self):
        """Test that identical files produce identical checksums."""
        # Create two identical files
        content = "Identical content for checksum test"
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"

        file1.write_text(content)
        file2.write_text(content)

        # Ingest both files
        result1 = self.ingestor.ingest_file(file1)
        result2 = self.ingestor.ingest_file(file2)

        # Checksums should be identical
        assert result1.checksum == result2.checksum