# Data Model: CLI Interface

**Feature**: #013 CLI Interface
**Date**: 2025-10-08
**Status**: Design Complete

---

## Overview

This document defines the data models for the CLI Interface feature. All models follow Python dataclass patterns and integrate with existing vault architecture.

---

## Entities

### 1. ProcessingContext

**Purpose**: Configuration and state container for pipeline execution

**Fields**:
```python
@dataclass
class ProcessingContext:
    """
    Configuration and state for processing pipeline execution.

    Attributes:
        source_path: Path to source files or directory
        vault_root: Path to vault root directory
        config: Configuration settings from ConfigurationManager
        dry_run: If True, simulate operations without making changes
        verbose: Enable detailed logging
        max_workers: Number of parallel workers (future use)
        batch_size: Number of files to process per batch
        created_at: Timestamp when context was created
    """
    source_path: Path
    vault_root: Path
    config: dict
    dry_run: bool = False
    verbose: bool = False
    max_workers: int = 1
    batch_size: int = 100
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
```

**Validation Rules**:
- `source_path` must exist and be readable
- `vault_root` must exist or be creatable
- `max_workers` must be >= 1
- `batch_size` must be > 0

**Relationships**:
- Contains configuration from ConfigurationManager
- Used by PipelineOrchestrator
- Referenced in ProcessingResult

---

### 2. ProgressState

**Purpose**: Real-time tracking of processing progress

**Fields**:
```python
@dataclass
class ProgressState:
    """
    Real-time state of processing progress.

    Attributes:
        total_files: Total number of files to process
        processed_files: Number of files processed so far
        current_file: Path to file currently being processed
        current_stage: Name of current pipeline stage
        successful_count: Number of successfully processed files
        duplicate_count: Number of duplicate files detected
        quarantine_count: Number of files quarantined
        failed_count: Number of files that failed processing
        started_at: Timestamp when processing started
        last_update: Timestamp of last progress update
        estimated_completion: Estimated completion time (calculated)
    """
    total_files: int
    processed_files: int = 0
    current_file: Optional[Path] = None
    current_stage: str = "initializing"
    successful_count: int = 0
    duplicate_count: int = 0
    quarantine_count: int = 0
    failed_count: int = 0
    started_at: datetime = None
    last_update: datetime = None
    estimated_completion: Optional[datetime] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        self.last_update = datetime.now()

    @property
    def percent_complete(self) -> float:
        """Calculate completion percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time since start."""
        return datetime.now() - self.started_at

    @property
    def avg_time_per_file(self) -> float:
        """Calculate average processing time per file in seconds."""
        if self.processed_files == 0:
            return 0.0
        return self.elapsed_time.total_seconds() / self.processed_files

    def update_estimates(self):
        """Update estimated completion time based on current progress."""
        if self.processed_files > 0:
            remaining_files = self.total_files - self.processed_files
            estimated_seconds = remaining_files * self.avg_time_per_file
            self.estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
```

**Validation Rules**:
- `total_files` must be >= 0
- `processed_files` must be <= `total_files`
- All counts must be >= 0
- Sum of counts should equal `processed_files`

**State Transitions**:
```
initializing → discovering → processing → summarizing → complete
```

**Relationships**:
- Updated by PipelineOrchestrator
- Read by ProgressMonitor
- Included in ProcessingResult

---

### 3. ProcessingResult

**Purpose**: Summary of completed pipeline execution

**Fields**:
```python
@dataclass
class ProcessingResult:
    """
    Summary of completed processing pipeline execution.

    Attributes:
        context: Original ProcessingContext
        final_state: Final ProgressState
        success: Whether processing completed successfully
        total_duration: Total processing time
        files_processed: Total files processed
        successful_files: List of successfully processed file paths
        duplicate_files: List of duplicate file paths
        quarantined_files: List of quarantined file paths
        failed_files: List of failed file paths with errors
        warnings: List of warning messages
        completed_at: Timestamp when processing completed
    """
    context: ProcessingContext
    final_state: ProgressState
    success: bool
    total_duration: timedelta
    files_processed: int
    successful_files: list[Path]
    duplicate_files: list[Path]
    quarantined_files: list[Path]
    failed_files: list[tuple[Path, str]]  # (path, error_message)
    warnings: list[str]
    completed_at: datetime = None

    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()

    @property
    def success_rate(self) -> float:
        """Calculate percentage of successfully processed files."""
        if self.files_processed == 0:
            return 0.0
        return (len(self.successful_files) / self.files_processed) * 100

    @property
    def had_errors(self) -> bool:
        """Check if any errors occurred during processing."""
        return len(self.failed_files) > 0 or len(self.quarantined_files) > 0

    @property
    def summary_stats(self) -> dict:
        """Generate summary statistics dictionary."""
        return {
            'total_files': self.files_processed,
            'successful': len(self.successful_files),
            'duplicates': len(self.duplicate_files),
            'quarantined': len(self.quarantined_files),
            'failed': len(self.failed_files),
            'success_rate': f"{self.success_rate:.1f}%",
            'duration': str(self.total_duration),
            'avg_time_per_file': f"{self.total_duration.total_seconds() / max(self.files_processed, 1):.2f}s"
        }
```

**Validation Rules**:
- `files_processed` must equal sum of all file lists
- `total_duration` must be > 0
- Lists must not contain duplicates

**Relationships**:
- Contains ProcessingContext and ProgressState
- Generated by PipelineOrchestrator
- Used by SummaryFormatter

---

### 4. CommandOptions

**Purpose**: Parsed CLI arguments and configuration flags

