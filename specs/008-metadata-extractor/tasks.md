# Tasks: Metadata Extractor

**Input**: Design documents from `/specs/008-metadata-extractor/`
**Prerequisites**: plan.md (required), contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → contracts/: Each file → contract test task
3. Generate tasks by category:
   → Setup: dependencies
   → Tests: contract tests, integration tests
   → Core: models, services
   → Integration: processor coordination, configuration
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
   → All components implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 8.1: Setup
- [ ] T001 No new dependencies needed (uses Python standard library only)

## Phase 8.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 8.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T002 [P] Contract test for MetadataConsolidator.consolidate in tests/contract/test_metadata_consolidator.py
- [ ] T003 [P] Contract test for MetadataConsolidator.assess_quality in tests/contract/test_metadata_quality.py
- [ ] T004 [P] Contract test for PriorityResolver.resolve_field in tests/contract/test_priority_resolver.py
- [ ] T005 [P] Contract test for PriorityResolver.get_priority_order in tests/contract/test_priority_order.py
- [ ] T006 [P] Contract test for TimezonePreserver.preserve_timezone in tests/contract/test_timezone_preserver.py
- [ ] T007 [P] Contract test for ManufacturerStandardizer.standardize in tests/contract/test_manufacturer_standardizer.py
- [ ] T008 [P] Integration test for single processor consolidation in tests/integration/test_single_processor_consolidation.py
- [ ] T009 [P] Integration test for multi-processor consolidation in tests/integration/test_multi_processor_consolidation.py
- [ ] T010 [P] Integration test for conflict resolution across sources in tests/integration/test_conflict_resolution.py
- [ ] T011 [P] Integration test for timezone preservation from EXIF in tests/integration/test_timezone_preservation.py
- [ ] T012 [P] Integration test for manufacturer standardization in tests/integration/test_manufacturer_mapping.py
- [ ] T013 [P] Integration test for quality scoring in tests/integration/test_quality_assessment.py

## Phase 8.3: Core Implementation (ONLY after tests are failing)
- [ ] T014 [P] Create MetadataSource enum in src/models/consolidated_metadata.py
- [ ] T015 [P] Create MetadataField data model in src/models/consolidated_metadata.py
- [ ] T016 Create ConsolidatedMetadata data model in src/models/consolidated_metadata.py
- [ ] T017 [P] Create MetadataQuality data model in src/models/consolidated_metadata.py
- [ ] T018 Implement PriorityResolver with configurable rules in src/services/priority_resolver.py
- [ ] T019 Implement TimezonePreserver for timezone preservation in src/services/timezone_preserver.py
- [ ] T020 Implement ManufacturerStandardizer with mappings in src/services/manufacturer_standardizer.py
- [ ] T021 Implement MetadataQualityAssessor for quality scoring in src/services/metadata_quality_assessor.py
- [ ] T022 Implement MetadataConsolidator main orchestration in src/services/metadata_consolidator.py

## Phase 8.4: Integration
- [ ] T023 Create priority rules configuration in config/metadata_priorities.json
- [ ] T024 Create manufacturer mappings configuration in config/manufacturer_mappings.json
- [ ] T025 Add comprehensive logging to metadata consolidation services
- [ ] T026 Integrate with existing image, document, audio, video processors
- [ ] T027 Add processor registry and coordination logic

## Phase 8.5: Polish
- [ ] T028 [P] Unit tests for priority resolution in tests/unit/test_priority_resolver.py
- [ ] T029 [P] Unit tests for timezone preservation in tests/unit/test_timezone_preserver.py
- [ ] T030 [P] Unit tests for manufacturer standardization in tests/unit/test_manufacturer_standardizer.py
- [ ] T031 [P] Unit tests for quality assessment in tests/unit/test_quality_assessor.py
- [ ] T032 [P] Unit tests for metadata field handling in tests/unit/test_metadata_field.py
- [ ] T033 Performance tests for large file consolidation
- [ ] T034 Performance tests for batch consolidation (100+ files)
- [ ] T035 Test conflict resolution with complex scenarios
- [ ] T036 Test timezone handling across different formats
- [ ] T037 Remove code duplication and optimize critical paths

