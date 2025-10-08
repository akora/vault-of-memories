# Implementation Tasks: Error Handler (012)

**Feature**: 012-error-handler
**Total Tasks**: 70
**Estimated Effort**: 3-4 days

---

## Phase 1: Error Severity (T001-T010)

### T001: Create ErrorSeverity enum
- [ ] Create `src/models/error_severity.py`
- [ ] Define ErrorSeverity enum: CRITICAL, ERROR, WARNING, INFO
- [ ] Add helper methods: `is_critical()`, `is_error()`, `requires_notification()`
- [ ] Add `__str__` and `__repr__` methods
- [ ] Export from `src/models/__init__.py`

### T002: Create severity classification contract
- [ ] Create `specs/012-error-handler/contracts/error_severity_classifier.py`
- [ ] Define `classify_error(error: Exception) -> ErrorSeverity` contract
- [ ] Document severity assignment rules
- [ ] Include edge cases (unknown errors, None, etc.)

### T003: Create contract tests for severity classification
- [ ] Create `tests/contract/test_error_severity.py`
- [ ] Test each error type maps to correct severity
- [ ] Test unknown errors default to ERROR
- [ ] Test None/missing error handling
- [ ] Test severity comparison operations

### T004: Update QuarantineRecord model with severity
- [ ] Add `severity: ErrorSeverity` field to QuarantineRecord
- [ ] Add `escalation_level: int` field (default: 0)
- [ ] Add `previous_attempts: list[datetime]` field (default: [])
- [ ] Update JSON serialization to include new fields
- [ ] Maintain backward compatibility

### T005: Update QuarantineManager to classify severity
- [ ] Add `classify_severity(error: Exception) -> ErrorSeverity` method
- [ ] Map QuarantineReason to ErrorSeverity
- [ ] Update `quarantine_file()` to set severity
- [ ] Update `_save_metadata_json()` to include severity
- [ ] Add severity parameter to constructor (optional override)

### T006: Update QuarantineManager contract tests
- [ ] Add tests for severity classification
- [ ] Verify severity saved in metadata JSON
- [ ] Test severity override functionality
- [ ] Test all QuarantineReason -> ErrorSeverity mappings

### T007: Add severity filtering to list_quarantined_files
- [ ] Add `severity: Optional[ErrorSeverity]` parameter
- [ ] Filter results by severity when specified
- [ ] Update return type documentation
- [ ] Add tests for severity filtering

### T008: Update CLI RecoverCommand with severity filter
- [ ] Add `--severity` option to recover command
- [ ] Support filtering by CRITICAL, ERROR, WARNING, INFO
- [ ] Update help text and examples
- [ ] Add integration test for severity filtering

### T009: Update CLI StatusCommand to show severity breakdown
- [ ] Group quarantined files by severity
- [ ] Display severity counts in status output
- [ ] Color-code severity levels (red/yellow/blue)
- [ ] Add integration test

### T010: Create severity classification reference doc
- [ ] Document ErrorSeverity enum values
- [ ] List default mappings (QuarantineReason -> ErrorSeverity)
- [ ] Explain severity override configuration
- [ ] Add examples of each severity level

---

## Phase 2: Error Statistics (T011-T020)

### T011: Create ErrorStatistics model
- [ ] Create `src/models/error_statistics.py`
- [ ] Define ErrorStatistics dataclass
- [ ] Fields: counts by severity, counts by type, time windows, success rates
- [ ] Add JSON serialization methods
- [ ] Export from models __init__

### T012: Create ErrorStatisticsCollector contract
- [ ] Create `specs/012-error-handler/contracts/error_statistics_collector.py`
- [ ] Define `record_error(error, severity, error_type)` contract
- [ ] Define `get_statistics(time_window) -> ErrorStatistics` contract
- [ ] Define `reset()` contract
- [ ] Document thread-safety requirements

### T013: Implement ErrorStatisticsCollector service
- [ ] Create `src/services/error_statistics_collector.py`
- [ ] Implement in-memory counters (thread-safe with Lock)
- [ ] Implement time-windowed aggregation (1h, 24h, 7d, 30d)
- [ ] Add file path correlation tracking
- [ ] Add error pattern tracking (most common errors)

