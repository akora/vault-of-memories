"""
T034: ClassificationEngine - Content classification with MIME detection and priority rules.
"""

from pathlib import Path
from typing import Any
import logging
from ..models.classification import Classification
from .mime_detector import MimeDetector


logger = logging.getLogger(__name__)


class ClassificationEngine:
    """Classifies files into vault categories using configurable rules."""

    # MIME type to category mapping
    MIME_TO_CATEGORY = {
        # Photos - Processed
        'image/jpeg': ('photos', 'processed'),
        'image/png': ('photos', 'processed'),
        'image/gif': ('photos', 'processed'),
        'image/webp': ('photos', 'processed'),
        'image/heic': ('photos', 'processed'),
        'image/heif': ('photos', 'processed'),

        # Photos - Raw
        'image/x-canon-cr2': ('photos', 'raw'),
        'image/x-canon-cr3': ('photos', 'raw'),
        'image/x-nikon-nef': ('photos', 'raw'),
        'image/x-sony-arw': ('photos', 'raw'),
        'image/x-adobe-dng': ('photos', 'raw'),
        'image/x-olympus-orf': ('photos', 'raw'),
        'image/x-panasonic-rw2': ('photos', 'raw'),
        'image/x-fuji-raf': ('photos', 'raw'),
        'image/x-pentax-pef': ('photos', 'raw'),

        # Documents
        'application/pdf': ('documents', 'pdf'),
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ('documents', 'office'),
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('documents', 'office'),
        'text/plain': ('documents', 'text'),
        'text/markdown': ('documents', 'text'),

        # Videos
        'video/mp4': ('videos', None),
        'video/quicktime': ('videos', None),
        'video/x-msvideo': ('videos', None),

        # Audio
        'audio/mpeg': ('audio', None),
        'audio/mp4': ('audio', None),
        'audio/flac': ('audio', None),

        # Archives
        'application/zip': ('archives', None),
        'application/x-7z-compressed': ('archives', None),
    }

    def __init__(self):
        self.mime_detector = MimeDetector()
        self.ambiguous_files = []

    def classify(self, file_path: Path, metadata: dict[str, Any]) -> Classification:
        """
        Classify file into primary category and subcategory.

        Args:
            file_path: Path to file
            metadata: File metadata including type information

        Returns:
            Classification with category, confidence, and reasoning
        """
        # Get MIME type from metadata
        mime_type = metadata.get('mime_type')

        # Handle MetadataField objects (from asdict conversion)
        if isinstance(mime_type, dict) and 'value' in mime_type:
            mime_type = mime_type['value']
            method = 'metadata'
            confidence = mime_type.get('confidence', 0.95) if isinstance(mime_type, dict) else 0.95
        elif mime_type:
            # Direct string value
            method = 'metadata'
            confidence = 0.95
        else:
            # No MIME type in metadata, detect it
            mime_type, method, confidence = self.mime_detector.detect(file_path)

        # Classify based on MIME type
        if mime_type in self.MIME_TO_CATEGORY:
            primary_category, subcategory = self.MIME_TO_CATEGORY[mime_type]
            reasoning = f"MIME: {mime_type} → {primary_category}"
            if subcategory:
                reasoning += f" → {subcategory}"
        else:
            primary_category = 'other'
            subcategory = None
            confidence = 0.0
            reasoning = f"MIME: {mime_type} → unknown, defaulting to 'other'"
            self.ambiguous_files.append((file_path, mime_type))

        classification = Classification(
            primary_category=primary_category,
            subcategory=subcategory,
            confidence=confidence,
            reasoning=reasoning,
            mime_type=mime_type,
            detection_method=method
        )

        logger.debug(f"Classified {file_path}: {classification.primary_category}/{classification.subcategory}")
        return classification

    def classify_batch(
        self,
        file_paths: list[Path],
        metadata_dict: dict[Path, dict[str, Any]]
    ) -> dict[Path, Classification]:
        """Classify multiple files efficiently."""
        results = {}
        for file_path in file_paths:
            metadata = metadata_dict.get(file_path, {})
            try:
                results[file_path] = self.classify(file_path, metadata)
            except Exception as e:
                logger.error(f"Failed to classify {file_path}: {e}")
                results[file_path] = Classification(
                    primary_category='other',
                    subcategory=None,
                    confidence=0.0,
                    reasoning=f"Error: {e}",
                    mime_type='application/octet-stream',
                    detection_method='fallback'
                )
        return results

    def get_ambiguous_files(self) -> list[tuple[Path, str]]:
        """Get files flagged as ambiguous during classification."""
        return self.ambiguous_files
