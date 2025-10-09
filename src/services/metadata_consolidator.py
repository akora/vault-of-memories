"""
Metadata consolidation service.

Main orchestration service that coordinates between specialized processors,
applies priority-based resolution, and produces unified metadata records.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.consolidated_metadata import (
    ConsolidatedMetadata,
    MetadataQuality,
    MetadataSource,
    MetadataField
)
from .priority_resolver import PriorityResolver
from .timezone_preserver import TimezonePreserver
from .manufacturer_standardizer import ManufacturerStandardizer
from .metadata_quality_assessor import MetadataQualityAssessor


logger = logging.getLogger(__name__)


class MetadataConsolidator:
    """
    Consolidate metadata from multiple specialized processors.

    Coordinates extraction from image, document, audio, and video processors,
    applies priority-based conflict resolution, and produces a unified metadata record.
    """

    def __init__(
        self,
        priority_config: Optional[Path] = None,
        manufacturer_config: Optional[Path] = None
    ):
        """
        Initialize metadata consolidator.

        Args:
            priority_config: Optional path to priority rules configuration
            manufacturer_config: Optional path to manufacturer mappings configuration
        """
        self.priority_resolver = PriorityResolver(priority_config)
        self.timezone_preserver = TimezonePreserver()
        self.manufacturer_standardizer = ManufacturerStandardizer(manufacturer_config)
        self.quality_assessor = MetadataQualityAssessor()

        # Registry of specialized processors
        self.processors = {}

        logger.info("MetadataConsolidator initialized")

    def consolidate(self, file_path: Path) -> ConsolidatedMetadata:
        """
        Consolidate metadata from all available sources for a file.

        Args:
            file_path: Path to the file to process

        Returns:
            ConsolidatedMetadata with resolved metadata from all sources

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            RuntimeError: If critical metadata extraction fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Consolidating metadata for: {file_path}")

        # Get file basic info
        file_stat = file_path.stat()
        file_size = file_stat.st_size

        # Determine file type and get appropriate processor
        file_type = self._determine_file_type(file_path)

        # Collect metadata from all sources
        metadata_sources = self._collect_metadata_sources(file_path, file_type)

        # Consolidate each field using priority resolution
        consolidated = self._consolidate_fields(
            file_path, file_size, file_type, metadata_sources
        )

        # Assess quality
        quality = self.quality_assessor.assess_quality(consolidated)
        consolidated.quality_score = (quality.completeness_score + quality.confidence_score) / 2
        consolidated.completeness_score = quality.completeness_score
        consolidated.confidence_score = quality.confidence_score

        logger.info(
            f"Consolidated metadata for {file_path.name}: "
            f"quality={consolidated.quality_score:.2f}, "
            f"completeness={consolidated.completeness_score:.2f}"
        )

        return consolidated

    def assess_quality(self, metadata: ConsolidatedMetadata) -> MetadataQuality:
        """
        Assess the quality and completeness of consolidated metadata.

        Args:
            metadata: Consolidated metadata to assess

        Returns:
            MetadataQuality with scores and analysis

        Raises:
            ValueError: If metadata is invalid
        """
        return self.quality_assessor.assess_quality(metadata)

    def register_processor(self, file_type: str, processor: Any) -> None:
        """
        Register a specialized processor for a file type.

        Args:
            file_type: File type identifier (e.g., "image", "document")
            processor: Processor instance
        """
        self.processors[file_type] = processor
        logger.info(f"Registered processor for type: {file_type}")

    def get_supported_file_types(self) -> List[str]:
        """
        Get list of supported file types (MIME types).

        Returns:
            List of file type identifiers
        """
        return list(self.processors.keys())

    def _determine_file_type(self, file_path: Path) -> str:
        """
        Determine file type from extension.

        Args:
            file_path: Path to file

        Returns:
            File type identifier
        """
        ext = file_path.suffix.lower()

        # Map extensions to file types
        image_exts = {
            # Standard formats
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp", ".heic", ".heif",
            # Raw formats
            ".nef", ".cr2", ".cr3", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef"
        }
        doc_exts = {".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf"}
        audio_exts = {".mp3", ".flac", ".m4a", ".ogg", ".wma", ".wav"}
        video_exts = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"}

        if ext in image_exts:
            return "image"
        elif ext in doc_exts:
            return "document"
        elif ext in audio_exts:
            return "audio"
        elif ext in video_exts:
            return "video"
        else:
            return "unknown"

    def _collect_metadata_sources(
        self, file_path: Path, file_type: str
    ) -> Dict[str, Dict[MetadataSource, Any]]:
        """
        Collect metadata from all available sources.

        Args:
            file_path: Path to file
            file_type: Type of file

        Returns:
            Dictionary mapping field names to source dictionaries
        """
        # Initialize collection structure
        field_sources = {}

        # Get processor for this file type
        processor = self.processors.get(file_type)

        if processor is None:
            logger.warning(f"No processor registered for type: {file_type}")
            return field_sources

        # Extract metadata from processor
        try:
            # Call the appropriate processor method based on file type
            if file_type == 'image' and hasattr(processor, 'process_image'):
                processor_metadata = processor.process_image(file_path)
            elif file_type == 'document' and hasattr(processor, 'process_document'):
                processor_metadata = processor.process_document(file_path)
            elif file_type == 'audio' and hasattr(processor, 'process_audio'):
                processor_metadata = processor.process_audio(file_path)
            elif file_type == 'video' and hasattr(processor, 'process_video'):
                processor_metadata = processor.process_video(file_path)
            else:
                logger.warning(f"Processor for {file_type} doesn't have expected process method")
                return field_sources

            # Convert processor metadata to field_sources format
            # This extracts attributes from the metadata object and maps them to sources
            field_sources = self._convert_processor_metadata(processor_metadata, file_type)
            logger.debug(f"Extracted {len(field_sources)} fields from {file_type} processor")

        except Exception as e:
            logger.error(f"Error extracting metadata with {file_type} processor: {e}")
            # Return empty sources on error - consolidation will still work with filesystem metadata

        return field_sources

    def _convert_processor_metadata(
        self, processor_metadata: Any, file_type: str
    ) -> Dict[str, Dict[MetadataSource, Any]]:
        """
        Convert processor-specific metadata to field_sources format.

        Args:
            processor_metadata: Metadata object from processor
            file_type: Type of file being processed

        Returns:
            Dictionary mapping field names to source dictionaries
        """
        field_sources = {}
        # Use EMBEDDED for processor-extracted metadata (PDF properties, ID3 tags, etc.)
        source = MetadataSource.EMBEDDED

        # Extract common fields from all processor types
        # Handle nested structures in DocumentMetadata
        if file_type == 'document':
            # Timestamps
            if hasattr(processor_metadata, 'timestamps') and processor_metadata.timestamps:
                ts = processor_metadata.timestamps
                if hasattr(ts, 'creation_date') and ts.creation_date:
                    field_sources['creation_date'] = {source: ts.creation_date}
                if hasattr(ts, 'modification_date') and ts.modification_date:
                    field_sources['modification_date'] = {source: ts.modification_date}
                # Fall back to filesystem dates
                if hasattr(ts, 'file_creation_date') and ts.file_creation_date:
                    if 'creation_date' not in field_sources:
                        field_sources['creation_date'] = {MetadataSource.FILESYSTEM: ts.file_creation_date}

            # Properties
            if hasattr(processor_metadata, 'properties') and processor_metadata.properties:
                props = processor_metadata.properties
                if hasattr(props, 'title') and props.title:
                    field_sources['title'] = {source: props.title}

            # PDF-specific properties
            if hasattr(processor_metadata, 'pdf_properties') and processor_metadata.pdf_properties:
                pdf_props = processor_metadata.pdf_properties
                if hasattr(pdf_props, 'page_count') and pdf_props.page_count:
                    field_sources['page_count'] = {source: pdf_props.page_count}

            # Office document properties (Word, PowerPoint, etc.)
            if hasattr(processor_metadata, 'office_properties') and processor_metadata.office_properties:
                office_props = processor_metadata.office_properties
                if hasattr(office_props, 'page_count') and office_props.page_count:
                    field_sources['page_count'] = {source: office_props.page_count}
                elif hasattr(office_props, 'slide_count') and office_props.slide_count:
                    # For PowerPoint, slide_count is equivalent to page_count
                    field_sources['page_count'] = {source: office_props.slide_count}

            # Author info
            if hasattr(processor_metadata, 'author_info') and processor_metadata.author_info:
                author_info = processor_metadata.author_info
                if hasattr(author_info, 'author') and author_info.author:
                    field_sources['author'] = {source: author_info.author}

        # Type-specific fields for images
        if file_type == 'image':
            # Camera info (nested in camera object)
            if hasattr(processor_metadata, 'camera') and processor_metadata.camera:
                camera = processor_metadata.camera
                if hasattr(camera, 'make') and camera.make:
                    field_sources['device_make'] = {source: camera.make}
                if hasattr(camera, 'model') and camera.model:
                    field_sources['device_model'] = {source: camera.model}

            # Timestamps (nested in timestamps object)
            if hasattr(processor_metadata, 'timestamps') and processor_metadata.timestamps:
                timestamps = processor_metadata.timestamps
                # Try different timestamp fields
                capture_time = (
                    getattr(timestamps, 'date_time_original', None) or
                    getattr(timestamps, 'create_date', None) or
                    getattr(timestamps, 'capture', None)
                )
                if capture_time:
                    field_sources['capture_date'] = {source: capture_time}

            # Dimensions (nested in dimensions object)
            if hasattr(processor_metadata, 'dimensions') and processor_metadata.dimensions:
                dims = processor_metadata.dimensions
                if hasattr(dims, 'width') and dims.width:
                    field_sources['width'] = {source: dims.width}
                if hasattr(dims, 'height') and dims.height:
                    field_sources['height'] = {source: dims.height}

            # GPS (nested in gps object)
            if hasattr(processor_metadata, 'gps') and processor_metadata.gps:
                gps = processor_metadata.gps
                if hasattr(gps, 'latitude') and gps.latitude is not None:
                    field_sources['gps_latitude'] = {source: gps.latitude}
                if hasattr(gps, 'longitude') and gps.longitude is not None:
                    field_sources['gps_longitude'] = {source: gps.longitude}
                if hasattr(gps, 'altitude') and gps.altitude is not None:
                    field_sources['gps_altitude'] = {source: gps.altitude}

        # Type-specific fields for audio
        elif file_type == 'audio':
            if hasattr(processor_metadata, 'artist') and processor_metadata.artist:
                field_sources['artist'] = {source: processor_metadata.artist}

            if hasattr(processor_metadata, 'album') and processor_metadata.album:
                field_sources['album'] = {source: processor_metadata.album}

            if hasattr(processor_metadata, 'duration_seconds') and processor_metadata.duration_seconds:
                field_sources['duration'] = {source: processor_metadata.duration_seconds}

        # Type-specific fields for video
        elif file_type == 'video':
            # Technical dimensions and duration
            if hasattr(processor_metadata, 'duration') and processor_metadata.duration:
                field_sources['duration'] = {source: processor_metadata.duration}

            if hasattr(processor_metadata, 'width') and processor_metadata.width:
                field_sources['width'] = {source: processor_metadata.width}

            if hasattr(processor_metadata, 'height') and processor_metadata.height:
                field_sources['height'] = {source: processor_metadata.height}

            # Camera/device information
            if hasattr(processor_metadata, 'camera_make') and processor_metadata.camera_make:
                field_sources['device_make'] = {source: processor_metadata.camera_make}

            if hasattr(processor_metadata, 'camera_model') and processor_metadata.camera_model:
                field_sources['device_model'] = {source: processor_metadata.camera_model}

            if hasattr(processor_metadata, 'recording_device') and processor_metadata.recording_device:
                # Use as fallback if no camera info available
                if 'device_make' not in field_sources and 'device_model' not in field_sources:
                    field_sources['device_model'] = {source: processor_metadata.recording_device}

            # Timestamps
            if hasattr(processor_metadata, 'creation_date') and processor_metadata.creation_date:
                field_sources['creation_date'] = {source: processor_metadata.creation_date}

            if hasattr(processor_metadata, 'recording_date') and processor_metadata.recording_date:
                field_sources['capture_date'] = {source: processor_metadata.recording_date}

            if hasattr(processor_metadata, 'modification_date') and processor_metadata.modification_date:
                field_sources['modification_date'] = {source: processor_metadata.modification_date}

            # GPS coordinates
            if hasattr(processor_metadata, 'gps_latitude') and processor_metadata.gps_latitude:
                field_sources['gps_latitude'] = {source: processor_metadata.gps_latitude}

            if hasattr(processor_metadata, 'gps_longitude') and processor_metadata.gps_longitude:
                field_sources['gps_longitude'] = {source: processor_metadata.gps_longitude}

            if hasattr(processor_metadata, 'gps_altitude') and processor_metadata.gps_altitude:
                field_sources['gps_altitude'] = {source: processor_metadata.gps_altitude}

            # Content categorization
            if hasattr(processor_metadata, 'primary_category') and processor_metadata.primary_category:
                field_sources['category'] = {source: processor_metadata.primary_category}

            # Resolution label (e.g., "4K", "1080p")
            if hasattr(processor_metadata, 'resolution_label') and processor_metadata.resolution_label:
                field_sources['resolution_label'] = {source: processor_metadata.resolution_label}

            # Frame rate (fps)
            if hasattr(processor_metadata, 'fps') and processor_metadata.fps:
                field_sources['fps'] = {source: processor_metadata.fps}

        return field_sources

    def _consolidate_fields(
        self,
        file_path: Path,
        file_size: int,
        file_type: str,
        metadata_sources: Dict[str, Dict[MetadataSource, Any]]
    ) -> ConsolidatedMetadata:
        """
        Consolidate metadata fields using priority resolution.

        Args:
            file_path: Path to file
            file_size: File size in bytes
            file_type: File type identifier
            metadata_sources: Collected metadata from all sources

        Returns:
            ConsolidatedMetadata with resolved fields
        """
        # Create base metadata record
        consolidated = ConsolidatedMetadata(
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            checksum="",  # Would be calculated by file ingestor
            extraction_timestamp=datetime.now(),
            processors_used=[file_type] if file_type != "unknown" else []
        )

        # Resolve each field that has multiple sources
        for field_name, sources in metadata_sources.items():
            if not sources:
                continue

            try:
                resolved_field = self.priority_resolver.resolve_field(field_name, sources)

                # Apply special handling for specific field types
                if "date" in field_name and resolved_field.value:
                    # Preserve timezone
                    resolved_field.value = self.timezone_preserver.preserve_timezone(
                        resolved_field.value, resolved_field.source
                    )

                if field_name == "device_make" and resolved_field.value:
                    # Standardize manufacturer name
                    resolved_field.value = self.manufacturer_standardizer.standardize(
                        str(resolved_field.value)
                    )

                # Set field on consolidated metadata
                setattr(consolidated, field_name, resolved_field)

                # Track conflicts
                if self.priority_resolver.detect_conflicts(sources):
                    consolidated.conflicts_detected.append({
                        "field": field_name,
                        "sources": {str(s): v for s, v in sources.items()},
                        "resolved_to": str(resolved_field.source)
                    })

            except Exception as e:
                logger.error(f"Failed to resolve field '{field_name}': {e}")
                consolidated.processing_errors.append(
                    f"Field '{field_name}' resolution failed: {str(e)}"
                )

        return consolidated
