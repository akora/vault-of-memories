"""
Contract test for FileIngestor.ingest_directory method
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
from src.services.file_ingestor import FileIngestorImpl
from src.models.file_record import ProcessingStatus


@pytest.mark.contract
class TestFileIngestorIngestDirectory:
    """Contract tests for FileIngestor.ingest_directory method."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ingest_directory_flat(self):
        """Test ingestion of flat directory structure."""
        test_dir = Path(self.temp_dir) / "flat_test"
        test_dir.mkdir()

        # Create test files
        (test_dir / "file1.txt").write_text("Content 1")
        (test_dir / "file2.txt").write_text("Content 2")
        (test_dir / "file3.txt").write_text("Content 3")

        # Test ingestion
        results = self.ingestor.ingest_directory(test_dir, recursive=False)

        # Verify contract requirements
        assert len(results) == 3
        for result in results:
            assert isinstance(result.file_path, Path)
            assert result.file_path.parent == test_dir
            assert len(result.checksum) == 64
            assert result.file_size > 0
            assert result.status in [ProcessingStatus.PROCESSED, ProcessingStatus.DUPLICATE]

    def test_ingest_directory_recursive(self):
        """Test recursive ingestion of nested directory structure."""
        test_dir = Path(self.temp_dir) / "nested_test"
        sub_dir = test_dir / "subdir"
        sub_sub_dir = sub_dir / "subsubdir"

        # Create nested structure
        test_dir.mkdir()
        sub_dir.mkdir()
        sub_sub_dir.mkdir()

        # Create files at different levels
        (test_dir / "root.txt").write_text("Root file")
        (sub_dir / "sub.txt").write_text("Sub file")
        (sub_sub_dir / "deep.txt").write_text("Deep file")

        # Test recursive ingestion
        results = self.ingestor.ingest_directory(test_dir, recursive=True)

        # Should find all 3 files
        assert len(results) == 3
        file_names = {r.file_path.name for r in results}
        assert file_names == {"root.txt", "sub.txt", "deep.txt"}

    def test_ingest_directory_non_recursive(self):
        """Test non-recursive ingestion ignores subdirectories."""
        test_dir = Path(self.temp_dir) / "non_recursive_test"
        sub_dir = test_dir / "subdir"

        # Create nested structure
        test_dir.mkdir()
        sub_dir.mkdir()

        # Create files at different levels
        (test_dir / "root.txt").write_text("Root file")
        (sub_dir / "sub.txt").write_text("Sub file")

        # Test non-recursive ingestion
        results = self.ingestor.ingest_directory(test_dir, recursive=False)

        # Should find only root file
        assert len(results) == 1
        assert results[0].file_path.name == "root.txt"

    def test_ingest_directory_not_found(self):
        """Test ingestion fails for non-existent directory."""
        non_existent = Path(self.temp_dir) / "does_not_exist"

        with pytest.raises(FileNotFoundError):
            self.ingestor.ingest_directory(non_existent)

    def test_ingest_directory_empty(self):
        """Test ingestion of empty directory."""
        empty_dir = Path(self.temp_dir) / "empty"
        empty_dir.mkdir()

        results = self.ingestor.ingest_directory(empty_dir)

        assert len(results) == 0
        assert isinstance(results, list)

    def test_ingest_directory_filters_system_files(self):
        """Test that system files are filtered out."""
        test_dir = Path(self.temp_dir) / "system_files_test"
        test_dir.mkdir()

        # Create regular and system files
        (test_dir / "regular.txt").write_text("Regular file")
        (test_dir / ".DS_Store").write_text("macOS metadata")
        (test_dir / "Thumbs.db").write_text("Windows metadata")

        results = self.ingestor.ingest_directory(test_dir)

        # Should only process regular file
        assert len(results) == 1
        assert results[0].file_path.name == "regular.txt"