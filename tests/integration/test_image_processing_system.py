"""
Integration tests for the complete image processing system.
Tests the interaction between all image processing components.
"""

import pytest
import tempfile
import time
from pathlib import Path
from PIL import Image, ExifTags
from datetime import datetime

from src.services.image_processor import ImageProcessorImpl
from src.services.image_classifier import ImageClassifierImpl
from src.services.timestamp_extractor import TimestampExtractorImpl
from src.models.image_metadata import (
    ImageType, ImageFormat, ConfidenceLevel
)


@pytest.mark.integration
class TestImageProcessingSystemIntegration:
    """Integration tests for complete image processing workflows."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = ImageProcessorImpl()
        self.classifier = ImageClassifierImpl()
        self.timestamp_extractor = TimestampExtractorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image_with_exif(
        self,
        filename: str,
        add_camera_info: bool = False,
        width: int = 800,
        height: int = 600
    ) -> Path:
        """Create a test image with optional EXIF data."""
        file_path = Path(self.temp_dir) / filename

        # Create image
        img = Image.new('RGB', (width, height), color='red')

        # Add EXIF data if requested
        if add_camera_info:
            from PIL.ExifTags import TAGS
            exif_dict = {
                "Make": "Canon",
                "Model": "EOS 5D Mark IV",
                "DateTime": "2023:12:25 14:30:22",
                "DateTimeOriginal": "2023:12:25 14:30:22",
            }

            # Convert tag names to tag IDs
            exif_data = {}
            for tag_name, value in exif_dict.items():
                tag_id = next((k for k, v in TAGS.items() if v == tag_name), None)
                if tag_id:
                    exif_data[tag_id] = value

            # Save with EXIF
            from PIL import Image as PILImage
            exif = img.getexif()
            for tag_id, value in exif_data.items():
                exif[tag_id] = value

            img.save(file_path, 'JPEG', exif=exif)
        else:
            img.save(file_path, 'JPEG')

        return file_path

    def test_complete_jpeg_processing_workflow(self):
        """Test complete processing workflow for JPEG with camera data."""
        file_path = self.create_test_image_with_exif(
            "camera_photo.jpg",
            add_camera_info=True,
            width=1920,
            height=1080
        )

        # Process image
        metadata = self.processor.process_image(file_path)

        # Verify file information
        assert metadata.file_path == file_path
        assert metadata.mime_type == "image/jpeg"
        assert metadata.file_size > 0

        # Verify dimensions
        assert metadata.dimensions.width == 1920
        assert metadata.dimensions.height == 1080
        assert metadata.dimensions.megapixels == 2.07  # 1920x1080 ≈ 2.07MP

        # Verify camera information
        assert metadata.camera.make == "Canon"
        assert metadata.camera.model == "EOS 5D Mark IV"

        # Verify classification
        assert metadata.classification.image_type == ImageType.CAMERA_PHOTO
        assert metadata.classification.image_format == ImageFormat.PROCESSED
        assert metadata.classification.type_confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]

        # Verify processing metadata
        assert metadata.is_successful()
        assert metadata.processing_time_ms > 0
        assert metadata.exiftool_version is not None

    def test_graphic_classification_workflow(self):
        """Test classification of graphics without camera info."""
        # Create PNG directly
        png_path = Path(self.temp_dir) / "screenshot.png"
        img = Image.new('RGB', (1280, 720), color='blue')
        img.save(png_path, 'PNG')

        # Process image
        metadata = self.processor.process_image(png_path)

        # Should be classified as graphic
        assert metadata.classification.image_type in [ImageType.GRAPHIC, ImageType.UNKNOWN]
        assert metadata.classification.image_format == ImageFormat.PROCESSED

        # Dimensions should still be extracted
        assert metadata.dimensions.width == 1280
        assert metadata.dimensions.height == 720

    def test_timestamp_extraction_workflow(self):
        """Test timestamp extraction and prioritization."""
        file_path = self.create_test_image_with_exif(
            "timestamped_photo.jpg",
            add_camera_info=True
        )

        metadata = self.processor.process_image(file_path)

        # Should have timestamps
        assert metadata.timestamps is not None

        # Should have a best timestamp
        best_timestamp = metadata.get_creation_timestamp()
        assert best_timestamp is not None
        assert isinstance(best_timestamp, datetime)

        # Source should be identified
        source = metadata.timestamps.get_timestamp_source()
        assert source is not None

    def test_performance_benchmark_workflow(self):
        """Test performance of image processing."""
        # Create multiple test images
        test_files = []
        for i in range(5):
            file_path = self.create_test_image_with_exif(
                f"test_{i}.jpg",
                add_camera_info=(i % 2 == 0),  # Alternate camera info
                width=800,
                height=600
            )
            test_files.append(file_path)

        # Measure processing time
        start_time = time.time()
        results = []

        for file_path in test_files:
            metadata = self.processor.process_image(file_path)
            results.append(metadata)

        total_time = time.time() - start_time

        # Performance assertions
        assert total_time < 5.0  # Should complete in under 5 seconds
        assert len(results) == 5
        assert all(result.is_successful() for result in results)

        # Average processing time should be reasonable
        avg_processing_time = sum(r.processing_time_ms for r in results) / len(results)
        assert avg_processing_time < 1000  # Under 1 second per image

    def test_error_handling_workflow(self):
        """Test error handling for problematic images."""
        # Create an empty file
        empty_file = Path(self.temp_dir) / "empty.jpg"
        empty_file.touch()

        # Processing should not crash, but may have errors
        metadata = self.processor.process_image(empty_file)

        assert isinstance(metadata, object)
        # Empty file might have extraction errors
        # But processing should complete

    def test_multiple_format_support_workflow(self):
        """Test processing multiple image formats."""
        formats_to_test = [
            ("test.jpg", "JPEG"),
            ("test.png", "PNG"),
        ]

        results = {}

        for filename, format_name in formats_to_test:
            file_path = Path(self.temp_dir) / filename
            img = Image.new('RGB', (400, 300), color='blue')
            img.save(file_path, format_name)

            metadata = self.processor.process_image(file_path)
            results[format_name] = metadata

        # All formats should be processed successfully
        for format_name, metadata in results.items():
            assert metadata.is_successful(), f"Failed to process {format_name}"
            assert metadata.dimensions.width == 400
            assert metadata.dimensions.height == 300

    def test_classification_confidence_workflow(self):
        """Test classification confidence levels."""
        # Camera photo (should be high confidence)
        camera_photo = self.create_test_image_with_exif(
            "camera.jpg",
            add_camera_info=True
        )
        camera_metadata = self.processor.process_image(camera_photo)

        assert camera_metadata.classification.is_camera_photo()
        assert camera_metadata.classification.type_confidence in [
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MEDIUM
        ]

        # Graphic (may be lower confidence)
        graphic = self.create_test_image_with_exif(
            "graphic.jpg",
            add_camera_info=False
        )
        graphic_metadata = self.processor.process_image(graphic)

        assert not graphic_metadata.classification.is_camera_photo()

    def test_metadata_extraction_completeness(self):
        """Test completeness of metadata extraction."""
        file_path = self.create_test_image_with_exif(
            "complete_metadata.jpg",
            add_camera_info=True,
            width=2048,
            height=1536
        )

        metadata = self.processor.process_image(file_path)

        # Verify all major components are present
        assert metadata.file_path is not None
        assert metadata.mime_type is not None
        assert metadata.dimensions is not None
        assert metadata.camera is not None
        assert metadata.timestamps is not None
        assert metadata.classification is not None
        assert metadata.raw_exif is not None

        # Verify metadata can be serialized
        metadata_dict = metadata.to_dict()
        assert isinstance(metadata_dict, dict)
        assert 'file_path' in metadata_dict
        assert 'dimensions' in metadata_dict
        assert 'classification' in metadata_dict

    def test_exiftool_availability_check(self):
        """Test exiftool availability detection."""
        # ExifTool should be available for these tests
        assert self.processor.is_exiftool_available()

        version = self.processor.get_exiftool_version()
        assert version is not None
        assert len(version) > 0

    def test_raw_format_classification(self):
        """Test RAW format detection."""
        # Test various RAW extensions
        raw_extensions = ["cr2", "nef", "arw", "dng"]

        for ext in raw_extensions:
            assert self.classifier.is_raw_format(ext)

        # Test processed formats
        processed_extensions = ["jpg", "png", "gif"]
        for ext in processed_extensions:
            assert not self.classifier.is_raw_format(ext)

    def test_concurrent_processing_safety(self):
        """Test thread safety of image processing."""
        import threading

        file_path = self.create_test_image_with_exif("concurrent_test.jpg", True)

        results = []
        errors = []

        def process_image_concurrently(thread_id):
            """Process image from multiple threads."""
            try:
                for _ in range(3):
                    metadata = self.processor.process_image(file_path)
                    results.append({
                        'thread_id': thread_id,
                        'success': metadata.is_successful(),
                        'width': metadata.dimensions.width
                    })
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=process_image_concurrently, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors in concurrent processing: {errors}"
        assert len(results) == 9  # 3 threads × 3 processes each

        # All results should be consistent
        assert all(result['success'] for result in results)
        widths = [result['width'] for result in results]
        assert all(w == widths[0] for w in widths)  # All widths should be the same
