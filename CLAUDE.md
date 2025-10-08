# vault-of-memories Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-08

## Active Technologies

**Language/Version**: Python 3.11
**Primary Dependencies**:
- Python standard library (os, pathlib, datetime, threading)
- pathvalidate (v3.3.1+) - cross-platform filename validation
- python-magic - MIME type detection
- Existing: MetadataConsolidator (feature 008)

**Storage**: Filesystem-based vault structure
**Testing**: pytest (contract, integration, unit tests)
**Project Type**: Single project (CLI-based)

## Project Structure
```
src/
├── models/          # Data models (VaultPath, Classification, DateInfo, etc.)
├── services/        # Core services (OrganizationManager, ClassificationEngine, etc.)
├── cli/            # Command-line interface
└── lib/            # Shared utilities

tests/
├── contract/       # Contract tests
├── integration/    # Integration tests
└── unit/          # Unit tests
```

## Key Concepts

### Organization Manager (010-organization-manager)
- Determines file placement in vault structure
- Applies content classification rules (photos, documents, videos, audio, archives)
- Creates date-based folder hierarchy (YYYY/YYYY-MM/YYYY-MM-DD)
- Handles cross-platform compatibility (Windows, macOS, Linux)
- Thread-safe parallel processing

### Classification Strategy
- Multi-level fallback: MIME → extension → header inspection → default
- Priority rules: Raw > Source > Processed > Derivative > Compressed
- Configurable classification rules

### Date Extraction
- Fallback cascade: EXIF DateTimeOriginal → file creation → modification → filename parsing
- UTC storage with timezone awareness
- Original local date for folder organization (user-friendly)

## Commands
```bash
# Create organization plan
/plan 010-organization-manager

# Generate tasks
/tasks

# Run implementation
/implement
```

## Code Style
- Python 3.11 type hints (use `str | None` not `Optional[str]`)
- Dataclasses for models
- Pathlib for all filesystem operations
- Explicit error handling with logging
- Cross-platform compatibility (Windows, macOS, Linux)

## Constitution Compliance
- **Simplicity First**: Use standard library where possible
- **Dependency Minimalism**: Only pathvalidate and python-magic added
- **Industry Standards**: Follow vault organization patterns
- **Test-Driven**: Contract tests before implementation
- **Strategic Documentation**: Self-documenting code with clear naming

## Recent Changes
- 010-organization-manager: Added Organization Manager with cross-platform file organization, classification engine, and date extraction

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->