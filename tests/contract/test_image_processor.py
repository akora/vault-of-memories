"""
Contract tests for Image Processor
These tests MUST pass for any implementation of the image processor interfaces.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Import implementations when available
try:
    from src.services.image_processor import ImageProcessorImpl
except ImportError:
    ImageProcessorImpl = None

try:
    from src.services.image_classifier import ImageClassifierImpl
except ImportError:
    ImageClassifierImpl = None

try:
    from src.services.timestamp_extractor import TimestampExtractorImpl
except ImportError:
    TimestampExtractorImpl = None

from src.models.image_metadata import (
    ImageMetadata, ImageType, ImageFormat, ConfidenceLevel,
    CameraInfo, ImageDimensions, TimestampCollection
)


@pytest.mark.contract
class TestImageProcessor:
    """Contract tests for ImageProcessor interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if ImageProcessorImpl:
            self.processor = ImageProcessorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image(self, filename: str, image_type: str = "jpeg") -> Path:
        """Create a simple test image file."""
        file_path = Path(self.temp_dir) / filename

        if image_type == "jpeg":
            # Create minimal valid JPEG with EXIF
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(file_path, 'JPEG')
        elif image_type == "png":
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(file_path, 'PNG')

        return file_path

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_process_image_jpeg(self):
        """Test processing a JPEG image."""
        file_path = self.create_test_image("test.jpg", "jpeg")

        result = self.processor.process_image(file_path)

        assert isinstance(result, ImageMetadata)
        assert result.file_path == file_path
        assert result.mime_type in ["image/jpeg", "image/jpg"]
        assert result.file_size > 0
        assert result.dimensions.width == 100
        assert result.dimensions.height == 100
        assert result.is_successful()

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_process_image_png(self):
        """Test processing a PNG image."""
        file_path = self.create_test_image("test.png", "png")

        result = self.processor.process_image(file_path)

        assert isinstance(result, ImageMetadata)
        assert result.mime_type == "image/png"
        assert result.dimensions.width == 100
        assert result.dimensions.height == 100

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_process_image_nonexistent(self):
        """Test processing fails for nonexistent file."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.jpg"

        with pytest.raises(FileNotFoundError):
            self.processor.process_image(nonexistent_path)

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.processor.get_supported_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        # Should support common formats
        assert "jpg" in formats or "jpeg" in formats
        assert "png" in formats
        # Should support RAW formats
        assert any(fmt in formats for fmt in ["cr2", "nef", "arw", "dng"])

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_is_exiftool_available(self):
        """Test checking if exiftool is available."""
        available = self.processor.is_exiftool_available()

        # For these tests, exiftool should be available
        assert available is True

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_get_exiftool_version(self):
        """Test getting exiftool version."""
        version = self.processor.get_exiftool_version()

        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_extract_dimensions(self):
        """Test extracting image dimensions."""
        file_path = self.create_test_image("dimensions.jpg", "jpeg")

        result = self.processor.process_image(file_path)

        assert result.dimensions.width == 100
        assert result.dimensions.height == 100
        assert result.dimensions.megapixels == 0.01  # 100x100 = 10,000 pixels
        assert result.dimensions.aspect_ratio() == "1:1"

    @pytest.mark.skipif(ImageProcessorImpl is None, reason="Implementation not available")
    def test_processing_time_recorded(self):
        """Test that processing time is recorded."""
        file_path = self.create_test_image("timing.jpg", "jpeg")

        result = self.processor.process_image(file_path)

        assert result.processing_time_ms >= 0
        assert result.processing_time_ms < 10000  # Should be under 10 seconds


@pytest.mark.contract
class TestImageClassifier:
    """Contract tests for ImageClassifier interface."""

    def setup_method(self):
        """Set up test environment."""
        if ImageClassifierImpl:
            self.classifier = ImageClassifierImpl()

    def create_metadata(
        self,
        file_extension: str = "jpg",
        has_camera_info: bool = False
    ) -> ImageMetadata:
        """Create test metadata."""
        metadata = ImageMetadata(
            file_path=Path(f"/test/image.{file_extension}"),
            file_name=f"image.{file_extension}",
            file_size=1000,
            mime_type="image/jpeg",
            file_extension=file_extension
        )

        if has_camera_info:
            metadata.camera = CameraInfo(
                make="Canon",
                model="EOS 5D Mark IV",
                iso=400,
                aperture=2.8,
                shutter_speed="1/250"
            )

        return metadata

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_classify_camera_photo(self):
        """Test classifying camera photo with EXIF."""
        metadata = self.create_metadata(has_camera_info=True)

        result = self.classifier.classify_image(metadata)

        assert result.classification.image_type == ImageType.CAMERA_PHOTO
        assert result.classification.type_confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_classify_graphic_no_camera_info(self):
        """Test classifying graphic without camera info."""
        metadata = self.create_metadata(has_camera_info=False)

        result = self.classifier.classify_image(metadata)

        assert result.classification.image_type in [ImageType.GRAPHIC, ImageType.UNKNOWN]

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_is_camera_photo(self):
        """Test camera photo detection."""
        metadata = self.create_metadata(has_camera_info=True)

        is_photo = self.classifier.is_camera_photo(metadata)

        assert is_photo is True

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_is_raw_format(self):
        """Test RAW format detection."""
        # RAW formats
        assert self.classifier.is_raw_format("cr2") is True
        assert self.classifier.is_raw_format("nef") is True
        assert self.classifier.is_raw_format("arw") is True
        assert self.classifier.is_raw_format("dng") is True

        # Processed formats
        assert self.classifier.is_raw_format("jpg") is False
        assert self.classifier.is_raw_format("png") is False

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_classify_raw_format(self):
        """Test classifying RAW format image."""
        metadata = self.create_metadata(file_extension="cr2", has_camera_info=True)

        result = self.classifier.classify_image(metadata)

        assert result.classification.image_format == ImageFormat.RAW

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_classify_processed_format(self):
        """Test classifying processed format image."""
        metadata = self.create_metadata(file_extension="jpg", has_camera_info=True)

        result = self.classifier.classify_image(metadata)

        assert result.classification.image_format == ImageFormat.PROCESSED

    @pytest.mark.skipif(ImageClassifierImpl is None, reason="Implementation not available")
    def test_get_raw_extensions(self):
        """Test getting RAW extensions."""
        extensions = self.classifier.get_raw_extensions()

        assert isinstance(extensions, list)
        assert "cr2" in extensions  # Canon
        assert "nef" in extensions  # Nikon
        assert "arw" in extensions  # Sony
        assert "dng" in extensions  # Adobe


@pytest.mark.contract
class TestTimestampExtractor:
    """Contract tests for TimestampExtractor interface."""

    def setup_method(self):
        """Set up test environment."""
        if TimestampExtractorImpl:
            self.extractor = TimestampExtractorImpl()

    @pytest.mark.skipif(TimestampExtractorImpl is None, reason="Implementation not available")
    def test_extract_timestamps_from_exif(self):
        """Test extracting timestamps from EXIF data."""
        raw_exif = {
            "EXIF:DateTimeOriginal": "2023:12:25 14:30:22",
            "EXIF:CreateDate": "2023:12:25 14:30:22",
            "File:FileModifyDate": "2024:01:01 10:00:00"
        }

        result = self.extractor.extract_timestamps(raw_exif)

        assert isinstance(result, TimestampCollection)
        assert result.date_time_original is not None
        assert result.create_date is not None
        assert result.file_modify_date is not None

    @pytest.mark.skipif(TimestampExtractorImpl is None, reason="Implementation not available")
    def test_parse_exif_datetime(self):
        """Test parsing EXIF datetime strings."""
        # Standard EXIF format
        dt = self.extractor.parse_exif_datetime("2023:12:25 14:30:22")

        assert dt is not None
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 25

    @pytest.mark.skipif(TimestampExtractorImpl is None, reason="Implementation not available")
    def test_timestamp_priority_order(self):
        """Test timestamp priority order."""
        priority = self.extractor.get_timestamp_priority_order()

        assert isinstance(priority, list)
        assert len(priority) > 0
        # DateTimeOriginal should be first
        assert priority[0] in ["DateTimeOriginal", "EXIF:DateTimeOriginal"]

    @pytest.mark.skipif(TimestampExtractorImpl is None, reason="Implementation not available")
    def test_get_best_timestamp(self):
        """Test getting best timestamp from collection."""
        timestamps = TimestampCollection(
            date_time_original=datetime(2023, 12, 25, 14, 30, 22),
            create_date=datetime(2023, 12, 25, 14, 35, 00),
            file_modify_date=datetime(2024, 1, 1, 10, 0, 0)
        )

        best = timestamps.get_best_timestamp()

        assert best == datetime(2023, 12, 25, 14, 30, 22)  # DateTimeOriginal
        assert timestamps.get_timestamp_source() == "EXIF:DateTimeOriginal"

    @pytest.mark.skipif(TimestampExtractorImpl is None, reason="Implementation not available")
    def test_fallback_to_file_timestamp(self):
        """Test fallback to file timestamp when no EXIF."""
        timestamps = TimestampCollection(
            file_modify_date=datetime(2024, 1, 1, 10, 0, 0)
        )

        best = timestamps.get_best_timestamp()

        assert best == datetime(2024, 1, 1, 10, 0, 0)
        assert timestamps.get_timestamp_source() == "FileSystem:ModifyDate"
