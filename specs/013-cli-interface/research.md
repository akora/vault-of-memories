# Research Findings: CLI Interface

**Feature**: #013 CLI Interface
**Date**: 2025-10-08
**Status**: Research Complete

---

## Overview

This document captures technical research decisions for building a command-line interface that orchestrates the vault processing pipeline. All decisions prioritize stdlib-only implementation, cross-platform compatibility, and integration with existing vault components.

---

## 1. CLI Framework Selection

### Decision: Python stdlib `argparse`

**Rationale**:
- Zero external dependencies (Constitution: Dependency Minimalism)
- Full-featured: subcommands, help generation, type validation
- Python 3.11 compatible and well-documented
- Supports all required CLI patterns (flags, arguments, subcommands)

**Alternatives Considered**:

**Click** (rejected):
- External dependency adds installation complexity
- Decorators hide argument structure
- Not justified for our simple CLI needs

**Typer** (rejected):
- External dependency with Click as transitive dependency
- Modern type hints are nice but argparse works fine
- Adds unnecessary complexity

**argparse Capabilities**:
```python
# Subcommands
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

# Type validation
parser.add_argument('--workers', type=int, default=1)

# Help generation
parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

# Required vs optional
parser.add_argument('source', help='Source directory (required)')
parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
```

---

## 2. Progress Reporting Strategy

### Decision: Event-driven progress updates with callback pattern

**Rationale**:
- Non-blocking: Processing continues while progress updates
- Flexible: Different formatters can subscribe to events
- Testable: Easy to mock progress callbacks
- Simple: No threading or async complexity

**Alternatives Considered**:

**Polling** (rejected):
- Requires periodic checking, adds overhead
- Not real-time, delays in progress updates
- Wastes CPU cycles checking state

**Threading** (rejected):
- Adds complexity and potential race conditions
- Overkill for progress reporting
- Harder to test and debug

**Implementation Approach**:
```python
class ProgressMonitor:
    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def update(self, current, total, message):
        for callback in self.callbacks:
            callback(current, total, message)

# Usage in pipeline
monitor = ProgressMonitor()
monitor.subscribe(lambda c, t, m: print(f"{c}/{t}: {m}"))

# FileIngestor calls monitor.update() during processing
```

**Update Frequency**: Every 100ms or every file (whichever is less frequent)

---

## 3. Pipeline Orchestration Pattern

### Decision: Sequential pipeline with dependency injection

**Rationale**:
- Clear execution flow: Ingest → Extract → Organize → Move
- Testable: Each stage can be mocked independently
- Aligns with existing architecture (no refactoring needed)
- Simple: No concurrency complexity

**Alternatives Considered**:

**Async/Parallel Pipeline** (rejected):
- Premature optimization (current performance is adequate)
- Adds complexity with async/await
- Harder to debug and test
- Not needed for MVP

**Message Queue Pattern** (rejected):
- Overkill for single-machine CLI
- Adds external dependencies (Redis, RabbitMQ)
- Doesn't fit use case (not distributed)

**Pipeline Stages**:
```
1. Validation
   ↓
2. File Ingestion (FileIngestor)
   ↓
3. Metadata Extraction (Video/Image/Document Processors)
   ↓
4. Metadata Consolidation (MetadataConsolidator)
   ↓
5. File Renaming (FilenameGenerator)
   ↓
6. Organization (OrganizationManager)
   ↓
7. File Moving (FileMover)
   ↓
8. Summary Generation
```

**Error Handling**: Each stage can fail independently; errors collected and reported at end

---

## 4. Signal Handling for Graceful Interruption

### Decision: Python `signal` module with cleanup handlers

**Rationale**:
- Standard Python approach (signal.signal)
- Cross-platform (SIGINT works on Windows/Unix)
- Allows graceful cleanup before exit
- Simple implementation

**Alternatives Considered**:

**Custom Interrupt Handling** (rejected):
- Reinvents wheel (signal module exists)
- Platform-specific differences hard to handle
- More error-prone

