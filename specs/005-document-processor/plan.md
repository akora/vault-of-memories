# Implementation Plan: Document Processor

## Overview
Implement a comprehensive document processing system that handles PDF, Office documents, and text files with metadata extraction, page counting, classification (brochure vs ebook), and OCR detection capabilities.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Type       │───▶│ Document         │───▶│ Metadata        │
│ Analyzer        │    │ Processor        │    │ Consolidator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌─────────────────┐  ┌──────────────────┐
           │ PDF Analyzer    │  │ Office Document  │
           │                 │  │ Analyzer         │
           └─────────────────┘  └──────────────────┘
```

## Implementation Phases

### Phase 5.1: Core Document Metadata Extraction (TDD)
**Duration**: 1-2 sessions
**Focus**: PDF and Office document metadata extraction using PyPDF2 and python-docx

**Components**:
- `DocumentProcessor`: Main processor interface and implementation
- `PDFAnalyzer`: PDF-specific metadata and page count extraction
- `OfficeDocumentAnalyzer`: Word/Excel/PowerPoint metadata extraction
- `DocumentMetadata`: Type-safe metadata model

**Contracts**:
- `DocumentProcessor` interface with `process_document()` method
- `DocumentMetadata` dataclass with all extracted fields
- Error handling for corrupted/password-protected documents

**Tests**:
- Contract tests for PDF, DOCX, XLSX, TXT formats
- Metadata extraction accuracy tests
- Error handling for corrupted/protected files

### Phase 5.2: PDF Classification System (TDD)
**Duration**: 1 session
**Focus**: Page counting and brochure vs ebook classification

**Components**:
- `PDFClassifier`: Classify PDFs based on page count
- `PageCounter`: Accurate page counting for various PDF types
- Classification threshold: ≤5 pages = brochure, >5 pages = ebook

**Contracts**:
- `PDFClassifier` interface with `classify_pdf()` method
- Classification result with confidence levels
- Page count extraction with error handling

**Tests**:
- Page count accuracy for various PDFs
- Brochure classification (1-5 pages)
- Ebook classification (6+ pages)
- Corrupted PDF handling

### Phase 5.3: OCR Detection & Document Type Classification (TDD)
**Duration**: 1 session
**Focus**: Detect scanned vs digital-native documents

**Components**:
- `OCRDetector`: Identify scanned documents
- `DocumentTypeClassifier`: Digital-native vs scanned
- Detection based on: embedded fonts, text layers, image content ratio

**Contracts**:
- `OCRDetector` interface with `is_scanned()` method
- Confidence levels for detection
- Handling of hybrid documents (mixed scanned/digital pages)

**Tests**:
- Digital-native document detection
- Scanned document detection
- Hybrid document handling
- Detection confidence levels

### Phase 5.4: Integration & Performance (TDD)
**Duration**: 1 session
**Focus**: Integration with processor router and performance optimization

**Integration**:
- Connect to `ProcessorRouter` from spec 003
- Register document processor for document MIME types
- Maintain consistent metadata output format

**Performance**:
- Efficient processing without loading entire documents
- Caching for repeated document processing
- Memory-efficient handling of large documents

**Tests**:
- End-to-end integration tests
- Performance benchmarks
- Memory usage validation

### Phase 5.5: Polish & Documentation (TDD)
**Duration**: 1 session
**Focus**: Code cleanup, documentation, and final validation

**Activities**:
- Code review and refactoring
- Comprehensive documentation
- Error message improvements
- Configuration integration
- Final test suite validation

## Key Design Decisions

### 1. Library Selection
- **PyPDF2**: PDF metadata and page count extraction
- **python-docx**: Word document metadata
- **openpyxl**: Excel document metadata
- **python-pptx**: PowerPoint metadata (if needed)
- Fallback to exiftool for additional metadata

### 2. Brochure vs Ebook Classification
- Threshold: 5 pages
- Brochure: ≤5 pages (manuals, flyers, forms, receipts)
- Ebook: >5 pages (books, long documents, reports)
- Configurable threshold via configuration system

### 3. OCR Detection Strategy
- Primary: Check for embedded fonts and text layers
- Secondary: Analyze text-to-image ratio
- Tertiary: Check for typical scan artifacts
- Does NOT perform OCR - only detects if document is scanned

### 4. Password-Protected Document Handling
- Detect password protection without attempting to crack
- Return metadata with "password_protected" flag
- Do not process content, only file-level metadata
- Log as processing error for user attention

### 5. Error Resilience
- Graceful handling of corrupted documents
- Partial metadata extraction when possible
- Detailed error reporting and logging
- Quarantine system for unprocessable documents

## Integration Points

### File Type Analyzer (Spec 003)
- Receives documents routed by `ProcessorRouter`
- Uses detected MIME type to select appropriate analyzer
- Returns standardized metadata to consolidator

### Configuration System (Spec 002)
- Configurable page count thresholds
- Configurable document type mappings
- Performance tuning parameters
- OCR detection sensitivity settings

### Metadata Consolidator (Future)
- Provides extracted metadata in standard format
- Participates in priority-based metadata merging
- Feeds into filename generation system

## Success Criteria

### Functional
- ✅ Extract metadata from PDF, DOCX, XLSX, TXT formats
- ✅ Accurate page counting for PDFs
- ✅ Classify brochures vs ebooks correctly (>95% accuracy)
- ✅ Detect scanned vs digital-native documents
- ✅ Handle password-protected documents gracefully
- ✅ Extract author, title, creation date, modification date

### Non-Functional
- ✅ Process documents efficiently without loading full content
- ✅ Maintain memory usage under configured limits
- ✅ Integrate seamlessly with processor routing system
- ✅ Provide comprehensive logging and error reporting

### Quality
- ✅ 100% test coverage with contract and integration tests
- ✅ Clear, documented interfaces for all components
- ✅ Robust error handling and recovery
- ✅ Performance benchmarks and optimization

## Dependencies

### External
- `PyPDF2`: PDF metadata and page counting
- `python-docx`: Word document processing
- `openpyxl`: Excel document processing
- `python-pptx`: PowerPoint processing (optional)

### Internal
- File type analyzer (003) ✅
- Configuration system (002) ✅
- File ingestion system (001) ✅

## Constitutional Compliance

- **[SF] Single Function**: Each component has one clear responsibility
- **[DM] Dependency Management**: Minimal dependencies (standard document libraries)
- **[ISA] Interface Separation**: Abstract contracts define all component interactions
- **[TDT] Test-Driven**: 100% TDD with contracts written before implementation
- **[SD] System Design**: Modular architecture with proper abstraction layers
- **[RP] Robust Programming**: Comprehensive error handling and edge case coverage
