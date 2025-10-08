# Implementation Plan: File Renamer

## Overview
Implement a comprehensive filename generation system that creates standardized, human-readable filenames using extracted metadata with configurable naming patterns, collision detection, length handling, and intelligent sanitization.

## Architecture Overview

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Consolidated     │───▶│ Naming Pattern   │───▶│ Filename         │
│ Metadata         │    │ Engine           │    │ Generator        │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                │                         │
                    ┌───────────┴──────────┐  ┌──────────▼──────────┐
                    ▼                      ▼  ▼                     ▼
           ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
           │ Metadata        │  │ Collision       │  │ Length           │
           │ Sanitizer       │  │ Detector        │  │ Limiter          │
           └─────────────────┘  └─────────────────┘  └──────────────────┘
```

## Implementation Phases

### Phase 9.1: Naming Pattern Engine (TDD)
**Duration**: 1-2 sessions
**Focus**: Template-based filename generation with metadata components

**Components**:
- `NamingPatternEngine`: Parse and apply naming pattern templates
- `PatternTemplate`: Define pattern syntax and component placeholders
- `ComponentFormatter`: Format metadata values for filename use
- Pattern syntax: `{date}`, `{time}`, `{device}`, `{size}`, `{resolution}`, etc.

**Contracts**:
- `NamingPatternEngine` interface with `apply_pattern()` method
- Template parsing and validation
- Component substitution with metadata

**Tests**:
- Pattern parsing and validation
- Component substitution
- Multiple file type patterns
- Missing component handling

**Pattern Examples**:
- Image: `{date}-{time}-{device_make}-{device_model}-ir{resolution}-s{size_kb}`
- Document: `{date}-{title}-p{page_count}-s{size_kb}`
- Audio: `{date}-{artist}-{title}-br{bitrate}`
- Video: `{date}-{time}-{resolution_label}-{category}-s{size_mb}`

### Phase 9.2: Metadata Sanitization (TDD)
**Duration**: 1 session
**Focus**: Clean metadata values for safe filename use

**Components**:
- `MetadataSanitizer`: Remove invalid filename characters
- `CharacterReplacer`: Replace problematic characters with safe alternatives
- `WhitespaceNormalizer`: Handle spaces and special whitespace
- Platform-specific restrictions (Windows, macOS, Linux)

**Contracts**:
- `MetadataSanitizer` interface with `sanitize()` method
- Character replacement rules
- Whitespace handling

**Tests**:
- Invalid character removal
- Special character replacement
- Unicode handling
- Platform-specific restrictions
- Whitespace normalization

**Sanitization Rules**:
- Replace spaces with hyphens
- Remove/replace: `/ \ : * ? " < > |`
- Handle Unicode characters
- Limit consecutive separators
- Trim leading/trailing separators

### Phase 9.3: Collision Detection (TDD)
**Duration**: 1 session
**Focus**: Ensure filename uniqueness across the vault

**Components**:
- `CollisionDetector`: Check for filename conflicts
- `FilenameRegistry`: Track existing filenames in vault
- `CounterGenerator`: Generate 8-digit zero-padded counters
- Collision resolution with suffixes

**Contracts**:
- `CollisionDetector` interface with `check_collision()` method
- Counter generation (00000001, 00000002, etc.)
- Filename registration

**Tests**:
- Collision detection
- Counter generation
- Multiple collisions
- Registry management
- Edge cases (counter overflow)

### Phase 9.4: Length Limitation (TDD)
**Duration**: 1 session
**Focus**: Handle filesystem filename length constraints

**Components**:
- `LengthLimiter`: Enforce maximum filename length
- `TruncationStrategy`: Intelligently shorten filenames
- `ComponentPriority`: Determine which components to truncate
- Default limit: 255 characters (common filesystem limit)

**Contracts**:
- `LengthLimiter` interface with `limit_length()` method
- Truncation strategies (truncate middle, drop low-priority components)
- Extension preservation

**Tests**:
- Length enforcement
- Intelligent truncation
- Component priority
- Extension preservation
- Edge cases (very long metadata)

**Truncation Strategy**:
1. Drop optional components (category, secondary device info)
2. Truncate long device model names
3. Shorten middle of remaining components with "..."
4. Always preserve: date, extension, counter

### Phase 9.5: Filename Generator (TDD)
**Duration**: 1-2 sessions
**Focus**: Main orchestration service integrating all components

**Components**:
- `FilenameGenerator`: Main service coordinating filename generation
- Pattern application → Sanitization → Collision check → Length limit
- Fallback strategies for missing metadata
- Preview mode support

**Contracts**:
- `FilenameGenerator` interface with `generate()` method
- Preview mode (no side effects)
- Audit logging

