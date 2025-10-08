# Implementation Plan: Video Processor

## Overview
Implement a comprehensive video processing system that handles various video formats (MP4, AVI, MOV, MKV, WMV, WebM) with metadata extraction using pymediainfo, technical specifications extraction, and intelligent content categorization.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Type       │───▶│ Video            │───▶│ Metadata        │
│ Analyzer        │    │ Processor        │    │ Consolidator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌─────────────────┐  ┌──────────────────┐
           │ Media Info      │  │ Content          │
           │ Extractor       │  │ Categorizer      │
           └─────────────────┘  └──────────────────┘
```

## Implementation Phases

### Phase 7.1: Core Video Metadata Extraction (TDD)
**Duration**: 1-2 sessions
**Focus**: Video metadata extraction using pymediainfo for all common formats

**Components**:
- `VideoProcessor`: Main processor interface and implementation
- `MediaInfoExtractor`: Technical metadata extraction using pymediainfo
- `VideoMetadata`: Type-safe metadata model
- Format handlers for MP4, AVI, MOV, MKV, WMV, WebM

**Contracts**:
- `VideoProcessor` interface with `process_video()` method
- `VideoMetadata` dataclass with all extracted fields
- Error handling for corrupted/unsupported video files

**Tests**:
- Contract tests for MP4, AVI, MOV, MKV, WMV, WebM formats
- Metadata extraction accuracy tests
- Error handling for corrupted/incomplete files

### Phase 7.2: Technical Specifications Extraction (TDD)
**Duration**: 1 session
**Focus**: Duration, resolution, FPS, codec, and quality information

**Components**:
- `TechnicalAnalyzer`: Extract video technical specifications
- `ResolutionDetector`: Determine resolution (4K, 1080p, 720p, etc.)
- `CodecIdentifier`: Identify video/audio codecs
- `QualityAnalyzer`: Assess video quality metrics

**Contracts**:
- `TechnicalAnalyzer` interface with `analyze_video()` method
- Resolution classification with standard labels
- Codec and container format identification
- Handling of multiple audio/video streams

**Tests**:
- Duration extraction accuracy
- Resolution detection and classification
- FPS and bitrate calculation
- Codec identification for various formats

### Phase 7.3: Camera and Device Information Extraction (TDD)
**Duration**: 1 session
**Focus**: Extract camera, device, and location metadata when available

**Components**:
- `CameraInfoExtractor`: Extract camera and device metadata
- `GPSExtractor`: Parse GPS location data from video metadata
- `TimestampExtractor`: Extract creation dates and recording times
- Handle manufacturer-specific metadata formats

**Contracts**:
- `CameraInfoExtractor` interface with `extract_camera_info()` method
- GPS data extraction with coordinate validation
- Timestamp extraction from multiple metadata sources

**Tests**:
- Camera make/model extraction
- GPS coordinate parsing and validation
- Creation date extraction from various sources
- Handling of missing camera information

### Phase 7.4: Content Categorization System (TDD)
**Duration**: 1-2 sessions
**Focus**: Intelligent video categorization based on metadata patterns and content analysis

**Components**:
- `ContentCategorizer`: Classify videos into predefined categories
- `CategoryRuleEngine`: Apply pattern matching and heuristics
- Categories: family, tutorials, work, tech, entertainment, other
- Confidence scoring for category assignments

**Contracts**:
- `ContentCategorizer` interface with `categorize()` method
- Category result with confidence levels and reasoning
- Configurable categorization rules

**Tests**:
- Category detection for various video types
- Confidence scoring validation
- Multiple category suggestions
- Edge case handling (ambiguous content)

**Categorization Strategies**:
- **Family**: Phone/camera metadata, personal device names, vacation/event patterns
- **Tutorials**: Screen recording indicators, tutorial keywords, specific durations
- **Work**: Meeting indicators, presentation formats, corporate metadata
- **Tech**: Technical content indicators, developer tools, coding patterns
- **Entertainment**: Media file characteristics, downloaded content patterns
- **Other**: Fallback for uncategorized content

### Phase 7.5: Integration & Performance (TDD)
**Duration**: 1 session
**Focus**: Integration with processor router and performance optimization

**Integration**:
- Connect to `ProcessorRouter` from spec 003
- Register video processor for video MIME types
- Maintain consistent metadata output format

**Performance**:
- Efficient processing without loading entire video files
- Stream-based metadata extraction
- Memory-efficient handling of large video files (multi-GB)

**Tests**:
- End-to-end integration tests
- Performance benchmarks with large files
- Memory usage validation

### Phase 7.6: Polish & Documentation (TDD)
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
- **pymediainfo**: Comprehensive video metadata library
- Wrapper around MediaInfo CLI tool
- Supports all major video formats and codecs
- Extracts detailed technical specifications

### 2. Metadata Source Priority
1. **Embedded metadata**: Camera tags, EXIF data, proprietary formats
2. **Container metadata**: MP4/MKV metadata atoms
3. **Technical analysis**: Derived from stream analysis
4. **Filename patterns**: Last resort for categorization hints

### 3. Resolution Classification
- **4K/UHD**: 3840x2160 and above
- **1080p/Full HD**: 1920x1080
- **720p/HD**: 1280x720
- **480p/SD**: 720x480 or 640x480
- **Custom**: Non-standard resolutions with actual dimensions

### 4. Content Categorization Strategy
- **Pattern-based**: Analyze metadata patterns and indicators
- **Confidence-based**: Assign confidence scores (0.0-1.0)
- **Multi-category**: Support primary and secondary categories
- **Configurable**: Rules defined in configuration files
- **Extensible**: Easy to add new categories

### 5. Error Resilience
- Graceful handling of corrupted video files
- Partial metadata extraction when possible
- Detailed error reporting and logging
- Quarantine system for unprocessable files
- Handle videos with unusual structures (multi-stream, multi-angle)

## Integration Points

### File Type Analyzer (Spec 003)
- Receives videos routed by `ProcessorRouter`
- Uses detected MIME type to select appropriate handler
- Returns standardized metadata to consolidator

### Configuration System (Spec 002)
- Configurable categorization rules
- Configurable quality thresholds
- Performance tuning parameters
- Category pattern definitions

### Metadata Consolidator (Future)
- Provides extracted metadata in standard format
- Participates in priority-based metadata merging
- Feeds into filename generation system

## Success Criteria

### Functional
- ✅ Extract metadata from MP4, AVI, MOV, MKV, WMV, WebM formats
- ✅ Extract duration, resolution, FPS, bitrate, codec information
- ✅ Extract camera and device information when available
- ✅ Extract GPS location data when present
- ✅ Categorize videos into predefined categories with confidence scores
- ✅ Handle videos with multiple streams (audio/video/subtitles)
- ✅ Extract creation dates from multiple metadata sources

### Non-Functional
- ✅ Process videos efficiently without loading full content
- ✅ Handle large video files (>1GB) with memory constraints
- ✅ Integrate seamlessly with processor routing system
- ✅ Provide comprehensive logging and error reporting

### Quality
- ✅ 100% test coverage with contract and integration tests
- ✅ Clear, documented interfaces for all components
- ✅ Robust error handling and recovery
- ✅ Performance benchmarks for various file sizes

## Dependencies

### External
- `pymediainfo`: Video metadata extraction library
- Requires MediaInfo CLI tool to be installed on system

### Internal
- File type analyzer (003) ✅
- Configuration system (002) ✅
- File ingestion system (001) ✅

## Constitutional Compliance

- **[SF] Simplicity First**: Single external dependency (pymediainfo)
- **[DM] Dependency Minimalism**: Minimal dependencies, standard library preferred
- **[ISA] Industry Standards**: Follow video metadata standards (MP4, MKV, etc.)
- **[TDT] Test-Driven**: 100% TDD with contracts written before implementation
- **[SD] System Design**: Modular architecture with proper abstraction layers
- **[RP] Robust Programming**: Comprehensive error handling and edge case coverage
