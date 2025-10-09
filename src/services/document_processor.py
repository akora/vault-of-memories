"""
Document Processor Implementation
Main processor for handling various document formats.
"""

import logging
import time
from pathlib import Path
from typing import List

from ..models.document_metadata import (
    DocumentMetadata, DocumentType, DocumentFormat, TimestampInfo,
    DocumentClassification, ConfidenceLevel
)
from .pdf_analyzer import PDFAnalyzerImpl
from .office_document_analyzer import OfficeDocumentAnalyzerImpl
from .ocr_detector import OCRDetectorImpl


class DocumentProcessorImpl:
    """
    Implementation of document processing.

    Handles PDF, Office documents, and text files by routing to
    appropriate analyzers and extracting comprehensive metadata.
    """

    def __init__(self):
        """Initialize the document processor."""
        self.logger = logging.getLogger(__name__)
        self.pdf_analyzer = PDFAnalyzerImpl()
        self.office_analyzer = OfficeDocumentAnalyzerImpl()
        self.ocr_detector = OCRDetectorImpl()

    def process_document(self, file_path: Path) -> DocumentMetadata:
        """
        Process a document file and extract all metadata.

        Args:
            file_path: Path to the document file to process

        Returns:
            DocumentMetadata object with extracted information

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a supported document format
            RuntimeError: If processing fails
        """
        start_time = time.time()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path.suffix.lstrip('.').lower()

        try:
            # Route to appropriate analyzer based on file extension
            if extension == 'pdf':
                metadata = self.pdf_analyzer.analyze_pdf(file_path)
                # Detect scan type for PDFs
                metadata.ocr_detection.scan_type = self.ocr_detector.detect_scan_type(metadata)
                metadata.ocr_detection.confidence = self.ocr_detector.get_detection_confidence(metadata)

            elif extension == 'docx':
                metadata = self.office_analyzer.analyze_docx(file_path)

            elif extension == 'xlsx':
                metadata = self.office_analyzer.analyze_xlsx(file_path)

            elif extension == 'pptx':
                metadata = self.office_analyzer.analyze_pptx(file_path)

            elif extension in ('txt', 'md', 'markdown'):
                metadata = self._process_text_file(file_path)

            else:
                raise ValueError(f"Unsupported document format: {extension}")

            # Add file system timestamps as fallback
            self._add_file_system_timestamps(metadata, file_path)

        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {e}")
            # Return metadata with error
            metadata = DocumentMetadata(
                file_path=file_path,
                file_name=file_path.name,
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                mime_type="",
                file_extension=extension
            )
            metadata.extraction_errors.append(str(e))

        # Record processing time
        metadata.processing_time_ms = (time.time() - start_time) * 1000

        return metadata

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats (file extensions).

        Returns:
            List of supported file extensions (without dots)
        """
        return [
            "pdf",
            "docx", "xlsx", "pptx",
            "txt", "md", "markdown",
            "odt", "ods", "odp",  # OpenDocument formats
        ]

    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file can be processed, False otherwise
        """
        extension = file_path.suffix.lstrip('.').lower()
        return extension in self.get_supported_formats()

    def _process_text_file(self, file_path: Path) -> DocumentMetadata:
        """Process a plain text file."""
        # Determine MIME type based on extension
        extension = file_path.suffix.lstrip('.').lower()
        if extension in ('md', 'markdown'):
            mime_type = "text/markdown"
        else:
            mime_type = "text/plain"

        metadata = DocumentMetadata(
            file_path=file_path,
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
            mime_type=mime_type,
            file_extension=extension
        )

        try:
            # For text files, we can count lines and estimate words
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.count('\n') + 1
                words = len(content.split())

                # Store basic stats in raw_metadata
                metadata.raw_metadata = {
                    'line_count': lines,
                    'word_count': words,
                    'character_count': len(content)
                }

            # Classification
            metadata.classification = DocumentClassification(
                document_type=DocumentType.TEXT_FILE,
                document_format=DocumentFormat.TXT,
                type_confidence=ConfidenceLevel.HIGH,
                format_confidence=ConfidenceLevel.HIGH,
                type_reason="Plain text file",
                format_reason="TXT format"
            )

        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {e}")
            metadata.extraction_errors.append(f"Text file error: {str(e)}")

        return metadata

    def _add_file_system_timestamps(self, metadata: DocumentMetadata, file_path: Path):
        """Add file system timestamps as fallback."""
        try:
            stat = file_path.stat()

            if not metadata.timestamps:
                metadata.timestamps = TimestampInfo()

            from datetime import datetime

            # File modification time
            metadata.timestamps.file_modification_date = datetime.fromtimestamp(stat.st_mtime)

            # File creation time (on some systems)
            if hasattr(stat, 'st_birthtime'):
                metadata.timestamps.file_creation_date = datetime.fromtimestamp(stat.st_birthtime)

        except Exception as e:
            self.logger.warning(f"Error adding file system timestamps: {e}")
