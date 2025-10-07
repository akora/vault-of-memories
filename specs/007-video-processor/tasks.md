# Tasks: Video Processor

**Input**: Design documents from `/specs/007-video-processor/`
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
   → Integration: processor routing, configuration
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

## Phase 7.1: Setup
- [ ] T001 Add pymediainfo dependency to requirements.txt

## Phase 7.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 7.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T002 [P] Contract test for VideoProcessor.process_video with MP4 in tests/contract/test_video_processor_mp4.py
- [ ] T003 [P] Contract test for VideoProcessor.process_video with AVI in tests/contract/test_video_processor_avi.py
- [ ] T004 [P] Contract test for VideoProcessor.process_video with MOV in tests/contract/test_video_processor_mov.py
- [ ] T005 [P] Contract test for VideoProcessor.process_video with MKV in tests/contract/test_video_processor_mkv.py
- [ ] T006 [P] Contract test for VideoProcessor.process_video with WebM in tests/contract/test_video_processor_webm.py
- [ ] T007 [P] Contract test for VideoProcessor.supports_format in tests/contract/test_video_processor_supports_format.py
- [ ] T008 [P] Contract test for ContentCategorizer.categorize in tests/contract/test_content_categorizer.py
- [ ] T009 [P] Integration test for MP4 metadata extraction in tests/integration/test_video_mp4_metadata.py
- [ ] T010 [P] Integration test for resolution detection in tests/integration/test_video_resolution_detection.py
- [ ] T011 [P] Integration test for camera info extraction in tests/integration/test_video_camera_info.py
- [ ] T012 [P] Integration test for content categorization in tests/integration/test_video_categorization.py
- [ ] T013 [P] Integration test for GPS extraction in tests/integration/test_video_gps_extraction.py
- [ ] T014 [P] Integration test for multi-stream videos in tests/integration/test_video_multi_stream.py

## Phase 7.3: Core Implementation (ONLY after tests are failing)
- [ ] T015 [P] Create VideoMetadata data model in src/models/video_metadata.py
- [ ] T016 [P] Create CategoryResult data model in src/models/video_metadata.py
- [ ] T017 Implement media info extractor using pymediainfo in src/services/media_info_extractor.py
- [ ] T018 Implement resolution detector in src/services/resolution_detector.py
- [ ] T019 Implement content categorizer in src/services/content_categorizer.py
- [ ] T020 Implement VideoProcessor interface in src/services/video_processor.py

## Phase 7.4: Integration
- [ ] T021 Register VideoProcessor with ProcessorRouter in src/services/processor_router.py
- [ ] T022 Add video format configuration to config/video_processing.json
- [ ] T023 Add comprehensive logging to video processing services
- [ ] T024 Integrate with configuration system for categorization rules

## Phase 7.5: Polish
- [ ] T025 [P] Unit tests for media info extraction in tests/unit/test_media_info_extractor.py
- [ ] T026 [P] Unit tests for resolution detection in tests/unit/test_resolution_detector.py
- [ ] T027 [P] Unit tests for content categorization in tests/unit/test_content_categorizer.py
- [ ] T028 [P] Unit tests for video metadata model in tests/unit/test_video_metadata.py
- [ ] T029 Performance tests for large video file processing (>1GB files)
- [ ] T030 Performance tests for batch video processing (50+ files)
- [ ] T031 Test categorization accuracy with various video types
- [ ] T032 Test multi-stream and multi-angle video handling
- [ ] T033 Remove code duplication and optimize critical paths

## Dependencies
- Setup (T001) before everything else
- Tests (T002-T014) before implementation (T015-T020)
- T015-T016 (models) before T017-T020 (services)
- T017-T019 (utilities) block T020 (processor)
- Core implementation before integration (T021-T024)
- Everything before polish (T025-T033)

## Parallel Example
```
# Launch T002-T008 contract tests together:
Task: "Contract test for VideoProcessor.process_video with MP4 in tests/contract/test_video_processor_mp4.py"
Task: "Contract test for VideoProcessor.process_video with AVI in tests/contract/test_video_processor_avi.py"
Task: "Contract test for VideoProcessor.process_video with MOV in tests/contract/test_video_processor_mov.py"
Task: "Contract test for VideoProcessor.process_video with MKV in tests/contract/test_video_processor_mkv.py"
Task: "Contract test for VideoProcessor.process_video with WebM in tests/contract/test_video_processor_webm.py"
Task: "Contract test for VideoProcessor.supports_format in tests/contract/test_video_processor_supports_format.py"
Task: "Contract test for ContentCategorizer.categorize in tests/contract/test_content_categorizer.py"
```

```
# Launch T009-T014 integration tests together:
Task: "Integration test for MP4 metadata extraction in tests/integration/test_video_mp4_metadata.py"
Task: "Integration test for resolution detection in tests/integration/test_video_resolution_detection.py"
Task: "Integration test for camera info extraction in tests/integration/test_video_camera_info.py"
Task: "Integration test for content categorization in tests/integration/test_video_categorization.py"
Task: "Integration test for GPS extraction in tests/integration/test_video_gps_extraction.py"
Task: "Integration test for multi-stream videos in tests/integration/test_video_multi_stream.py"
```

```
# Launch T025-T028 unit tests together:
Task: "Unit tests for media info extraction in tests/unit/test_media_info_extractor.py"
Task: "Unit tests for resolution detection in tests/unit/test_resolution_detector.py"
Task: "Unit tests for content categorization in tests/unit/test_content_categorizer.py"
Task: "Unit tests for video metadata model in tests/unit/test_video_metadata.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- Use pymediainfo for all video format handling
- Ensure MediaInfo CLI tool is installed on system

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - contracts/video_processor.py → 8 contract test tasks [P]
     - 5 format-specific tests (MP4, AVI, MOV, MKV, WebM)
     - 1 supports_format test
     - 1 ContentCategorizer test
     - 1 error handling test

2. **From Plan Components**:
   - VideoMetadata entity → model creation task [P]
   - CategoryResult entity → model creation task [P]
   - MediaInfoExtractor service → implementation task
   - ResolutionDetector service → implementation task
   - ContentCategorizer service → implementation task
   - VideoProcessor service → implementation task

3. **From Integration Points**:
   - ProcessorRouter integration → integration task
   - Configuration system integration → integration task
   - Logging integration → integration task

4. **From Success Criteria**:
   - MP4 metadata extraction → integration test [P]
   - Resolution detection → integration test [P]
   - Camera info extraction → integration test [P]
   - Content categorization → integration test [P]
   - GPS extraction → integration test [P]
   - Multi-stream handling → integration test [P]

5. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (2 contracts → 8 contract tests)
- [x] All entities have model tasks (2 entities → 2 model tasks)
- [x] All tests come before implementation (T002-T014 before T015-T020)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
