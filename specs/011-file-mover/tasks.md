# Tasks: File Mover

**Input**: Design documents from `/specs/011-file-mover/`
**Prerequisites**: plan.md (required), data-model.md, contracts/, research.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Each entity → model task
   → contracts/: Each file → contract test task
   → quickstart.md: Each scenario → integration test task
3. Generate tasks by category:
   → Setup: dependencies, configuration
   → Tests: contract tests, integration tests
   → Core: models, services
   → Integration: logging, database schema
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
   → All entities implemented?
   → All scenarios covered?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 11.1: Setup
- [x] T001 Verify existing dependencies are sufficient (shutil, hashlib, pathlib from stdlib)
- [x] T002 Create database schema for move operations, quarantine records, and duplicate tracking in src/services/database_manager.py
- [x] T003 Create quarantine directory structure configuration in config/quarantine_settings.json

## Phase 11.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 11.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Parallel)
- [ ] T004 [P] Contract test for FileMover.move_file in tests/contract/test_file_mover.py
- [ ] T005 [P] Contract test for FileMover.move_batch in tests/contract/test_file_mover.py
- [ ] T006 [P] Contract test for FileMover.preview_move in tests/contract/test_file_mover.py
- [ ] T007 [P] Contract test for AtomicMover.execute_move in tests/contract/test_atomic_mover.py
- [ ] T008 [P] Contract test for AtomicMover.rollback_move in tests/contract/test_atomic_mover.py
- [ ] T009 [P] Contract test for AtomicMover.verify_move in tests/contract/test_atomic_mover.py
- [ ] T010 [P] Contract test for DuplicateHandler.check_duplicate in tests/contract/test_duplicate_handler.py
- [ ] T011 [P] Contract test for DuplicateHandler.handle_duplicate in tests/contract/test_duplicate_handler.py
- [ ] T012 [P] Contract test for DuplicateHandler.get_duplicate_path in tests/contract/test_duplicate_handler.py
- [ ] T013 [P] Contract test for QuarantineManager.quarantine_file in tests/contract/test_quarantine_manager.py
- [ ] T014 [P] Contract test for QuarantineManager.classify_error in tests/contract/test_quarantine_manager.py
- [ ] T015 [P] Contract test for QuarantineManager.get_quarantine_path in tests/contract/test_quarantine_manager.py
- [ ] T016 [P] Contract test for QuarantineManager.list_quarantined_files in tests/contract/test_quarantine_manager.py
- [ ] T017 [P] Contract test for IntegrityVerifier.calculate_hash in tests/contract/test_integrity_verifier.py
- [ ] T018 [P] Contract test for IntegrityVerifier.verify_integrity in tests/contract/test_integrity_verifier.py
- [ ] T019 [P] Contract test for IntegrityVerifier.batch_verify in tests/contract/test_integrity_verifier.py
- [ ] T020 [P] Contract test for TransactionManager.execute_transaction in tests/contract/test_transaction_manager.py
- [ ] T021 [P] Contract test for TransactionManager.begin in tests/contract/test_transaction_manager.py
- [ ] T022 [P] Contract test for TransactionManager.commit in tests/contract/test_transaction_manager.py
- [ ] T023 [P] Contract test for TransactionManager.rollback in tests/contract/test_transaction_manager.py

### Integration Tests (Parallel - from quickstart scenarios)
- [ ] T024 [P] Integration test for Scenario 1: Successful single file move in tests/integration/test_successful_file_move.py
- [ ] T025 [P] Integration test for Scenario 2: Duplicate file handling in tests/integration/test_duplicate_file_handling.py
- [ ] T026 [P] Integration test for Scenario 3: File quarantine on checksum mismatch in tests/integration/test_quarantine_checksum_mismatch.py
- [ ] T027 [P] Integration test for Scenario 4: Transaction rollback on database failure in tests/integration/test_transaction_rollback.py
- [ ] T028 [P] Integration test for Scenario 5: Batch move with mixed outcomes in tests/integration/test_batch_mixed_outcomes.py
- [ ] T029 [P] Integration test for Scenario 6: Storage space validation in tests/integration/test_storage_space_validation.py
- [ ] T030 [P] Integration test for Scenario 7: Concurrent file operations in tests/integration/test_concurrent_operations.py
- [ ] T031 [P] Integration test for Scenario 8: Preview mode (dry run) in tests/integration/test_preview_mode.py

