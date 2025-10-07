# Tasks: File Renamer

**Input**: Design documents from `/specs/009-file-renamer/`
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
   → Integration: configuration, metadata consolidator
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

## Phase 9.1: Setup
- [ ] T001 No new dependencies needed (uses Python standard library only)

## Phase 9.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 9.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T002 [P] Contract test for FilenameGenerator.generate in tests/contract/test_filename_generator.py
- [ ] T003 [P] Contract test for FilenameGenerator.check_collision in tests/contract/test_filename_collision.py
- [ ] T004 [P] Contract test for NamingPatternEngine.apply_pattern in tests/contract/test_naming_pattern.py
- [ ] T005 [P] Contract test for MetadataSanitizer.sanitize in tests/contract/test_metadata_sanitizer.py
- [ ] T006 [P] Contract test for CollisionDetector.resolve_collision in tests/contract/test_collision_detector.py
- [ ] T007 [P] Contract test for LengthLimiter.limit_length in tests/contract/test_length_limiter.py
- [ ] T008 [P] Integration test for image filename generation in tests/integration/test_image_filename_generation.py
- [ ] T009 [P] Integration test for document filename generation in tests/integration/test_document_filename_generation.py
- [ ] T010 [P] Integration test for audio filename generation in tests/integration/test_audio_filename_generation.py
- [ ] T011 [P] Integration test for video filename generation in tests/integration/test_video_filename_generation.py
- [ ] T012 [P] Integration test for collision resolution in tests/integration/test_collision_resolution_flow.py
- [ ] T013 [P] Integration test for length truncation in tests/integration/test_length_truncation_flow.py

## Phase 9.3: Core Implementation (ONLY after tests are failing)
- [ ] T014 [P] Create GeneratedFilename data model in src/models/generated_filename.py
- [ ] T015 Implement NamingPatternEngine with template parsing in src/services/naming_pattern_engine.py
- [ ] T016 Implement ComponentFormatter for metadata formatting in src/services/component_formatter.py
- [ ] T017 Implement MetadataSanitizer for character cleaning in src/services/metadata_sanitizer.py
- [ ] T018 Implement CollisionDetector with 8-digit counters in src/services/collision_detector.py
- [ ] T019 Implement LengthLimiter with intelligent truncation in src/services/length_limiter.py
- [ ] T020 Implement FilenameGenerator main orchestration in src/services/filename_generator.py

## Phase 9.4: Integration
- [ ] T021 Create naming patterns configuration in config/naming_patterns.json
- [ ] T022 Create sanitization rules configuration in config/filename_sanitization.json
- [ ] T023 Create truncation priority configuration in config/truncation_rules.json
- [ ] T024 Add comprehensive logging to filename generation services
- [ ] T025 Integrate with MetadataConsolidator for metadata input
- [ ] T026 Add filename registry and collision tracking

## Phase 9.5: Polish
- [ ] T027 [P] Unit tests for pattern parsing in tests/unit/test_pattern_engine.py
- [ ] T028 [P] Unit tests for sanitization in tests/unit/test_sanitizer.py
- [ ] T029 [P] Unit tests for collision detection in tests/unit/test_collision_detector.py
- [ ] T030 [P] Unit tests for length limiting in tests/unit/test_length_limiter.py
- [ ] T031 [P] Unit tests for component formatting in tests/unit/test_component_formatter.py
- [ ] T032 Performance tests for bulk filename generation (1000+ files)
- [ ] T033 Test edge cases (extremely long metadata, Unicode, special characters)
- [ ] T034 Test cross-platform compatibility (Windows, macOS, Linux)
- [ ] T035 Test preview mode functionality
- [ ] T036 Remove code duplication and optimize critical paths

## Dependencies
- Tests (T002-T013) before implementation (T014-T020)
- T014 (model) before T015-T020 (services)
- T015-T019 (utility services) block T020 (main generator)
- Core implementation before integration (T021-T026)
- Everything before polish (T027-T036)

## Parallel Example
```
# Launch T002-T007 contract tests together:
Task: "Contract test for FilenameGenerator.generate in tests/contract/test_filename_generator.py"
Task: "Contract test for FilenameGenerator.check_collision in tests/contract/test_filename_collision.py"
Task: "Contract test for NamingPatternEngine.apply_pattern in tests/contract/test_naming_pattern.py"
Task: "Contract test for MetadataSanitizer.sanitize in tests/contract/test_metadata_sanitizer.py"
Task: "Contract test for CollisionDetector.resolve_collision in tests/contract/test_collision_detector.py"
Task: "Contract test for LengthLimiter.limit_length in tests/contract/test_length_limiter.py"
```

```
# Launch T008-T013 integration tests together:
Task: "Integration test for image filename generation in tests/integration/test_image_filename_generation.py"
Task: "Integration test for document filename generation in tests/integration/test_document_filename_generation.py"
Task: "Integration test for audio filename generation in tests/integration/test_audio_filename_generation.py"
Task: "Integration test for video filename generation in tests/integration/test_video_filename_generation.py"
Task: "Integration test for collision resolution in tests/integration/test_collision_resolution_flow.py"
Task: "Integration test for length truncation in tests/integration/test_length_truncation_flow.py"
```

```
# Launch T027-T031 unit tests together:
Task: "Unit tests for pattern parsing in tests/unit/test_pattern_engine.py"
Task: "Unit tests for sanitization in tests/unit/test_sanitizer.py"
Task: "Unit tests for collision detection in tests/unit/test_collision_detector.py"
Task: "Unit tests for length limiting in tests/unit/test_length_limiter.py"
Task: "Unit tests for component formatting in tests/unit/test_component_formatter.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- No external dependencies needed (standard library only)
- Filename generation is critical - ensure cross-platform compatibility

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - contracts/filename_generator.py → 6 contract test tasks [P]
     - FilenameGenerator.generate
     - FilenameGenerator.check_collision
     - NamingPatternEngine.apply_pattern
     - MetadataSanitizer.sanitize
     - CollisionDetector.resolve_collision
     - LengthLimiter.limit_length

2. **From Plan Components**:
   - GeneratedFilename entity → model creation task [P]
   - NamingPatternEngine service → implementation task
   - ComponentFormatter service → implementation task
   - MetadataSanitizer service → implementation task
   - CollisionDetector service → implementation task
   - LengthLimiter service → implementation task
   - FilenameGenerator service → implementation task

3. **From Integration Points**:
   - Naming patterns configuration → config task
   - Sanitization rules configuration → config task
   - Truncation priorities configuration → config task
   - MetadataConsolidator integration → integration task
   - Logging integration → integration task

4. **From Success Criteria**:
   - Image filename generation → integration test [P]
   - Document filename generation → integration test [P]
   - Audio filename generation → integration test [P]
   - Video filename generation → integration test [P]
   - Collision resolution → integration test [P]
   - Length truncation → integration test [P]

5. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (6 contracts → 6 contract tests + 6 integration tests)
- [x] All entities have model tasks (1 entity → 1 model task)
- [x] All tests come before implementation (T002-T013 before T014-T020)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
