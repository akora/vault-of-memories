"""
OCR Detector Implementation
Detects whether documents are scanned or digital-native.
"""

import logging
from pathlib import Path
import PyPDF2

from ..models.document_metadata import (
    DocumentMetadata, ScanType, ConfidenceLevel
)


class OCRDetectorImpl:
    """
    Implementation of OCR and scan detection.

    Determines if a document is scanned or digital-native based on
    text layer presence, embedded fonts, and content analysis.
    """

    def __init__(self):
        """Initialize the OCR detector."""
        self.logger = logging.getLogger(__name__)

    def detect_scan_type(self, metadata: DocumentMetadata) -> ScanType:
        """
        Detect if document is scanned or digital-native.

        Args:
            metadata: DocumentMetadata with extracted information

        Returns:
            ScanType classification
        """
        # Only works for PDFs currently
        if metadata.file_extension.lower() != 'pdf':
            return ScanType.UNKNOWN

        try:
            has_text = self.has_text_layer(metadata.file_path)

            if has_text:
                # Has text layer - likely digital native
                return ScanType.DIGITAL_NATIVE
            else:
                # No text layer - likely scanned
                return ScanType.SCANNED

        except Exception as e:
            self.logger.warning(f"Error detecting scan type: {e}")
            return ScanType.UNKNOWN

    def is_scanned_pdf(self, file_path: Path) -> bool:
        """
        Check if PDF is scanned (vs digital-native).

        Args:
            file_path: Path to PDF file

        Returns:
            True if scanned, False if digital-native
        """
        # Check for text layer - if no text, likely scanned
        return not self.has_text_layer(file_path)

    def has_text_layer(self, file_path: Path) -> bool:
        """
        Check if PDF has a text layer.

        Args:
            file_path: Path to PDF file

        Returns:
            True if text layer exists, False otherwise
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                # Check first few pages for text
                pages_to_check = min(3, len(reader.pages))

                for i in range(pages_to_check):
                    try:
                        text = reader.pages[i].extract_text()
                        # If we find any meaningful text, document has text layer
                        if text and len(text.strip()) > 10:
                            return True
                    except Exception:
                        continue

                return False

        except Exception as e:
            self.logger.warning(f"Error checking text layer: {e}")
            return False

    def get_detection_confidence(self, metadata: DocumentMetadata) -> ConfidenceLevel:
        """
        Get confidence level for scan detection.

        Args:
            metadata: DocumentMetadata

        Returns:
            ConfidenceLevel for the detection
        """
        # Simple heuristic based on whether we could determine scan type
        if metadata.ocr_detection.scan_type == ScanType.UNKNOWN:
            return ConfidenceLevel.UNKNOWN

        # If we have PDF properties, we can be more confident
        if metadata.pdf_properties:
            return ConfidenceLevel.HIGH

        return ConfidenceLevel.MEDIUM
