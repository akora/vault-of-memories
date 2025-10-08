"""
Image Metadata Models
Type-safe data structures for image metadata extracted by the image processor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class ImageType(Enum):
    """Classification of image type."""
    CAMERA_PHOTO = "camera_photo"  # Photo taken with a camera
    GRAPHIC = "graphic"  # Screenshot, logo, diagram, etc.
    UNKNOWN = "unknown"  # Cannot determine


class ImageFormat(Enum):
    """Classification of image format."""
    RAW = "raw"  # RAW camera format (CR2, NEF, ARW, etc.)
    PROCESSED = "processed"  # Processed format (JPEG, PNG, TIFF, etc.)
    UNKNOWN = "unknown"  # Cannot determine


class ConfidenceLevel(Enum):
    """Confidence level for classifications."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class CameraInfo:
    """Camera information extracted from EXIF."""
    make: Optional[str] = None
    model: Optional[str] = None
    lens_make: Optional[str] = None
    lens_model: Optional[str] = None
    lens_id: Optional[str] = None

    # Camera settings
    iso: Optional[int] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    focal_length: Optional[float] = None
    focal_length_35mm: Optional[int] = None

    # Additional camera data
    flash: Optional[str] = None
    metering_mode: Optional[str] = None
    exposure_mode: Optional[str] = None
    white_balance: Optional[str] = None

    def has_camera_info(self) -> bool:
        """Check if any camera information is present."""
        return bool(self.make or self.model)

    def has_lens_info(self) -> bool:
        """Check if lens information is present."""
        return bool(self.lens_make or self.lens_model or self.lens_id)

    def has_settings_info(self) -> bool:
        """Check if camera settings are present."""
        return bool(self.iso or self.aperture or self.shutter_speed or self.focal_length)


@dataclass
class ImageDimensions:
    """Image dimensions and resolution information."""
    width: Optional[int] = None
    height: Optional[int] = None
    x_resolution: Optional[float] = None
    y_resolution: Optional[float] = None
    resolution_unit: Optional[str] = None
    color_space: Optional[str] = None
    bit_depth: Optional[int] = None
    megapixels: Optional[float] = None

    def __post_init__(self):
        """Calculate megapixels if dimensions are available."""
        if self.width and self.height and not self.megapixels:
            self.megapixels = round((self.width * self.height) / 1_000_000, 2)

    def aspect_ratio(self) -> Optional[str]:
        """Calculate aspect ratio as a string (e.g., '16:9')."""
        if not self.width or not self.height:
            return None

        from math import gcd
        divisor = gcd(self.width, self.height)
        return f"{self.width // divisor}:{self.height // divisor}"


@dataclass
class TimestampCollection:
    """Collection of timestamps from various sources."""
    # EXIF timestamps (preferred)
    date_time_original: Optional[datetime] = None  # When photo was taken
    create_date: Optional[datetime] = None  # When file was created
    date_time_digitized: Optional[datetime] = None  # When scanned/digitized
    modify_date: Optional[datetime] = None  # When file was modified

    # File system timestamps (fallback)
    file_create_date: Optional[datetime] = None
    file_modify_date: Optional[datetime] = None
    file_access_date: Optional[datetime] = None

    # GPS timestamp
    gps_date_time: Optional[datetime] = None

    # Timezone information
    offset_time: Optional[str] = None
    offset_time_original: Optional[str] = None

    def get_best_timestamp(self) -> Optional[datetime]:
        """
        Get the best available timestamp based on priority.

        Priority order:
        1. DateTimeOriginal (when photo was actually taken)
        2. CreateDate (when file was created)
        3. DateTimeDigitized (when scanned)
        4. ModifyDate (EXIF modify date)
        5. FileCreateDate (file system)
        6. FileModifyDate (file system, last resort)
        """
        return (
            self.date_time_original or
            self.create_date or
            self.date_time_digitized or
            self.modify_date or
            self.file_create_date or
            self.file_modify_date
        )

    def get_timestamp_source(self) -> Optional[str]:
        """Get the source of the best timestamp."""
        if self.date_time_original:
            return "EXIF:DateTimeOriginal"
        elif self.create_date:
            return "EXIF:CreateDate"
        elif self.date_time_digitized:
            return "EXIF:DateTimeDigitized"
        elif self.modify_date:
            return "EXIF:ModifyDate"
        elif self.file_create_date:
            return "FileSystem:CreateDate"
        elif self.file_modify_date:
            return "FileSystem:ModifyDate"
        return None


