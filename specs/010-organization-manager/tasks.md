# Tasks: Organization Manager

**Input**: Design documents from `/specs/010-organization-manager/`
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
   → Integration: logging, config loading
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

## Phase 10.1: Setup
- [x] T001 Install new dependencies: pathvalidate>=3.3.1 and python-magic (update requirements.txt)
- [x] T002 Create configuration directory structure: config/classification_rules.json, config/folder_structure.json

## Phase 10.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 10.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Parallel)
- [ ] T003 [P] Contract test for OrganizationManager.determine_path in tests/contract/test_organization_manager.py
- [ ] T004 [P] Contract test for OrganizationManager.preview_organization in tests/contract/test_organization_manager.py
- [ ] T005 [P] Contract test for OrganizationManager.organize_batch in tests/contract/test_organization_manager.py
- [ ] T006 [P] Contract test for ClassificationEngine.classify in tests/contract/test_classification_engine.py
- [ ] T007 [P] Contract test for ClassificationEngine.classify_batch in tests/contract/test_classification_engine.py
- [ ] T008 [P] Contract test for DateExtractor.extract_date in tests/contract/test_date_extractor.py
- [ ] T009 [P] Contract test for DateExtractor.parse_filename_date in tests/contract/test_date_extractor.py
- [ ] T010 [P] Contract test for FolderCreator.create_hierarchy in tests/contract/test_folder_creator.py
- [ ] T011 [P] Contract test for FolderCreator.validate_path in tests/contract/test_folder_creator.py
- [ ] T012 [P] Contract test for FolderCreator.sanitize_folder_name in tests/contract/test_folder_creator.py
- [ ] T013 [P] Contract test for DateHierarchyBuilder.build_path in tests/contract/test_date_hierarchy_builder.py
- [ ] T014 [P] Contract test for DateHierarchyBuilder.get_date_components in tests/contract/test_date_hierarchy_builder.py

### Integration Tests (Parallel - from quickstart scenarios)
- [ ] T015 [P] Integration test for Scenario 1: Family photo with EXIF organization in tests/integration/test_photo_with_exif_organization.py
- [ ] T016 [P] Integration test for Scenario 2: Office document with no EXIF in tests/integration/test_document_without_exif.py
- [ ] T017 [P] Integration test for Scenario 3: Video with unclear classification in tests/integration/test_video_with_fallback.py
- [ ] T018 [P] Integration test for Scenario 4: File with date in filename in tests/integration/test_filename_date_parsing.py
- [ ] T019 [P] Integration test for Scenario 5: Batch organization with preview in tests/integration/test_batch_preview.py
- [ ] T020 [P] Integration test for Scenario 6: Parallel batch organization in tests/integration/test_parallel_batch_organization.py
- [ ] T021 [P] Integration test for Scenario 7: Cross-platform path validation in tests/integration/test_cross_platform_paths.py

## Phase 10.3: Core Implementation (ONLY after tests are failing)

### Models (Parallel - different files)
- [x] T022 [P] Create VaultPath data model in src/models/vault_path.py
- [x] T023 [P] Create Classification data model in src/models/classification.py
- [x] T024 [P] Create DateInfo data model in src/models/date_info.py
- [x] T025 [P] Create OrganizationDecision data model in src/models/organization_decision.py
- [x] T026 [P] Create ClassificationRule data model in src/models/classification_rule.py
- [x] T027 [P] Create FolderStructure data model in src/models/folder_structure.py
- [x] T028 [P] Create CreationResult data model in src/models/creation_result.py
- [x] T029 [P] Create enumerations (PrimaryCategory, DateSource, ExecutionStatus, DetectionMethod) in src/models/enums.py

