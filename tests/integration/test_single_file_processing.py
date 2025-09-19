"""
Integration test for single file processing workflow
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
import hashlib
from src.services.file_ingestor import FileIngestorImpl
from src.models.file_record import ProcessingStatus


@pytest.mark.integration
class TestSingleFileProcessing:
    """Integration tests for single file processing workflow."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_end_to_end_single_file_workflow(self):
        """Test complete workflow for processing a single file."""
        # Create test file
        test_file = Path(self.temp_dir) / "integration_test.txt"
        test_content = "Integration test content for single file processing"
        test_file.write_text(test_content)

        # Calculate expected checksum
        expected_checksum = hashlib.sha256(test_content.encode()).hexdigest()

        # Process the file
        result = self.ingestor.ingest_file(test_file)

        # Verify complete workflow
        assert result.file_path == test_file
        assert result.checksum == expected_checksum
        assert result.file_size == len(test_content.encode())
        assert result.status == ProcessingStatus.PROCESSED

        # Verify duplicate detection works
        assert self.ingestor.is_duplicate(expected_checksum)

        # Get processing stats
        stats = self.ingestor.get_processing_stats()
        assert stats.total_files >= 1
        assert stats.processed_files >= 1
        assert stats.duplicate_files == 0
        assert stats.error_files == 0

    def test_duplicate_detection_workflow(self):
        """Test that duplicate files are properly detected and handled."""
        # Create original file
        original_file = Path(self.temp_dir) / "original.txt"
        content = "Content for duplicate detection test"
        original_file.write_text(content)

        # Create duplicate file with same content
        duplicate_file = Path(self.temp_dir) / "duplicate.txt"
        duplicate_file.write_text(content)

        # Process original file first
        result1 = self.ingestor.ingest_file(original_file)
        assert result1.status == ProcessingStatus.PROCESSED

        # Process duplicate file
        result2 = self.ingestor.ingest_file(duplicate_file)
        assert result2.status == ProcessingStatus.DUPLICATE

        # Both should have same checksum
        assert result1.checksum == result2.checksum

        # Stats should reflect duplicate detection
        stats = self.ingestor.get_processing_stats()
        assert stats.duplicate_files >= 1

    def test_system_file_filtering_workflow(self):
        """Test that system files are properly filtered during processing."""
        # Create regular file
        regular_file = Path(self.temp_dir) / "regular.txt"
        regular_file.write_text("Regular file content")

        # Create system files
        ds_store = Path(self.temp_dir) / ".DS_Store"
        ds_store.write_text("macOS metadata")

        thumbs_db = Path(self.temp_dir) / "Thumbs.db"
        thumbs_db.write_text("Windows metadata")

        # Test system file detection
        assert not self.ingestor.is_system_file(regular_file)
        assert self.ingestor.is_system_file(ds_store)
        assert self.ingestor.is_system_file(thumbs_db)

        # Process regular file should work
        result = self.ingestor.ingest_file(regular_file)
        assert result.status == ProcessingStatus.PROCESSED

        # Processing system files should be filtered or handled appropriately
        # (Implementation may skip them or mark them differently)

    def test_error_handling_workflow(self):
        """Test that errors are properly handled and tracked."""
        # Try to process non-existent file
        non_existent = Path(self.temp_dir) / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError):
            self.ingestor.ingest_file(non_existent)

        # Stats should track errors appropriately
        stats = self.ingestor.get_processing_stats()
        # Error count tracking may vary by implementation

    def test_large_file_processing_workflow(self):
        """Test processing of larger files efficiently."""
        # Create larger test file (1MB)
        large_file = Path(self.temp_dir) / "large_file.txt"
        large_content = "Large file content. " * 50000  # ~1MB
        large_file.write_text(large_content)

        # Process large file
        result = self.ingestor.ingest_file(large_file)

        # Should handle large files efficiently
        assert result.status == ProcessingStatus.PROCESSED
        assert result.file_size == len(large_content.encode())
        assert len(result.checksum) == 64

    def test_timestamp_preservation_workflow(self):
        """Test that file timestamps are properly preserved."""
        # Create test file
        test_file = Path(self.temp_dir) / "timestamp_test.txt"
        test_file.write_text("Timestamp preservation test")

        # Get original modification time
        original_mtime = test_file.stat().st_mtime

        # Process file
        result = self.ingestor.ingest_file(test_file)

        # Verify timestamp preservation
        assert abs(result.modification_time - original_mtime) < 1.0  # Within 1 second tolerance
        assert result.created_at > 0  # Should have creation timestamp