## Phase 11.3: Core Implementation (ONLY after tests are failing)

### Models (Parallel - different files)
- [x] T032 [P] Create MoveOperation data model in src/models/move_operation.py
- [x] T033 [P] Create MoveResult data model in src/models/move_result.py
- [ ] T034 [P] Create DuplicateRecord data model in src/models/duplicate_record.py
- [x] T035 [P] Create QuarantineRecord data model in src/models/quarantine_record.py
- [ ] T036 [P] Create TransactionContext data model in src/models/transaction_context.py
- [x] T037 [P] Create BatchMoveRequest data model in src/models/batch_move_request.py
- [x] T038 [P] Create BatchMoveResult data model in src/models/batch_move_result.py
- [x] T039 [P] Create IntegrityCheckResult data model in src/models/integrity_check_result.py (integrated in IntegrityVerifier)
- [x] T040 [P] Create OperationStatus and QuarantineReason enumerations in src/models/enums.py (OperationStatus in move_operation.py, QuarantineReason in quarantine_record.py)

### Services (Sequential - dependencies between services)
- [x] T041 Implement IntegrityVerifier with hash calculation and batch verification in src/services/integrity_verifier.py
- [x] T042 Implement AtomicMover with shutil-based moves and rollback in src/services/atomic_mover.py
- [ ] T043 Implement DuplicateHandler with content-based deduplication in src/services/duplicate_handler.py (uses existing DuplicateDatabase)
- [x] T044 Implement QuarantineManager with error classification and structured storage in src/services/quarantine_manager.py
- [ ] T045 Implement TransactionManager for coordinating file and database operations in src/services/transaction_manager.py
- [x] T046 Implement FileMover main orchestration logic in src/services/file_mover.py

## Phase 11.4: Configuration & Integration
- [ ] T047 Extend database schema with move_operations, quarantine_records, and batch_operations tables in src/services/database_manager.py
- [ ] T048 Create quarantine_settings.json configuration (folder structure, recovery policies) in config/quarantine_settings.json
- [ ] T049 Add comprehensive logging to all file mover services (using Python logging module)
- [ ] T050 Integrate with OrganizationManager (feature 010) for destination path determination
- [ ] T051 Add storage space validation utilities in src/lib/file_utils.py
- [ ] T052 Add move operation audit logging (track all moves, duplicates, quarantines)

## Phase 11.5: Polish

### Unit Tests (Parallel - different files)
- [ ] T053 [P] Unit tests for MoveOperation validation and state transitions in tests/unit/test_move_operation.py
- [ ] T054 [P] Unit tests for MoveResult derived properties and aggregation in tests/unit/test_move_result.py
- [ ] T055 [P] Unit tests for DuplicateRecord relationship validation in tests/unit/test_duplicate_record.py
- [ ] T056 [P] Unit tests for QuarantineRecord error classification in tests/unit/test_quarantine_record.py
- [ ] T057 [P] Unit tests for IntegrityVerifier hash algorithms and streaming in tests/unit/test_integrity_verifier.py
- [ ] T058 [P] Unit tests for AtomicMover cross-platform path handling in tests/unit/test_atomic_mover.py
- [ ] T059 [P] Unit tests for DuplicateHandler path generation in tests/unit/test_duplicate_handler.py
- [ ] T060 [P] Unit tests for QuarantineManager error classification logic in tests/unit/test_quarantine_manager.py
- [ ] T061 [P] Unit tests for TransactionManager rollback scenarios in tests/unit/test_transaction_manager.py