### T014: Add persistent storage to ErrorStatisticsCollector
- [ ] Implement `save_to_file(path: Path)` method
- [ ] Implement `load_from_file(path: Path)` method
- [ ] Use JSON format with human-readable timestamps
- [ ] Handle missing/corrupt files gracefully
- [ ] Auto-save on collection interval

### T015: Create contract tests for ErrorStatisticsCollector
- [ ] Create `tests/contract/test_error_statistics_collector.py`
- [ ] Test error recording with different severities
- [ ] Test time window calculations
- [ ] Test statistics aggregation
- [ ] Test persistence (save/load)
- [ ] Test thread-safety with concurrent recording

### T016: Create ErrorTrendAnalyzer service
- [ ] Create `src/services/error_trend_analyzer.py`
- [ ] Implement `analyze_trends(stats: ErrorStatistics)` method
- [ ] Detect increasing/decreasing error rates
- [ ] Identify anomalies (sudden spikes)
- [ ] Generate trend summary text

### T017: Create contract tests for ErrorTrendAnalyzer
- [ ] Create `tests/contract/test_error_trend_analyzer.py`
- [ ] Test trend detection (increasing/decreasing/stable)
- [ ] Test anomaly detection
- [ ] Test edge cases (no data, insufficient data)

### T018: Integrate ErrorStatisticsCollector with PipelineOrchestrator
- [ ] Add ErrorStatisticsCollector to PipelineOrchestrator
- [ ] Record errors during pipeline execution
- [ ] Save statistics to file after pipeline completion
- [ ] Add statistics to ProcessingResult

### T019: Create CLI stats command
- [ ] Add `vault stats` command to arg_parser.py
- [ ] Create StatsCommand handler
- [ ] Display error statistics with formatting
- [ ] Support `--time-window` option (1h, 24h, 7d, 30d)
- [ ] Support `--format` option (text, json)
- [ ] Add integration tests

### T020: Update SummaryFormatter to show statistics
- [ ] Add `format_statistics(stats: ErrorStatistics)` method
- [ ] Show error rate trends
- [ ] Highlight anomalies
- [ ] Add to verbose output

---

## Phase 3: Error Notifications (T021-T030)

### T021: Create NotificationHandler interface
- [ ] Create `src/services/notification_handlers.py`
- [ ] Define NotificationHandler abstract base class
- [ ] Define `notify(severity, message, context)` method
- [ ] Define `is_enabled()` method
- [ ] Define `get_severity_threshold()` method

### T022: Implement ConsoleHandler
- [ ] Create ConsoleHandler class (inherits NotificationHandler)
- [ ] Color-code output by severity
- [ ] Support severity threshold filtering
- [ ] Add timestamp to messages
- [ ] Test with various severity levels

### T023: Implement FileHandler
- [ ] Create FileHandler class (inherits NotificationHandler)
- [ ] Write to log file (append mode)
- [ ] Support log rotation (max size, max files)
- [ ] Include full context in log entries
- [ ] Support configurable log path
- [ ] Test file creation, writing, rotation

### T024: Implement WebhookHandler (extensibility)
- [ ] Create WebhookHandler class (inherits NotificationHandler)
- [ ] Send HTTP POST with error details
- [ ] Support retry logic with exponential backoff
- [ ] Handle network errors gracefully
- [ ] Support configurable webhook URL
- [ ] Test with mock HTTP server

### T025: Create notification handler contracts
- [ ] Create `specs/012-error-handler/contracts/notification_handler.py`
- [ ] Define interface contract
- [ ] Document threading requirements
- [ ] Document error handling expectations

### T026: Create contract tests for notification handlers
- [ ] Create `tests/contract/test_notification_handlers.py`
- [ ] Test ConsoleHandler output and filtering
- [ ] Test FileHandler writing and rotation
- [ ] Test WebhookHandler HTTP calls
- [ ] Test severity threshold filtering
- [ ] Test handler enable/disable

