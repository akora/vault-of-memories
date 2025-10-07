# Implementation Plan: Metadata Extractor

## Overview
Implement a comprehensive metadata extraction and consolidation system that coordinates between specialized processors (image, document, audio, video), applies priority-based resolution rules, preserves timezone information, and standardizes manufacturer names through configurable mappings.

## Architecture Overview

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Image            │    │ Document         │    │ Audio            │
│ Processor        │    │ Processor        │    │ Processor        │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Metadata                │
                    │  Extractor               │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Priority                │
                    │  Resolver                │
                    └────────────┬─────────────┘
                                 │
         ┌───────────────────────┴────────────────────────┐
         │                       │                        │
┌────────▼─────────┐  ┌─────────▼────────┐   ┌──────────▼─────────┐
│ Timezone         │  │ Manufacturer     │   │ Metadata           │
│ Preserver        │  │ Standardizer     │   │ Consolidator       │
└──────────────────┘  └──────────────────┘   └────────────────────┘
```

## Implementation Phases

### Phase 8.1: Core Metadata Models (TDD)
**Duration**: 1 session
**Focus**: Define consolidated metadata structures and source tracking

**Components**:
- `ConsolidatedMetadata`: Unified metadata record from all sources
- `MetadataSource`: Enum for tracking metadata origins (EXIF, Filename, Filesystem, etc.)
- `MetadataField`: Individual field with value, source, and confidence
- `MetadataQuality`: Quality assessment with completeness and confidence scores

**Contracts**:
- `ConsolidatedMetadata` dataclass with all possible metadata fields
- Source tracking for each field
- Quality scoring interface

**Tests**:
- Metadata record creation and field access
- Source tracking validation
- Quality score calculation

### Phase 8.2: Priority Resolution Engine (TDD)
**Duration**: 1-2 sessions
**Focus**: Implement configurable priority-based conflict resolution

**Components**:
- `PriorityResolver`: Apply priority rules to resolve conflicts
- `ResolutionStrategy`: Different strategies for different field types
- `PriorityRuleEngine`: Configurable rule management
- Default priority: EXIF > Filename > Filesystem > Default

**Contracts**:
- `PriorityResolver` interface with `resolve_field()` method
- Configurable priority rules per field type
- Conflict detection and logging

**Tests**:
- Single source resolution (no conflict)
- Multi-source conflict resolution
- Priority rule application
- Custom priority configurations
- Edge cases (all sources None, conflicting data types)

### Phase 8.3: Timezone Preservation (TDD)
**Duration**: 1 session
**Focus**: Preserve original timezone without UTC conversion

**Components**:
- `TimezonePreserver`: Maintain timezone context
- `TimestampParser`: Parse timestamps with timezone awareness
- `TimezoneValidator`: Validate timezone information
- Handle missing timezone gracefully

**Contracts**:
- `TimezonePreserver` interface with `preserve_timezone()` method
- Timezone-aware timestamp storage
- Original timezone metadata retention

**Tests**:
- Timezone preservation from EXIF data
- Handling timestamps without timezone
- Multiple timezone formats
- Invalid timezone handling
- Timezone metadata extraction

### Phase 8.4: Manufacturer Standardization (TDD)
**Duration**: 1 session
**Focus**: Standardize manufacturer names using configurable mappings

**Components**:
- `ManufacturerStandardizer`: Normalize manufacturer names
- `ManufacturerMappingLoader`: Load mapping configuration
- Default mappings (NIKON CORPORATION → Nikon, etc.)
- Case-insensitive matching

**Contracts**:
- `ManufacturerStandardizer` interface with `standardize()` method
- Configurable mapping rules
- Fallback for unmapped manufacturers

**Tests**:
- Known manufacturer standardization
- Unknown manufacturer handling
- Case-insensitive matching
- Custom mapping configuration
- Multiple alias resolution

### Phase 8.5: Metadata Consolidator (TDD)
**Duration**: 1-2 sessions
**Focus**: Main orchestration service integrating all components

**Components**:
- `MetadataConsolidator`: Main service coordinating extraction
- Processor registry for image/document/audio/video processors
- Source aggregation from multiple processors
- Priority resolution application
- Quality assessment

**Contracts**:
- `MetadataConsolidator` interface with `consolidate()` method
- Processor registration and coordination
- Audit trail generation
- Quality scoring

**Tests**:
- Single processor consolidation
- Multi-processor consolidation
- Conflict resolution across sources
- Quality score calculation
- Missing processor handling
- Processor failure handling

### Phase 8.6: Integration & Configuration (TDD)
**Duration**: 1 session
**Focus**: Integration with existing processors and configuration system

**Integration**:
- Connect to existing image, document, audio, video processors
- Configuration file for priority rules
- Configuration file for manufacturer mappings
- Logging and audit trail

**Configuration Files**:
- `config/metadata_consolidation.json`: Priority rules per field
- `config/manufacturer_mappings.json`: Manufacturer standardization

**Tests**:
- End-to-end consolidation with real processors
- Configuration loading and application
- Audit trail validation

### Phase 8.7: Quality Assessment & Polish (TDD)
**Duration**: 1 session
**Focus**: Metadata quality scoring and final refinements

**Components**:
- `MetadataQualityAssessor`: Calculate quality scores
- Completeness scoring (% of fields populated)
- Confidence scoring (based on source reliability)
- Conflict flagging for manual review

**Activities**:
- Code review and refactoring
- Comprehensive documentation
- Error message improvements
- Performance optimization
- Final test suite validation

## Key Design Decisions

### 1. Priority Resolution Strategy
- **Default Priority**: EXIF > Filename > Filesystem > Default
- **Field-Specific Priority**: Configurable per field type
- **Conflict Logging**: All conflicts logged for audit
- **Resolution Strategies**:
  - Most Recent (for timestamps)
  - Highest Priority (default)
  - Manual Review Flag (for critical conflicts)

### 2. Timezone Handling
- **Preservation**: Store original timezone, never convert to UTC
- **Timezone-Aware**: Use timezone-aware datetime objects
- **Fallback**: When timezone missing, store as naive datetime with note
- **Metadata**: Track timezone source and confidence

### 3. Manufacturer Standardization
- **Mapping Configuration**: JSON file with aliases → standard name
- **Case Insensitive**: Normalize to lowercase for matching
- **Unknown Handling**: Keep original name, flag for review
- **Extensible**: Easy to add new mappings

### 4. Quality Assessment
- **Completeness Score**: Percentage of fields with values (0.0-1.0)
- **Confidence Score**: Weighted by source reliability (0.0-1.0)
- **Source Reliability Weights**:
  - EXIF: 1.0
  - Embedded Metadata: 0.9
  - Filename: 0.6
  - Filesystem: 0.4
  - Default/Inferred: 0.2

### 5. Audit Trail
- Track which processor provided each field
- Log all conflicts and resolutions
- Store metadata extraction timestamp
- Record quality scores

## Integration Points

### Existing Processors (Specs 004-007)
- Image Processor: EXIF, image classification
- Document Processor: PDF metadata, OCR detection
- Audio Processor: ID3 tags, quality classification
- Video Processor: Media info, content categorization

### Configuration System (Spec 002)
- Priority rules configuration
- Manufacturer mappings configuration
- Source reliability weights

### Future Components
- File Renamer (009): Consumes consolidated metadata
- Organization Manager (010): Uses metadata for folder structure
- File Mover (011): Coordinates with consolidated metadata

## Success Criteria

### Functional
- ✅ Consolidate metadata from image, document, audio, video processors
- ✅ Apply priority rules (EXIF > Filename > Filesystem)
- ✅ Preserve original timezone without UTC conversion
- ✅ Standardize manufacturer names using configurable mappings
- ✅ Provide unified metadata record for any file type
- ✅ Generate audit trail showing metadata sources
- ✅ Handle missing metadata gracefully
- ✅ Support custom priority rules through configuration

### Non-Functional
- ✅ Process consolidation without significant performance overhead
- ✅ Provide comprehensive logging for debugging
- ✅ Integrate seamlessly with existing processors
- ✅ Configuration-driven for easy customization

### Quality
- ✅ 100% test coverage with contract and integration tests
- ✅ Clear, documented interfaces for all components
- ✅ Robust error handling and recovery
- ✅ Quality scores for metadata completeness and confidence

## Dependencies

### External
- None (uses Python standard library)

### Internal
- Image processor (004) ✅
- Document processor (005) ✅
- Audio processor (006) ✅
- Video processor (007) ✅
- Configuration system (002) ✅

## Constitutional Compliance

- **[SF] Simplicity First**: No external dependencies, straightforward design
- **[DM] Dependency Minimalism**: Uses only standard library
- **[ISA] Industry Standards**: Follows metadata best practices
- **[TDT] Test-Driven**: 100% TDD with contracts before implementation
- **[SD] Strategic Documentation**: Self-documenting code with clear naming
- **[RP] Robust Programming**: Comprehensive error handling and edge case coverage
