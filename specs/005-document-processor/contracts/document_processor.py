"""
Contract Interface for Document Processor
Defines the abstract interface that all document processor implementations must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from src.models.document_metadata import (
    DocumentMetadata, DocumentType, DocumentFormat, ScanType
)


class DocumentProcessor(ABC):
    """
    Abstract interface for document processing and metadata extraction.

    Implementations must extract metadata from various document formats
    including PDF, Office documents, and text files.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats (file extensions).

        Returns:
            List of supported file extensions (without dots)
        """
        pass

    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file can be processed, False otherwise
        """
        pass


class PDFAnalyzer(ABC):
    """
    Abstract interface for PDF-specific analysis.

    Handles PDF metadata extraction, page counting, and classification.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def is_password_protected(self, file_path: Path) -> bool:
        """
        Check if PDF is password protected.

        Args:
            file_path: Path to PDF file

        Returns:
            True if password protected, False otherwise
        """
        pass

    @abstractmethod
    def classify_pdf(self, page_count: int) -> DocumentType:
        """
        Classify PDF as brochure or ebook based on page count.

        Args:
            page_count: Number of pages in PDF

        Returns:
            DocumentType.BROCHURE (≤5 pages) or DocumentType.EBOOK (>5 pages)
        """
        pass


class OfficeDocumentAnalyzer(ABC):
    """
    Abstract interface for Office document analysis.

    Handles Word, Excel, and PowerPoint document metadata extraction.
    """

    @abstractmethod
    def analyze_docx(self, file_path: Path) -> DocumentMetadata:
        """
        Analyze a Word document and extract metadata.

        Args:
            file_path: Path to DOCX file

        Returns:
            DocumentMetadata with Word-specific information
        """
        pass

    @abstractmethod
    def analyze_xlsx(self, file_path: Path) -> DocumentMetadata:
        """
        Analyze an Excel document and extract metadata.

        Args:
            file_path: Path to XLSX file

        Returns:
            DocumentMetadata with Excel-specific information
        """
        pass

    @abstractmethod
    def analyze_pptx(self, file_path: Path) -> DocumentMetadata:
        """
        Analyze a PowerPoint document and extract metadata.

        Args:
            file_path: Path to PPTX file

        Returns:
            DocumentMetadata with PowerPoint-specific information
        """
        pass

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if format is supported.

        Args:
            file_extension: File extension (without dot)

        Returns:
            True if format is supported, False otherwise
        """
        pass


class OCRDetector(ABC):
    """
    Abstract interface for OCR and scan detection.

    Determines if a document is scanned or digital-native.
    """

    @abstractmethod
    def detect_scan_type(self, metadata: DocumentMetadata) -> ScanType:
        """
        Detect if document is scanned or digital-native.

        Args:
            metadata: DocumentMetadata with extracted information

        Returns:
            ScanType classification
        """
        pass

    @abstractmethod
    def is_scanned_pdf(self, file_path: Path) -> bool:
        """
        Check if PDF is scanned (vs digital-native).

        Args:
            file_path: Path to PDF file

        Returns:
            True if scanned, False if digital-native
        """
        pass

    @abstractmethod
    def has_text_layer(self, file_path: Path) -> bool:
        """
        Check if PDF has a text layer.

        Args:
            file_path: Path to PDF file

        Returns:
            True if text layer exists, False otherwise
        """
        pass

    @abstractmethod
    def get_detection_confidence(self, metadata: DocumentMetadata) -> 'ConfidenceLevel':
        """
        Get confidence level for scan detection.

        Args:
            metadata: DocumentMetadata

        Returns:
            ConfidenceLevel for the detection
        """
        pass
