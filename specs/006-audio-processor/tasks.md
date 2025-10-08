# Tasks: Audio Processor

**Input**: Design documents from `/specs/006-audio-processor/`
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

## Phase 6.1: Setup
- [x] T001 Add mutagen dependency to requirements.txt

## Phase 6.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 6.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T002 [P] Contract test for AudioProcessor.process_audio with MP3 in tests/contract/test_audio_processor_mp3.py
- [x] T003 [P] Contract test for AudioProcessor.process_audio with FLAC in tests/contract/test_audio_processor_flac.py
- [x] T004 [P] Contract test for AudioProcessor.process_audio with M4A in tests/contract/test_audio_processor_m4a.py
- [x] T005 [P] Contract test for AudioProcessor.process_audio with OGG in tests/contract/test_audio_processor_ogg.py
- [x] T006 [P] Contract test for AudioProcessor.process_audio with WMA in tests/contract/test_audio_processor_wma.py
- [x] T007 [P] Contract test for AudioProcessor.supports_format in tests/contract/test_audio_processor_supports_format.py
- [x] T008 [P] Integration test for MP3 metadata extraction in tests/integration/test_audio_mp3_metadata.py
- [x] T009 [P] Integration test for FLAC metadata extraction in tests/integration/test_audio_flac_metadata.py
- [x] T010 [P] Integration test for audio quality classification in tests/integration/test_audio_quality_classification.py
- [x] T011 [P] Integration test for missing metadata handling in tests/integration/test_audio_missing_metadata.py
- [x] T012 [P] Integration test for corrupted audio file handling in tests/integration/test_audio_corrupted_files.py

## Phase 6.3: Core Implementation (ONLY after tests are failing)
- [x] T013 [P] Create AudioMetadata data model in src/models/audio_metadata.py
- [x] T014 Implement tag extraction service using mutagen in src/services/tag_extractor.py
- [x] T015 Implement audio quality classifier in src/services/audio_quality_classifier.py
- [x] T016 Implement AudioProcessor interface in src/services/audio_processor.py

## Phase 6.4: Integration
- [x] T017 Register AudioProcessor with ProcessorRouter in src/services/processor_router.py
- [x] T018 Add audio format configuration to config/audio_processing.json
- [x] T019 Add comprehensive logging to audio processing services
- [x] T020 Integrate with configuration system for quality thresholds

## Phase 6.5: Polish
- [ ] T021 [P] Unit tests for tag extraction in tests/unit/test_tag_extractor.py
- [ ] T022 [P] Unit tests for quality classification in tests/unit/test_audio_quality_classifier.py
- [ ] T023 [P] Unit tests for audio metadata model in tests/unit/test_audio_metadata.py
- [ ] T024 Performance tests for large audio file processing (>100MB files)
- [ ] T025 Performance tests for batch audio processing (100+ files)
- [ ] T026 Test VBR vs CBR bitrate calculation accuracy
- [ ] T027 Test multiple tag format handling (ID3v1, ID3v2, Vorbis)
- [ ] T028 Remove code duplication and optimize critical paths

## Dependencies
- Setup (T001) before everything else
- Tests (T002-T012) before implementation (T013-T016)
- T013 (model) before T014-T016 (services)
- T014-T015 (utilities) block T016 (processor)
- Core implementation before integration (T017-T020)
- Everything before polish (T021-T028)

## Parallel Example
```
# Launch T002-T007 contract tests together:
Task: "Contract test for AudioProcessor.process_audio with MP3 in tests/contract/test_audio_processor_mp3.py"
Task: "Contract test for AudioProcessor.process_audio with FLAC in tests/contract/test_audio_processor_flac.py"
Task: "Contract test for AudioProcessor.process_audio with M4A in tests/contract/test_audio_processor_m4a.py"
Task: "Contract test for AudioProcessor.process_audio with OGG in tests/contract/test_audio_processor_ogg.py"
Task: "Contract test for AudioProcessor.process_audio with WMA in tests/contract/test_audio_processor_wma.py"
Task: "Contract test for AudioProcessor.supports_format in tests/contract/test_audio_processor_supports_format.py"
```

```
# Launch T008-T012 integration tests together:
Task: "Integration test for MP3 metadata extraction in tests/integration/test_audio_mp3_metadata.py"
Task: "Integration test for FLAC metadata extraction in tests/integration/test_audio_flac_metadata.py"
Task: "Integration test for audio quality classification in tests/integration/test_audio_quality_classification.py"
Task: "Integration test for missing metadata handling in tests/integration/test_audio_missing_metadata.py"
Task: "Integration test for corrupted audio file handling in tests/integration/test_audio_corrupted_files.py"
```

```
# Launch T021-T023 unit tests together:
Task: "Unit tests for tag extraction in tests/unit/test_tag_extractor.py"
Task: "Unit tests for quality classification in tests/unit/test_audio_quality_classifier.py"
Task: "Unit tests for audio metadata model in tests/unit/test_audio_metadata.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all contract tests fail before implementing services
- Each task must include exact file path for implementation
- Follow TDD strictly: Red → Green → Refactor
- Constitution compliance verified at each phase
- Use mutagen for all audio format handling

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - contracts/audio_processor.py → 7 contract test tasks [P]
     - 5 format-specific tests (MP3, FLAC, M4A, OGG, WMA)
     - 1 supports_format test
     - 1 error handling test

2. **From Plan Components**:
   - AudioMetadata entity → model creation task [P]
   - TagExtractor service → implementation task
   - QualityClassifier service → implementation task
   - AudioProcessor service → implementation task

3. **From Integration Points**:
   - ProcessorRouter integration → integration task
   - Configuration system integration → integration task
   - Logging integration → integration task

4. **From Success Criteria**:
   - MP3 metadata extraction → integration test [P]
   - FLAC metadata extraction → integration test [P]
   - Quality classification → integration test [P]
   - Missing metadata handling → integration test [P]
   - Corrupted file handling → integration test [P]

5. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (1 contract → 7 contract tests)
- [x] All entities have model tasks (1 entity → 1 model task)
- [x] All tests come before implementation (T002-T012 before T013-T016)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path for implementation
- [x] No task modifies same file as another [P] task
