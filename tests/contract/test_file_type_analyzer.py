"""
Contract tests for File Type Analyzer
These tests MUST pass for any implementation of the file type analyzer interfaces.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import implementations when available
try:
    from src.services.file_type_analyzer import FileTypeAnalyzerImpl
except ImportError:
    FileTypeAnalyzerImpl = None

try:
    from src.services.extension_validator import ExtensionValidatorImpl
except ImportError:
    ExtensionValidatorImpl = None

try:
    from src.services.processor_router import ProcessorRouterImpl
except ImportError:
    ProcessorRouterImpl = None

try:
    from src.services.content_type_registry import ContentTypeRegistryImpl
except ImportError:
    ContentTypeRegistryImpl = None

from src.models.file_type_analysis import (
    AnalysisResult, ValidationResult, RoutingDecision,
    ConfidenceLevel, ValidationSeverity
)


@pytest.mark.contract
class TestFileTypeAnalyzer:
    """Contract tests for FileTypeAnalyzer interface."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        if FileTypeAnalyzerImpl:
            self.analyzer = FileTypeAnalyzerImpl()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: bytes) -> Path:
        """Create a test file with specific content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_file_jpeg_image(self):
        """Test analysis of JPEG image file."""
        # JPEG file header
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        file_path = self.create_test_file("test.jpg", jpeg_content)

        result = self.analyzer.analyze_file(file_path)

        assert isinstance(result, AnalysisResult)
        assert result.file_path == file_path
        assert "image/jpeg" in result.detected_mime_type
        assert result.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
        assert result.file_size > 0
        assert result.analysis_time_ms >= 0
        assert result.error_message is None

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_file_pdf_document(self):
        """Test analysis of PDF document."""
        # PDF file header
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>'
        file_path = self.create_test_file("test.pdf", pdf_content)

        result = self.analyzer.analyze_file(file_path)

        assert isinstance(result, AnalysisResult)
        assert "application/pdf" in result.detected_mime_type
        assert result.confidence_level != ConfidenceLevel.UNKNOWN
        assert result.error_message is None

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_file_text_plain(self):
        """Test analysis of plain text file."""
        text_content = b'This is a plain text file with some content.'
        file_path = self.create_test_file("test.txt", text_content)

        result = self.analyzer.analyze_file(file_path)

        assert isinstance(result, AnalysisResult)
        assert "text/" in result.detected_mime_type
        assert result.confidence_level != ConfidenceLevel.UNKNOWN

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_file_nonexistent(self):
        """Test analysis fails for nonexistent file."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file(nonexistent_path)

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_content_direct(self):
        """Test direct content analysis."""
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'

        result = self.analyzer.analyze_content(jpeg_content, "test.jpg")

        assert isinstance(result, AnalysisResult)
        assert "image/jpeg" in result.detected_mime_type
        assert result.confidence_level != ConfidenceLevel.UNKNOWN

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_get_supported_types(self):
        """Test getting supported MIME types."""
        supported_types = self.analyzer.get_supported_types()

        assert isinstance(supported_types, list)
        assert len(supported_types) > 0
        assert all(isinstance(mime_type, str) for mime_type in supported_types)
        # Should support common types
        assert any("image/" in mime_type for mime_type in supported_types)
        assert any("text/" in mime_type for mime_type in supported_types)

    @pytest.mark.skipif(FileTypeAnalyzerImpl is None, reason="Implementation not available")
    def test_analyze_corrupted_file(self):
        """Test analysis of corrupted file."""
        # Create file with incomplete JPEG header
        corrupted_content = b'\xff\xd8\xff'  # Incomplete JPEG
        file_path = self.create_test_file("corrupted.jpg", corrupted_content)

        result = self.analyzer.analyze_file(file_path)

        assert isinstance(result, AnalysisResult)
        # Should still detect something, even if low confidence
        assert result.confidence_level is not None


@pytest.mark.contract
class TestExtensionValidator:
    """Contract tests for ExtensionValidator interface."""

    def setup_method(self):
        """Set up test environment."""
        if ExtensionValidatorImpl:
            self.validator = ExtensionValidatorImpl()

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_validate_extension_correct_match(self):
        """Test validation with correct extension/MIME type match."""
        file_path = Path("/test/image.jpg")

        result = self.validator.validate_extension(file_path, "image/jpeg")

        assert isinstance(result, ValidationResult)
        assert result.file_path == file_path
        assert result.extension == "jpg"
        assert result.detected_mime_type == "image/jpeg"
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_validate_extension_mismatch(self):
        """Test validation with extension/MIME type mismatch."""
        file_path = Path("/test/image.txt")  # JPEG content with .txt extension

        result = self.validator.validate_extension(file_path, "image/jpeg")

        assert isinstance(result, ValidationResult)
        assert result.extension == "txt"
        assert result.detected_mime_type == "image/jpeg"
        assert result.is_valid is False
        assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING]
        assert result.suggested_extension is not None

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_validate_extension_no_extension(self):
        """Test validation with no file extension."""
        file_path = Path("/test/noextension")

        result = self.validator.validate_extension(file_path, "image/jpeg")

        assert isinstance(result, ValidationResult)
        assert result.extension == ""
        assert result.is_valid is False
        assert result.suggested_extension is not None

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_get_expected_extensions(self):
        """Test getting expected extensions for MIME type."""
        extensions = self.validator.get_expected_extensions("image/jpeg")

        assert isinstance(extensions, list)
        assert len(extensions) > 0
        assert "jpg" in extensions or "jpeg" in extensions

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_suggest_extension(self):
        """Test extension suggestion for MIME type."""
        suggestion = self.validator.suggest_extension("image/jpeg")

        assert suggestion is not None
        assert isinstance(suggestion, str)
        assert suggestion in ["jpg", "jpeg"]

    @pytest.mark.skipif(ExtensionValidatorImpl is None, reason="Implementation not available")
    def test_suggest_extension_unknown_type(self):
        """Test extension suggestion for unknown MIME type."""
        suggestion = self.validator.suggest_extension("unknown/type")

        # Should return None for unknown types
        assert suggestion is None