**No Handling** (rejected):
- Bad user experience (files left in inconsistent state)
- Violates digital preservation principle (data integrity)

**Implementation Approach**:
```python
import signal
import sys

class InterruptHandler:
    def __init__(self):
        self.interrupted = False

    def signal_handler(self, sig, frame):
        print("\nInterrupted. Cleaning up...")
        self.interrupted = True
        # Finish current file operation
        # Save state
        # Exit gracefully
        sys.exit(0)

    def register(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
```

**Cleanup Steps**:
1. Finish current file operation (don't leave partial moves)
2. Save progress state to resume later (optional)
3. Close database connections
4. Print summary of what was completed
5. Exit with status code 130 (SIGINT)

---

## 5. Output Formatting

### Decision: Plain text with ANSI colors (optional)

**Rationale**:
- Universal compatibility (works in all terminals)
- Simple implementation (no dependencies)
- ANSI colors improve readability (but optional for non-TTY)
- Easy to test (just strings)

**Alternatives Considered**:

**Rich Library** (rejected):
- External dependency (violates DM principle)
- Overkill for simple CLI output
- Not needed for our requirements

**JSON Only** (rejected):
- Not user-friendly for interactive use
- Good for automation but bad for humans
- Can add as `--json` flag later if needed

**HTML Output** (rejected):
- Not appropriate for CLI
- Adds complexity
- No user need identified

**ANSI Color Codes**:
```python
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    @classmethod
    def disable_if_not_tty(cls):
        import sys
        if not sys.stdout.isatty():
            cls.GREEN = cls.YELLOW = cls.RED = cls.RESET = ''

# Usage
print(f"{Colors.GREEN}✓{Colors.RESET} File processed successfully")
print(f"{Colors.RED}✗{Colors.RESET} File quarantined: {path}")
```

**Output Modes**:
- Default: Colored text with progress bar
- `--quiet`: Errors only
- `--verbose`: Detailed progress for each file
- Non-TTY: Automatically disables colors

---

## 6. Configuration Loading

### Decision: Prioritize CLI flags > Config file > Defaults

**Rationale**:
- Standard CLI behavior (most specific wins)
- Existing ConfigurationManager can be reused
- Allows both quick flags and persistent config

**Configuration Precedence**:
```
1. Command-line flags (highest priority)
   --vault-root /custom/vault

2. Config file (if specified with --config)
   vault_root: /default/vault

3. Built-in defaults (lowest priority)
   vault_root: ./vault
```

**Implementation**:
```python
def load_config(args):
    # Start with defaults
    config = get_default_config()

    # Override with config file if provided
    if args.config:
        file_config = ConfigurationManager.load(args.config)
        config.update(file_config)

    # Override with CLI flags (highest priority)
    if args.vault_root:
        config['vault_root'] = args.vault_root

    return config
```

---

## 7. Exit Codes

### Decision: Follow POSIX conventions

**Exit Code Map**:
```
0   - Success (all files processed)
1   - General error (unspecified)
2   - Misuse of shell command (invalid arguments)
64  - Command line usage error (argparse)
65  - Data format error (invalid file)
73  - Cannot create (permission denied)
74  - IO error (disk full, read/write failure)
75  - Temporary failure (retry might succeed)
130 - Interrupted by signal (Ctrl+C)
```

**Rationale**:
- Standard conventions improve automation
- Allows shell scripts to handle errors appropriately
- Clear distinction between error types

---

## 8. Logging Strategy

### Decision: Python stdlib `logging` with file + console handlers

**Rationale**:
- Existing vault components already use logging
- Console output for user, file for debugging
- Configurable verbosity levels
- No external dependencies

**Log Levels**:
- ERROR: Critical failures (quarantine, pipeline errors)
- WARNING: Non-critical issues (file skipped, fallback used)
- INFO: Progress updates (file processed, stage complete)
- DEBUG: Detailed diagnostics (metadata values, paths)

**Implementation**:
```python
import logging

def setup_logging(verbose=False, log_file=None):
    level = logging.DEBUG if verbose else logging.INFO

    # Console handler (formatted for users)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))

    # File handler (detailed for debugging)
    handlers = [console]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers)
```

---

## 9. Command Structure

### Decision: Subcommand-based CLI

**Commands**:
```bash
# Main processing command
vault process <source> [--vault-root PATH] [--dry-run] [--verbose]

# Status/recovery commands
vault status [--vault-root PATH]
vault recover [--vault-root PATH] [--quarantine-type TYPE]

# Utility commands
vault validate <source>  # Check files before processing
vault help [command]     # Detailed help
```

**Rationale**:
- Follows industry standards (git, docker pattern)
- Extensible (easy to add new commands)
- Self-documenting (each command has help)
- Clear separation of concerns

---

## 10. Dry-Run Implementation

### Decision: Preview mode that simulates all operations

**Rationale**:
- Critical for user confidence (preview before change)
- Reuses existing preview capabilities (FileMover.preview_move)
- Simple flag: `--dry-run`

**Implementation**:
- All write operations are skipped
- Database operations are read-only
- Full pipeline executes to detect errors
- Summary shows what *would* happen

---

## Performance Considerations

**Target Metrics** (from Technical Context):
- Process 100 files in <20 seconds (200ms per file)
- Progress updates every 100ms minimum
- Memory usage <500MB for typical batches

**Optimizations** (if needed later):
- Batch database commits (not per-file)
- Parallel metadata extraction (future)
- Lazy loading of processors

**Current Approach**: Measure first, optimize only if needed

---

## Cross-Platform Compatibility

**Tested Platforms**:
- macOS (primary development)
- Linux (Ubuntu/Debian)
- Windows 10+ (via WSL and native Python)

**Platform Considerations**:
- Use pathlib.Path for all file operations
- ANSI color detection (sys.stdout.isatty())
- Signal handling (SIGINT/SIGTERM on Unix, Ctrl+C on Windows)
- Exit codes (consistent across platforms)

---

## Integration with Existing Components

**Existing Services to Integrate**:
1. FileIngestor - File discovery and duplicate detection
2. VideoProcessor, ImageProcessor, DocumentProcessor - Metadata extraction
3. MetadataConsolidator - Metadata merging
4. FilenameGenerator - Filename generation
5. OrganizationManager - Destination path determination
6. FileMover - Atomic file operations
7. DatabaseManager - State persistence
8. QuarantineManager - Error handling

**Integration Pattern**:
- Dependency injection (pass services to orchestrator)
- All services already have clean interfaces
- No modifications needed to existing code
- CLI is a thin orchestration layer

---

## Summary of Decisions

| Decision | Choice | Justification |
|----------|--------|---------------|
| CLI Framework | argparse (stdlib) | Zero dependencies, full-featured |
| Progress Reporting | Callback pattern | Non-blocking, flexible, testable |
| Pipeline Pattern | Sequential with DI | Simple, testable, clear flow |
| Signal Handling | signal module | Standard, cross-platform |
| Output Format | Plain text + ANSI | Universal, simple, optional colors |
| Configuration | CLI > File > Defaults | Standard precedence |
| Exit Codes | POSIX conventions | Automation-friendly |
| Logging | stdlib logging | Existing usage, no dependencies |
| Command Structure | Subcommands | Industry standard, extensible |
| Dry-Run | Full simulation | User confidence, error detection |

**Constitution Compliance**: ✅ All decisions align with constitutional principles
- Simplicity First: stdlib-only, minimal complexity
- Dependency Minimalism: Zero external dependencies
- Industry Standards: POSIX CLI conventions, standard patterns
- Test-Driven: All components designed for testing
- Strategic Documentation: Self-documenting commands
- Readability Priority: Clear structure, explicit logic

---

**Status**: ✅ All research complete, no NEEDS CLARIFICATION remaining
**Next Step**: Execute Phase 1 (Design & Contracts)
