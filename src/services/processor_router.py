"""
Processor Router Implementation
Routes files to appropriate specialized processors based on detected content type.
"""

import logging
from typing import Dict, List, Optional

from abc import ABC, abstractmethod
from ..models.file_type_analysis import AnalysisResult, RoutingDecision, ConfidenceLevel


class ProcessorRouter(ABC):
    """Abstract interface for routing files to appropriate processors."""

    @abstractmethod
    def route_file(self, analysis_result: AnalysisResult) -> RoutingDecision:
        """Determine which processor should handle this file."""
        pass

    @abstractmethod
    def get_processor_for_type(self, mime_type: str) -> Optional[str]:
        """Get the processor name for a specific MIME type."""
        pass

    @abstractmethod
    def get_supported_processors(self) -> Dict[str, List[str]]:
        """Get mapping of processors to their supported MIME types."""
        pass


class ProcessorRouterImpl(ProcessorRouter):
    """
    Implementation of processor routing based on content types.

    Routes files to specialized processors based on detected MIME types
    with fallback handling for unknown or unsupported types.
    """

    def __init__(self):
        """Initialize the processor router."""
        self.logger = logging.getLogger(__name__)

        # Mapping of MIME types to processors
        self._processor_mappings = self._build_processor_mappings()

        # Category mappings for easier routing
        self._category_mappings = self._build_category_mappings()

        # Fallback processors for each category
        self._fallback_processors = {
            "image": "generic_image_processor",
            "document": "generic_document_processor",
            "audio": "generic_audio_processor",
            "video": "generic_video_processor",
            "text": "generic_text_processor",
            "archive": "generic_archive_processor",
            "unknown": "generic_file_processor"
        }

    def route_file(self, analysis_result: AnalysisResult) -> RoutingDecision:
        """
        Determine which processor should handle this file.

        Args:
            analysis_result: Result from file type analysis

        Returns:
            RoutingDecision with target processor and reasoning
        """
        mime_type = analysis_result.detected_mime_type
        confidence = analysis_result.confidence_level

        # Get the target processor
        target_processor = self.get_processor_for_type(mime_type)

        # Determine processor category
        category = self._get_category_for_mime_type(mime_type)

        # If no specific processor found, use category fallback
        if not target_processor:
            target_processor = self._fallback_processors.get(category, self._fallback_processors["unknown"])
            routing_reason = f"No specific processor for {mime_type}, using {category} fallback"
            routing_confidence = ConfidenceLevel.LOW
            fallback = self._fallback_processors.get("unknown") if category != "unknown" else None
        else:
            routing_reason = f"Matched {mime_type} to specialized {target_processor}"
            routing_confidence = self._determine_routing_confidence(confidence, mime_type)
            fallback = self._fallback_processors.get(category)

        return RoutingDecision(
            file_path=analysis_result.file_path,
            detected_mime_type=mime_type,
            target_processor=target_processor,
            processor_category=category,
            routing_confidence=routing_confidence,
            routing_reason=routing_reason,
            fallback_processor=fallback
        )

    def get_processor_for_type(self, mime_type: str) -> Optional[str]:
        """
        Get the processor name for a specific MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            Processor name or None if no specific processor available
        """
        return self._processor_mappings.get(mime_type.lower())

    def get_supported_processors(self) -> Dict[str, List[str]]:
        """
        Get mapping of processors to their supported MIME types.

        Returns:
            Dictionary mapping processor names to lists of MIME types
        """
        # Reverse the mapping from MIME -> processor to processor -> [MIME types]
        processor_to_mimes = {}

        for mime_type, processor in self._processor_mappings.items():
            if processor not in processor_to_mimes:
                processor_to_mimes[processor] = []
            processor_to_mimes[processor].append(mime_type)

        # Add fallback processors
        for category, processor in self._fallback_processors.items():
            if processor not in processor_to_mimes:
                processor_to_mimes[processor] = []
            processor_to_mimes[processor].append(f"{category}/*")

        return processor_to_mimes

    def _build_processor_mappings(self) -> Dict[str, str]:
        """Build mapping of MIME types to specific processors."""
        return {
            # Image processors
            'image/jpeg': 'image_processor',
            'image/png': 'image_processor',
            'image/gif': 'image_processor',
            'image/bmp': 'image_processor',
            'image/tiff': 'image_processor',
            'image/webp': 'image_processor',
            'image/svg+xml': 'image_processor',

            # Document processors
            'application/pdf': 'document_processor',
            'application/msword': 'document_processor',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document_processor',
            'application/vnd.ms-excel': 'document_processor',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document_processor',
            'application/vnd.ms-powerpoint': 'document_processor',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document_processor',
            'application/rtf': 'document_processor',

            # Audio processors
            'audio/mpeg': 'audio_processor',
            'audio/wav': 'audio_processor',
            'audio/ogg': 'audio_processor',
            'audio/mp4': 'audio_processor',
            'audio/flac': 'audio_processor',
            'audio/aac': 'audio_processor',

            # Video processors
            'video/mp4': 'video_processor',
            'video/avi': 'video_processor',
            'video/quicktime': 'video_processor',
            'video/webm': 'video_processor',
            'video/x-matroska': 'video_processor',

            # Text processors
            'text/plain': 'text_processor',
            'text/html': 'text_processor',
            'text/css': 'text_processor',
            'text/javascript': 'text_processor',
            'text/csv': 'text_processor',
            'application/json': 'text_processor',
            'text/xml': 'text_processor',
            'application/xml': 'text_processor',

            # Archive processors
            'application/zip': 'archive_processor',
            'application/x-rar-compressed': 'archive_processor',
            'application/x-tar': 'archive_processor',
            'application/gzip': 'archive_processor',
            'application/x-7z-compressed': 'archive_processor'
        }

    def _build_category_mappings(self) -> Dict[str, str]:
        """Build mapping of MIME type prefixes to categories."""
        return {
            'image/': 'image',
            'video/': 'video',
            'audio/': 'audio',
            'text/': 'text',
            'application/pdf': 'document',
            'application/msword': 'document',
            'application/vnd.openxmlformats': 'document',
            'application/vnd.ms-': 'document',
            'application/vnd.oasis': 'document',
            'application/rtf': 'document',
            'application/zip': 'archive',
            'application/x-rar': 'archive',
            'application/x-tar': 'archive',
            'application/x-7z': 'archive',
            'application/gzip': 'archive',
            'application/x-bzip': 'archive'
        }

    def _get_category_for_mime_type(self, mime_type: str) -> str:
        """Determine the category for a MIME type."""
        mime_lower = mime_type.lower()

        # Check exact matches first
        for pattern, category in self._category_mappings.items():
            if pattern.endswith('/'):
                # Prefix match
                if mime_lower.startswith(pattern):
                    return category
            else:
                # Exact or substring match
                if pattern in mime_lower:
                    return category

        # Check major category by prefix
        if mime_lower.startswith('image/'):
            return 'image'
        elif mime_lower.startswith('video/'):
            return 'video'
        elif mime_lower.startswith('audio/'):
            return 'audio'
        elif mime_lower.startswith('text/'):
            return 'text'
        elif mime_lower.startswith('application/'):
            # Try to categorize application types
            if any(doc_type in mime_lower for doc_type in ['word', 'excel', 'powerpoint', 'pdf', 'document']):
                return 'document'
            elif any(arch_type in mime_lower for arch_type in ['zip', 'rar', 'tar', 'gzip', 'compress']):
                return 'archive'
            else:
                return 'unknown'
        else:
            return 'unknown'

    def _determine_routing_confidence(self, analysis_confidence: ConfidenceLevel, mime_type: str) -> ConfidenceLevel:
        """
        Determine routing confidence based on analysis confidence and MIME type.

        Args:
            analysis_confidence: Confidence from content analysis
            mime_type: Detected MIME type

        Returns:
            Routing confidence level
        """
        # Start with analysis confidence
        if analysis_confidence == ConfidenceLevel.HIGH:
            base_confidence = ConfidenceLevel.HIGH
        elif analysis_confidence == ConfidenceLevel.MEDIUM:
            base_confidence = ConfidenceLevel.MEDIUM
        elif analysis_confidence == ConfidenceLevel.LOW:
            base_confidence = ConfidenceLevel.LOW
        else:
            base_confidence = ConfidenceLevel.UNKNOWN

        # Adjust based on processor availability
        has_specific_processor = self.get_processor_for_type(mime_type) is not None

        if not has_specific_processor:
            # Lower confidence if using fallback
            if base_confidence == ConfidenceLevel.HIGH:
                return ConfidenceLevel.MEDIUM
            elif base_confidence == ConfidenceLevel.MEDIUM:
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.UNKNOWN

        # Check if it's a well-supported type
        well_supported_types = [
            'image/jpeg', 'image/png', 'application/pdf',
            'video/mp4', 'audio/mpeg', 'text/plain'
        ]

        if mime_type in well_supported_types:
            return base_confidence

        # Slightly lower confidence for less common types
        if base_confidence == ConfidenceLevel.HIGH:
            return ConfidenceLevel.MEDIUM

        return base_confidence

    def add_processor_mapping(self, mime_type: str, processor: str) -> None:
        """
        Add a new processor mapping.

        Args:
            mime_type: MIME type to map
            processor: Processor name to handle this type
        """
        self._processor_mappings[mime_type.lower()] = processor
        self.logger.info(f"Added processor mapping: {mime_type} -> {processor}")

    def remove_processor_mapping(self, mime_type: str) -> bool:
        """
        Remove a processor mapping.

        Args:
            mime_type: MIME type to unmap

        Returns:
            True if mapping was removed, False if it didn't exist
        """
        if mime_type.lower() in self._processor_mappings:
            del self._processor_mappings[mime_type.lower()]
            self.logger.info(f"Removed processor mapping for: {mime_type}")
            return True
        return False

    def get_routing_statistics(self) -> Dict[str, int]:
        """
        Get statistics about routing capabilities.

        Returns:
            Dictionary with routing statistics
        """
        stats = {
            'total_mappings': len(self._processor_mappings),
            'unique_processors': len(set(self._processor_mappings.values())),
            'categories': len(self._fallback_processors),
            'fallback_processors': len(self._fallback_processors)
        }

        # Count by category
        for category in self._fallback_processors.keys():
            category_count = sum(1 for mime_type in self._processor_mappings.keys()
                               if self._get_category_for_mime_type(mime_type) == category)
            stats[f'{category}_mappings'] = category_count

        return stats