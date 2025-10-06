"""
Integration test for directory processing workflow
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
from src.services.file_ingestor import FileIngestorImpl
from src.models.file_record import ProcessingStatus


@pytest.mark.integration
class TestDirectoryProcessing:
    """Integration tests for directory processing workflow."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_directory_workflow(self):
        """Test end-to-end directory processing workflow."""
        # Create test directory structure
        test_dir = Path(self.temp_dir) / "test_directory"
        sub_dir = test_dir / "subdirectory"
        test_dir.mkdir()
        sub_dir.mkdir()

        # Create files at different levels
        (test_dir / "root1.txt").write_text("Root file 1")
        (test_dir / "root2.txt").write_text("Root file 2")
        (sub_dir / "sub1.txt").write_text("Sub file 1")
        (sub_dir / "sub2.txt").write_text("Sub file 2")

        # Add system files that should be filtered
        (test_dir / ".DS_Store").write_text("System file")
        (sub_dir / "Thumbs.db").write_text("Windows metadata")

        # Process directory recursively
        results = self.ingestor.ingest_directory(test_dir, recursive=True)

        # Should process only regular files (4 total)
        assert len(results) == 4
        processed_files = {r.file_path.name for r in results}
        expected_files = {"root1.txt", "root2.txt", "sub1.txt", "sub2.txt"}
        assert processed_files == expected_files

        # All should be processed status
        for result in results:
            assert result.status == ProcessingStatus.PROCESSED

        # Verify stats
        stats = self.ingestor.get_processing_stats()
        assert stats.total_files >= 4
        assert stats.system_files_removed >= 2