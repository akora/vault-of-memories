# Tasks: CLI Interface

**Feature**: #013 CLI Interface
**Branch**: `013-cli-interface`
**Input**: Design documents from `/specs/013-cli-interface/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

---

## Overview

This task list implements the CLI Interface feature that orchestrates the complete vault processing pipeline. The implementation follows TDD principles with contract tests before implementation.

**Total Tasks**: 38
**Estimated Duration**: 3-4 days

---

## Phase 13.1: Setup & Configuration

### T001: Verify stdlib dependencies
**File**: N/A (verification only)
**Action**: Verify Python 3.11 stdlib modules are available (argparse, logging, pathlib, signal, sys)
**Success**: All modules importable, no installation needed

### T002: Create CLI module structure
**Files**:
- `src/cli/__init__.py`
- `src/cli/commands/__init__.py`
- `src/cli/formatters/__init__.py`

**Action**: Create directory structure and empty __init__.py files for CLI module
**Success**: Directories created, imports work

### T003 [P]: Configure logging for CLI
**File**: `src/cli/logging_config.py`
**Action**: Create logging configuration with console and file handlers
**Success**: Logging setup with INFO/DEBUG levels, formatted output

---

## Phase 13.2: Data Models (TDD - Models First)

### T004 [P]: Create PipelineStage enum
**File**: `src/models/pipeline_stage.py`
**Action**: Create PipelineStage enum with all processing stages
**Success**: Enum with INITIALIZING, DISCOVERING, INGESTING, EXTRACTING, CONSOLIDATING, RENAMING, ORGANIZING, MOVING, SUMMARIZING, COMPLETE, FAILED

### T005 [P]: Create ProcessingContext model
**File**: `src/models/processing_context.py`
**Action**: Create ProcessingContext dataclass with validation
**Contract**: See data-model.md section 1
**Success**: Model with source_path, vault_root, config, dry_run, verbose, max_workers, batch_size, created_at

### T006 [P]: Create ProgressState model
**File**: `src/models/progress_state.py`
**Action**: Create ProgressState dataclass with calculated properties
**Contract**: See data-model.md section 2
**Success**: Model with counters, properties for percent_complete, elapsed_time, avg_time_per_file, update_estimates()

### T007 [P]: Create ProcessingResult model
**File**: `src/models/processing_result.py`
**Action**: Create ProcessingResult dataclass with summary methods
**Contract**: See data-model.md section 3
**Success**: Model with context, final_state, file lists, properties for success_rate, had_errors, summary_stats

### T008 [P]: Create CommandOptions model
**File**: `src/models/command_options.py`
**Action**: Create CommandOptions dataclass with from_args classmethod
**Contract**: See data-model.md section 4
**Success**: Model with all CLI options, from_args() converts argparse.Namespace

### T009: Update models __init__.py
**File**: `src/models/__init__.py`
**Action**: Export new CLI models (ProcessingContext, ProgressState, ProcessingResult, CommandOptions, PipelineStage)
**Success**: All models importable from src.models

---

## Phase 13.3: Contract Tests (TDD - Tests MUST Fail)

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY service implementation

### T010 [P]: Contract test for PipelineOrchestrator
**File**: `tests/contract/test_pipeline_orchestrator.py`
**Action**: Write contract test validating PipelineOrchestrator protocol
**Contract**: See contracts/pipeline_orchestrator.py
**Test Cases**:
- test_execute_contract: Validates execute() signature and behavior
- test_validate_context_contract: Validates validation errors format
- test_discover_files_contract: Validates file discovery
- test_process_file_contract: Validates single file processing
- test_handle_interruption_contract: Validates graceful interruption

**Success**: Test fails with "PipelineOrchestrator not implemented"

### T011 [P]: Contract test for ProgressMonitor
**File**: `tests/contract/test_progress_monitor.py`
**Action**: Write contract test validating ProgressMonitor protocol
**Contract**: See contracts/progress_monitor.py
**Test Cases**:
- test_subscribe_contract: Validates subscription mechanism
- test_update_contract: Validates state updates and notifications
- test_get_state_contract: Validates state snapshot
- test_reset_contract: Validates progress reset

**Success**: Test fails with "ProgressMonitor not implemented"

### T012 [P]: Contract test for CommandHandler
**File**: `tests/contract/test_command_handler.py`
**Action**: Write contract test validating CommandHandler protocol
**Contract**: See contracts/command_handler.py
**Test Cases**:
- test_process_command_contract: Validates process command
- test_status_command_contract: Validates status command
- test_recover_command_contract: Validates recover command
- test_validate_command_contract: Validates validate command

**Success**: Test fails with "Commands not implemented"

### T013 [P]: Contract test for SummaryFormatter
**File**: `tests/contract/test_summary_formatter.py`
**Action**: Write contract test validating SummaryFormatter protocol
**Contract**: See contracts/summary_formatter.py
**Test Cases**:
- test_format_result_contract: Validates result formatting
- test_format_error_report_contract: Validates error report
- test_format_statistics_contract: Validates statistics table

**Success**: Test fails with "SummaryFormatter not implemented"

---

## Phase 13.4: Core Service Implementation

### T014: Implement PipelineOrchestrator service
**File**: `src/services/pipeline_orchestrator.py`
**Action**: Implement PipelineOrchestrator that coordinates all processing modules
**Contract**: See contracts/pipeline_orchestrator.py
**Dependencies**: T005-T007 (models), existing services (FileIngestor, MetadataConsolidator, OrganizationManager, FileMover)
**Success**:
- execute() runs complete pipeline
- validate_context() checks source/vault paths
- discover_files() finds all processable files
- process_file() executes all stages
- handle_interruption() saves state gracefully
- T010 contract test passes

### T015: Implement InterruptHandler service
**File**: `src/services/interrupt_handler.py`
**Action**: Implement signal handling for graceful interruption
**Contract**: See contracts/pipeline_orchestrator.py InterruptHandler
**Success**:
- register() sets SIGINT/SIGTERM handlers
- is_interrupted() returns flag
- Coordinates with orchestrator for cleanup

### T016: Implement ProgressMonitor service
**File**: `src/services/progress_monitor.py`
**Action**: Implement progress tracking with subscriber notifications
**Contract**: See contracts/progress_monitor.py ProgressMonitor
**Dependencies**: T006 (ProgressState model)
**Success**:
- subscribe/unsubscribe manage callbacks
- update() modifies state and notifies
- get_state() returns immutable snapshot
- reset() starts new tracking
- Throttles updates (100ms minimum)
- T011 contract test passes

### T017 [P]: Implement ProgressFormatter
**File**: `src/cli/formatters/progress_formatter.py`
**Action**: Implement progress display formatting
**Contract**: See contracts/progress_monitor.py ProgressFormatter
**Success**:
- format() creates single-line progress display
- format_summary() creates final statistics
- Handles terminal width detection

### T018 [P]: Implement ProgressBar renderer
**File**: `src/cli/formatters/progress_bar.py`
**Action**: Implement ASCII progress bar rendering
**Contract**: See contracts/progress_monitor.py ProgressBar
**Success**:
- render() creates progress bar with percentage
- Auto-detects terminal width
- Handles edge cases (current > total, total = 0)

### T019: Implement SummaryFormatter service
**File**: `src/cli/formatters/summary_formatter.py`
**Action**: Implement result and error report formatting
**Contract**: See contracts/summary_formatter.py SummaryFormatter
**Dependencies**: T007 (ProcessingResult model)
**Success**:
- format_result() creates readable summary
- format_error_report() lists errors by type
- format_statistics() creates aligned table
- format_file_list() shows file paths
- T013 contract test passes

### T020 [P]: Implement ColorFormatter utility
**File**: `src/cli/formatters/color_formatter.py`
**Action**: Implement ANSI color formatting utilities
**Contract**: See contracts/summary_formatter.py ColorFormatter
**Success**:
- colorize() applies ANSI codes
- success/warning/error/info helpers
- is_terminal() detects TTY
- Respects NO_COLOR env var

### T021 [P]: Implement ProgressDisplay
**File**: `src/cli/formatters/progress_display.py`
**Action**: Implement real-time progress display
**Contract**: See contracts/summary_formatter.py ProgressDisplay
**Success**:
- display() updates single line
- display_final() shows final state
- clear() clears display line

### T022: Update services __init__.py
**File**: `src/services/__init__.py`
**Action**: Export new services (PipelineOrchestrator, InterruptHandler, ProgressMonitor)
**Success**: Services importable from src.services

---

## Phase 13.5: CLI Commands Implementation

### T023: Implement ProcessCommand
**File**: `src/cli/commands/process.py`
**Action**: Implement main processing command
**Contract**: See contracts/command_handler.py ProcessCommand
**Dependencies**: T014 (PipelineOrchestrator), T016 (ProgressMonitor), T019 (SummaryFormatter)
**Success**:
- validate() checks source path exists
- execute() runs pipeline with progress
- Displays progress (unless --quiet)
- Generates summary
- Returns appropriate exit code
- T012 contract test passes (process command)

### T024 [P]: Implement StatusCommand
**File**: `src/cli/commands/status.py`
**Action**: Implement vault status checking command
**Contract**: See contracts/command_handler.py StatusCommand
**Success**:
- Queries database for statistics
- Checks quarantine folders
- Displays file counts by type
- Highlights issues
- T012 contract test passes (status command)

### T025 [P]: Implement RecoverCommand
**File**: `src/cli/commands/recover.py`
**Action**: Implement quarantine recovery command
**Contract**: See contracts/command_handler.py RecoverCommand
**Dependencies**: T014 (PipelineOrchestrator)
**Success**:
- Lists quarantined files
- Filters by quarantine_type if specified
- Reprocesses through pipeline
- Updates quarantine records
- Asks confirmation unless --force
- T012 contract test passes (recover command)

### T026 [P]: Implement ValidateCommand
**File**: `src/cli/commands/validate.py`
**Action**: Implement pre-processing validation command
**Contract**: See contracts/command_handler.py ValidateCommand
**Success**:
- Checks files are readable
- Detects file types
- Estimates disk space needed
- Reports unsupported formats
- No modifications (dry-run++)
- T012 contract test passes (validate command)

### T027: Update commands __init__.py
**File**: `src/cli/commands/__init__.py`
**Action**: Export all commands (ProcessCommand, StatusCommand, RecoverCommand, ValidateCommand)
**Success**: Commands importable from src.cli.commands

---

## Phase 13.6: CLI Entry Point & Argument Parsing

### T028: Implement argument parser
**File**: `src/cli/arg_parser.py`
**Action**: Create argparse-based CLI argument parser
**Success**:
- Main parser with subcommands
- process subcommand with source, --dry-run, --verbose, --quiet
- status subcommand with --vault-root
- recover subcommand with --quarantine-type, --force
- validate subcommand with source
- Global options: --vault-root, --config, --log-file, --workers, --batch-size
- Generates help text

### T029: Implement main CLI entry point
**File**: `src/cli/main.py`
**Action**: Create main() function that coordinates argument parsing and command execution
**Dependencies**: T023-T026 (commands), T028 (arg_parser)
**Success**:
- Parses arguments
- Creates CommandOptions
- Selects appropriate command
- Executes command
- Returns exit code
- Handles exceptions gracefully

### T030: Update cli __init__.py
**File**: `src/cli/__init__.py`
**Action**: Export main entry point
**Success**: main() importable from src.cli

---

## Phase 13.7: Integration Tests (User Story Validation)

**Reference**: quickstart.md for detailed scenarios

### T031 [P]: Integration test - Single file processing
**File**: `tests/integration/test_cli_single_file.py`
**Action**: Test complete pipeline on single file
**Scenario**: quickstart.md Scenario 1
**Success**: File processed, moved to vault, database updated

### T032 [P]: Integration test - Directory processing
**File**: `tests/integration/test_cli_directory.py`
**Action**: Test processing directory with mixed files
**Scenario**: quickstart.md Scenario 2
**Success**: All files processed, organized by type

### T033 [P]: Integration test - Error handling
**File**: `tests/integration/test_cli_errors.py`
**Action**: Test quarantine of problematic files
**Scenario**: quickstart.md Scenario 3
**Success**: Good files processed, bad files quarantined, summary shows errors

### T034 [P]: Integration test - Interruption handling
**File**: `tests/integration/test_cli_interrupt.py`
**Action**: Test graceful Ctrl+C handling
**Scenario**: quickstart.md Scenario 4
**Success**: Current file finishes, state saved, partial summary

### T035 [P]: Integration test - Dry-run mode
**File**: `tests/integration/test_cli_dry_run.py`
**Action**: Test preview mode without modifications
**Scenario**: quickstart.md Scenario 5
**Success**: No files modified, preview report generated

### T036 [P]: Integration test - Duplicate detection
**File**: `tests/integration/test_cli_duplicates.py`
**Action**: Test duplicate file handling
**Scenario**: quickstart.md Scenario 6
**Success**: First file to vault, duplicate detected and stored separately

### T037 [P]: Integration test - Commands (status, recover, validate)
**File**: `tests/integration/test_cli_commands.py`
**Action**: Test status, recover, and validate commands
**Scenarios**: quickstart.md Scenarios 7, 8
**Success**: All commands work correctly, appropriate output

---

## Phase 13.8: Polish & Documentation

### T038: Run full test suite and verify
**Files**: All test files
**Action**: Run all contract and integration tests, verify 100% pass rate
**Success**:
- All contract tests pass (T010-T013)
- All integration tests pass (T031-T037)
- No regressions in existing tests

---

## Dependencies

**Critical Path**:
```
Setup (T001-T003)
    ↓
