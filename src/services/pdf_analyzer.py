"""
PDF Analyzer Implementation
Analyzes PDF documents to extract metadata, count pages, and classify documents.
"""

import logging
from pathlib import Path
from typing import Optional
import PyPDF2

from ..models.document_metadata import (
    DocumentMetadata, DocumentType, DocumentFormat, PDFProperties,
    DocumentAuthor, DocumentProperties, TimestampInfo, ConfidenceLevel,
    DocumentClassification
)


class PDFAnalyzerImpl:
    """
    Implementation of PDF analysis.

    Extracts metadata, counts pages, and classifies PDFs as brochures or ebooks.
    """

    def __init__(self, page_threshold: int = 5):
        """
        Initialize the PDF analyzer.

        Args:
            page_threshold: Page count threshold for brochure/ebook classification (default: 5)
        """
        self.logger = logging.getLogger(__name__)
        self.page_threshold = page_threshold

    def analyze_pdf(self, file_path: Path) -> DocumentMetadata:
        """
        Analyze a PDF file and extract metadata.

        Args:
            file_path: Path to PDF file

        Returns:
            DocumentMetadata with PDF-specific information

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a valid PDF
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize metadata
        metadata = DocumentMetadata(
            file_path=file_path,
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
            mime_type="application/pdf",
            file_extension="pdf"
        )

        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                # Extract PDF properties
                metadata.pdf_properties = self._extract_pdf_properties(reader)

                # Extract document information
                if reader.metadata:
                    metadata.author_info = self._extract_author_info(reader.metadata)
                    metadata.properties = self._extract_document_properties(reader.metadata)
                    metadata.timestamps = self._extract_timestamps(reader.metadata)

                # Classify document
                if metadata.pdf_properties and metadata.pdf_properties.page_count:
                    doc_type = self.classify_pdf(metadata.pdf_properties.page_count)
                    metadata.classification = DocumentClassification(
                        document_type=doc_type,
                        document_format=DocumentFormat.PDF,
                        type_confidence=ConfidenceLevel.HIGH,
                        format_confidence=ConfidenceLevel.HIGH,
                        type_reason=f"Page count: {metadata.pdf_properties.page_count}",
                        format_reason="Valid PDF file"
                    )

        except PyPDF2.errors.PdfReadError as e:
            self.logger.error(f"Error reading PDF {file_path}: {e}")
            metadata.extraction_errors.append(f"PDF read error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error analyzing PDF {file_path}: {e}")
            metadata.extraction_errors.append(f"Unexpected error: {str(e)}")

        return metadata

    def get_page_count(self, file_path: Path) -> int:
        """
        Get the number of pages in a PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Number of pages

        Raises:
            ValueError: If page count cannot be determined
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            raise ValueError(f"Cannot determine page count: {e}")

    def is_password_protected(self, file_path: Path) -> bool:
        """
        Check if PDF is password protected.

        Args:
            file_path: Path to PDF file

        Returns:
            True if password protected, False otherwise
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return reader.is_encrypted
        except Exception:
            return False

    def classify_pdf(self, page_count: int) -> DocumentType:
        """
        Classify PDF as brochure or ebook based on page count.

        Args:
            page_count: Number of pages in PDF

        Returns:
            DocumentType.BROCHURE (≤5 pages) or DocumentType.EBOOK (>5 pages)
        """
        if page_count <= self.page_threshold:
            return DocumentType.BROCHURE
        else:
            return DocumentType.EBOOK

    def _extract_pdf_properties(self, reader: PyPDF2.PdfReader) -> PDFProperties:
        """Extract PDF-specific properties."""
        props = PDFProperties()

        try:
            # Page count
            props.page_count = len(reader.pages)

            # Encryption status
            props.is_encrypted = reader.is_encrypted
            props.is_password_protected = reader.is_encrypted

            # PDF version (if available in metadata)
            if hasattr(reader, 'pdf_header'):
                props.pdf_version = reader.pdf_header

        except Exception as e:
            self.logger.warning(f"Error extracting PDF properties: {e}")

        return props

    def _extract_author_info(self, metadata: PyPDF2.DocumentInformation) -> DocumentAuthor:
        """Extract author information from PDF metadata."""
        author_info = DocumentAuthor()

        try:
            if '/Author' in metadata:
                author_info.author = str(metadata['/Author'])
            if '/Creator' in metadata:
                author_info.creator = str(metadata['/Creator'])
            if '/Producer' in metadata:
                # Producer is often the PDF generation software
                pass  # We'll use this for PDF properties instead
        except Exception as e:
            self.logger.warning(f"Error extracting author info: {e}")

        return author_info

    def _extract_document_properties(self, metadata: PyPDF2.DocumentInformation) -> DocumentProperties:
        """Extract general document properties from PDF metadata."""
        props = DocumentProperties()

        try:
            if '/Title' in metadata:
                props.title = str(metadata['/Title'])
            if '/Subject' in metadata:
                props.subject = str(metadata['/Subject'])
            if '/Keywords' in metadata:
                keywords_str = str(metadata['/Keywords'])
                # Split keywords by common delimiters
                props.keywords = [k.strip() for k in keywords_str.replace(';', ',').split(',') if k.strip()]
        except Exception as e:
            self.logger.warning(f"Error extracting document properties: {e}")

        return props

    def _extract_timestamps(self, metadata: PyPDF2.DocumentInformation) -> TimestampInfo:
        """Extract timestamps from PDF metadata."""
        timestamps = TimestampInfo()

        try:
            if '/CreationDate' in metadata:
                timestamps.creation_date = self._parse_pdf_date(metadata['/CreationDate'])
            if '/ModDate' in metadata:
                timestamps.modification_date = self._parse_pdf_date(metadata['/ModDate'])
        except Exception as e:
            self.logger.warning(f"Error extracting timestamps: {e}")

        return timestamps

    def _parse_pdf_date(self, date_str: str) -> Optional['datetime']:
        """
        Parse PDF date string to datetime.

        PDF dates are in format: D:YYYYMMDDHHmmSS+HH'mm'
        """
        from datetime import datetime

        if not date_str:
            return None

        try:
            # Remove 'D:' prefix if present
            if date_str.startswith('D:'):
                date_str = date_str[2:]

            # Extract basic date components (first 14 characters: YYYYMMDDHHmmSS)
            if len(date_str) >= 14:
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])

                return datetime(year, month, day, hour, minute, second)
        except Exception as e:
            self.logger.warning(f"Error parsing PDF date '{date_str}': {e}")

        return None