### Services (Sequential - dependencies between services)
- [x] T030 Implement DateHierarchyBuilder.build_path and get_date_components in src/services/date_hierarchy_builder.py
- [x] T031 Implement FolderCreator with cross-platform path validation and sanitization in src/services/folder_creator.py
- [x] T032 Implement DateExtractor with fallback cascade (EXIF → creation → modification → filename) in src/services/date_extractor.py
- [x] T033 Implement filename date parser with multiple format support in src/services/filename_date_parser.py
- [x] T034 Implement ClassificationEngine with MIME detection and priority rules in src/services/classification_engine.py
- [x] T035 Implement MIME type detector with fallback strategies in src/services/mime_detector.py
- [x] T036 Implement OrganizationManager main orchestration logic in src/services/organization_manager.py

## Phase 10.4: Configuration & Integration
- [x] T037 Create classification rules configuration (MIME to category mapping) in config/classification_rules.json
- [x] T038 Create folder structure configuration (vault layout, permissions) in config/folder_structure.json
- [x] T039 Implement configuration loader for classification rules in src/services/config_loader.py
- [x] T040 Add comprehensive logging to all organization services (using Python logging module)
- [x] T041 Integrate with MetadataConsolidator (feature 008) for metadata input
- [x] T042 Add organization decision audit logging (track all classification and placement decisions)

## Phase 10.5: Polish

### Unit Tests (Parallel - different files)
- [x] T043 [P] Unit tests for VaultPath validation and construction in tests/unit/test_vault_path.py
- [x] T044 [P] Unit tests for Classification validation and confidence handling in tests/unit/test_classification.py
- [x] T045 [P] Unit tests for DateInfo timezone handling in tests/unit/test_date_info.py
- [x] T046 [P] Unit tests for DateHierarchyBuilder date formatting in tests/unit/test_date_hierarchy_builder.py
- [x] T047 [P] Unit tests for FolderCreator path sanitization in tests/unit/test_folder_creator.py
- [x] T048 [P] Unit tests for filename date parsing patterns in tests/unit/test_filename_date_parser.py
- [x] T049 [P] Unit tests for MIME detection fallback strategies in tests/unit/test_mime_detector.py
- [x] T050 [P] Unit tests for classification priority rules in tests/unit/test_classification_engine.py

### Performance & Edge Cases
- [x] T051 Performance test for single file organization (<100ms) in tests/performance/test_single_file_performance.py
- [x] T052 Performance test for batch organization (100 files in <5 seconds) in tests/performance/test_batch_performance.py
- [x] T053 Test edge case: Files with extremely long paths (>260 chars on Windows) in tests/edge_cases/test_long_paths.py
- [x] T054 Test edge case: Files with reserved names (CON, PRN, etc.) in tests/edge_cases/test_reserved_names.py
- [x] T055 Test edge case: Files with invalid characters in names in tests/edge_cases/test_invalid_characters.py
- [x] T056 Test edge case: Files with timezone boundary dates (near midnight) in tests/edge_cases/test_timezone_boundaries.py
- [x] T057 Test edge case: Files with corrupted or missing metadata in tests/edge_cases/test_missing_metadata.py
- [x] T058 Test thread safety with concurrent folder creation in tests/edge_cases/test_concurrent_folder_creation.py

### Documentation
- [x] T059 Add docstrings to all public methods (follow Google style)
- [x] T060 Create README for organization manager usage and configuration

## Dependencies

**Phase Dependencies**:
- Tests (T003-T021) before implementation (T022-T036)
- Models (T022-T029) before services (T030-T036)
- DateHierarchyBuilder and FolderCreator (T030-T031) before other services
- DateExtractor (T032-T033) before OrganizationManager (T036)
- ClassificationEngine (T034-T035) before OrganizationManager (T036)
- Core implementation before integration (T037-T042)
- Everything before polish (T043-T060)

**Service-Level Dependencies**:
```
T030 DateHierarchyBuilder
  ↓
T031 FolderCreator
  ↓
T032 DateExtractor ← T033 FilenameDateParser
  ↓
T034 ClassificationEngine ← T035 MimeDetector
  ↓
T036 OrganizationManager (orchestrates all services)
```

**Configuration Dependencies**:
- T037-T038 (config files) before T039 (config loader)
- T039 (config loader) before services that use config (T034, T036)

## Parallel Execution Examples

