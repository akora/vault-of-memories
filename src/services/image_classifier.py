"""
Image Classifier Implementation
Classifies images by type (photo vs graphic) and format (raw vs processed).
"""

import logging
from typing import List

from ..models.image_metadata import (
    ImageMetadata, ImageType, ImageFormat, ImageClassification, ConfidenceLevel
)


class ImageClassifierImpl:
    """
    Implementation of image classification logic.

    Determines whether an image is a camera photo or graphic,
    and whether it's in RAW or processed format.
    """

    # Known RAW format extensions
    RAW_EXTENSIONS = {
        # Canon
        "cr2", "cr3", "crw",
        # Nikon
        "nef", "nrw",
        # Sony
        "arw", "srf", "sr2",
        # Olympus
        "orf",
        # Panasonic
        "rw2", "raw",
        # Fujifilm
        "raf",
        # Pentax
        "pef", "ptx",
        # Samsung
        "srw",
        # Leica
        "rwl", "dng",
        # Hasselblad
        "3fr", "fff",
        # Sigma
        "x3f",
        # Adobe universal RAW
        "dng",
        # Phase One
        "iiq",
        # Mamiya
        "mef",
        # Kodak
        "dcr", "kdc",
        # Minolta
        "mrw",
    }

    # Camera-specific EXIF tags that indicate a photo was taken with a camera
    CAMERA_TAGS = {
        "Make", "Model", "LensMake", "LensModel", "LensID",
        "ISO", "FNumber", "Aperture", "ShutterSpeed", "ExposureTime",
        "FocalLength", "Flash", "MeteringMode", "ExposureMode"
    }

    def __init__(self):
        """Initialize the image classifier."""
        self.logger = logging.getLogger(__name__)

    def classify_image(self, metadata: ImageMetadata) -> ImageMetadata:
        """
        Classify an image based on its metadata.

        Args:
            metadata: ImageMetadata with extracted EXIF data

        Returns:
            ImageMetadata with classification field populated
        """
        # Classify image type (photo vs graphic)
        image_type, type_confidence, type_reason = self._classify_image_type(metadata)

        # Classify image format (RAW vs processed)
        image_format, format_confidence, format_reason = self._classify_image_format(metadata)

        # Update classification
        metadata.classification = ImageClassification(
            image_type=image_type,
            image_format=image_format,
            type_confidence=type_confidence,
            format_confidence=format_confidence,
            type_reason=type_reason,
            format_reason=format_reason
        )

        return metadata

    def is_camera_photo(self, metadata: ImageMetadata) -> bool:
        """
        Determine if image is a camera photo based on metadata.

        Args:
            metadata: ImageMetadata to analyze

        Returns:
            True if image is a camera photo, False otherwise
        """
        # Check for camera information
        if metadata.camera.has_camera_info():
            return True

        # Check for camera-specific settings
        if metadata.camera.has_settings_info():
            return True

        # Check raw EXIF for camera tags
        if metadata.raw_exif:
            for tag in self.CAMERA_TAGS:
                # Check with and without group prefix
                if tag in metadata.raw_exif:
                    return True
                if f"EXIF:{tag}" in metadata.raw_exif:
                    return True

        return False

    def is_raw_format(self, file_extension: str) -> bool:
        """
        Determine if file extension indicates RAW format.

        Args:
            file_extension: File extension (without dot)

        Returns:
            True if extension indicates RAW format, False otherwise
        """
        return file_extension.lower() in self.RAW_EXTENSIONS

    def get_raw_extensions(self) -> List[str]:
        """
        Get list of known RAW format extensions.

        Returns:
            List of RAW format file extensions
        """
        return sorted(list(self.RAW_EXTENSIONS))

    def _classify_image_type(self, metadata: ImageMetadata) -> tuple[ImageType, ConfidenceLevel, str]:
        """
        Classify image type (camera photo vs graphic).

        Returns:
            Tuple of (ImageType, ConfidenceLevel, reason string)
        """
        # Check for camera information in metadata
        has_camera = metadata.camera.has_camera_info()
        has_settings = metadata.camera.has_settings_info()
        has_lens = metadata.camera.has_lens_info()

        if has_camera and has_settings:
            return (
                ImageType.CAMERA_PHOTO,
                ConfidenceLevel.HIGH,
                f"Has camera info ({metadata.camera.make} {metadata.camera.model}) and settings"
            )

        if has_camera:
            return (
                ImageType.CAMERA_PHOTO,
                ConfidenceLevel.MEDIUM,
                f"Has camera info ({metadata.camera.make} {metadata.camera.model})"
            )

        if has_settings or has_lens:
            return (
                ImageType.CAMERA_PHOTO,
                ConfidenceLevel.MEDIUM,
                "Has camera settings or lens info"
            )

        # Check for camera tags in raw EXIF
        if metadata.raw_exif:
            camera_tag_count = 0
            found_tags = []

            for tag in self.CAMERA_TAGS:
                if tag in metadata.raw_exif or f"EXIF:{tag}" in metadata.raw_exif:
                    camera_tag_count += 1
                    found_tags.append(tag)

            if camera_tag_count >= 3:
                return (
                    ImageType.CAMERA_PHOTO,
                    ConfidenceLevel.MEDIUM,
                    f"Has {camera_tag_count} camera tags: {', '.join(found_tags[:3])}"
                )

        # No camera indicators - likely a graphic
        return (
            ImageType.GRAPHIC,
            ConfidenceLevel.MEDIUM,
            "No camera metadata found"
        )

    def _classify_image_format(self, metadata: ImageMetadata) -> tuple[ImageFormat, ConfidenceLevel, str]:
        """
        Classify image format (RAW vs processed).

        Returns:
            Tuple of (ImageFormat, ConfidenceLevel, reason string)
        """
        extension = metadata.file_extension.lower()

        if self.is_raw_format(extension):
            return (
                ImageFormat.RAW,
                ConfidenceLevel.HIGH,
                f"File extension .{extension} is a known RAW format"
            )

        # Check MIME type for additional confirmation
        if metadata.mime_type and "image/" in metadata.mime_type.lower():
            common_processed = ["jpeg", "jpg", "png", "gif", "tiff", "tif", "webp", "bmp"]
            if extension in common_processed:
                return (
                    ImageFormat.PROCESSED,
                    ConfidenceLevel.HIGH,
                    f"File extension .{extension} is a standard processed format"
                )

        # Default to processed if we can't determine
        return (
            ImageFormat.PROCESSED,
            ConfidenceLevel.MEDIUM,
            f"Assuming processed format for .{extension}"
        )
