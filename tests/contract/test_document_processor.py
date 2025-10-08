"""
Contract tests for Document Processor
These tests MUST pass for any implementation of the document processor interfaces.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

# Import implementations when available
try:
    from src.services.document_processor import DocumentProcessorImpl
except ImportError:
    DocumentProcessorImpl = None

try:
    from src.services.pdf_analyzer import PDFAnalyzerImpl
except ImportError:
    PDFAnalyzerImpl = None

try:
    from src.services.office_document_analyzer import OfficeDocumentAnalyzerImpl
except ImportError:
    OfficeDocumentAnalyzerImpl = None

try:
    from src.services.ocr_detector import OCRDetectorImpl
except ImportError:
    OCRDetectorImpl = None

from src.models.document_metadata import (
    DocumentMetadata, DocumentType, DocumentFormat, ScanType, ConfidenceLevel
)


@pytest.mark.contract
class TestDocumentProcessor:
    """Contract tests for DocumentProcessor interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if DocumentProcessorImpl:
            self.processor = DocumentProcessorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_pdf(self, filename: str, page_count: int = 1) -> Path:
        """Create a simple test PDF."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        file_path = Path(self.temp_dir) / filename
        c = canvas.Canvas(str(file_path), pagesize=letter)

        for i in range(page_count):
            c.drawString(100, 750, f"Test Page {i + 1}")
            c.showPage()

        c.save()
        return file_path

    def create_test_text_file(self, filename: str, content: str = "Test content") -> Path:
        """Create a simple text file."""
        file_path = Path(self.temp_dir) / filename
        file_path.write_text(content)
        return file_path

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_process_pdf_document(self):
        """Test processing a PDF document."""
        file_path = self.create_test_pdf("test.pdf", page_count=3)

        result = self.processor.process_document(file_path)

        assert isinstance(result, DocumentMetadata)
        assert result.file_path == file_path
        assert result.mime_type in ["application/pdf", "application/x-pdf"]
        assert result.file_size > 0
        assert result.is_successful()

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_process_text_file(self):
        """Test processing a text file."""
        file_path = self.create_test_text_file("test.txt", "Sample text content")

        result = self.processor.process_document(file_path)

        assert isinstance(result, DocumentMetadata)
        assert result.mime_type in ["text/plain", "text/txt"]
        assert result.classification.document_type == DocumentType.TEXT_FILE

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_process_document_nonexistent(self):
        """Test processing fails for nonexistent file."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.pdf"

        with pytest.raises(FileNotFoundError):
            self.processor.process_document(nonexistent_path)

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.processor.get_supported_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        # Should support common formats
        assert "pdf" in formats
        assert "txt" in formats
        # Should support Office formats
        assert any(fmt in formats for fmt in ["docx", "xlsx", "pptx"])

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_can_process(self):
        """Test can_process check."""
        pdf_path = self.create_test_pdf("test.pdf")
        txt_path = self.create_test_text_file("test.txt")

        assert self.processor.can_process(pdf_path) is True
        assert self.processor.can_process(txt_path) is True

    @pytest.mark.skipif(DocumentProcessorImpl is None, reason="Implementation not available")
    def test_processing_time_recorded(self):
        """Test that processing time is recorded."""
        file_path = self.create_test_pdf("timing.pdf")

        result = self.processor.process_document(file_path)

        assert result.processing_time_ms >= 0
        assert result.processing_time_ms < 10000  # Should be under 10 seconds