Models (T004-T009)
    ↓
Contract Tests (T010-T013) ← MUST FAIL before implementation
    ↓
Services (T014-T022)
    ↓
Commands (T023-T027)
    ↓
Entry Point (T028-T030)
    ↓
Integration Tests (T031-T037)
    ↓
Polish (T038)
```

**Blocking Dependencies**:
- T010-T013 (tests) MUST complete before T014-T022 (implementation)
- T014 (PipelineOrchestrator) blocks T023, T025
- T016 (ProgressMonitor) blocks T023
- T019 (SummaryFormatter) blocks T023
- T023-T026 (commands) block T029 (main entry)
- T029 blocks T031-T037 (integration tests)

---

## Parallel Execution Examples

### Phase 13.2: Models (All Parallel)
```bash
# Launch T004-T008 together:
Task: "Create PipelineStage enum in src/models/pipeline_stage.py"
Task: "Create ProcessingContext model in src/models/processing_context.py"
Task: "Create ProgressState model in src/models/progress_state.py"
Task: "Create ProcessingResult model in src/models/processing_result.py"
Task: "Create CommandOptions model in src/models/command_options.py"
```

### Phase 13.3: Contract Tests (All Parallel)
```bash
# Launch T010-T013 together:
Task: "Contract test for PipelineOrchestrator in tests/contract/test_pipeline_orchestrator.py"
Task: "Contract test for ProgressMonitor in tests/contract/test_progress_monitor.py"
Task: "Contract test for CommandHandler in tests/contract/test_command_handler.py"
Task: "Contract test for SummaryFormatter in tests/contract/test_summary_formatter.py"
```

### Phase 13.5: Commands (Parallel after orchestrator)
```bash
# After T014-T022 complete, launch T024-T026 together (T023 sequential):
Task: "Implement StatusCommand in src/cli/commands/status.py"
Task: "Implement RecoverCommand in src/cli/commands/recover.py"
Task: "Implement ValidateCommand in src/cli/commands/validate.py"
```

### Phase 13.7: Integration Tests (All Parallel)
```bash
# Launch T031-T037 together:
Task: "Integration test single file in tests/integration/test_cli_single_file.py"
Task: "Integration test directory in tests/integration/test_cli_directory.py"
Task: "Integration test errors in tests/integration/test_cli_errors.py"
Task: "Integration test interrupt in tests/integration/test_cli_interrupt.py"
Task: "Integration test dry-run in tests/integration/test_cli_dry_run.py"
Task: "Integration test duplicates in tests/integration/test_cli_duplicates.py"
Task: "Integration test commands in tests/integration/test_cli_commands.py"
```

---

## Task Checklist

### Phase 13.1: Setup
- [ ] T001: Verify stdlib dependencies
- [ ] T002: Create CLI module structure
- [ ] T003 [P]: Configure logging

### Phase 13.2: Models
- [ ] T004 [P]: PipelineStage enum
- [ ] T005 [P]: ProcessingContext model
- [ ] T006 [P]: ProgressState model
- [ ] T007 [P]: ProcessingResult model
- [ ] T008 [P]: CommandOptions model
- [ ] T009: Update models __init__.py

### Phase 13.3: Contract Tests (MUST FAIL)
- [ ] T010 [P]: Contract test PipelineOrchestrator
- [ ] T011 [P]: Contract test ProgressMonitor
- [ ] T012 [P]: Contract test CommandHandler
- [ ] T013 [P]: Contract test SummaryFormatter

### Phase 13.4: Services
- [ ] T014: Implement PipelineOrchestrator
- [ ] T015: Implement InterruptHandler
- [ ] T016: Implement ProgressMonitor
- [ ] T017 [P]: Implement ProgressFormatter
- [ ] T018 [P]: Implement ProgressBar
- [ ] T019: Implement SummaryFormatter
- [ ] T020 [P]: Implement ColorFormatter
- [ ] T021 [P]: Implement ProgressDisplay
- [ ] T022: Update services __init__.py

### Phase 13.5: Commands
- [ ] T023: Implement ProcessCommand
- [ ] T024 [P]: Implement StatusCommand
- [ ] T025 [P]: Implement RecoverCommand
- [ ] T026 [P]: Implement ValidateCommand
- [ ] T027: Update commands __init__.py

### Phase 13.6: Entry Point
- [ ] T028: Implement argument parser
- [ ] T029: Implement main entry point
- [ ] T030: Update cli __init__.py

### Phase 13.7: Integration Tests
- [ ] T031 [P]: Test single file processing
- [ ] T032 [P]: Test directory processing
- [ ] T033 [P]: Test error handling
- [ ] T034 [P]: Test interruption
- [ ] T035 [P]: Test dry-run mode
- [ ] T036 [P]: Test duplicate detection
- [ ] T037 [P]: Test CLI commands

### Phase 13.8: Polish
- [ ] T038: Run full test suite

---

## Validation Checklist

- [x] All contracts have corresponding tests (T010-T013)
- [x] All entities have model tasks (T004-T008)
- [x] All tests come before implementation
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Integration tests cover all quickstart scenarios

---

## Notes

- **[P] tasks**: Different files, no dependencies, can run in parallel
- **TDD approach**: Contract tests (T010-T013) MUST fail before implementation
- **Commit strategy**: Commit after each task or logical group
- **Exit codes**: Follow POSIX conventions (0=success, 1=error, 2=usage, 130=interrupted)
- **Cross-platform**: Test on macOS, Linux, Windows (via WSL)

---

**Status**: ✅ Tasks generated and ready for execution
**Next Step**: Execute `/implement` command or manually process tasks T001-T038