@dataclass
class GPSCoordinates:
    """GPS location information."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    latitude_ref: Optional[str] = None  # N or S
    longitude_ref: Optional[str] = None  # E or W
    altitude_ref: Optional[int] = None  # Above or below sea level

    def has_coordinates(self) -> bool:
        """Check if GPS coordinates are present."""
        return self.latitude is not None and self.longitude is not None

    def to_decimal_degrees(self) -> Optional[tuple[float, float]]:
        """Convert to decimal degrees format (lat, lon)."""
        if not self.has_coordinates():
            return None
        return (self.latitude, self.longitude)


@dataclass
class ImageClassification:
    """Image classification results."""
    image_type: ImageType = ImageType.UNKNOWN
    image_format: ImageFormat = ImageFormat.UNKNOWN
    type_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    format_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # Classification reasons (for debugging/logging)
    type_reason: Optional[str] = None
    format_reason: Optional[str] = None

    def is_camera_photo(self) -> bool:
        """Check if classified as camera photo."""
        return self.image_type == ImageType.CAMERA_PHOTO

    def is_raw_format(self) -> bool:
        """Check if classified as RAW format."""
        return self.image_format == ImageFormat.RAW

    def is_confident(self) -> bool:
        """Check if classification is confident."""
        return (
            self.type_confidence == ConfidenceLevel.HIGH and
            self.format_confidence == ConfidenceLevel.HIGH
        )


@dataclass
class ImageMetadata:
    """
    Complete metadata extracted from an image file.

    This is the primary data structure returned by the ImageProcessor.
    """
    # File information
    file_path: Path
    file_name: str
    file_size: int
    mime_type: str
    file_extension: str

    # Image dimensions and properties
    dimensions: ImageDimensions = field(default_factory=ImageDimensions)

    # Camera information (if applicable)
    camera: CameraInfo = field(default_factory=CameraInfo)

    # Timestamps
    timestamps: TimestampCollection = field(default_factory=TimestampCollection)

    # GPS location (if present)
    gps: Optional[GPSCoordinates] = None

    # Classification
    classification: ImageClassification = field(default_factory=ImageClassification)

    # Raw EXIF data (for reference)
    raw_exif: Dict[str, Any] = field(default_factory=dict)

    # Processing information
    processing_time_ms: float = 0.0
    exiftool_version: Optional[str] = None
    extraction_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and derive additional fields."""
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

        if not self.file_name:
            self.file_name = self.file_path.name

        if not self.file_extension:
            self.file_extension = self.file_path.suffix.lstrip('.')

    def is_successful(self) -> bool:
        """Check if metadata extraction was successful."""
        return len(self.extraction_errors) == 0

    def has_exif_data(self) -> bool:
        """Check if any EXIF data was extracted."""
        return len(self.raw_exif) > 0

    def has_camera_metadata(self) -> bool:
        """Check if camera metadata is present."""
        return self.camera.has_camera_info()

    def has_gps_data(self) -> bool:
        """Check if GPS data is present."""
        return self.gps is not None and self.gps.has_coordinates()

    def get_creation_timestamp(self) -> Optional[datetime]:
        """Get the best creation timestamp."""
        return self.timestamps.get_best_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_extension': self.file_extension,
            'dimensions': {
                'width': self.dimensions.width,
                'height': self.dimensions.height,
                'megapixels': self.dimensions.megapixels,
                'aspect_ratio': self.dimensions.aspect_ratio(),
            },
            'camera': {
                'make': self.camera.make,
                'model': self.camera.model,
                'iso': self.camera.iso,
                'aperture': self.camera.aperture,
                'shutter_speed': self.camera.shutter_speed,
            } if self.camera.has_camera_info() else None,
            'classification': {
                'type': self.classification.image_type.value,
                'format': self.classification.image_format.value,
                'confidence': {
                    'type': self.classification.type_confidence.value,
                    'format': self.classification.format_confidence.value,
                }
            },
            'timestamps': {
                'creation': self.get_creation_timestamp().isoformat() if self.get_creation_timestamp() else None,
                'source': self.timestamps.get_timestamp_source(),
            },
            'gps': {
                'coordinates': self.gps.to_decimal_degrees()
            } if self.has_gps_data() else None,
            'processing': {
                'time_ms': self.processing_time_ms,
                'errors': self.extraction_errors,
                'warnings': self.warnings,
            }
        }
