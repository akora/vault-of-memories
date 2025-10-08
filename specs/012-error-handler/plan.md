# Implementation Plan: Error Handler

**Feature**: 012-error-handler
**Status**: Planning
**Based on**: specs/012-error-handler/spec.md

## Overview

Complete the error handler implementation by adding missing components: error severity levels, notification system, statistics/trends, enhanced reporting, circuit breaker, and error escalation. This builds on the existing QuarantineManager from Feature 011.

## Current State (Feature 011 Implementation)

**Already Implemented (58%)**:
- ✅ QuarantineManager with 9 error categories
- ✅ QuarantineRecord model with context logging
- ✅ Basic error reporting in SummaryFormatter
- ✅ Recovery command in CLI
- ✅ File integrity preservation

**Gaps to Address (42%)**:
- ❌ Error severity levels (FR-007)
- ❌ Error notification system (FR-009)
- ❌ Error statistics & trends (FR-010)
- ❌ Error escalation (FR-011)
- ⚠️ Enhanced error reporting (FR-005)
- ⚠️ Circuit breaker pattern (FR-008)

## Design Decisions

### 1. Error Severity Model
```
ErrorSeverity enum:
- CRITICAL: System-level failures requiring immediate attention
- ERROR: Processing failures that prevent file handling
- WARNING: Issues that may degrade quality but allow processing
- INFO: Informational notices about edge cases
```

**Mapping Strategy**:
- CRITICAL: Permission errors, disk space errors, system failures
- ERROR: Corruption, checksum mismatches, invalid file operations
- WARNING: Path too long, invalid characters (recoverable)
- INFO: Destination exists (duplicate), network errors (retryable)

### 2. Error Notification Architecture
```
ErrorNotificationManager
├── NotificationHandler (interface)
│   ├── ConsoleHandler
│   ├── FileHandler
│   └── WebhookHandler (extensible)
└── Configuration-driven threshold filtering
```

**Notification Triggers**:
- CRITICAL: Immediate notification
- ERROR: Batch notification (configurable interval)
- WARNING: Summary only
- INFO: No notification by default

### 3. Error Statistics Design
```
ErrorStatisticsCollector
├── In-memory counters (per session)
├── Persistent storage (JSON file)
└── Time-windowed aggregation (hourly/daily/weekly)
```

**Metrics Tracked**:
- Error counts by type, severity, time window
- Success/failure rates
- Recovery attempt success rates
- Most common error patterns
- File type correlation

### 4. Circuit Breaker Pattern
```
CircuitBreaker
├── States: CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
├── Thresholds: error rate, consecutive failures, time window
└── Integration: PipelineOrchestrator
```

**Thresholds** (configurable):
- Error rate > 50% over 10 files → OPEN
- 5 consecutive CRITICAL errors → OPEN
- Recovery: exponential backoff, test with single file

### 5. Error Escalation Logic
```
ErrorEscalationManager
├── Track failure history per file (by hash)
├── Escalation levels:
│   ├── Level 0: First failure → normal quarantine
│   ├── Level 1: 2nd failure → escalate to ERROR
│   ├── Level 2: 3rd+ failure → escalate to CRITICAL + notify
└── Integration: QuarantineManager
```

## Component Architecture

### New Components

1. **ErrorSeverity** (model)
   - Enum: CRITICAL, ERROR, WARNING, INFO
   - Location: `src/models/error_severity.py`

2. **ErrorNotificationManager** (service)
   - Sends notifications based on severity
   - Pluggable handlers (console, file, webhook)
   - Location: `src/services/error_notification_manager.py`

3. **NotificationHandler** (interface + implementations)
   - Base interface for notification handlers
   - ConsoleHandler, FileHandler, WebhookHandler
   - Location: `src/services/notification_handlers.py`

4. **ErrorStatisticsCollector** (service)
   - Collects and aggregates error metrics
   - Persistent storage with JSON
   - Time-windowed analysis
   - Location: `src/services/error_statistics_collector.py`

5. **ErrorTrendAnalyzer** (service)
   - Analyzes error trends over time
   - Identifies patterns and anomalies
   - Location: `src/services/error_trend_analyzer.py`

6. **CircuitBreaker** (service)
   - Implements circuit breaker pattern
   - Integrates with PipelineOrchestrator
   - Location: `src/services/circuit_breaker.py`

7. **ErrorEscalationManager** (service)
   - Tracks repeated failures
   - Escalates based on attempt count
   - Location: `src/services/error_escalation_manager.py`

### Enhanced Components

1. **QuarantineRecord** (model)
   - Add `severity: ErrorSeverity` field
   - Add `escalation_level: int` field
   - Add `previous_attempts: List[datetime]` field

2. **QuarantineManager** (service)
   - Integrate ErrorEscalationManager
   - Classify severity for each error
   - Trigger notifications

3. **SummaryFormatter** (CLI formatter)
   - Group errors by severity and type
   - Show error statistics
   - Add actionable recommendations

4. **PipelineOrchestrator** (service)
   - Integrate CircuitBreaker
   - Report error statistics
   - Handle circuit breaker state changes