@pytest.mark.contract
class TestProcessorRouter:
    """Contract tests for ProcessorRouter interface."""

    def setup_method(self):
        """Set up test environment."""
        if ProcessorRouterImpl:
            self.router = ProcessorRouterImpl()

    def create_analysis_result(self, mime_type: str, confidence: ConfidenceLevel) -> AnalysisResult:
        """Create a mock analysis result."""
        return AnalysisResult(
            file_path=Path("/test/file.ext"),
            detected_mime_type=mime_type,
            confidence_level=confidence,
            file_size=1024,
            magic_description="Test file",
            analysis_time_ms=10.0
        )

    @pytest.mark.skipif(ProcessorRouterImpl is None, reason="Implementation not available")
    def test_route_file_image(self):
        """Test routing of image file."""
        analysis_result = self.create_analysis_result("image/jpeg", ConfidenceLevel.HIGH)

        decision = self.router.route_file(analysis_result)

        assert isinstance(decision, RoutingDecision)
        assert decision.file_path == analysis_result.file_path
        assert decision.detected_mime_type == "image/jpeg"
        assert decision.processor_category == "image"
        assert decision.target_processor is not None
        assert decision.routing_confidence != ConfidenceLevel.UNKNOWN

    @pytest.mark.skipif(ProcessorRouterImpl is None, reason="Implementation not available")
    def test_route_file_document(self):
        """Test routing of document file."""
        analysis_result = self.create_analysis_result("application/pdf", ConfidenceLevel.HIGH)

        decision = self.router.route_file(analysis_result)

        assert isinstance(decision, RoutingDecision)
        assert decision.processor_category == "document"
        assert decision.target_processor is not None

    @pytest.mark.skipif(ProcessorRouterImpl is None, reason="Implementation not available")
    def test_route_file_unknown_type(self):
        """Test routing of unknown file type."""
        analysis_result = self.create_analysis_result("unknown/type", ConfidenceLevel.LOW)

        decision = self.router.route_file(analysis_result)

        assert isinstance(decision, RoutingDecision)
        assert decision.target_processor is not None  # Should have fallback
        assert decision.fallback_processor is not None or decision.processor_category in ["generic", "unknown"]

    @pytest.mark.skipif(ProcessorRouterImpl is None, reason="Implementation not available")
    def test_get_processor_for_type(self):
        """Test getting processor for specific MIME type."""
        processor = self.router.get_processor_for_type("image/jpeg")

        assert processor is not None
        assert isinstance(processor, str)

    @pytest.mark.skipif(ProcessorRouterImpl is None, reason="Implementation not available")
    def test_get_supported_processors(self):
        """Test getting all supported processors."""
        processors = self.router.get_supported_processors()

        assert isinstance(processors, dict)
        assert len(processors) > 0
        # Should have processors for major categories
        processor_names = list(processors.keys())
        assert any("image" in name.lower() for name in processor_names)


@pytest.mark.contract
class TestContentTypeRegistry:
    """Contract tests for ContentTypeRegistry interface."""

    def setup_method(self):
        """Set up test environment."""
        if ContentTypeRegistryImpl:
            self.registry = ContentTypeRegistryImpl()

    @pytest.mark.skipif(ContentTypeRegistryImpl is None, reason="Implementation not available")
    def test_get_mime_for_extension(self):
        """Test getting MIME type for extension."""
        mime_type = self.registry.get_mime_for_extension("jpg")

        assert mime_type is not None
        assert "image/jpeg" in mime_type

    @pytest.mark.skipif(ContentTypeRegistryImpl is None, reason="Implementation not available")
    def test_get_extensions_for_mime(self):
        """Test getting extensions for MIME type."""
        extensions = self.registry.get_extensions_for_mime("image/jpeg")

        assert isinstance(extensions, list)
        assert len(extensions) > 0
        assert "jpg" in extensions or "jpeg" in extensions

    @pytest.mark.skipif(ContentTypeRegistryImpl is None, reason="Implementation not available")
    def test_register_type_mapping(self):
        """Test registering new type mapping."""
        # Register a custom type
        self.registry.register_type_mapping(
            "application/x-custom",
            ["cust", "custom"],
            "custom_processor"
        )

        # Verify registration
        mime_type = self.registry.get_mime_for_extension("custom")
        assert "application/x-custom" in mime_type

        extensions = self.registry.get_extensions_for_mime("application/x-custom")
        assert "custom" in extensions

    @pytest.mark.skipif(ContentTypeRegistryImpl is None, reason="Implementation not available")
    def test_is_known_type(self):
        """Test checking if type is known."""
        # Known type
        assert self.registry.is_known_type("image/jpeg") is True

        # Unknown type
        assert self.registry.is_known_type("unknown/type") is False