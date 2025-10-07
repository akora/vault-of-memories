"""
Contract test for AudioProcessor.process_audio with MP3 files
This test MUST pass for any implementation of the AudioProcessor interface.
"""

import pytest
import tempfile
from pathlib import Path

# Import implementations when available
try:
    from src.services.audio_processor import AudioProcessorImpl
except ImportError:
    AudioProcessorImpl = None

try:
    from src.models.audio_metadata import AudioMetadata
except ImportError:
    from specs.audio_processor.contracts.audio_processor import AudioMetadata


@pytest.mark.contract
class TestAudioProcessorMP3:
    """Contract tests for AudioProcessor with MP3 files."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if AudioProcessorImpl:
            self.processor = AudioProcessorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_mp3_with_full_metadata(self):
        """Test processing MP3 file with complete ID3 tags."""
        # Note: This test requires a real MP3 file with ID3 tags
        # For now, it will be skipped until we have real test fixtures
        pytest.skip("Requires real MP3 test fixture")

        file_path = Path(self.temp_dir) / "test_with_tags.mp3"
        # Would create/copy a real MP3 file here

        result = self.processor.process_audio(file_path)

        assert isinstance(result, AudioMetadata)
        assert result.file_path == file_path
        assert result.format in ["MP3", "MPEG"]
        assert result.duration is not None
        assert result.bitrate is not None
        assert result.sample_rate is not None
        assert result.channels is not None

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_mp3_with_missing_tags(self):
        """Test processing MP3 file with no ID3 tags."""
        pytest.skip("Requires real MP3 test fixture")

        file_path = Path(self.temp_dir) / "test_no_tags.mp3"
        # Would create/copy a real MP3 file without tags

        result = self.processor.process_audio(file_path)

        assert isinstance(result, AudioMetadata)
        assert result.file_path == file_path
        assert result.format in ["MP3", "MPEG"]
        # Technical metadata should still be extracted
        assert result.duration is not None
        assert result.bitrate is not None
        # Tag metadata may be None
        assert result.title is None or isinstance(result.title, str)
        assert result.artist is None or isinstance(result.artist, str)

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_mp3_quality_classification(self):
        """Test quality classification for MP3 files."""
        pytest.skip("Requires real MP3 test fixtures")

        # High quality MP3 (320kbps)
        high_quality_file = Path(self.temp_dir) / "high_quality.mp3"
        # Would create/copy a 320kbps MP3 file

        result = self.processor.process_audio(high_quality_file)

        assert result.compression_type == "lossy"
        assert result.is_lossless is False
        # Quality level depends on bitrate threshold configuration
        assert result.quality_level in ["high", "medium", "low"]

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_mp3_with_id3v2_tags(self):
        """Test processing MP3 with ID3v2 tags."""
        pytest.skip("Requires real MP3 test fixture")

        file_path = Path(self.temp_dir) / "test_id3v2.mp3"
        # Would create/copy MP3 with ID3v2 tags

        result = self.processor.process_audio(file_path)

        assert result.tag_format is not None
        assert "ID3" in result.tag_format or result.tag_format.startswith("ID3v2")

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_nonexistent_mp3_raises_error(self):
        """Test that processing nonexistent file raises FileNotFoundError."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.mp3"

        with pytest.raises(FileNotFoundError):
            self.processor.process_audio(nonexistent_file)

    @pytest.mark.skipif(AudioProcessorImpl is None, reason="Implementation not available")
    def test_process_corrupted_mp3_raises_error(self):
        """Test that processing corrupted MP3 raises RuntimeError."""
        corrupted_file = Path(self.temp_dir) / "corrupted.mp3"
        # Create a file with invalid MP3 data
        corrupted_file.write_bytes(b"This is not a valid MP3 file")

        with pytest.raises((RuntimeError, ValueError)):
            self.processor.process_audio(corrupted_file)
