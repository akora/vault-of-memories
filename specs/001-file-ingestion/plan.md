# Implementation Plan: File Ingestion System

**Branch**: `001-file-ingestion` | **Date**: 2025-09-19 | **Spec**: [specs/001-file-ingestion/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-file-ingestion/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

## Summary
File ingestion system that accepts various input types (single files, multiple files, nested folders), calculates SHA-256 checksums, detects duplicates using SQLite database, filters system files, and routes clean files to processing pipeline. Core foundation component for vault processing workflow.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: hashlib (stdlib), sqlite3 (stdlib), os/pathlib (stdlib)
**Storage**: SQLite database for duplicate detection and file tracking
**Testing**: pytest with comprehensive test coverage
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: single - command-line tool with modular libraries
**Performance Goals**: Handle large file collections (10k+ files) efficiently
**Constraints**: Must preserve file timestamps, handle permission errors gracefully
**Scale/Scope**: Process nested directory structures without depth limits

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle Compliance Review**:
- [x] **Simplicity First (SF)**: Uses Python stdlib for core operations, minimal external dependencies
- [x] **Dependency Minimalism (DM)**: Leverages hashlib, sqlite3, os/pathlib from standard library
- [x] **Industry Standards Adherence (ISA)**: Uses SHA-256 (industry standard), SQLite (widely adopted)
- [x] **Test-Driven Thinking (TDT)**: All interfaces designed for testability
- [x] **Strategic Documentation (SD)**: Code is self-documenting, external docs minimal
- [x] **Readability Priority (RP)**: Clear module structure reflecting problem domain

**Digital Preservation Standards**:
- [x] Original data integrity preserved
- [x] Operations are reversible or auditable
- [x] Metadata extraction does not modify source files

**Spec-Driven Development Workflow**:
- [x] Follows constitution → specify → plan → tasks → implement workflow

## Project Structure

### Documentation (this feature)
```
specs/001-file-ingestion/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: DEFAULT to Option 1 - single project with modular libraries

## Phase 0: Outline & Research

**Research Findings**:

### Python Standard Library Analysis
- **hashlib.sha256()**: Efficient cryptographic hashing, optimal for file integrity checking
- **sqlite3**: Built-in database support, perfect for duplicate tracking with ACID compliance
- **pathlib.Path**: Modern path handling, cross-platform compatibility
- **os.walk()**: Efficient recursive directory traversal for large file trees

### File Processing Patterns
- **Streaming checksum calculation**: Process files in chunks to handle large files without memory issues
- **Database schema design**: Simple table structure for file records with indexed checksum field
- **Error handling patterns**: Continue processing on individual file errors, log all issues

### Performance Considerations
- **Chunked file reading**: 64KB chunks for optimal I/O performance
- **Database batching**: Batch insert operations for better performance with large file sets
- **Memory management**: Generator patterns for processing large directory structures

**Output**: All technical unknowns resolved, standard library approach validated

## Phase 1: Design & Contracts

### Data Model
```python
# File Record Entity
FileRecord:
  - id: INTEGER PRIMARY KEY
  - file_path: TEXT UNIQUE
  - checksum: TEXT (SHA-256 hex)
  - file_size: INTEGER
  - modification_time: REAL (Unix timestamp)
  - created_at: REAL (Unix timestamp)
  - status: TEXT (pending, processed, duplicate, error)
```

### API Contracts

#### File Ingestion Interface
```python
class FileIngestor:
    def ingest_file(self, file_path: Path) -> FileRecord
    def ingest_directory(self, dir_path: Path, recursive: bool = True) -> List[FileRecord]
    def is_duplicate(self, checksum: str) -> bool
    def get_processing_stats() -> ProcessingStats
```

#### Database Interface
```python
class DuplicateDatabase:
    def initialize() -> None
    def add_file_record(record: FileRecord) -> None
    def find_by_checksum(checksum: str) -> Optional[FileRecord]
    def get_all_duplicates() -> List[FileRecord]
```

### Contract Tests
- **File ingestion contracts**: Test single file, multiple files, directory processing
- **Database contracts**: Test CRUD operations, duplicate detection, concurrent access
- **Error handling contracts**: Test permission errors, corrupted files, database failures

### Quickstart Validation
1. Initialize empty database
2. Process test directory with known files
3. Verify checksums calculated correctly
4. Confirm duplicate detection works
5. Validate system file filtering

**Output**: Contracts defined, failing tests written, data model specified

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load contracts from Phase 1 design docs
- Generate database setup tasks (schema, initialization)
- Create checksum calculation tasks (streaming, validation)
- Add duplicate detection tasks (database integration)
- Include system file filtering tasks
- Create integration tests for end-to-end flows

**Ordering Strategy**:
- TDD order: Database schema → Contract tests → Core services → Integration
- Dependency order: Database layer → Services layer → CLI interface
- Mark [P] for parallel execution where files are independent

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*