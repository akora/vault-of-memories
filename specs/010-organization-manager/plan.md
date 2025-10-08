
# Implementation Plan: Organization Manager

**Branch**: `010-organization-manager` | **Date**: 2025-10-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-organization-manager/spec.md`

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

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
The Organization Manager determines final file placement in the vault structure by applying content classification rules and creating date-based folder hierarchies (YYYY/YYYY-MM/YYYY-MM-DD). It ensures consistent folder structure across all content types and handles edge cases in file classification with configurable fallback rules.

## Technical Context
**Language/Version**: Python 3.11
**Primary Dependencies**: Python standard library (os, pathlib, datetime), existing metadata consolidator
**Storage**: Filesystem-based vault structure
**Testing**: pytest (contract, integration, unit tests)
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: single - determines source structure
**Performance Goals**: <100ms per organization decision, support parallel processing for batch operations
**Constraints**: Cross-platform filesystem compatibility, atomic folder creation, thread-safe operations
**Scale/Scope**: Support vaults with 100k+ files, handle 1000+ files/batch

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle Compliance Review**:
- [x] **Simplicity First (SF)**: Uses filesystem operations and date-based hierarchies, no complex storage systems
- [x] **Dependency Minimalism (DM)**: Only Python standard library (os, pathlib, datetime) and existing metadata consolidator
- [x] **Industry Standards Adherence (ISA)**: Follows common vault organization patterns (type/date hierarchy)
- [x] **Test-Driven Thinking (TDT)**: All classification and organization logic designed with testability in mind
- [x] **Strategic Documentation (SD)**: Self-documenting service structure with clear naming
- [x] **Readability Priority (RP)**: Clear separation between classification rules, folder creation, and organization logic

**Digital Preservation Standards**:
- [x] Original data integrity preserved (no file modifications, only placement decisions)
- [x] Operations are reversible or auditable (all decisions logged, preview mode available)
- [x] Metadata extraction does not modify source files (reads only from metadata consolidator)

**Spec-Driven Development Workflow**:
- [x] Follows constitution → specify → plan → tasks → implement workflow

## Project Structure

### Documentation (this feature)
```
specs/010-organization-manager/
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

**Structure Decision**: Option 1 (single project) - CLI-based digital vault organizer

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Research best practices for cross-platform filesystem operations
   - Research thread-safe folder creation patterns
   - Research content classification strategies based on file type and metadata
   - Research date-based folder hierarchy standards

2. **Generate and dispatch research agents**:
   - Research cross-platform filesystem compatibility (Windows MAX_PATH, reserved names, special characters)
   - Research atomic folder creation patterns in Python (race conditions, permissions)
   - Research content classification best practices for digital vaults
   - Research date extraction fallback strategies (file metadata, filename parsing)

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all technical decisions documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - VaultPath: Target path with category, subcategory, date hierarchy
   - ClassificationRule: Logic for determining file category from metadata
   - FolderStructure: Representation of vault organization hierarchy
   - OrganizationDecision: Record of classification and placement choice

2. **Generate API contracts** from functional requirements:
   - OrganizationManager.determine_path(metadata) → VaultPath
   - ClassificationEngine.classify(file_type, metadata) → Classification
   - FolderCreator.create_hierarchy(vault_path) → CreationResult
   - DateHierarchyBuilder.build_path(date) → str

3. **Generate contract tests** from contracts:
   - One test file per service contract
   - Assert input/output contracts
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each acceptance scenario → integration test
   - Preview mode test
   - Parallel processing test

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude` for Claude Code
   - Add organization manager tech stack
   - Update recent changes

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass
- Configuration tasks for classification rules and folder patterns

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before integration
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No violations - all constitutional principles satisfied.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [x] Phase 4: Implementation complete (/implement command)
- [ ] Phase 5: Validation passed (requires: pip install -r requirements.txt)

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

**Artifacts Generated**:
- [x] research.md - Technical decisions and cross-platform strategies
- [x] data-model.md - Core entities and relationships
- [x] contracts/ - Service contracts (5 files)
- [x] quickstart.md - Validation scenarios
- [x] CLAUDE.md - Agent context updated
- [x] tasks.md - 60 implementation tasks (12 contract tests, 7 integration tests, 8 models, 7 services, 26 polish tasks)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
