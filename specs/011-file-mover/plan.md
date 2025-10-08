
# Implementation Plan: File Mover

**Branch**: `011-file-mover` | **Date**: 2025-10-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-file-mover/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (single project)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
The File Mover handles final file operations including moving files to vault locations, creating destination directories, handling duplicates and quarantine files, updating database records, and ensuring atomic operations to prevent data loss. It ensures data safety through transaction management, integrity verification, and comprehensive error handling.

## Technical Context
**Language/Version**: Python 3.11
**Primary Dependencies**: Python standard library (os, pathlib, shutil, hashlib), existing DatabaseManager, existing OrganizationManager
**Storage**: Filesystem-based vault structure with SQLite database tracking
**Testing**: pytest (contract, integration, unit tests)
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: single - determines source structure
**Performance Goals**: <200ms per file move, support parallel processing for batch operations, maintain ACID properties
**Constraints**: Atomic file operations, cross-platform compatibility, database consistency, rollback capability
**Scale/Scope**: Support vaults with 100k+ files, handle 1000+ files/batch, manage duplicates and quarantine efficiently

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle Compliance Review**:
- [x] **Simplicity First (SF)**: Uses standard filesystem operations (shutil.move2) and SQLite transactions, no complex storage systems
- [x] **Dependency Minimalism (DM)**: Only Python standard library (shutil, hashlib, contextlib) and existing components
- [x] **Industry Standards Adherence (ISA)**: Follows ACID transaction principles, uses standard file operation patterns
- [x] **Test-Driven Thinking (TDT)**: All move operations and edge cases designed with testability in mind
- [x] **Strategic Documentation (SD)**: Self-documenting service structure with clear separation of concerns
- [x] **Readability Priority (RP)**: Clear separation between move logic, transaction management, duplicate handling, and quarantine

**Digital Preservation Standards**:
- [x] Original data integrity preserved (file verification before and after move)
- [x] Operations are reversible or auditable (all moves logged, transaction rollback available)
- [x] Metadata and file moves are atomic (database records updated only when file move succeeds)

**Spec-Driven Development Workflow**:
- [x] Follows constitution → specify → plan → tasks → implement workflow

## Project Structure

### Documentation (this feature)
```
specs/011-file-mover/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Single project structure
src/
├── models/
│   ├── move_operation.py       # Move operation tracking model
│   ├── move_result.py          # Result of move operation
│   ├── duplicate_record.py     # Duplicate file tracking
│   └── quarantine_record.py    # Quarantine entry model
├── services/
│   ├── file_mover.py           # Main orchestration service
│   ├── atomic_mover.py         # Atomic file move operations
│   ├── duplicate_handler.py    # Duplicate file management
│   ├── quarantine_manager.py   # Quarantine operations
│   ├── integrity_verifier.py   # File integrity checking
│   └── transaction_manager.py  # Database transaction coordination
└── lib/
    └── file_utils.py           # Shared file utilities

tests/
├── contract/
│   ├── test_file_mover.py
│   ├── test_atomic_mover.py
│   ├── test_duplicate_handler.py
│   ├── test_quarantine_manager.py
│   └── test_integrity_verifier.py
├── integration/
│   ├── test_successful_move.py
│   ├── test_duplicate_handling.py
│   ├── test_quarantine_flow.py
│   └── test_transaction_rollback.py
└── unit/
    ├── test_move_operation.py
    ├── test_integrity_verification.py
    └── test_transaction_coordination.py
```

**Structure Decision**: Option 1 (single project) - CLI-based digital vault organizer

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Research atomic file move operations across platforms
   - Research transaction management patterns for file + database operations
   - Research file integrity verification strategies
   - Research duplicate detection and handling approaches
   - Research quarantine management best practices
   - Research rollback strategies for failed file operations

2. **Generate and dispatch research agents**:
   - Research atomic file operations (shutil.move2 vs os.rename, handling cross-device moves)
   - Research transaction patterns (contextmanager for filesystem + database coordination)
   - Research integrity verification (checksum strategies, performance considerations)
   - Research duplicate handling (content vs metadata comparison, storage strategies)
   - Research quarantine patterns (error classification, recovery workflows)
   - Research storage space validation (pre-flight checks, graceful degradation)

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all technical decisions documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - MoveOperation: Tracks source, destination, status, timestamps, checksums
   - MoveResult: Result of move operation with success/failure details
   - DuplicateRecord: Information about duplicate files and relationships
   - QuarantineRecord: Quarantine entry with error details and recovery info
   - TransactionContext: Context manager for coordinated file+database operations

2. **Generate API contracts** from functional requirements:
   - FileMover.move_file(source, destination, metadata) → MoveResult
   - FileMover.move_batch(operations) → List[MoveResult]
   - AtomicMover.execute_move(operation) → MoveResult
   - DuplicateHandler.handle_duplicate(file_hash, metadata) → DuplicateRecord
   - QuarantineManager.quarantine_file(file_path, error) → QuarantineRecord
   - IntegrityVerifier.verify_move(source_hash, dest_path) → bool
   - TransactionManager.execute(file_op, db_op) → Result

3. **Generate contract tests** from contracts:
   - One test file per service contract
   - Assert input/output contracts
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each acceptance scenario → integration test
   - Atomic operation tests
   - Rollback scenario tests
   - Concurrent operation tests

5. **Update CLAUDE.md incrementally**:
   - Add file mover tech stack
   - Update recent changes

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

The /tasks command will:
1. Load plan.md and extract tech stack, dependencies, structure
2. Load data-model.md and create model tasks (one per entity)
3. Load contracts/ and create contract test tasks (one per contract)
4. Load quickstart.md and create integration test tasks (one per scenario)
5. Create service implementation tasks in dependency order:
   - IntegrityVerifier (no dependencies)
   - AtomicMover (uses IntegrityVerifier)
   - DuplicateHandler (uses existing DuplicateDatabase)
   - QuarantineManager (no dependencies)
   - TransactionManager (coordinates all operations)
   - FileMover (orchestrates all services)
6. Mark parallel tasks with [P] (different files, no dependencies)
7. Order tasks: Setup → Tests → Models → Services → Integration → Polish
8. Generate task dependency graph
9. Output to tasks.md with exact file paths

**Phase 2 Output**: tasks.md (created by /tasks command)

## Phase 3-4: Implementation & Polish
*Executed after /tasks command, not part of /plan*

1. Execute tasks in dependency order
2. Run contract tests (verify they fail)
3. Implement models and services
4. Run contract tests (verify they pass)
5. Run integration tests
6. Add unit tests
7. Performance testing
8. Edge case handling
9. Documentation

## Progress Tracking
- [x] Feature spec loaded
- [x] Technical context filled
- [x] Initial constitution check passed
- [x] Phase 0: Research complete (research.md)
- [x] Phase 1: Design & contracts complete (data-model.md, contracts/, quickstart.md)
- [x] Post-design constitution check passed
- [x] Phase 2: Task planning approach documented
- [x] Ready for /tasks command

## Next Steps
1. Execute Phase 0 research
2. Execute Phase 1 design
3. Run constitution check
4. Ready for /tasks command
