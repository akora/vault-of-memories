# Tasks: File Ingestion System

**Input**: Design documents from `/specs/001-file-ingestion/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 3.1: Setup
- [x] T001 Create Python project structure with src/ and tests/ directories
- [x] T002 Initialize Python project with requirements.txt and setup configuration
- [x] T003 [P] Configure pytest testing framework and coverage reporting
- [x] T004 [P] Set up code formatting with black and linting with flake8

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T005 [P] Contract test for FileIngestor.ingest_file in tests/contract/test_file_ingestor_ingest_file.py
- [x] T006 [P] Contract test for FileIngestor.ingest_directory in tests/contract/test_file_ingestor_ingest_directory.py
- [x] T007 [P] Contract test for FileIngestor.is_duplicate in tests/contract/test_file_ingestor_is_duplicate.py
- [x] T008 [P] Contract test for DuplicateDatabase.add_file_record in tests/contract/test_duplicate_database_add.py
- [x] T009 [P] Contract test for DuplicateDatabase.find_by_checksum in tests/contract/test_duplicate_database_find.py
- [x] T010 [P] Integration test single file processing in tests/integration/test_single_file_processing.py
- [x] T011 [P] Integration test directory processing in tests/integration/test_directory_processing.py
- [x] T012 [P] Integration test duplicate detection in tests/integration/test_duplicate_detection.py
- [x] T013 [P] Integration test system file filtering in tests/integration/test_system_file_filtering.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T014 [P] Create FileRecord data model in src/models/file_record.py
- [ ] T015 [P] Create ProcessingStats data model in src/models/processing_stats.py
- [ ] T016 [P] Implement database schema setup in src/services/database_manager.py
- [ ] T017 Implement DuplicateDatabase interface in src/services/duplicate_database.py
- [ ] T018 Implement checksum calculation service in src/services/checksum_calculator.py
- [ ] T019 Implement system file filter in src/services/system_file_filter.py
- [ ] T020 Implement FileIngestor interface in src/services/file_ingestor.py
- [ ] T021 Create CLI interface in src/cli/ingest_command.py
- [ ] T022 Implement error handling and logging in src/services/error_handler.py

## Phase 3.4: Integration
- [ ] T023 Connect FileIngestor to DuplicateDatabase
- [ ] T024 Integrate system file filtering into ingestion pipeline
- [ ] T025 Add comprehensive logging throughout all services
- [ ] T026 Implement database connection pooling and management
- [ ] T027 Add configuration management for database paths and settings

## Phase 3.5: Polish
- [ ] T028 [P] Unit tests for checksum calculation in tests/unit/test_checksum_calculator.py
- [ ] T029 [P] Unit tests for system file filtering in tests/unit/test_system_file_filter.py
- [ ] T030 [P] Unit tests for file record validation in tests/unit/test_file_record.py
- [ ] T031 Performance tests for large file processing (>100MB files)
- [ ] T032 Performance tests for batch processing (1000+ files)
- [ ] T033 [P] Update quickstart.md validation scenarios
- [ ] T034 Remove code duplication and optimize critical paths
- [ ] T035 Run manual testing scenarios from quickstart.md

## Dependencies
- Setup (T001-T004) before everything else
- Tests (T005-T013) before implementation (T014-T022)
- T014-T015 (models) before T016-T020 (services)
- T017 (database) blocks T020 (ingestor), T023 (integration)
- T018-T019 (utilities) block T020 (ingestor)
- Core implementation before integration (T023-T027)
- Everything before polish (T028-T035)

## Parallel Example
```
# Launch T005-T009 contract tests together:
Task: "Contract test for FileIngestor.ingest_file in tests/contract/test_file_ingestor_ingest_file.py"
Task: "Contract test for FileIngestor.ingest_directory in tests/contract/test_file_ingestor_ingest_directory.py"
Task: "Contract test for FileIngestor.is_duplicate in tests/contract/test_file_ingestor_is_duplicate.py"
Task: "Contract test for DuplicateDatabase.add_file_record in tests/contract/test_duplicate_database_add.py"
Task: "Contract test for DuplicateDatabase.find_by_checksum in tests/contract/test_duplicate_database_find.py"
```

```
# Launch T010-T013 integration tests together:
Task: "Integration test single file processing in tests/integration/test_single_file_processing.py"
Task: "Integration test directory processing in tests/integration/test_directory_processing.py"
Task: "Integration test duplicate detection in tests/integration/test_duplicate_detection.py"
Task: "Integration test system file filtering in tests/integration/test_system_file_filtering.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - contracts/file_ingestor.py → 5 contract test tasks [P]
   - contracts/duplicate_database.py → 2 contract test tasks [P]

2. **From Data Model**:
   - FileRecord entity → model creation task [P]
   - ProcessingStats entity → model creation task [P]
   - Database schema → database manager task

3. **From Quickstart Scenarios**:
   - Single file processing → integration test [P]
   - Directory processing → integration test [P]
   - Duplicate detection → integration test [P]
   - System file filtering → integration test [P]

4. **Ordering**:
   - Setup → Tests → Models → Services → CLI → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (7 contracts → 7 contract tests)
- [x] All entities have model tasks (2 entities → 2 model tasks)
- [x] All tests come before implementation (T005-T013 before T014-T022)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task