**Fields**:
```python
@dataclass
class CommandOptions:
    """
    Parsed command-line arguments and options.

    Attributes:
        command: Subcommand name (process, status, recover)
        source: Source path (for process command)
        vault_root: Vault root directory path
        config_file: Path to configuration file
        dry_run: Preview mode flag
        verbose: Verbose output flag
        quiet: Suppress non-error output
        log_file: Path to log file
        workers: Number of parallel workers
        batch_size: Files per batch
        force: Force operation (skip confirmations)
        quarantine_type: Quarantine category for recovery
    """
    command: str
    source: Optional[Path] = None
    vault_root: Path = None
    config_file: Optional[Path] = None
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    log_file: Optional[Path] = None
    workers: int = 1
    batch_size: int = 100
    force: bool = False
    quarantine_type: Optional[str] = None

    def __post_init__(self):
        # Set default vault_root if not provided
        if self.vault_root is None:
            self.vault_root = Path.cwd() / 'vault'

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'CommandOptions':
        """Create CommandOptions from argparse.Namespace."""
        return cls(
            command=args.command,
            source=Path(args.source) if hasattr(args, 'source') and args.source else None,
            vault_root=Path(args.vault_root) if args.vault_root else None,
            config_file=Path(args.config) if args.config else None,
            dry_run=getattr(args, 'dry_run', False),
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False),
            log_file=Path(args.log_file) if getattr(args, 'log_file', None) else None,
            workers=getattr(args, 'workers', 1),
            batch_size=getattr(args, 'batch_size', 100),
            force=getattr(args, 'force', False),
            quarantine_type=getattr(args, 'quarantine_type', None)
        )
```

**Validation Rules**:
- `command` must be one of: process, status, recover, help, validate
- `source` must exist for process command
- `workers` must be >= 1
- `batch_size` must be > 0
- `verbose` and `quiet` are mutually exclusive

**Relationships**:
- Created from argparse.Namespace
- Used to create ProcessingContext
- Validated before pipeline execution

---

### 5. PipelineStage (Enum)

**Purpose**: Define processing pipeline stages

```python
from enum import Enum

class PipelineStage(Enum):
    """Processing pipeline stages."""
    INITIALIZING = "initializing"
    DISCOVERING = "discovering"
    INGESTING = "ingesting"
    EXTRACTING = "extracting"
    CONSOLIDATING = "consolidating"
    RENAMING = "renaming"
    ORGANIZING = "organizing"
    MOVING = "moving"
    SUMMARIZING = "summarizing"
    COMPLETE = "complete"
    FAILED = "failed"

    def __str__(self):
        return self.value
```

**Stage Flow**:
```
INITIALIZING → DISCOVERING → INGESTING → EXTRACTING → CONSOLIDATING →
RENAMING → ORGANIZING → MOVING → SUMMARIZING → COMPLETE
                                    ↓
                                 FAILED (on error)
```

---

## Validation

### Cross-Entity Validation

1. **ProcessingContext + CommandOptions**:
   - vault_root must be consistent
   - dry_run flag must match
   - Configuration must be compatible

2. **ProgressState + ProcessingResult**:
   - Final state counts must match result file lists
   - Timestamps must be consistent
   - Duration calculations must align

3. **CommandOptions Validation**:
   - Source path validation depends on command
   - Mutually exclusive flags checked
   - Required arguments per command

---

## Serialization

All models support serialization for logging and state persistence:

```python
# To dict (for JSON serialization)
result.to_dict()

# From dict (for state restoration)
ProcessingContext.from_dict(data)

# String representation (for logging)
str(progress_state)
```

---

## Usage Examples

### Create Processing Context
```python
from src.models import ProcessingContext, CommandOptions

# From command-line options
options = CommandOptions.from_args(args)
config = ConfigurationManager.load(options.config_file)

context = ProcessingContext(
    source_path=options.source,
    vault_root=options.vault_root,
    config=config,
    dry_run=options.dry_run,
    verbose=options.verbose
)
```

### Track Progress
```python
from src.models import ProgressState

# Initialize progress
progress = ProgressState(total_files=100)

# Update during processing
progress.processed_files += 1
progress.current_file = Path("/source/photo.jpg")
progress.current_stage = "extracting"
progress.successful_count += 1
progress.update_estimates()

# Check progress
print(f"Progress: {progress.percent_complete:.1f}%")
print(f"ETA: {progress.estimated_completion}")
```

### Generate Result
```python
from src.models import ProcessingResult

# After pipeline completion
result = ProcessingResult(
    context=context,
    final_state=progress,
    success=True,
    total_duration=timedelta(seconds=45.2),
    files_processed=100,
    successful_files=successful_paths,
    duplicate_files=duplicate_paths,
    quarantined_files=quarantined_paths,
    failed_files=failed_with_errors,
    warnings=warnings_list
)

# Get summary
print(result.summary_stats)
print(f"Success rate: {result.success_rate:.1f}%")
```

---

## Entity Relationship Diagram

```
CommandOptions
    ↓ (creates)
ProcessingContext
    ↓ (used by)
PipelineOrchestrator
    ↓ (updates)
ProgressState
    ↓ (included in)
ProcessingResult
    ↓ (formatted by)
SummaryFormatter
```

---

## Testing Strategy

### Model Validation Tests
- Test all validation rules
- Test property calculations (percent_complete, success_rate)
- Test state transitions

### Serialization Tests
- Test to_dict() / from_dict() round-trip
- Test JSON serialization
- Test str() representations

### Integration Tests
- Test model interactions in pipeline
- Test state updates during processing
- Test result generation

---

**Status**: ✅ Data model complete
**Entities**: 5 (ProcessingContext, ProgressState, ProcessingResult, CommandOptions, PipelineStage)
**Next Step**: Create service contracts
