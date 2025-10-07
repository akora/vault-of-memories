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
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp", ".heic"}
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
        # Note: Each processor would have been registered with their extract method
        # This is a simplified version - in practice would call processor.process_xxx()
        logger.debug(f"Would extract metadata using {file_type} processor")

        # For now, return empty sources (processors would populate this)
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
