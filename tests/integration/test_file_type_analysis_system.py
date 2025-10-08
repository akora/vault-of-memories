"""
Integration tests for the complete file type analysis system.
Tests the interaction between all file type analysis components.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.file_type_analyzer import FileTypeAnalyzerImpl
from src.services.extension_validator import ExtensionValidatorImpl
from src.services.processor_router import ProcessorRouterImpl
from src.services.content_type_registry import ContentTypeRegistryImpl
from src.models.file_type_analysis import (
    AnalysisResult, ValidationResult, RoutingDecision,
    ConfidenceLevel, ValidationSeverity
)


@pytest.mark.integration
class TestFileTypeAnalysisSystemIntegration:
    """Integration tests for complete file type analysis workflows."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Initialize all components with proper dependency injection
        self.registry = ContentTypeRegistryImpl()
        self.analyzer = FileTypeAnalyzerImpl()
        self.validator = ExtensionValidatorImpl(registry=self.registry)
        self.router = ProcessorRouterImpl()

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

    def test_complete_jpeg_analysis_workflow(self):
        """Test complete analysis workflow for JPEG image."""
        # Create JPEG test file
        jpeg_content = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xfe\x00\x13Lavc58.54.100\x00\xff\xdb\x00C\x00\x02\x01\x01'
        )
        file_path = self.create_test_file("test_image.jpg", jpeg_content)

        # Step 1: Analyze file content
        analysis_result = self.analyzer.analyze_file(file_path)

        assert analysis_result.detected_mime_type == "image/jpeg"
        assert analysis_result.confidence_level == ConfidenceLevel.HIGH
        assert analysis_result.is_successful()

        # Step 2: Validate extension
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )

        assert validation_result.is_valid is True
        assert validation_result.severity == ValidationSeverity.INFO
        assert validation_result.extension == "jpg"

        # Step 3: Route to processor
        routing_decision = self.router.route_file(analysis_result)

        assert routing_decision.target_processor == "image_processor"
        assert routing_decision.processor_category == "image"
        assert routing_decision.is_confident_routing()

        # Step 4: Verify registry consistency
        expected_extensions = self.registry.get_extensions_for_mime("image/jpeg")
        assert "jpg" in expected_extensions

        registry_mime = self.registry.get_mime_for_extension("jpg")
        assert registry_mime == "image/jpeg"

    def test_extension_mismatch_detection_workflow(self):
        """Test workflow when file extension doesn't match content."""
        # Create JPEG content with .txt extension
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        file_path = self.create_test_file("misleading_file.txt", jpeg_content)

        # Analyze content
        analysis_result = self.analyzer.analyze_file(file_path)
        assert analysis_result.detected_mime_type == "image/jpeg"

        # Validate extension (should detect mismatch)
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )

        assert validation_result.is_valid is False
        assert validation_result.severity in [ValidationSeverity.WARNING, ValidationSeverity.ERROR]
        assert validation_result.suggested_extension == "jpg"
        assert validation_result.requires_attention()

        # Router should still work correctly
        routing_decision = self.router.route_file(analysis_result)
        assert routing_decision.target_processor == "image_processor"

    def test_unknown_file_type_workflow(self):
        """Test workflow for unknown/unrecognized file types."""
        # Create file with unknown content
        unknown_content = b'\x00\x01\x02\x03UNKNOWN_FORMAT\x04\x05\x06\x07'
        file_path = self.create_test_file("unknown_file.xyz", unknown_content)

        # Analyze content
        analysis_result = self.analyzer.analyze_file(file_path)

        # Should default to generic binary type
        assert "application/octet-stream" in analysis_result.detected_mime_type or "data" in analysis_result.magic_description.lower()

        # Validate extension
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )

        # Extension validation should handle unknown types gracefully
        assert isinstance(validation_result, ValidationResult)

        # Router should provide fallback
        routing_decision = self.router.route_file(analysis_result)
        assert routing_decision.target_processor is not None
        assert routing_decision.processor_category in ["unknown", "generic"]

    def test_pdf_document_analysis_workflow(self):
        """Test complete workflow for PDF document."""
        # Create minimal PDF content
        pdf_content = (
            b'%PDF-1.4\n'
            b'1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n'
            b'2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n'
            b'3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n>>\nendobj\n'
            b'xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n'
            b'trailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n%%EOF'
        )
        file_path = self.create_test_file("document.pdf", pdf_content)

        # Complete analysis workflow
        analysis_result = self.analyzer.analyze_file(file_path)
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )
        routing_decision = self.router.route_file(analysis_result)

        # Verify results
        assert "application/pdf" in analysis_result.detected_mime_type
        assert validation_result.is_valid is True
        assert routing_decision.target_processor == "document_processor"
        assert routing_decision.processor_category == "document"

    def test_plain_text_file_workflow(self):
        """Test workflow for plain text files."""
        text_content = b'This is a simple text file with some content.\nSecond line of text.'
        file_path = self.create_test_file("readme.txt", text_content)

        # Analyze
        analysis_result = self.analyzer.analyze_file(file_path)
        assert "text/" in analysis_result.detected_mime_type
        assert analysis_result.encoding is not None

        # Validate
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )
        assert validation_result.is_valid is True

        # Route
        routing_decision = self.router.route_file(analysis_result)
        assert routing_decision.processor_category == "text"

    def test_performance_benchmark_workflow(self):
        """Test performance of complete analysis workflow."""
        # Create multiple test files
        test_files = []

        # JPEG image
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        test_files.append(self.create_test_file("test1.jpg", jpeg_content))

        # PDF document
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF'
        test_files.append(self.create_test_file("test2.pdf", pdf_content))

        # Text file
        text_content = b'Simple text content for testing.'
        test_files.append(self.create_test_file("test3.txt", text_content))

        # Measure performance
        start_time = time.time()
        results = []

        for file_path in test_files:
            # Complete workflow
            analysis_result = self.analyzer.analyze_file(file_path)
            validation_result = self.validator.validate_extension(
                file_path, analysis_result.detected_mime_type
            )
            routing_decision = self.router.route_file(analysis_result)

            results.append({
                'analysis': analysis_result,
                'validation': validation_result,
                'routing': routing_decision
            })

        total_time = time.time() - start_time

        # Performance assertions
        assert total_time < 1.0  # Should complete in under 1 second
        assert len(results) == 3
        assert all(result['analysis'].is_successful() for result in results)

        # Average analysis time should be reasonable
        avg_analysis_time = sum(result['analysis'].analysis_time_ms for result in results) / len(results)
        assert avg_analysis_time < 100  # Under 100ms per file

    def test_concurrent_analysis_workflow(self):
        """Test thread safety of analysis components."""
        import threading

        # Create test file
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        file_path = self.create_test_file("concurrent_test.jpg", jpeg_content)

        results = []
        errors = []

        def analyze_file_concurrently(thread_id):
            """Analyze file from multiple threads."""
            try:
                for _ in range(5):
                    analysis_result = self.analyzer.analyze_file(file_path)
                    validation_result = self.validator.validate_extension(
                        file_path, analysis_result.detected_mime_type
                    )
                    routing_decision = self.router.route_file(analysis_result)

                    results.append({
                        'thread_id': thread_id,
                        'mime_type': analysis_result.detected_mime_type,
                        'is_valid': validation_result.is_valid,
                        'processor': routing_decision.target_processor
                    })
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=analyze_file_concurrently, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors in concurrent analysis: {errors}"
        assert len(results) == 15  # 3 threads × 5 analyses each

        # All results should be consistent
        mime_types = [result['mime_type'] for result in results]
        processors = [result['processor'] for result in results]

        assert all(mime_type == "image/jpeg" for mime_type in mime_types)
        assert all(processor == "image_processor" for processor in processors)

    def test_custom_type_registration_workflow(self):
        """Test workflow with custom type registrations."""
        # Register custom type
        self.registry.register_type_mapping(
            "application/x-vault-backup",
            ["vbak", "backup"],
            "backup_processor"
        )

        # Add custom processor mapping to router
        self.router.add_processor_mapping("application/x-vault-backup", "backup_processor")

        # Create file with custom extension
        custom_content = b'VAULT_BACKUP_v1.0\x00\x01\x02\x03'
        file_path = self.create_test_file("data.vbak", custom_content)

        # Test registry lookup
        registry_mime = self.registry.get_mime_for_extension("vbak")
        assert registry_mime == "application/x-vault-backup"

        # Test extension validation with custom type
        validation_result = self.validator.validate_extension(file_path, "application/x-vault-backup")
        assert validation_result.is_valid is True

        # Test routing with custom processor
        mock_analysis = AnalysisResult(
            file_path=file_path,
            detected_mime_type="application/x-vault-backup",
            confidence_level=ConfidenceLevel.HIGH,
            file_size=len(custom_content),
            magic_description="Custom vault backup file"
        )

        routing_decision = self.router.route_file(mock_analysis)
        assert routing_decision.target_processor == "backup_processor"

    def test_error_handling_workflow(self):
        """Test error handling throughout the analysis workflow."""
        # Test with corrupted/empty file
        empty_file = self.create_test_file("empty.dat", b'')

        # Analysis should handle empty files gracefully
        analysis_result = self.analyzer.analyze_file(empty_file)
        assert isinstance(analysis_result, AnalysisResult)

        # Validation should work even with generic types
        validation_result = self.validator.validate_extension(
            empty_file, analysis_result.detected_mime_type
        )
        assert isinstance(validation_result, ValidationResult)

        # Routing should provide fallback
        routing_decision = self.router.route_file(analysis_result)
        assert routing_decision.target_processor is not None

    def test_integration_with_file_size_limits(self):
        """Test analysis workflow with large files."""
        # Create larger test file (simulate large file without using too much memory)
        large_content = b'\xff\xd8\xff\xe0\x00\x10JFIF' + (b'A' * 10000) + b'\xff\xd9'
        file_path = self.create_test_file("large_image.jpg", large_content)

        # Analysis should handle large files efficiently
        start_time = time.time()
        analysis_result = self.analyzer.analyze_file(file_path)
        analysis_time = time.time() - start_time

        # Should still detect correctly and complete quickly
        assert "image/jpeg" in analysis_result.detected_mime_type
        assert analysis_time < 0.5  # Should complete in under 500ms
        assert analysis_result.file_size > 10000

        # Rest of workflow should work normally
        validation_result = self.validator.validate_extension(
            file_path, analysis_result.detected_mime_type
        )
        routing_decision = self.router.route_file(analysis_result)

        assert validation_result.is_valid is True
        assert routing_decision.target_processor == "image_processor"

    def test_metadata_extraction_workflow(self):
        """Test metadata extraction throughout the workflow."""
        # Create JPEG with some content for metadata extraction
        jpeg_with_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xe1\x00\x22Exif\x00\x00II*\x00\x08\x00\x00\x00\x01\x00'
            b'\x12\x01\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00'  # Basic EXIF
            b'\xff\xd9'  # End of image
        )
        file_path = self.create_test_file("with_metadata.jpg", jpeg_with_data)

        # Analysis should extract metadata
        analysis_result = self.analyzer.analyze_file(file_path)

        assert analysis_result.metadata is not None
        assert len(analysis_result.metadata) > 0
        assert 'content_length' in analysis_result.metadata
        assert 'has_magic_signature' in analysis_result.metadata

        # Metadata should indicate JPEG signature
        assert analysis_result.metadata['has_magic_signature'] is True