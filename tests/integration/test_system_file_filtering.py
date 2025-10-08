"""
Integration test for system file filtering workflow
This test MUST fail until the implementation is complete.
"""

import pytest
from pathlib import Path
import tempfile
from src.services.file_ingestor import FileIngestorImpl


@pytest.mark.integration
class TestSystemFileFiltering:
    """Integration tests for system file filtering workflow."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = FileIngestorImpl()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_system_file_filtering_comprehensive(self):
        """Test comprehensive system file filtering."""
        test_dir = Path(self.temp_dir) / "filtering_test"
        test_dir.mkdir()

        # Create regular files
        (test_dir / "document.txt").write_text("Regular document")
        (test_dir / "photo.jpg").write_text("Photo data")

        # Create system files that should be filtered
        system_files = [
            ".DS_Store",      # macOS
            "Thumbs.db",      # Windows
            "desktop.ini",    # Windows
            ".hidden_file",   # Unix hidden
            "temp.tmp",       # Temporary
        ]

        for sys_file in system_files:
            (test_dir / sys_file).write_text("System file content")

        # Test individual system file detection
        for sys_file in system_files:
            assert self.ingestor.is_system_file(test_dir / sys_file)

        # Regular files should not be system files
        assert not self.ingestor.is_system_file(test_dir / "document.txt")
        assert not self.ingestor.is_system_file(test_dir / "photo.jpg")

        # Process directory - should only include regular files
        results = self.ingestor.ingest_directory(test_dir)
        assert len(results) == 2

        processed_names = {r.file_path.name for r in results}
        assert processed_names == {"document.txt", "photo.jpg"}

        # Stats should reflect system files removed
        stats = self.ingestor.get_processing_stats()
        assert stats.system_files_removed >= len(system_files)