### Performance & Edge Cases
- [ ] T062 Performance test for single file move (<200ms) in tests/performance/test_single_file_performance.py
- [ ] T063 Performance test for batch move (100 files in <20 seconds) in tests/performance/test_batch_performance.py
- [ ] T064 Performance test for hash calculation (10MB file in <50ms) in tests/performance/test_hash_performance.py
- [ ] T065 Test edge case: Very large files (>1GB) in tests/edge_cases/test_large_files.py
- [ ] T066 Test edge case: Cross-device moves (different filesystems) in tests/edge_cases/test_cross_device_moves.py
- [ ] T067 Test edge case: Interrupted operations (simulate power loss) in tests/edge_cases/test_interrupted_operations.py
- [ ] T068 Test edge case: Duplicate detection with hash collisions in tests/edge_cases/test_hash_collisions.py
- [ ] T069 Test edge case: Permission errors during move in tests/edge_cases/test_permission_errors.py
- [ ] T070 Test edge case: Disk full during move operation in tests/edge_cases/test_disk_full.py
- [ ] T071 Test edge case: Network interruption for network storage in tests/edge_cases/test_network_interruption.py
- [ ] T072 Test thread safety with concurrent moves to same directory in tests/edge_cases/test_concurrent_directory_access.py

### Documentation
- [ ] T073 Add docstrings to all public methods (follow Google style)
- [ ] T074 Create README for file mover usage, quarantine management, and recovery workflows

## Dependencies

**Phase Dependencies**:
- Tests (T004-T031) before implementation (T032-T046)
- Models (T032-T040) before services (T041-T046)
- IntegrityVerifier (T041) before AtomicMover (T042)
- AtomicMover (T042) before FileMover (T046)
- DuplicateHandler (T043) before FileMover (T046)
- QuarantineManager (T044) before FileMover (T046)
- TransactionManager (T045) before FileMover (T046)
- Core implementation before integration (T047-T052)
- Everything before polish (T053-T074)

**Service-Level Dependencies**:
```
T041 IntegrityVerifier
  ↓
T042 AtomicMover (uses IntegrityVerifier)
  ↓
T043 DuplicateHandler (standalone, uses DuplicateDatabase)
  ↓
T044 QuarantineManager (standalone)
  ↓
T045 TransactionManager (coordinates all operations)
  ↓
T046 FileMover (orchestrates all services)
```

**Database Dependencies**:
- T002 (initial schema) before T047 (extended schema)
- T047 (extended schema) before services that use it (T042-T046)

**Integration Dependencies**:
- T050 (OrganizationManager integration) before T046 (FileMover)
- T051 (storage utilities) before T046 (FileMover)

## Parallel Execution Examples

### Launch T004-T023 contract tests together:
```bash
# All contract tests can run in parallel (different test files)
Task: "Contract test for FileMover.move_file in tests/contract/test_file_mover.py"
Task: "Contract test for FileMover.move_batch in tests/contract/test_file_mover.py"
Task: "Contract test for FileMover.preview_move in tests/contract/test_file_mover.py"
Task: "Contract test for AtomicMover.execute_move in tests/contract/test_atomic_mover.py"
Task: "Contract test for AtomicMover.rollback_move in tests/contract/test_atomic_mover.py"
Task: "Contract test for AtomicMover.verify_move in tests/contract/test_atomic_mover.py"
Task: "Contract test for DuplicateHandler.check_duplicate in tests/contract/test_duplicate_handler.py"
Task: "Contract test for DuplicateHandler.handle_duplicate in tests/contract/test_duplicate_handler.py"
Task: "Contract test for DuplicateHandler.get_duplicate_path in tests/contract/test_duplicate_handler.py"
Task: "Contract test for QuarantineManager.quarantine_file in tests/contract/test_quarantine_manager.py"
Task: "Contract test for QuarantineManager.classify_error in tests/contract/test_quarantine_manager.py"
Task: "Contract test for QuarantineManager.get_quarantine_path in tests/contract/test_quarantine_manager.py"
Task: "Contract test for QuarantineManager.list_quarantined_files in tests/contract/test_quarantine_manager.py"
Task: "Contract test for IntegrityVerifier.calculate_hash in tests/contract/test_integrity_verifier.py"
Task: "Contract test for IntegrityVerifier.verify_integrity in tests/contract/test_integrity_verifier.py"
Task: "Contract test for IntegrityVerifier.batch_verify in tests/contract/test_integrity_verifier.py"
Task: "Contract test for TransactionManager.execute_transaction in tests/contract/test_transaction_manager.py"
Task: "Contract test for TransactionManager.begin in tests/contract/test_transaction_manager.py"
Task: "Contract test for TransactionManager.commit in tests/contract/test_transaction_manager.py"
Task: "Contract test for TransactionManager.rollback in tests/contract/test_transaction_manager.py"
```

