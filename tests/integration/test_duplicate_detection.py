"""
Integration test for duplicate detection workflow
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
from src.services.file_ingestor import FileIngestorImpl
from src.models.file_record import ProcessingStatus


@pytest.mark.integration
class TestDuplicateDetection:
    """Integration tests for duplicate detection workflow."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_duplicate_detection_across_directories(self):
        """Test duplicate detection works across different directories."""
        # Create directory structure
        dir1 = Path(self.temp_dir) / "dir1"
        dir2 = Path(self.temp_dir) / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Create identical files in different directories
        content = "Duplicate content for cross-directory test"
        (dir1 / "file1.txt").write_text(content)
        (dir2 / "file2.txt").write_text(content)
        (dir2 / "file3.txt").write_text(content)

        # Process first directory
        results1 = self.ingestor.ingest_directory(dir1)
        assert len(results1) == 1
        assert results1[0].status == ProcessingStatus.PROCESSED

        # Process second directory - should detect duplicates
        results2 = self.ingestor.ingest_directory(dir2)
        assert len(results2) == 2

        # Both files in dir2 should be duplicates
        for result in results2:
            assert result.status == ProcessingStatus.DUPLICATE

        # All should have same checksum
        checksums = {r.checksum for r in results1 + results2}
        assert len(checksums) == 1