## Implementation Phases

### Phase 1: Error Severity (T001-T010)
- Create ErrorSeverity enum
- Update QuarantineRecord model
- Update QuarantineManager to classify severity
- Add severity-based filtering to CLI
- Contract tests for severity classification

### Phase 2: Error Statistics (T011-T020)
- Create ErrorStatisticsCollector
- Create ErrorTrendAnalyzer
- Add persistent statistics storage
- Integrate with PipelineOrchestrator
- Create CLI command for statistics
- Contract tests for statistics

### Phase 3: Error Notifications (T021-T030)
- Create NotificationHandler interface
- Implement ConsoleHandler, FileHandler
- Create ErrorNotificationManager
- Add configuration for notifications
- Integrate with QuarantineManager
- Contract tests for notifications

### Phase 4: Circuit Breaker (T031-T040)
- Create CircuitBreaker service
- Define error thresholds
- Integrate with PipelineOrchestrator
- Add configuration for thresholds
- Add circuit state to progress updates
- Contract tests for circuit breaker

### Phase 5: Error Escalation (T041-T050)
- Create ErrorEscalationManager
- Track failure history per file
- Implement escalation logic
- Integrate with QuarantineManager
- Add escalation info to error reports
- Contract tests for escalation

### Phase 6: Enhanced Reporting (T051-T060)
- Enhance SummaryFormatter with grouping
- Add trend analysis to reports
- Add actionable recommendations
- Add recovery success rate display
- Contract tests for enhanced reporting

### Phase 7: Integration & Testing (T061-T070)
- Integration tests for full error flow
- Integration tests for notifications
- Integration tests for circuit breaker
- Performance testing
- Documentation updates
- Final validation

## Configuration Schema

```json
{
  "error_handling": {
    "severity_classification": {
      "permission_errors": "CRITICAL",
      "disk_space_errors": "CRITICAL",
      "corruption_errors": "ERROR",
      "checksum_errors": "ERROR",
      "path_too_long": "WARNING",
      "invalid_characters": "WARNING",
      "destination_exists": "INFO",
      "network_errors": "INFO"
    },
    "notifications": {
      "enabled": true,
      "handlers": ["console", "file"],
      "console": {
        "severity_threshold": "ERROR"
      },
      "file": {
        "severity_threshold": "WARNING",
        "log_path": "vault/logs/errors.log"
      },
      "webhook": {
        "enabled": false,
        "url": "https://example.com/webhook",
        "severity_threshold": "CRITICAL"
      }
    },
    "circuit_breaker": {
      "enabled": true,
      "error_rate_threshold": 0.5,
      "consecutive_critical_threshold": 5,
      "time_window_seconds": 60,
      "recovery_test_count": 1,
      "backoff_multiplier": 2.0
    },
    "escalation": {
      "enabled": true,
      "max_attempts": 3,
      "escalate_to_critical_after": 3,
      "escalate_to_error_after": 2
    },
    "statistics": {
      "enabled": true,
      "storage_path": "vault/stats/error_stats.json",
      "time_windows": ["1h", "24h", "7d", "30d"]
    }
  }
}
```

## Success Criteria

1. **Error Severity**: All quarantined files have severity classification
2. **Notifications**: Critical errors trigger immediate console/file notifications
3. **Statistics**: Error metrics tracked and displayable via CLI
4. **Circuit Breaker**: Pipeline halts when error rate exceeds threshold
5. **Escalation**: Repeated failures tracked and escalated appropriately
6. **Enhanced Reports**: Error reports group by severity and show trends
7. **Tests**: 95%+ test coverage for all new components
8. **Integration**: All components work seamlessly with existing pipeline

## Dependencies

- Feature 011 (File Mover) - QuarantineManager base
- Feature 013 (CLI Interface) - Command integration
- Configuration system - Settings storage

## Risks & Mitigations

**Risk**: Notification system performance impact
**Mitigation**: Async notification handling, batching for non-critical

**Risk**: Statistics storage growth over time
**Mitigation**: Configurable retention, automatic cleanup of old data

**Risk**: Circuit breaker too aggressive
**Mitigation**: Configurable thresholds, clear state visibility

**Risk**: Breaking changes to QuarantineRecord model
**Mitigation**: Database migration strategy, backward compatibility

## Testing Strategy

### Contract Tests
- ErrorSeverity classification logic
- NotificationHandler interface compliance
- ErrorStatisticsCollector metrics accuracy
- CircuitBreaker state transitions
- ErrorEscalationManager escalation logic

### Integration Tests
- End-to-end error flow with notifications
- Statistics collection during pipeline execution
- Circuit breaker triggering and recovery
- Escalation across multiple processing attempts

### Performance Tests
- Notification latency under load
- Statistics collection overhead
- Circuit breaker decision time

## Documentation Requirements

1. Update CLAUDE.md with error handling guidelines
2. Add notification handler extension guide
3. Document configuration options
4. Add troubleshooting guide for common errors
5. Create error severity classification reference