### Launch T024-T031 integration tests together:
```bash
# All integration tests can run in parallel (different test files)
Task: "Integration test for Scenario 1: Successful single file move in tests/integration/test_successful_file_move.py"
Task: "Integration test for Scenario 2: Duplicate file handling in tests/integration/test_duplicate_file_handling.py"
Task: "Integration test for Scenario 3: File quarantine on checksum mismatch in tests/integration/test_quarantine_checksum_mismatch.py"
Task: "Integration test for Scenario 4: Transaction rollback on database failure in tests/integration/test_transaction_rollback.py"
Task: "Integration test for Scenario 5: Batch move with mixed outcomes in tests/integration/test_batch_mixed_outcomes.py"
Task: "Integration test for Scenario 6: Storage space validation in tests/integration/test_storage_space_validation.py"
Task: "Integration test for Scenario 7: Concurrent file operations in tests/integration/test_concurrent_operations.py"
Task: "Integration test for Scenario 8: Preview mode (dry run) in tests/integration/test_preview_mode.py"
```

### Launch T032-T040 model creation together:
```bash
# All models can be created in parallel (different files, no dependencies)
Task: "Create MoveOperation data model in src/models/move_operation.py"
Task: "Create MoveResult data model in src/models/move_result.py"
Task: "Create DuplicateRecord data model in src/models/duplicate_record.py"
Task: "Create QuarantineRecord data model in src/models/quarantine_record.py"
Task: "Create TransactionContext data model in src/models/transaction_context.py"
Task: "Create BatchMoveRequest data model in src/models/batch_move_request.py"
Task: "Create BatchMoveResult data model in src/models/batch_move_result.py"
Task: "Create IntegrityCheckResult data model in src/models/integrity_check_result.py"
Task: "Create OperationStatus and QuarantineReason enumerations in src/models/enums.py"
```

### Launch T053-T061 unit tests together:
```bash
# All unit tests can run in parallel (different test files)
Task: "Unit tests for MoveOperation validation and state transitions in tests/unit/test_move_operation.py"
Task: "Unit tests for MoveResult derived properties and aggregation in tests/unit/test_move_result.py"
Task: "Unit tests for DuplicateRecord relationship validation in tests/unit/test_duplicate_record.py"
Task: "Unit tests for QuarantineRecord error classification in tests/unit/test_quarantine_record.py"
Task: "Unit tests for IntegrityVerifier hash algorithms and streaming in tests/unit/test_integrity_verifier.py"
Task: "Unit tests for AtomicMover cross-platform path handling in tests/unit/test_atomic_mover.py"
Task: "Unit tests for DuplicateHandler path generation in tests/unit/test_duplicate_handler.py"
Task: "Unit tests for QuarantineManager error classification logic in tests/unit/test_quarantine_manager.py"
Task: "Unit tests for TransactionManager rollback scenarios in tests/unit/test_transaction_manager.py"
```

## Notes

- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- Cross-platform compatibility required for all filesystem operations
- Atomic operations required for data integrity
- All moves must be logged for audit trail
- Performance targets: <200ms per file, <20s for 100 files
- Thread-safe operations required for batch processing

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts** (6 contract files → 20 contract test tasks):
   - file_mover.py → 3 tests (move_file, move_batch, preview_move)
   - atomic_mover.py → 3 tests (execute_move, rollback_move, verify_move)
   - duplicate_handler.py → 3 tests (check_duplicate, handle_duplicate, get_duplicate_path)
   - quarantine_manager.py → 4 tests (quarantine_file, classify_error, get_quarantine_path, list_quarantined_files)
   - integrity_verifier.py → 3 tests (calculate_hash, verify_integrity, batch_verify)
   - transaction_manager.py → 4 tests (execute_transaction, begin, commit, rollback)

