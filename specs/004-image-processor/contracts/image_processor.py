"""
Contract Interface for Image Processor
Defines the abstract interface that all image processor implementations must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from src.models.image_metadata import ImageMetadata, ImageType, ImageFormat


class ImageProcessor(ABC):
    """
    Abstract interface for image processing and metadata extraction.

    Implementations must use exiftool to extract comprehensive metadata
    from image files and provide structured, type-safe results.
    """

    @abstractmethod
    def process_image(self, file_path: Path) -> ImageMetadata:
        """
        Process an image file and extract all metadata.

        Args:
            file_path: Path to the image file to process

        Returns:
            ImageMetadata object with extracted information

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a supported image format
            RuntimeError: If exiftool is not available or fails
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported image formats (file extensions).

        Returns:
            List of supported file extensions (without dots)
        """
        pass

    @abstractmethod
    def is_exiftool_available(self) -> bool:
        """
        Check if exiftool is available on the system.

        Returns:
            True if exiftool can be executed, False otherwise
        """
        pass

    @abstractmethod
    def get_exiftool_version(self) -> Optional[str]:
        """
        Get the version of exiftool being used.

        Returns:
            Version string or None if exiftool is not available
        """
        pass


class ImageClassifier(ABC):
    """
    Abstract interface for classifying images.

    Determines whether an image is a camera photo or graphic,
    and whether it's in RAW or processed format.
    """

    @abstractmethod
    def classify_image(self, metadata: ImageMetadata) -> ImageMetadata:
        """
        Classify an image based on its metadata.

        Args:
            metadata: ImageMetadata with extracted EXIF data

        Returns:
            ImageMetadata with classification field populated

        Note:
            Modifies the classification field in the metadata object
        """
        pass

    @abstractmethod
    def is_camera_photo(self, metadata: ImageMetadata) -> bool:
        """
        Determine if image is a camera photo based on metadata.

        Args:
            metadata: ImageMetadata to analyze

        Returns:
            True if image is a camera photo, False otherwise
        """
        pass

    @abstractmethod
    def is_raw_format(self, file_extension: str) -> bool:
        """
        Determine if file extension indicates RAW format.

        Args:
            file_extension: File extension (without dot)

        Returns:
            True if extension indicates RAW format, False otherwise
        """
        pass

    @abstractmethod
    def get_raw_extensions(self) -> List[str]:
        """
        Get list of known RAW format extensions.

        Returns:
            List of RAW format file extensions
        """
        pass


class TimestampExtractor(ABC):
    """
    Abstract interface for extracting and prioritizing timestamps.

    Handles the complexity of multiple timestamp sources and
    determines the best creation timestamp for an image.
    """

    @abstractmethod
    def extract_timestamps(self, raw_exif: dict) -> 'TimestampCollection':
        """
        Extract all timestamps from EXIF data.

        Args:
            raw_exif: Raw EXIF data dictionary

        Returns:
            TimestampCollection with all available timestamps
        """
        pass

    @abstractmethod
    def parse_exif_datetime(self, datetime_str: str) -> Optional['datetime']:
        """
        Parse EXIF datetime string to Python datetime.

        Args:
            datetime_str: EXIF datetime string (various formats)

        Returns:
            Parsed datetime object or None if parsing fails
        """
        pass

    @abstractmethod
    def get_timestamp_priority_order(self) -> List[str]:
        """
        Get the priority order for timestamp selection.

        Returns:
            List of timestamp field names in priority order
        """
        pass
