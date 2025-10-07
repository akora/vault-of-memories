"""
Contract test for FileIngestor.is_duplicate method
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
import hashlib
from src.services.file_ingestor import FileIngestorImpl


@pytest.mark.contract
class TestFileIngestorIsDuplicate:
    """Contract tests for FileIngestor.is_duplicate method."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_duplicate_false_for_new_checksum(self):
        """Test that new checksums are not considered duplicates."""
        # Create a unique checksum
        test_content = "Unique content for duplicate test"
        checksum = hashlib.sha256(test_content.encode()).hexdigest()

        # Should not be duplicate initially
        assert not self.ingestor.is_duplicate(checksum)

    def test_is_duplicate_true_after_ingestion(self):
        """Test that checksum becomes duplicate after file ingestion."""
        # Create and ingest a file
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Content for duplicate detection test"
        test_file.write_text(test_content)

        # Ingest the file
        result = self.ingestor.ingest_file(test_file)

        # Now the checksum should be considered duplicate
        assert self.ingestor.is_duplicate(result.checksum)

    def test_is_duplicate_with_invalid_checksum(self):
        """Test behavior with invalid checksum format."""
        invalid_checksums = [
            "not_a_hash",
            "too_short",
            "g" * 64,  # Invalid hex character
            "1" * 63,  # Too short
            "1" * 65,  # Too long
        ]

        for invalid_checksum in invalid_checksums:
            # Should handle gracefully (return False or raise ValueError)
            try:
                result = self.ingestor.is_duplicate(invalid_checksum)
                assert isinstance(result, bool)
            except ValueError:
                # Acceptable to raise ValueError for invalid input
                pass

    def test_is_duplicate_empty_string(self):
        """Test behavior with empty checksum."""
        with pytest.raises(ValueError):
            self.ingestor.is_duplicate("")

    def test_is_duplicate_none_input(self):
        """Test behavior with None input."""
        with pytest.raises((ValueError, TypeError)):
            self.ingestor.is_duplicate(None)

    def test_is_duplicate_case_sensitivity(self):
        """Test that checksum comparison is case-insensitive."""
        # Create and ingest a file
        test_file = Path(self.temp_dir) / "case_test.txt"
        test_file.write_text("Case sensitivity test")

        result = self.ingestor.ingest_file(test_file)
        original_checksum = result.checksum

        # Test different cases
        assert self.ingestor.is_duplicate(original_checksum.upper())
        assert self.ingestor.is_duplicate(original_checksum.lower())
        assert self.ingestor.is_duplicate(original_checksum)