2. **From Data Model** (8 entities → 9 model creation tasks):
   - MoveOperation, MoveResult, DuplicateRecord, QuarantineRecord
   - TransactionContext, BatchMoveRequest, BatchMoveResult, IntegrityCheckResult
   - Enumerations (OperationStatus, QuarantineReason)

3. **From Quickstart** (8 scenarios → 8 integration tests):
   - Scenario 1: Successful single file move
   - Scenario 2: Duplicate file handling
   - Scenario 3: File quarantine on checksum mismatch
   - Scenario 4: Transaction rollback on database failure
   - Scenario 5: Batch move with mixed outcomes
   - Scenario 6: Storage space validation
   - Scenario 7: Concurrent file operations
   - Scenario 8: Preview mode (dry run)

4. **From Research** (Technical decisions → Implementation tasks):
   - Atomic file operations (AtomicMover)
   - Transaction coordination (TransactionManager)
   - Integrity verification (IntegrityVerifier)
   - Duplicate handling (DuplicateHandler)
   - Quarantine management (QuarantineManager)
   - Storage space validation (file_utils)

5. **From Plan** (Tech stack → Setup and integration):
   - Dependencies: stdlib only (shutil, hashlib, pathlib)
   - Database: Extend schema for move operations
   - Configuration: quarantine_settings.json
   - Integration: OrganizationManager, logging, audit trail

6. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (20 contract tests for 6 contracts)
- [x] All entities have model tasks (9 model tasks for 8 entities + enums)
- [x] All quickstart scenarios have integration tests (8 tests for 8 scenarios)
- [x] All tests come before implementation (T004-T031 before T032-T046)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
- [x] Service dependencies correctly ordered (IntegrityVerifier → AtomicMover → FileMover)
- [x] Database schema extended before services that depend on it
- [x] Performance and edge case tests included
- [x] Cross-platform compatibility and thread safety validated

## Implementation Strategy

**Phase 11.2 (Tests First)**:
- Write all contract tests (T004-T023) in parallel
- Write all integration tests (T024-T031) in parallel
- Run tests - ALL MUST FAIL (no implementation yet)
- Verify test coverage aligns with contracts and quickstart scenarios

**Phase 11.3 (Core Implementation)**:
- Create all models (T032-T040) in parallel
- Implement services in dependency order:
  1. IntegrityVerifier (T041) - no dependencies
  2. AtomicMover (T042) - uses IntegrityVerifier
  3. DuplicateHandler (T043) - uses DuplicateDatabase
  4. QuarantineManager (T044) - no dependencies
  5. TransactionManager (T045) - coordinates all operations
  6. FileMover (T046) - orchestrates all services
- Run tests after each service - should progressively pass

**Phase 11.4 (Integration)**:
- Extend database schema (T047)
- Create configuration files (T048)
- Add logging (T049)
- Integrate with OrganizationManager (T050)
- Add storage utilities (T051)
- Add audit logging (T052)
- Run integration tests - should all pass

**Phase 11.5 (Polish)**:
- Write unit tests (T053-T061) in parallel
- Run performance tests (T062-T064)
- Test edge cases (T065-T072)
- Add documentation (T073-T074)
- Final validation: Run full test suite, verify quickstart scenarios

## Success Criteria

- All contract tests pass
- All integration tests pass
- All unit tests pass
- Performance benchmarks met (<200ms per file, <20s for 100 files)
- Cross-platform compatibility validated (Windows, macOS, Linux)
- Thread safety validated for concurrent operations
- Edge cases handled gracefully
- Code coverage >90%
- Quickstart scenarios complete successfully
- Constitution compliance verified

---

**Total Tasks**: 74
**Estimated Effort**: 20-25 hours
**Ready for**: `/implement` command

*Task generation complete - Ready for TDD implementation*