## Dependencies
- Tests (T002-T013) before implementation (T014-T022)
- T014-T017 (models) before T018-T022 (services)
- T018-T020 (utility services) block T021-T022 (consolidator)
- Core implementation before integration (T023-T027)
- Everything before polish (T028-T037)

## Parallel Example
```
# Launch T002-T007 contract tests together:
Task: "Contract test for MetadataConsolidator.consolidate in tests/contract/test_metadata_consolidator.py"
Task: "Contract test for MetadataConsolidator.assess_quality in tests/contract/test_metadata_quality.py"
Task: "Contract test for PriorityResolver.resolve_field in tests/contract/test_priority_resolver.py"
Task: "Contract test for PriorityResolver.get_priority_order in tests/contract/test_priority_order.py"
Task: "Contract test for TimezonePreserver.preserve_timezone in tests/contract/test_timezone_preserver.py"
Task: "Contract test for ManufacturerStandardizer.standardize in tests/contract/test_manufacturer_standardizer.py"
```

```
# Launch T008-T013 integration tests together:
Task: "Integration test for single processor consolidation in tests/integration/test_single_processor_consolidation.py"
Task: "Integration test for multi-processor consolidation in tests/integration/test_multi_processor_consolidation.py"
Task: "Integration test for conflict resolution across sources in tests/integration/test_conflict_resolution.py"
Task: "Integration test for timezone preservation from EXIF in tests/integration/test_timezone_preservation.py"
Task: "Integration test for manufacturer standardization in tests/integration/test_manufacturer_mapping.py"
Task: "Integration test for quality scoring in tests/integration/test_quality_assessment.py"
```

```
# Launch T014, T015, T017 model creation together:
Task: "Create MetadataSource enum in src/models/consolidated_metadata.py"
Task: "Create MetadataField data model in src/models/consolidated_metadata.py"
Task: "Create MetadataQuality data model in src/models/consolidated_metadata.py"
```

```
# Launch T028-T032 unit tests together:
Task: "Unit tests for priority resolution in tests/unit/test_priority_resolver.py"
Task: "Unit tests for timezone preservation in tests/unit/test_timezone_preserver.py"
Task: "Unit tests for manufacturer standardization in tests/unit/test_manufacturer_standardizer.py"
Task: "Unit tests for quality assessment in tests/unit/test_quality_assessor.py"
Task: "Unit tests for metadata field handling in tests/unit/test_metadata_field.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- No external dependencies needed (standard library only)
- Timezone preservation is critical - never convert to UTC

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - contracts/metadata_consolidator.py → 6 contract test tasks [P]
     - MetadataConsolidator.consolidate
     - MetadataConsolidator.assess_quality
     - PriorityResolver.resolve_field
     - PriorityResolver.get_priority_order
     - TimezonePreserver.preserve_timezone
     - ManufacturerStandardizer.standardize

2. **From Plan Components**:
   - MetadataSource enum → model creation task [P]
   - MetadataField entity → model creation task [P]
   - ConsolidatedMetadata entity → model creation task
   - MetadataQuality entity → model creation task [P]
   - PriorityResolver service → implementation task
   - TimezonePreserver service → implementation task
   - ManufacturerStandardizer service → implementation task
   - MetadataQualityAssessor service → implementation task
   - MetadataConsolidator service → implementation task

3. **From Integration Points**:
   - Priority rules configuration → config task
   - Manufacturer mappings configuration → config task
   - Processor coordination → integration task
   - Logging integration → integration task

4. **From Success Criteria**:
   - Single processor consolidation → integration test [P]
   - Multi-processor consolidation → integration test [P]
   - Conflict resolution → integration test [P]
   - Timezone preservation → integration test [P]
   - Manufacturer standardization → integration test [P]
   - Quality assessment → integration test [P]

5. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (6 contracts → 6 contract tests + 6 integration tests)
- [x] All entities have model tasks (4 entities → 4 model tasks)
- [x] All tests come before implementation (T002-T013 before T014-T022)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
