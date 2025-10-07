# Implementation Plan: Audio Processor

## Overview
Implement a comprehensive audio processing system that handles various audio formats (MP3, FLAC, M4A, OGG, WMA) with ID3 tag extraction, metadata extraction, quality classification, and consistent standardized output across all formats.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Type       │───▶│ Audio            │───▶│ Metadata        │
│ Analyzer        │    │ Processor        │    │ Consolidator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌─────────────────┐  ┌──────────────────┐
           │ Tag Extractor   │  │ Quality          │
           │ (mutagen)       │  │ Classifier       │
           └─────────────────┘  └──────────────────┘
```

## Implementation Phases

### Phase 6.1: Core Audio Metadata Extraction (TDD)
**Duration**: 1-2 sessions
**Focus**: Audio metadata extraction using mutagen for all common formats

**Components**:
- `AudioProcessor`: Main processor interface and implementation
- `TagExtractor`: ID3 and metadata tag extraction using mutagen
- `AudioMetadata`: Type-safe metadata model
- Format handlers for MP3, FLAC, M4A, OGG, WMA

**Contracts**:
- `AudioProcessor` interface with `process_audio()` method
- `AudioMetadata` dataclass with all extracted fields
- Error handling for corrupted/unsupported audio files

**Tests**:
- Contract tests for MP3, FLAC, M4A, OGG, WMA formats
- Metadata extraction accuracy tests
- Error handling for corrupted/incomplete files

### Phase 6.2: Technical Specifications Extraction (TDD)
**Duration**: 1 session
**Focus**: Duration, bitrate, sample rate, channels, and format information

**Components**:
- `TechnicalAnalyzer`: Extract audio technical specifications
- `DurationExtractor`: Accurate duration calculation
- `BitrateAnalyzer`: Bitrate and quality metrics
- `FormatDetector`: Audio format and codec identification

**Contracts**:
- `TechnicalAnalyzer` interface with `analyze_audio()` method
- Technical specifications with accuracy validation
- Handling of variable bitrate (VBR) vs constant bitrate (CBR)

**Tests**:
- Duration extraction accuracy
- Bitrate calculation for CBR and VBR files
- Sample rate and channel detection
- Format and codec identification

### Phase 6.3: Quality Classification System (TDD)
**Duration**: 1 session
**Focus**: Audio quality classification based on bitrate, format, and compression

**Components**:
- `QualityClassifier`: Classify audio quality (lossy/lossless, high/medium/low)
- `CompressionDetector`: Identify compression type and level
- Classification criteria:
  - Lossless: FLAC, WAV, ALAC
  - High Quality: MP3 ≥320kbps, M4A ≥256kbps
  - Medium Quality: MP3 128-319kbps, M4A 128-255kbps
  - Low Quality: <128kbps

**Contracts**:
- `QualityClassifier` interface with `classify_quality()` method
- Classification result with confidence levels
- Configurable quality thresholds

**Tests**:
- Lossless format detection
- High/medium/low quality classification
- VBR quality calculation
- Edge case handling

### Phase 6.4: Integration & Performance (TDD)
**Duration**: 1 session
**Focus**: Integration with processor router and performance optimization

**Integration**:
- Connect to `ProcessorRouter` from spec 003
- Register audio processor for audio MIME types
- Maintain consistent metadata output format

**Performance**:
- Efficient processing without loading entire audio files
- Caching for repeated audio file processing
- Memory-efficient handling of large audio files

**Tests**:
- End-to-end integration tests
- Performance benchmarks
- Memory usage validation

### Phase 6.5: Polish & Documentation (TDD)
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
- **mutagen**: Universal audio metadata library supporting all major formats
- Handles ID3v1, ID3v2, Vorbis comments, MP4 tags, APE tags
- Single library for all formats reduces complexity and dependencies

### 2. Tag Format Handling
- ID3v2 prioritized over ID3v1 when both present
- Vorbis comments for FLAC and OGG
- MP4 tags for M4A/AAC
- Unified output regardless of source tag format

### 3. Quality Classification Strategy
- Primary: Format type (lossless > lossy)
- Secondary: Bitrate (for lossy formats)
- Tertiary: Sample rate and bit depth
- Configurable thresholds via configuration system

### 4. Missing Metadata Handling
- Extract available technical information even if tags missing
- Return partial metadata with flags for missing fields
- Log missing metadata for user attention
- Do not fail processing for incomplete metadata

### 5. Error Resilience
- Graceful handling of corrupted audio files
- Partial metadata extraction when possible
- Detailed error reporting and logging
- Quarantine system for unprocessable files

## Integration Points

### File Type Analyzer (Spec 003)
- Receives audio files routed by `ProcessorRouter`
- Uses detected MIME type to select appropriate handler
- Returns standardized metadata to consolidator

### Configuration System (Spec 002)
- Configurable quality thresholds
- Configurable format mappings
- Performance tuning parameters
- Tag extraction preferences

### Metadata Consolidator (Future)
- Provides extracted metadata in standard format
- Participates in priority-based metadata merging
- Feeds into filename generation system

## Success Criteria

### Functional
- ✅ Extract metadata from MP3, FLAC, M4A, OGG, WMA formats
- ✅ Extract duration, bitrate, sample rate, channels
- ✅ Extract artist, album, title, track number, year, genre
- ✅ Classify audio quality (lossless/lossy, high/medium/low)
- ✅ Handle missing metadata gracefully
- ✅ Support multiple tag formats (ID3, Vorbis, MP4)

### Non-Functional
- ✅ Process audio files efficiently without loading full content
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
- `mutagen`: Universal audio metadata library

### Internal
- File type analyzer (003) ✅
- Configuration system (002) ✅
- File ingestion system (001) ✅

## Constitutional Compliance

- **[SF] Single Function**: Each component has one clear responsibility
- **[DM] Dependency Management**: Single external dependency (mutagen)
- **[ISA] Interface Separation**: Abstract contracts define all component interactions
- **[TDT] Test-Driven**: 100% TDD with contracts written before implementation
- **[SD] System Design**: Modular architecture with proper abstraction layers
- **[RP] Robust Programming**: Comprehensive error handling and edge case coverage