### Launch T003-T014 contract tests together:
```bash
# All contract tests can run in parallel (different test files)
Task: "Contract test for OrganizationManager.determine_path in tests/contract/test_organization_manager.py"
Task: "Contract test for OrganizationManager.preview_organization in tests/contract/test_organization_manager.py"
Task: "Contract test for OrganizationManager.organize_batch in tests/contract/test_organization_manager.py"
Task: "Contract test for ClassificationEngine.classify in tests/contract/test_classification_engine.py"
Task: "Contract test for ClassificationEngine.classify_batch in tests/contract/test_classification_engine.py"
Task: "Contract test for DateExtractor.extract_date in tests/contract/test_date_extractor.py"
Task: "Contract test for DateExtractor.parse_filename_date in tests/contract/test_date_extractor.py"
Task: "Contract test for FolderCreator.create_hierarchy in tests/contract/test_folder_creator.py"
Task: "Contract test for FolderCreator.validate_path in tests/contract/test_folder_creator.py"
Task: "Contract test for FolderCreator.sanitize_folder_name in tests/contract/test_folder_creator.py"
Task: "Contract test for DateHierarchyBuilder.build_path in tests/contract/test_date_hierarchy_builder.py"
Task: "Contract test for DateHierarchyBuilder.get_date_components in tests/contract/test_date_hierarchy_builder.py"
```

### Launch T015-T021 integration tests together:
```bash
# All integration tests can run in parallel (different test files)
Task: "Integration test for Scenario 1: Family photo with EXIF organization in tests/integration/test_photo_with_exif_organization.py"
Task: "Integration test for Scenario 2: Office document with no EXIF in tests/integration/test_document_without_exif.py"
Task: "Integration test for Scenario 3: Video with unclear classification in tests/integration/test_video_with_fallback.py"
Task: "Integration test for Scenario 4: File with date in filename in tests/integration/test_filename_date_parsing.py"
Task: "Integration test for Scenario 5: Batch organization with preview in tests/integration/test_batch_preview.py"
Task: "Integration test for Scenario 6: Parallel batch organization in tests/integration/test_parallel_batch_organization.py"
Task: "Integration test for Scenario 7: Cross-platform path validation in tests/integration/test_cross_platform_paths.py"
```

### Launch T022-T029 model creation together:
```bash
# All models can be created in parallel (different files, no dependencies)
Task: "Create VaultPath data model in src/models/vault_path.py"
Task: "Create Classification data model in src/models/classification.py"
Task: "Create DateInfo data model in src/models/date_info.py"
Task: "Create OrganizationDecision data model in src/models/organization_decision.py"
Task: "Create ClassificationRule data model in src/models/classification_rule.py"
Task: "Create FolderStructure data model in src/models/folder_structure.py"
Task: "Create CreationResult data model in src/models/creation_result.py"
Task: "Create enumerations (PrimaryCategory, DateSource, ExecutionStatus, DetectionMethod) in src/models/enums.py"
```

### Launch T043-T050 unit tests together:
```bash
# All unit tests can run in parallel (different test files)
Task: "Unit tests for VaultPath validation and construction in tests/unit/test_vault_path.py"
Task: "Unit tests for Classification validation and confidence handling in tests/unit/test_classification.py"
Task: "Unit tests for DateInfo timezone handling in tests/unit/test_date_info.py"
Task: "Unit tests for DateHierarchyBuilder date formatting in tests/unit/test_date_hierarchy_builder.py"
Task: "Unit tests for FolderCreator path sanitization in tests/unit/test_folder_creator.py"
Task: "Unit tests for filename date parsing patterns in tests/unit/test_filename_date_parser.py"
Task: "Unit tests for MIME detection fallback strategies in tests/unit/test_mime_detector.py"
Task: "Unit tests for classification priority rules in tests/unit/test_classification_engine.py"
```

## Notes

- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- Cross-platform compatibility required for all filesystem operations
- All dates stored in UTC, local dates for folder organization
- Thread-safe operations required for batch processing
- Performance targets: <100ms per file, <5s for 100 files

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts** (5 contract files → 12 contract test tasks):
   - organization_manager.py → 3 tests (determine_path, preview_organization, organize_batch)
   - classification_engine.py → 2 tests (classify, classify_batch)
   - date_extractor.py → 2 tests (extract_date, parse_filename_date)
   - folder_creator.py → 3 tests (create_hierarchy, validate_path, sanitize_folder_name)
   - date_hierarchy_builder.py → 2 tests (build_path, get_date_components)

2. **From Data Model** (7 entities → 8 model creation tasks):
   - VaultPath, Classification, DateInfo, OrganizationDecision
   - ClassificationRule, FolderStructure, CreationResult
   - Enumerations (PrimaryCategory, DateSource, ExecutionStatus, DetectionMethod)

3. **From Quickstart** (7 scenarios → 7 integration tests):
   - Scenario 1: Photo with EXIF
   - Scenario 2: Document without EXIF
   - Scenario 3: Video with fallback
   - Scenario 4: Filename date parsing
   - Scenario 5: Batch preview
   - Scenario 6: Parallel batch
   - Scenario 7: Cross-platform paths

4. **From Research** (Technical decisions → Implementation tasks):
   - Cross-platform path handling (FolderCreator)
   - MIME detection fallback (MimeDetector)
   - Date extraction cascade (DateExtractor)
   - Filename parsing patterns (FilenameDateParser)
   - Classification priority rules (ClassificationEngine)

5. **From Plan** (Tech stack → Setup and integration):
   - Dependencies: pathvalidate, python-magic
   - Configuration: classification_rules.json, folder_structure.json
   - Integration: MetadataConsolidator, logging, audit trail

6. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (12 contract tests for 5 contracts)
- [x] All entities have model tasks (8 model tasks for 7 entities + enums)
- [x] All quickstart scenarios have integration tests (7 tests for 7 scenarios)
- [x] All tests come before implementation (T003-T021 before T022-T036)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
- [x] Service dependencies correctly ordered (DateHierarchyBuilder → FolderCreator → DateExtractor → ClassificationEngine → OrganizationManager)
- [x] Configuration loaded before services that depend on it
- [x] Performance and edge case tests included
- [x] Cross-platform compatibility validated

## Implementation Strategy

**Phase 10.2 (Tests First)**:
- Write all contract tests (T003-T014) in parallel
- Write all integration tests (T015-T021) in parallel
- Run tests - ALL MUST FAIL (no implementation yet)
- Verify test coverage aligns with contracts and quickstart scenarios

**Phase 10.3 (Core Implementation)**:
- Create all models (T022-T029) in parallel
- Implement services in dependency order:
  1. DateHierarchyBuilder (T030) - no dependencies
  2. FolderCreator (T031) - uses DateHierarchyBuilder
  3. FilenameDateParser (T033) - no dependencies
  4. DateExtractor (T032) - uses FilenameDateParser
  5. MimeDetector (T035) - no dependencies
  6. ClassificationEngine (T034) - uses MimeDetector
  7. OrganizationManager (T036) - orchestrates all services
- Run tests after each service - should progressively pass

**Phase 10.4 (Integration)**:
- Create configuration files (T037-T038)
- Implement config loader (T039)
- Add logging (T040)
- Integrate with MetadataConsolidator (T041)
- Add audit logging (T042)
- Run integration tests - should all pass

**Phase 10.5 (Polish)**:
- Write unit tests (T043-T050) in parallel
- Run performance tests (T051-T052)
- Test edge cases (T053-T058)
- Add documentation (T059-T060)
- Final validation: Run full test suite, verify quickstart scenarios

## Success Criteria

- All contract tests pass
- All integration tests pass
- All unit tests pass
- Performance benchmarks met (<100ms per file, <5s for 100 files)
- Cross-platform compatibility validated (Windows, macOS, Linux)
- Edge cases handled gracefully
- Code coverage >90%
- Quickstart scenarios complete successfully
- Constitution compliance verified

---

**Total Tasks**: 60
**Estimated Effort**: 15-20 hours
**Ready for**: `/implement` command

*Task generation complete - Ready for TDD implementation*
