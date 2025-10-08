# vault-of-memories Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-08

## Active Technologies

**Language/Version**: Python 3.11
**Primary Dependencies**:
- Python standard library (argparse, logging, pathlib, signal, os, datetime, threading)
- pathvalidate (v3.3.1+) - cross-platform filename validation
- python-magic - MIME type detection
- Existing vault modules (FileIngestor, MetadataConsolidator, OrganizationManager, FileMover)

**Storage**: Filesystem-based vault structure
**Testing**: pytest (contract, integration, unit tests)
**Project Type**: Single project (CLI-based)

## Project Structure
```
src/
├── models/          # Data models (VaultPath, Classification, DateInfo, etc.)
├── services/        # Core services (OrganizationManager, ClassificationEngine, etc.)
├── cli/            # Command-line interface (Feature 013)
│   ├── commands/   # Command implementations (process, status, recover)
│   └── formatters/ # Output formatting (progress, summary)
└── lib/            # Shared utilities

tests/
├── contract/       # Contract tests
├── integration/    # Integration tests
└── unit/          # Unit tests
```

## Key Concepts

### CLI Interface (013-cli-interface)
- Orchestrates complete vault processing pipeline
- Provides real-time progress feedback with callback pattern
- Generates comprehensive processing summaries
- Handles graceful interruption (SIGINT/SIGTERM)
- Supports dry-run mode for preview
- Uses stdlib argparse (zero external dependencies)

### Pipeline Stages
```
Validation → Discovery → Ingestion → Extraction → Consolidation →
Renaming → Organization → Moving → Summary
```

### Organization Manager (010-organization-manager)
- Determines file placement in vault structure
- Applies content classification rules (photos, documents, videos, audio, archives)
- Creates date-based folder hierarchy (YYYY/YYYY-MM/YYYY-MM-DD)
- Handles cross-platform compatibility (Windows, macOS, Linux)
- Thread-safe parallel processing

### File Mover (011-file-mover)
- Atomic file operations with cross-device support
- SHA256 integrity verification
- Automatic rollback on failure
- Duplicate detection and handling
- 9-type quarantine error classification

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
# Main processing command
vault process <source> [--vault-root PATH] [--dry-run] [--verbose]

# Status/recovery commands
vault status [--vault-root PATH]
vault recover [--vault-root PATH] [--quarantine-type TYPE]

# Utility commands
vault validate <source>  # Check files before processing
vault help [command]     # Detailed help

# Development commands
/plan <feature-id>       # Create implementation plan
/tasks                   # Generate task breakdown
/implement               # Execute implementation
```

## Code Style
- Python 3.11 type hints (use `str | None` not `Optional[str]`)
- Dataclasses for models
- Pathlib for all filesystem operations
- Explicit error handling with logging
- Cross-platform compatibility (Windows, macOS, Linux)
- Follow POSIX CLI conventions and standard exit codes

## Constitution Compliance
- **Simplicity First**: Use standard library where possible
- **Dependency Minimalism**: Only pathvalidate and python-magic added
- **Industry Standards**: Follow vault organization patterns
- **Test-Driven**: Contract tests before implementation
- **Strategic Documentation**: Self-documenting code with clear naming

## Recent Changes
- 013-cli-interface: Added CLI orchestration with argparse-based interface, progress monitoring, and command structure
- 011-file-mover: Added File Mover with atomic operations, integrity verification, and quarantine management
- 010-organization-manager: Added Organization Manager with cross-platform file organization, classification engine, and date extraction

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