### T027: Create ErrorNotificationManager service
- [ ] Create `src/services/error_notification_manager.py`
- [ ] Manage list of NotificationHandler instances
- [ ] Implement `notify(severity, message, context)` method
- [ ] Route to appropriate handlers based on severity
- [ ] Support async notification (threaded)
- [ ] Add batching for non-critical notifications

### T028: Create contract tests for ErrorNotificationManager
- [ ] Create `tests/contract/test_error_notification_manager.py`
- [ ] Test handler registration
- [ ] Test notification routing by severity
- [ ] Test async notification execution
- [ ] Test batching behavior
- [ ] Test error handling when handlers fail

### T029: Integrate ErrorNotificationManager with QuarantineManager
- [ ] Add ErrorNotificationManager to QuarantineManager constructor
- [ ] Call notify() when file quarantined
- [ ] Include file path, error type, severity in notification
- [ ] Add configuration for notification enable/disable
- [ ] Test integration with mock handlers

### T030: Add notification configuration
- [ ] Create `config/notification_settings.json`
- [ ] Define handler configuration schema
- [ ] Support per-handler severity thresholds
- [ ] Add configuration loading to ErrorNotificationManager
- [ ] Test configuration parsing and validation

---

## Phase 4: Circuit Breaker (T031-T040)

### T031: Create CircuitBreakerState enum
- [ ] Create `src/models/circuit_breaker_state.py`
- [ ] Define states: CLOSED, OPEN, HALF_OPEN
- [ ] Add transition validation methods
- [ ] Export from models __init__

### T032: Create CircuitBreaker contract
- [ ] Create `specs/012-error-handler/contracts/circuit_breaker.py`
- [ ] Define `record_success()` contract
- [ ] Define `record_failure(severity)` contract
- [ ] Define `get_state() -> CircuitBreakerState` contract
- [ ] Define `can_proceed() -> bool` contract
- [ ] Document state transition rules

