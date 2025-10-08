"""
Image Processor Implementation
Main processor for extracting metadata from image files using exiftool.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional

from ..models.image_metadata import (
    ImageMetadata, CameraInfo, ImageDimensions, GPSCoordinates
)
from .exiftool_wrapper import ExifToolWrapper
from .timestamp_extractor import TimestampExtractorImpl
from .image_classifier import ImageClassifierImpl


class ImageProcessorImpl:
    """
    Implementation of image processing with exiftool.

    Extracts comprehensive metadata from image files including EXIF data,
    camera information, timestamps, GPS coordinates, and image dimensions.
    """

    def __init__(self, exiftool_path: str = "exiftool"):
        """
        Initialize the image processor.

        Args:
            exiftool_path: Path to exiftool executable
        """
        self.logger = logging.getLogger(__name__)
        self.exiftool = ExifToolWrapper(exiftool_path)
        self.timestamp_extractor = TimestampExtractorImpl()
        self.classifier = ImageClassifierImpl()

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
        start_time = time.time()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize metadata object
        metadata = ImageMetadata(
            file_path=file_path,
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
            mime_type="",  # Will be extracted from EXIF
            file_extension=file_path.suffix.lstrip('.').lower()
        )

        try:
            # Extract raw EXIF data
            raw_exif = self.exiftool.extract_metadata(file_path)
            metadata.raw_exif = raw_exif

            # Extract MIME type
            metadata.mime_type = self._extract_mime_type(raw_exif)

            # Extract camera information
            metadata.camera = self._extract_camera_info(raw_exif)

            # Extract image dimensions
            metadata.dimensions = self._extract_dimensions(raw_exif)

            # Extract timestamps
            metadata.timestamps = self.timestamp_extractor.extract_timestamps(raw_exif)

            # Extract GPS coordinates
            metadata.gps = self._extract_gps_coordinates(raw_exif)

            # Classify the image
            metadata = self.classifier.classify_image(metadata)

            # Get exiftool version
            metadata.exiftool_version = self.exiftool.get_version()

        except Exception as e:
            self.logger.error(f"Error processing image {file_path}: {e}")
            metadata.extraction_errors.append(str(e))

        # Record processing time
        metadata.processing_time_ms = (time.time() - start_time) * 1000

        return metadata

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported image formats (file extensions).

        Returns:
            List of supported file extensions (without dots)
        """
        # Common image formats supported by exiftool
        formats = [
            # Standard formats
            "jpg", "jpeg", "jpe",
            "png",
            "gif",
            "tiff", "tif",
            "bmp",
            "webp",
            # RAW formats
            "cr2", "cr3", "crw",  # Canon
            "nef", "nrw",  # Nikon
            "arw", "srf", "sr2",  # Sony
            "orf",  # Olympus
            "rw2", "raw",  # Panasonic
            "raf",  # Fujifilm
            "pef", "ptx",  # Pentax
            "srw",  # Samsung
            "dng",  # Adobe/Leica
            "3fr", "fff",  # Hasselblad
            "x3f",  # Sigma
            "iiq",  # Phase One
            "mef",  # Mamiya
            "dcr", "kdc",  # Kodak
            "mrw",  # Minolta
            "rwl",  # Leica
        ]
        return formats

    def is_exiftool_available(self) -> bool:
        """
        Check if exiftool is available on the system.

        Returns:
            True if exiftool can be executed, False otherwise
        """
        return self.exiftool.is_available()

    def get_exiftool_version(self) -> Optional[str]:
        """
        Get the version of exiftool being used.

        Returns:
            Version string or None if exiftool is not available
        """
        return self.exiftool.get_version()

    def _extract_mime_type(self, raw_exif: dict) -> str:
        """Extract MIME type from EXIF."""
        mime_type = (
            raw_exif.get("File:MIMEType") or
            raw_exif.get("MIMEType") or
            ""
        )
        return str(mime_type) if mime_type else ""

    def _extract_camera_info(self, raw_exif: dict) -> CameraInfo:
        """Extract camera information from EXIF."""
        camera = CameraInfo()

        # Camera make and model
        camera.make = self._get_tag(raw_exif, "Make")
        camera.model = self._get_tag(raw_exif, "Model")

        # Lens information
        camera.lens_make = self._get_tag(raw_exif, "LensMake")
        camera.lens_model = self._get_tag(raw_exif, "LensModel")
        camera.lens_id = self._get_tag(raw_exif, "LensID")

        # Camera settings
        camera.iso = self._get_int(raw_exif, "ISO")
        camera.aperture = self._get_float(raw_exif, "Aperture") or self._get_float(raw_exif, "FNumber")
        camera.shutter_speed = self._get_tag(raw_exif, "ShutterSpeed") or self._get_tag(raw_exif, "ExposureTime")
        camera.focal_length = self._get_float(raw_exif, "FocalLength")
        camera.focal_length_35mm = self._get_int(raw_exif, "FocalLengthIn35mmFormat")

        # Additional settings
        camera.flash = self._get_tag(raw_exif, "Flash")
        camera.metering_mode = self._get_tag(raw_exif, "MeteringMode")
        camera.exposure_mode = self._get_tag(raw_exif, "ExposureMode")
        camera.white_balance = self._get_tag(raw_exif, "WhiteBalance")

        return camera

    def _extract_dimensions(self, raw_exif: dict) -> ImageDimensions:
        """Extract image dimensions from EXIF."""
        # Image dimensions - try multiple sources
        width = (
            self._get_int(raw_exif, "ImageWidth") or
            self._get_int(raw_exif, "ExifImageWidth") or
            raw_exif.get("PNG:ImageWidth") or
            raw_exif.get("File:ImageWidth")
        )
        height = (
            self._get_int(raw_exif, "ImageHeight") or
            self._get_int(raw_exif, "ExifImageHeight") or
            raw_exif.get("PNG:ImageHeight") or
            raw_exif.get("File:ImageHeight")
        )

        dimensions = ImageDimensions(
            width=int(width) if width else None,
            height=int(height) if height else None
        )

        # Resolution
        dimensions.x_resolution = self._get_float(raw_exif, "XResolution")
        dimensions.y_resolution = self._get_float(raw_exif, "YResolution")
        dimensions.resolution_unit = self._get_tag(raw_exif, "ResolutionUnit")

        # Color information
        dimensions.color_space = self._get_tag(raw_exif, "ColorSpace")
        dimensions.bit_depth = self._get_int(raw_exif, "BitDepth")

        return dimensions

    def _extract_gps_coordinates(self, raw_exif: dict) -> Optional[GPSCoordinates]:
        """Extract GPS coordinates from EXIF."""
        # Check if GPS data exists
        has_gps = any(key.startswith("GPS") for key in raw_exif.keys())
        if not has_gps:
            return None

        gps = GPSCoordinates()

        # GPS coordinates (exiftool with -n flag gives us decimal values)
        gps.latitude = self._get_float(raw_exif, "GPSLatitude")
        gps.longitude = self._get_float(raw_exif, "GPSLongitude")
        gps.altitude = self._get_float(raw_exif, "GPSAltitude")

        # GPS reference
        gps.latitude_ref = self._get_tag(raw_exif, "GPSLatitudeRef")
        gps.longitude_ref = self._get_tag(raw_exif, "GPSLongitudeRef")
        gps.altitude_ref = self._get_int(raw_exif, "GPSAltitudeRef")

        # Only return if we have actual coordinates
        if gps.has_coordinates():
            return gps

        return None

    def _get_tag(self, raw_exif: dict, tag_name: str) -> Optional[str]:
        """Get a tag value as string, trying multiple group prefixes."""
        for prefix in ["EXIF:", "Composite:", "File:", ""]:
            key = f"{prefix}{tag_name}"
            value = raw_exif.get(key)
            if value is not None:
                return str(value)
        return None

    def _get_int(self, raw_exif: dict, tag_name: str) -> Optional[int]:
        """Get a tag value as integer."""
        value = self._get_tag(raw_exif, tag_name)
        if value:
            try:
                # Remove any non-numeric characters (like 'mm' from focal length)
                numeric_part = ''.join(c for c in str(value) if c.isdigit() or c == '.')
                return int(float(numeric_part))
            except (ValueError, TypeError):
                return None
        return None

    def _get_float(self, raw_exif: dict, tag_name: str) -> Optional[float]:
        """Get a tag value as float."""
        value = self._get_tag(raw_exif, tag_name)
        if value:
            try:
                # Remove any non-numeric characters
                numeric_part = ''.join(c for c in str(value) if c.isdigit() or c in '.-')
                return float(numeric_part)
            except (ValueError, TypeError):
                return None
        return None