**Tests**:
- End-to-end generation
- Missing metadata handling
- Collision resolution
- Length limiting
- Preview mode
- Audit logging

### Phase 9.6: Configuration & Integration (TDD)
**Duration**: 1 session
**Focus**: Configuration and integration with metadata consolidator

**Integration**:
- Connect to MetadataConsolidator (008)
- Load naming patterns from configuration
- File type specific patterns
- Configurable component formatters

**Configuration Files**:
- `config/naming_patterns.json`: Patterns per file type
- `config/filename_sanitization.json`: Sanitization rules
- `config/truncation_rules.json`: Component priorities

**Tests**:
- Configuration loading
- Pattern selection by file type
- Integration with metadata consolidator
- End-to-end workflow

### Phase 9.7: Polish & Documentation (TDD)
**Duration**: 1 session
**Focus**: Code cleanup and final validation

**Activities**:
- Code review and refactoring
- Comprehensive documentation
- Error message improvements
- Performance optimization
- Final test suite validation

## Key Design Decisions

### 1. Pattern Syntax
- **Placeholder Format**: `{component_name}`
- **Supported Components**:
  - Date/Time: `{date}`, `{time}`, `{year}`, `{month}`, `{day}`
  - Device: `{device_make}`, `{device_model}`, `{device}`
  - Technical: `{width}`, `{height}`, `{resolution}`, `{resolution_label}`
  - Size: `{size_kb}`, `{size_mb}`, `{size_bytes}`
  - Content: `{title}`, `{category}`, `{author}`
  - Audio/Video: `{duration}`, `{bitrate}`, `{fps}`
  - Counters: `{counter}`
- **Conditional Components**: Components missing in metadata are omitted

### 2. Sanitization Strategy
- **Character Replacement**: Map unsafe → safe characters
- **Whitespace Handling**: Replace with hyphens
- **Unicode Support**: Allow most Unicode, normalize forms
- **Platform Safety**: Strictest common rules (Windows-compatible)

### 3. Collision Resolution
- **8-Digit Counters**: `{base}-{counter}.ext` where counter is `00000001`
- **Counter Placement**: Before file extension
- **Registry**: In-memory during session, persistent across runs via database
- **Scope**: Unique across entire vault

### 4. Length Handling
- **Max Length**: 255 characters (filesystem limit)
- **Truncation Priority** (lowest to highest):
  1. Drop category/secondary metadata
  2. Truncate long device models
  3. Shorten middle components
  4. Never truncate: date, extension, counter
- **Extension**: Always preserved

### 5. Fallback Naming
When metadata is insufficient:
- Use original filename (sanitized)
- Add timestamp from file system
- Add checksum prefix for uniqueness
- Pattern: `{checksum_short}-{original_name_sanitized}`

## Integration Points

### Metadata Consolidator (Spec 008)
- Receives ConsolidatedMetadata with all extracted fields
- Uses metadata fields to populate pattern components
- Relies on source priority already resolved

### Configuration System (Spec 002)
- Load naming patterns from JSON
- Load sanitization rules
- Load truncation priorities

### Future Components
- Organization Manager (010): Uses generated filenames for folder structure
- File Mover (011): Applies generated filenames during move operations

## Success Criteria

### Functional
- ✅ Generate human-readable filenames using metadata
- ✅ Apply configurable naming patterns per file type
- ✅ Ensure uniqueness with 8-digit counters
- ✅ Handle length limits intelligently
- ✅ Sanitize metadata for safe filenames
- ✅ Preserve file extensions
- ✅ Support preview mode
- ✅ Log all renaming operations

### Non-Functional
- ✅ Process filename generation efficiently
- ✅ Provide comprehensive logging for debugging
- ✅ Configuration-driven for easy customization
- ✅ Cross-platform compatible (Windows, macOS, Linux)

### Quality
- ✅ 100% test coverage with contract and integration tests
- ✅ Clear, documented interfaces for all components
- ✅ Robust error handling and recovery
- ✅ Validation of all generated filenames

## Dependencies

### External
- None (uses Python standard library)

### Internal
- Metadata consolidator (008) ✅
- Configuration system (002) ✅

## Constitutional Compliance

- **[SF] Simplicity First**: No external dependencies, straightforward design
- **[DM] Dependency Minimalism**: Uses only standard library
- **[ISA] Industry Standards**: Follows filesystem naming best practices
- **[TDT] Test-Driven**: 100% TDD with contracts before implementation
- **[SD] Strategic Documentation**: Self-documenting code with clear naming
- **[RP] Robust Programming**: Comprehensive error handling and edge cases