### T033: Implement CircuitBreaker service
- [ ] Create `src/services/circuit_breaker.py`
- [ ] Implement state machine (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- [ ] Track error rate over sliding time window
- [ ] Track consecutive critical errors
- [ ] Implement exponential backoff for recovery
- [ ] Add configurable thresholds

### T034: Create contract tests for CircuitBreaker
- [ ] Create `tests/contract/test_circuit_breaker.py`
- [ ] Test state transitions
- [ ] Test error rate threshold triggering
- [ ] Test consecutive critical error threshold
- [ ] Test recovery logic (HALF_OPEN testing)
- [ ] Test can_proceed() behavior in each state

### T035: Integrate CircuitBreaker with PipelineOrchestrator
- [ ] Add CircuitBreaker to PipelineOrchestrator constructor
- [ ] Check `can_proceed()` before processing each file
- [ ] Record success/failure after each file
- [ ] Halt pipeline when circuit OPEN
- [ ] Attempt recovery when appropriate
- [ ] Log state transitions

### T036: Add circuit breaker state to ProgressState
- [ ] Add `circuit_breaker_state: Optional[CircuitBreakerState]` field
- [ ] Update ProgressMonitor to include circuit state
- [ ] Add circuit state to progress updates

### T037: Update CLI to display circuit breaker state
- [ ] Show circuit state in progress formatter
- [ ] Color-code state (green/yellow/red)
- [ ] Show when pipeline halts due to circuit breaker
- [ ] Add to summary output

### T038: Add circuit breaker configuration
- [ ] Add circuit_breaker section to config
- [ ] Support enabling/disabling
- [ ] Configurable thresholds (error rate, consecutive failures)
- [ ] Configurable time window
- [ ] Configurable recovery settings

### T039: Create integration tests for circuit breaker
- [ ] Create `tests/integration/test_circuit_breaker.py`
- [ ] Test pipeline halts when error rate exceeds threshold
- [ ] Test recovery behavior
- [ ] Test state visibility in CLI output
- [ ] Test configuration loading

### T040: Update documentation for circuit breaker
- [ ] Document circuit breaker behavior
- [ ] Explain state transitions
- [ ] Document configuration options
- [ ] Add troubleshooting guide

---

## Phase 5: Error Escalation (T041-T050)

### T041: Create ErrorEscalationRecord model
- [ ] Create `src/models/error_escalation_record.py`
- [ ] Fields: file_hash, attempt_count, timestamps, severities, last_error
- [ ] Add JSON serialization
- [ ] Export from models __init__

### T042: Create ErrorEscalationManager contract
- [ ] Create `specs/012-error-handler/contracts/error_escalation_manager.py`
- [ ] Define `record_failure(file_hash, severity, error)` contract
- [ ] Define `get_escalation_level(file_hash) -> int` contract
- [ ] Define `should_escalate(file_hash) -> bool` contract
- [ ] Document escalation rules

### T043: Implement ErrorEscalationManager service
- [ ] Create `src/services/error_escalation_manager.py`
- [ ] Track failure history by file hash
- [ ] Implement escalation logic (1st -> 2nd -> 3rd+ failure)
- [ ] Escalate severity on repeated failures
- [ ] Persist escalation data to JSON
- [ ] Support configurable escalation thresholds

### T044: Create contract tests for ErrorEscalationManager
- [ ] Create `tests/contract/test_error_escalation_manager.py`
- [ ] Test first failure (no escalation)
- [ ] Test second failure (escalate to ERROR)
- [ ] Test third+ failure (escalate to CRITICAL)
- [ ] Test severity escalation logic
- [ ] Test persistence (save/load)

### T045: Integrate ErrorEscalationManager with QuarantineManager
- [ ] Add ErrorEscalationManager to QuarantineManager constructor
- [ ] Check escalation level before quarantining
- [ ] Escalate severity if needed
- [ ] Update QuarantineRecord with escalation_level
- [ ] Record attempt in previous_attempts list

### T046: Add escalation info to error reports
- [ ] Show escalation level in error report
- [ ] Highlight escalated files
- [ ] Show attempt history
- [ ] Add recommendations for escalated files

### T047: Create CLI command to view escalated files
- [ ] Add `vault recover --escalated` option
- [ ] List files with escalation_level > 0
- [ ] Show attempt count and history
- [ ] Support filtering by escalation level

### T048: Add escalation configuration
- [ ] Add escalation section to config
- [ ] Configurable attempt thresholds
- [ ] Configurable severity escalation rules
- [ ] Support enabling/disabling

### T049: Create integration tests for escalation
- [ ] Create `tests/integration/test_error_escalation.py`
- [ ] Test repeated failures escalate severity
- [ ] Test escalation info in CLI output
- [ ] Test recovery of escalated files

### T050: Update documentation for escalation
- [ ] Document escalation behavior
- [ ] Explain escalation levels
- [ ] Document configuration
- [ ] Add troubleshooting guide

---

## Phase 6: Enhanced Reporting (T051-T060)

### T051: Enhance format_error_report with severity grouping
- [ ] Update SummaryFormatter.format_error_report()
- [ ] Group errors by severity (CRITICAL, ERROR, WARNING, INFO)
- [ ] Show count for each severity level
- [ ] Color-code severity groups
- [ ] Sort by severity (CRITICAL first)

### T052: Add error type breakdown to reports
- [ ] Show counts by QuarantineReason within each severity
- [ ] Display most common error types
- [ ] Show file type correlation (images vs documents vs videos)

### T053: Add trend analysis to reports
- [ ] Integrate ErrorTrendAnalyzer with SummaryFormatter
- [ ] Show error rate trends
- [ ] Highlight anomalies in error patterns
- [ ] Compare current session to historical data

### T054: Add actionable recommendations to reports
- [ ] Create recommendation engine
- [ ] Suggest fixes for common errors (disk space, permissions, etc.)
- [ ] Link to documentation for complex errors
- [ ] Prioritize by severity and impact

### T055: Add recovery success rate to reports
- [ ] Track recovery attempts and outcomes
- [ ] Show success rate by error type
- [ ] Highlight files that may never succeed
- [ ] Suggest manual intervention when needed

### T056: Create enhanced report contract tests
- [ ] Create `tests/contract/test_enhanced_error_reporting.py`
- [ ] Test severity grouping
- [ ] Test type breakdown
- [ ] Test trend display
- [ ] Test recommendations

### T057: Add report export functionality
- [ ] Support exporting reports to JSON
- [ ] Support exporting to CSV
- [ ] Add `--export` option to CLI commands
- [ ] Test export formats

### T058: Create example reports documentation
- [ ] Document report structure
- [ ] Show example outputs for various scenarios
- [ ] Explain how to interpret reports
- [ ] Add troubleshooting guide

### T059: Create integration tests for enhanced reporting
- [ ] Create `tests/integration/test_enhanced_reporting.py`
- [ ] Test full report generation with real errors
- [ ] Test grouping and sorting
- [ ] Test trend analysis integration
- [ ] Test recommendations

### T060: Performance test report generation
- [ ] Test with 1000+ errors
- [ ] Test with complex error patterns
- [ ] Ensure < 100ms generation time
- [ ] Optimize if needed

---

## Phase 7: Integration & Testing (T061-T070)

### T061: Create end-to-end error flow integration test
- [ ] Create `tests/integration/test_error_handler_e2e.py`
- [ ] Test complete flow: error -> quarantine -> classify -> notify -> stats
- [ ] Test severity classification
- [ ] Test notifications triggered
- [ ] Test statistics recorded

### T062: Test circuit breaker integration
- [ ] Trigger circuit breaker with high error rate
- [ ] Verify pipeline halts
- [ ] Verify recovery behavior
- [ ] Test notification on circuit open

### T063: Test escalation integration
- [ ] Quarantine same file multiple times
- [ ] Verify escalation occurs
- [ ] Verify severity increases
- [ ] Verify escalation notifications

### T064: Test notification system under load
- [ ] Generate 100+ errors rapidly
- [ ] Verify all notifications sent
- [ ] Verify batching works
- [ ] Measure notification latency

### T065: Test statistics persistence
- [ ] Run pipeline, generate errors
- [ ] Verify statistics saved to file
- [ ] Load statistics in new session
- [ ] Verify data integrity

### T066: Run full test suite
- [ ] Run all contract tests (pytest tests/contract/)
- [ ] Run all integration tests (pytest tests/integration/)
- [ ] Ensure 95%+ pass rate
- [ ] Fix any failures

### T067: Performance benchmarking
- [ ] Benchmark error handling overhead
- [ ] Benchmark notification latency
- [ ] Benchmark statistics collection
- [ ] Ensure < 5% impact on pipeline throughput

### T068: Update CLAUDE.md
- [ ] Add error handler overview
- [ ] Document severity levels
- [ ] Document notification configuration
- [ ] Document circuit breaker usage
- [ ] Document escalation behavior

### T069: Create error handler user guide
- [ ] Create docs/error-handler-guide.md
- [ ] Explain all components
- [ ] Show configuration examples
- [ ] Add troubleshooting section
- [ ] Include CLI command reference

### T070: Final validation and PR
- [ ] Run full test suite one final time
- [ ] Verify all 70 tasks completed
- [ ] Create comprehensive commit
- [ ] Push branch to origin
- [ ] Create pull request with detailed description
- [ ] Request review

---

## Task Dependencies

**Prerequisites**:
- Feature 011 (File Mover) completed
- Feature 013 (CLI Interface) completed

**Critical Path**:
1. Phase 1 (Severity) must complete before Phase 3 (Notifications) and Phase 4 (Circuit Breaker)
2. Phase 2 (Statistics) must complete before Phase 6 (Enhanced Reporting)
3. Phase 5 (Escalation) depends on Phase 1 (Severity)
4. Phase 6 (Enhanced Reporting) depends on Phases 1, 2, 5
5. Phase 7 (Integration) depends on all previous phases

**Parallelizable**:
- Phase 2 (Statistics) can run parallel with Phase 1 (Severity)
- Phase 4 (Circuit Breaker) can start after Phase 1, parallel with Phases 2-3

## Estimates

- **Phase 1**: 4-5 hours
- **Phase 2**: 6-7 hours
- **Phase 3**: 5-6 hours
- **Phase 4**: 4-5 hours
- **Phase 5**: 4-5 hours
- **Phase 6**: 5-6 hours
- **Phase 7**: 3-4 hours

**Total**: 31-38 hours (3.9-4.8 days)