@pytest.mark.contract
class TestPDFAnalyzer:
    """Contract tests for PDFAnalyzer interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if PDFAnalyzerImpl:
            self.analyzer = PDFAnalyzerImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_pdf(self, filename: str, page_count: int = 1) -> Path:
        """Create a simple test PDF."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        file_path = Path(self.temp_dir) / filename
        c = canvas.Canvas(str(file_path), pagesize=letter)

        for i in range(page_count):
            c.drawString(100, 750, f"Test Page {i + 1}")
            c.showPage()

        c.save()
        return file_path

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_pdf(self):
        """Test analyzing a PDF."""
        file_path = self.create_test_pdf("test.pdf", page_count=3)

        result = self.analyzer.analyze_pdf(file_path)

        assert isinstance(result, DocumentMetadata)
        assert result.pdf_properties is not None
        assert result.pdf_properties.page_count == 3

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_get_page_count(self):
        """Test getting page count."""
        file_path = self.create_test_pdf("test.pdf", page_count=5)

        page_count = self.analyzer.get_page_count(file_path)

        assert page_count == 5

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_classify_brochure(self):
        """Test classifying PDF as brochure (≤5 pages)."""
        # Test boundary cases
        assert self.analyzer.classify_pdf(1) == DocumentType.BROCHURE
        assert self.analyzer.classify_pdf(5) == DocumentType.BROCHURE

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_classify_ebook(self):
        """Test classifying PDF as ebook (>5 pages)."""
        assert self.analyzer.classify_pdf(6) == DocumentType.EBOOK
        assert self.analyzer.classify_pdf(100) == DocumentType.EBOOK

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_page_count_accuracy(self):
        """Test page count accuracy for various sizes."""
        test_cases = [1, 3, 5, 10, 50]

        for expected_pages in test_cases:
            file_path = self.create_test_pdf(f"test_{expected_pages}.pdf", page_count=expected_pages)
            actual_pages = self.analyzer.get_page_count(file_path)
            assert actual_pages == expected_pages, f"Expected {expected_pages} pages, got {actual_pages}"

    @pytest.mark.skipif(PDFAnalyzerImpl is None, reason="Implementation not available")
    def test_is_password_protected(self):
        """Test password protection detection."""
        # Regular PDF should not be password protected
        file_path = self.create_test_pdf("test.pdf")
        assert self.analyzer.is_password_protected(file_path) is False


@pytest.mark.contract
class TestOfficeDocumentAnalyzer:
    """Contract tests for OfficeDocumentAnalyzer interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if OfficeDocumentAnalyzerImpl:
            self.analyzer = OfficeDocumentAnalyzerImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_docx(self, filename: str, title: str = "Test Document") -> Path:
        """Create a simple Word document."""
        from docx import Document

        file_path = Path(self.temp_dir) / filename
        doc = Document()
        doc.core_properties.title = title
        doc.add_paragraph("Test content")
        doc.save(str(file_path))
        return file_path

    @pytest.mark.skipif(OfficeDocumentAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_docx(self):
        """Test analyzing Word document."""
        file_path = self.create_test_docx("test.docx", title="Sample Document")

        result = self.analyzer.analyze_docx(file_path)

        assert isinstance(result, DocumentMetadata)
        assert result.office_properties is not None
        assert result.properties.title == "Sample Document"

    @pytest.mark.skipif(OfficeDocumentAnalyzerImpl is None, reason="Implementation not available")
    def test_supports_format(self):
        """Test format support checking."""
        assert self.analyzer.supports_format("docx") is True
        assert self.analyzer.supports_format("xlsx") is True
        assert self.analyzer.supports_format("pptx") is True
        assert self.analyzer.supports_format("pdf") is False


@pytest.mark.contract
class TestOCRDetector:
    """Contract tests for OCRDetector interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if OCRDetectorImpl:
            self.detector = OCRDetectorImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_pdf(self, filename: str) -> Path:
        """Create a simple digital-native PDF."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        file_path = Path(self.temp_dir) / filename
        c = canvas.Canvas(str(file_path), pagesize=letter)
        c.drawString(100, 750, "Digital native text")
        c.showPage()
        c.save()
        return file_path

    @pytest.mark.skipif(OCRDetectorImpl is None, reason="Implementation not available")
    def test_has_text_layer(self):
        """Test text layer detection."""
        file_path = self.create_test_pdf("digital.pdf")

        # Digital-native PDF should have text layer
        has_text = self.detector.has_text_layer(file_path)
        assert has_text is True

    @pytest.mark.skipif(OCRDetectorImpl is None, reason="Implementation not available")
    def test_detect_scan_type_digital(self):
        """Test detecting digital-native documents."""
        from src.services.pdf_analyzer import PDFAnalyzerImpl

        file_path = self.create_test_pdf("digital.pdf")

        # Get metadata first
        analyzer = PDFAnalyzerImpl()
        metadata = analyzer.analyze_pdf(file_path)

        scan_type = self.detector.detect_scan_type(metadata)

        # Should be detected as digital-native
        assert scan_type in [ScanType.DIGITAL_NATIVE, ScanType.UNKNOWN]

    @pytest.mark.skipif(OCRDetectorImpl is None, reason="Implementation not available")
    def test_get_detection_confidence(self):
        """Test confidence level reporting."""
        from src.services.pdf_analyzer import PDFAnalyzerImpl

        file_path = self.create_test_pdf("test.pdf")
        analyzer = PDFAnalyzerImpl()
        metadata = analyzer.analyze_pdf(file_path)

        confidence = self.detector.get_detection_confidence(metadata)

        assert isinstance(confidence, ConfidenceLevel)
