# Implementation Plan: Image Processor

## Overview
Implement a robust image processing system that extracts comprehensive metadata using exiftool, distinguishes camera photos from graphics, classifies raw vs processed formats, and preserves original timestamps.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Type       │───▶│ Image            │───▶│ Metadata        │
│ Analyzer        │    │ Processor        │    │ Consolidator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ ExifTool         │
                       │ Wrapper          │
                       └──────────────────┘
```

## Implementation Phases

### Phase 4.1: Core Metadata Extraction (TDD)
**Duration**: 1-2 sessions
**Focus**: ExifTool integration and metadata extraction

**Components**:
- `ImageProcessor`: Main processor interface and implementation
- `ExifToolWrapper`: Abstraction layer for exiftool CLI
- `ImageMetadata`: Type-safe metadata model

**Contracts**:
- `ImageProcessor` interface with `process_image()` method
- `ImageMetadata` dataclass with all extracted fields
- Error handling for missing exiftool or corrupted images

**Tests**:
- Contract tests for JPEG, PNG, TIFF, RAW formats
- EXIF extraction accuracy tests
- Error handling for corrupted/missing files

### Phase 4.2: Classification System (TDD)
**Duration**: 1 session
**Focus**: Photo vs graphic and raw vs processed classification

**Components**:
- `ImageClassifier`: Classify images by type and format
- `CameraPhotoDetector`: Identify camera photos via EXIF
- `RawFormatDetector`: Identify RAW formats

**Contracts**:
- `ImageClassifier` interface with `classify_image()` method
- Classification result with confidence levels
- Camera information extraction

**Tests**:
- Camera photo detection (with/without EXIF)
- RAW format detection (CR2, NEF, ARW, DNG, etc.)
- Graphics classification (screenshots, logos, etc.)

### Phase 4.3: Timestamp Handling (TDD)
**Duration**: 1 session
**Focus**: Extract and prioritize multiple timestamp sources

**Components**:
- `TimestampExtractor`: Extract all available timestamps
- `TimestampPrioritizer`: Determine best creation timestamp
- Priority order: EXIF DateTimeOriginal > CreateDate > FileModifyDate

**Contracts**:
- `TimestampExtractor` interface with `extract_timestamps()` method
- Timestamp collection with source attribution
- Fallback to file system timestamps

**Tests**:
- EXIF timestamp extraction
- Timestamp priority resolution
- Timezone handling
- Missing timestamp scenarios

### Phase 4.4: Integration & Performance (TDD)
**Duration**: 1 session
**Focus**: Integration with file type analyzer and performance optimization

**Integration**:
- Connect to `ProcessorRouter` from spec 003
- Register image processor for image MIME types
- Maintain consistent metadata output format

**Performance**:
- Batch processing optimization
- Caching for repeated exiftool calls
- Memory-efficient handling of large images

**Tests**:
- End-to-end integration tests
- Performance benchmarks
- Memory usage validation

### Phase 4.5: Polish & Documentation (TDD)
**Duration**: 1 session
**Focus**: Code cleanup, documentation, and final validation

**Activities**:
- Code review and refactoring
- Comprehensive documentation
- Error message improvements
- Configuration integration
- Final test suite validation

## Key Design Decisions

### 1. ExifTool Over Pillow
- Use exiftool as external dependency for comprehensive metadata extraction
- Supports all image formats including RAW files
- More reliable EXIF parsing than pure Python libraries
- Wrapper class abstracts CLI interaction

### 2. Camera Photo Detection Strategy
- Primary: Check for camera-specific EXIF tags (Make, Model, etc.)
- Secondary: Verify presence of photography-specific metadata (aperture, shutter speed, ISO)
- Fallback: Classify as graphic if no camera metadata present

### 3. RAW Format Handling
- Whitelist-based detection using file extensions (.CR2, .NEF, .ARW, .DNG, etc.)
- Extract embedded preview/thumbnail if available
- Use exiftool's RAW format support

### 4. Timestamp Priority
1. EXIF DateTimeOriginal (when photo was taken)
2. EXIF CreateDate (when file was created)
3. EXIF DateTimeDigitized (when scanned/digitized)
4. File system ModifyDate (last resort)

### 5. Error Resilience
- Graceful handling of missing exiftool
- Partial metadata extraction on corrupted EXIF
- Detailed error reporting and logging
- Quarantine system for unprocessable images

## Integration Points

### File Type Analyzer (Spec 003)
- Receives images routed by `ProcessorRouter`
- Uses detected MIME type to validate image format
- Returns standardized metadata to consolidator

### Configuration System (Spec 002)
- Configurable RAW format extensions
- Configurable timestamp priority order
- Configurable privacy settings (GPS stripping)
- Performance tuning parameters

### Metadata Consolidator (Future)
- Provides extracted metadata in standard format
- Participates in priority-based metadata merging
- Feeds into filename generation system

## Success Criteria

### Functional
- ✅ Extract EXIF metadata from JPEG, PNG, TIFF, RAW formats
- ✅ Distinguish camera photos from graphics (>95% accuracy)
- ✅ Classify RAW vs processed formats correctly
- ✅ Extract and prioritize timestamps correctly
- ✅ Handle corrupted/incomplete metadata gracefully

### Non-Functional
- ✅ Process images efficiently without loading full image data
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
- `exiftool`: Core metadata extraction tool (CLI)
- Python wrapper for exiftool subprocess calls

### Internal
- File type analyzer (003) ✅
- Configuration system (002) ✅
- File ingestion system (001) ✅

## Constitutional Compliance

- **[SF] Single Function**: Each component has one clear responsibility
- **[DM] Dependency Management**: Minimal dependencies (exiftool only)
- **[ISA] Interface Separation**: Abstract contracts define all component interactions
- **[TDT] Test-Driven**: 100% TDD with contracts written before implementation
- **[SD] System Design**: Modular architecture with proper abstraction layers
- **[RP] Robust Programming**: Comprehensive error handling and edge case coverage
