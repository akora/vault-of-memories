# Implementation Plan: CLI Interface

**Branch**: `013-cli-interface` | **Date**: 2025-10-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-cli-interface/spec.md`

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
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file
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

Build a command-line interface that orchestrates the complete vault processing pipeline. The CLI will coordinate all existing processing modules (file ingestion, metadata extraction, organization, file moving) in the correct sequence, provide real-time progress feedback, generate processing summaries, handle errors gracefully, and support both interactive and batch processing modes.

## Technical Context
**Language/Version**: Python 3.11 (existing project standard)
**Primary Dependencies**:
- Python standard library (argparse, logging, pathlib, signal)
- Existing vault modules (FileIngestor, MetadataConsolidator, OrganizationManager, FileMover)
**Storage**: Filesystem-based vault structure (existing)
**Testing**: pytest (contract, integration, unit tests - existing)
**Target Platform**: Cross-platform CLI (macOS, Linux, Windows)
**Project Type**: Single project (CLI extension to existing codebase)
**Performance Goals**: Process 100 files in <20 seconds, real-time progress updates every 100ms
**Constraints**: Must work with existing vault structure, no external dependencies beyond stdlib
**Scale/Scope**: Single CLI entry point with ~5-8 subcommands, orchestrates existing 11 features

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle Compliance Review**:
- [x] **Simplicity First (SF)**: Uses stdlib argparse for CLI, leverages existing modules
- [x] **Dependency Minimalism (DM)**: Zero new external dependencies - stdlib only
- [x] **Industry Standards Adherence (ISA)**: Follows POSIX CLI conventions, standard exit codes
- [x] **Test-Driven Thinking (TDT)**: Contract tests for each command, integration tests for pipeline
- [x] **Strategic Documentation (SD)**: Self-documenting command structure, inline help text
- [x] **Readability Priority (RP)**: Clear command names, explicit orchestration logic

**Digital Preservation Standards**:
- [x] Original data integrity preserved (delegates to existing FileMover)
- [x] Operations are reversible or auditable (logging, dry-run mode)
- [x] Metadata extraction does not modify source files (existing behavior maintained)

**Spec-Driven Development Workflow**:
- [x] Follows constitution → specify → plan → tasks → implement workflow

## Project Structure

### Documentation (this feature)
```
specs/013-cli-interface/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/              # Existing + ProcessingContext, ProgressState
├── services/            # Existing + PipelineOrchestrator, ProgressMonitor
├── cli/                 # NEW: CLI module
│   ├── __init__.py
│   ├── main.py         # Entry point
│   ├── commands/       # Command implementations
│   │   ├── __init__.py
│   │   ├── process.py  # Main processing command
│   │   ├── status.py   # Status checking
│   │   └── recover.py  # Recovery command
│   └── formatters/     # Output formatting
│       ├── __init__.py
│       ├── progress.py # Progress display
│       └── summary.py  # Summary generation
└── lib/                 # Existing utilities

tests/
├── contract/            # Contract tests for CLI commands
├── integration/         # End-to-end pipeline tests
└── unit/               # Unit tests for formatters
```

**Structure Decision**: Option 1 (Single project) - extending existing vault codebase with CLI module

## Phase 0: Outline & Research

### Research Tasks

1. **CLI Framework Selection**
   - Decision: Python stdlib `argparse`
   - Rationale: Zero dependencies, full-featured, Python 3.11 compatible
   - Alternatives considered: Click (dependency), Typer (dependency)

2. **Progress Reporting Strategy**
   - Decision: Event-driven progress updates with callback pattern
   - Rationale: Allows real-time updates without blocking main processing
   - Alternatives considered: Polling (inefficient), Threading (complex)

3. **Pipeline Orchestration Pattern**
   - Decision: Sequential pipeline with dependency injection
   - Rationale: Clear flow, testable, aligns with existing architecture
   - Alternatives considered: Async/parallel (premature optimization)

4. **Signal Handling for Graceful Interruption**
   - Decision: Python signal module with cleanup handlers
   - Rationale: Standard approach, cross-platform
   - Alternatives considered: Custom interrupt handling (complex)

5. **Output Formatting**
   - Decision: Plain text with ANSI colors (optional)
   - Rationale: Universal compatibility, simple implementation
   - Alternatives considered: Rich library (dependency), JSON only (not user-friendly)

**Output**: research.md with detailed analysis of each decision

## Phase 1: Design & Contracts

### Data Model Entities

1. **ProcessingContext**: Configuration and state for pipeline execution
2. **ProgressState**: Real-time tracking of processing progress
3. **ProcessingResult**: Summary of completed pipeline execution
4. **CommandOptions**: Parsed CLI arguments and flags

### Service Contracts

1. **PipelineOrchestrator**: Coordinates execution of all processing modules
2. **ProgressMonitor**: Tracks and reports processing progress
3. **CommandHandler**: Base interface for CLI command implementations
4. **SummaryFormatter**: Generates human-readable processing reports

### Contract Tests

- `test_process_command_contract`: Validates main processing command
- `test_status_command_contract`: Validates status checking
- `test_recover_command_contract`: Validates recovery workflow
- `test_pipeline_orchestrator_contract`: Validates orchestration logic
- `test_progress_monitor_contract`: Validates progress tracking

### Integration Test Scenarios

1. Process single file through complete pipeline
2. Process directory with mixed file types
3. Handle errors gracefully and quarantine problematic files
4. Interrupt processing and verify cleanup
5. Recover quarantined files successfully

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md update

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- Phase 1: Models (ProcessingContext, ProgressState, ProcessingResult, CommandOptions) [P]
- Phase 2: Contract tests for services [P]
- Phase 3: Service implementations (PipelineOrchestrator, ProgressMonitor)
- Phase 4: CLI commands (process, status, recover) [P after services done]
- Phase 5: Formatters and output [P]
- Phase 6: Integration tests
- Phase 7: Entry point and packaging

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations - all principles satisfied*

No violations to track.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
