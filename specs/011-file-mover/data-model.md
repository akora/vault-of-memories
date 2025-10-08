# Data Model: File Mover

**Feature**: 011-file-mover | **Date**: 2025-10-08
**Input**: Key entities from spec.md, technical decisions from research.md

## Overview

The File Mover data model defines the structures for tracking file move operations, managing duplicates, handling quarantine, and coordinating transactions between filesystem and database operations.

---

## Entity 1: MoveOperation

**Purpose**: Tracks a single file move operation from source to destination

**Attributes**:
```python
@dataclass
class MoveOperation:
    """Represents a file move operation with full tracking"""
    operation_id: str              # Unique operation identifier (UUID)
    source_path: Path              # Source file path
    destination_path: Path         # Intended destination path
    file_hash: str                 # SHA256 hash of source file
    file_size: int                 # File size in bytes
    status: OperationStatus        # Current operation status
    created_at: datetime           # When operation was created
    started_at: datetime | None    # When move started
    completed_at: datetime | None  # When move completed
    error_message: str | None      # Error details if failed
    rollback_attempted: bool       # Whether rollback was attempted
    rollback_success: bool | None  # Whether rollback succeeded
```

**Enumerations**:
```python
class OperationStatus(Enum):
    """Status of a move operation"""
    PENDING = "pending"           # Not yet started
    IN_PROGRESS = "in_progress"   # Currently executing
    VERIFYING = "verifying"       # Verifying integrity
    COMPLETED = "completed"       # Successfully completed
    FAILED = "failed"             # Failed with error
    ROLLED_BACK = "rolled_back"   # Rolled back after failure
    QUARANTINED = "quarantined"   # File moved to quarantine
```

**Validation Rules**:
- `operation_id` must be valid UUID
- `source_path` must exist at creation time
- `destination_path` must not be same as source_path
- `file_hash` must be valid SHA256 hex string (64 characters)
- `file_size` must be non-negative
- `completed_at` must be after `started_at` if both present

**Usage Context**:
- Created before each file move
- Updated as operation progresses
- Persisted to database for audit trail
- Used for rollback if operation fails

---

## Entity 2: MoveResult

**Purpose**: Result of a move operation, returned to caller

**Attributes**:
```python
@dataclass
class MoveResult:
    """Result of a file move operation"""
    success: bool                  # Whether operation succeeded
    operation: MoveOperation       # The operation that was executed
    actual_destination: Path | None # Actual destination (may differ if duplicate)
    is_duplicate: bool             # Whether file was identified as duplicate
    is_quarantined: bool           # Whether file was quarantined
    execution_time_ms: float       # Time taken for operation in milliseconds
    error: Exception | None        # Exception if failed
    warnings: list[str]            # Non-fatal warnings
```

**Derived Properties**:
```python
@property
def moved_to_vault(self) -> bool:
    """True if file successfully moved to intended vault location"""
    return self.success and not self.is_duplicate and not self.is_quarantined

@property
def needs_attention(self) -> bool:
    """True if operation requires user attention"""
    return self.is_quarantined or (not self.success) or len(self.warnings) > 0
```

**Validation Rules**:
- If `success=True`, must have `actual_destination`
- If `success=False`, must have `error`
- Cannot be both `is_duplicate` and `is_quarantined`
- `execution_time_ms` must be non-negative

**Usage Context**:
- Returned from move_file() and move_batch()
- Used for logging and reporting
- Aggregated for batch operation summaries

---

## Entity 3: DuplicateRecord

**Purpose**: Tracks duplicate files and their relationships

**Attributes**:
```python
@dataclass
class DuplicateRecord:
    """Record of a duplicate file"""
    duplicate_id: str              # Unique identifier for this duplicate
    original_file_id: str          # ID of original file in vault
    duplicate_path: Path           # Path where duplicate was stored
    original_path: Path            # Path of original file
    file_hash: str                 # Content hash (same for both)
    detected_at: datetime          # When duplicate was detected
    duplicate_size: int            # File size in bytes
    metadata_diff: dict            # Differences in metadata from original
    source_path: Path              # Where duplicate came from
```

**Relationships**:
- Links to original file via `original_file_id`
- One original can have many duplicates
- Duplicates stored in separate folder structure

**Validation Rules**:
- `file_hash` must match original file's hash
- `duplicate_path` must be in duplicates folder
- `original_path` must be in vault
- `duplicate_size` should match original (hash collision if not)

**Usage Context**:
- Created when duplicate detected during move
- Queried to find all duplicates of a file
- Used for deduplication reports

---

## Entity 4: QuarantineRecord

**Purpose**: Tracks files in quarantine with recovery information

**Attributes**:
```python
@dataclass
class QuarantineRecord:
    """Record of a quarantined file"""
    quarantine_id: str             # Unique identifier
    file_path: Path                # Current path in quarantine
    original_path: Path            # Original source path
    intended_destination: Path     # Where file was supposed to go
    error_type: QuarantineReason   # Reason for quarantine
    error_message: str             # Detailed error description
    error_traceback: str | None    # Full traceback if available
    quarantined_at: datetime       # When file was quarantined
    recovery_attempts: int         # Number of recovery attempts
    last_recovery_attempt: datetime | None  # Last recovery attempt time
    metadata_snapshot: dict        # File metadata at quarantine time
    file_hash: str | None          # Hash if calculable
    file_size: int                 # File size in bytes
    can_retry: bool                # Whether automated retry is possible
```

**Enumerations**:
```python
class QuarantineReason(Enum):
    """Reason a file was quarantined"""
    CHECKSUM_MISMATCH = "checksum_mismatch"    # Integrity verification failed
    PERMISSION_ERROR = "permission_error"       # Access/permission issues
    DISK_SPACE_ERROR = "disk_space_error"       # Out of disk space
    PATH_TOO_LONG = "path_too_long"            # Path exceeds OS limits
    INVALID_CHARACTERS = "invalid_characters"   # Invalid chars in path
    DESTINATION_EXISTS = "destination_exists"   # Destination already exists
    NETWORK_ERROR = "network_error"             # Network storage issue
    CORRUPTION_DETECTED = "corruption_detected" # File appears corrupted
    UNKNOWN_ERROR = "unknown_error"             # Unclassified error
```

**Validation Rules**:
- `file_path` must be in quarantine folder
- `error_type` must be valid QuarantineReason
- `recovery_attempts` must be non-negative
- `last_recovery_attempt` must be after `quarantined_at` if present

**Usage Context**:
- Created when file cannot be moved safely
- Used by recovery workflows
- Queried for quarantine reports and cleanup

---

## Entity 5: TransactionContext

**Purpose**: Coordinates file and database operations atomically

**Attributes**:
```python
@dataclass
class TransactionContext:
    """Context for atomic file + database operations"""
    transaction_id: str            # Unique transaction identifier
    db_manager: DatabaseManager    # Database manager instance
    operations: list[MoveOperation] # Operations in this transaction
    started_at: datetime           # Transaction start time
    committed: bool                # Whether transaction was committed
    rolled_back: bool              # Whether transaction was rolled back
    rollback_log: list[dict]       # Log of rollback operations
```

**Methods** (conceptual, for context):
```python
def begin(self) -> None:
    """Start database transaction"""

def commit(self) -> None:
    """Commit database transaction"""

def rollback(self) -> None:
    """Rollback database and reverse file operations"""

def record_operation(self, operation: MoveOperation) -> None:
    """Record operation for potential rollback"""
```

**Validation Rules**:
- Cannot commit if `rolled_back=True`
- Cannot rollback if `committed=True`
- Must call `begin()` before `commit()` or `rollback()`

**Usage Context**:
- Used as context manager for atomic operations
- Ensures consistency between filesystem and database
- Provides rollback capability on failures

---

## Entity 6: BatchMoveRequest

**Purpose**: Represents a batch move operation request

**Attributes**:
```python
@dataclass
class BatchMoveRequest:
    """Request to move multiple files as a batch"""
    batch_id: str                  # Unique batch identifier
    operations: list[MoveOperation] # Individual move operations
    validate_space: bool           # Whether to validate storage space
    parallel: bool                 # Whether to execute in parallel
    max_workers: int               # Max parallel workers (if parallel=True)
    stop_on_error: bool            # Whether to stop batch on first error
    created_at: datetime           # When batch was created
```

**Derived Properties**:
```python
@property
def total_size(self) -> int:
    """Total size of all files in batch"""
    return sum(op.file_size for op in self.operations)

@property
def operation_count(self) -> int:
    """Number of operations in batch"""
    return len(self.operations)
```

**Validation Rules**:
- `operations` must not be empty
- `max_workers` must be positive if `parallel=True`
- All operations must have unique `operation_id`

**Usage Context**:
- Created for batch move operations
- Used to configure batch execution behavior
- Passed to move_batch() method

---

## Entity 7: BatchMoveResult

**Purpose**: Result of a batch move operation

**Attributes**:
```python
@dataclass
class BatchMoveResult:
    """Result of a batch move operation"""
    batch_id: str                  # Batch identifier
    results: list[MoveResult]      # Individual operation results
    total_operations: int          # Total number of operations
    successful_count: int          # Number of successful moves
    duplicate_count: int           # Number of duplicates found
    quarantine_count: int          # Number of files quarantined
    failed_count: int              # Number of failed operations
    total_time_ms: float           # Total batch execution time
    average_time_ms: float         # Average time per operation
    warnings: list[str]            # Batch-level warnings
```

**Derived Properties**:
```python
@property
def success_rate(self) -> float:
    """Percentage of successful operations"""
    return (self.successful_count / self.total_operations) * 100 if self.total_operations > 0 else 0.0

@property
def all_succeeded(self) -> bool:
    """True if all operations succeeded"""
    return self.successful_count == self.total_operations

@property
def any_failed(self) -> bool:
    """True if any operations failed"""
    return self.failed_count > 0
```

**Validation Rules**:
- `total_operations` must equal `len(results)`
- Sum of counts must equal `total_operations`
- `average_time_ms` should be `total_time_ms / total_operations`

**Usage Context**:
- Returned from move_batch()
- Used for batch operation reports
- Logged for audit trail

---

## Entity 8: IntegrityCheckResult

**Purpose**: Result of file integrity verification

**Attributes**:
```python
@dataclass
class IntegrityCheckResult:
    """Result of file integrity check"""
    file_path: Path                # Path to file checked
    expected_hash: str             # Expected hash value
    actual_hash: str               # Actual hash value
    match: bool                    # Whether hashes match
    check_time_ms: float           # Time taken for check
    algorithm: str                 # Hash algorithm used (e.g., "sha256")
    file_size: int                 # File size in bytes
    checked_at: datetime           # When check was performed
```

**Derived Properties**:
```python
@property
def integrity_valid(self) -> bool:
    """True if integrity check passed"""
    return self.match

@property
def throughput_mbps(self) -> float:
    """Throughput in MB/s during check"""
    size_mb = self.file_size / (1024 * 1024)
    time_s = self.check_time_ms / 1000
    return size_mb / time_s if time_s > 0 else 0.0
```

**Validation Rules**:
- `expected_hash` and `actual_hash` must be valid hex strings
- Hash length must match algorithm (64 chars for SHA256)
- `match` must be True if `expected_hash == actual_hash`

**Usage Context**:
- Created after file move operations
- Used to verify data integrity
- Triggers quarantine if check fails

---

## Relationships

```
MoveOperation
    → MoveResult (1:1)
    → DuplicateRecord (0:1) if duplicate detected
    → QuarantineRecord (0:1) if quarantined
    → IntegrityCheckResult (1:1) verification result

BatchMoveRequest
    → MoveOperation (1:N) operations in batch
    → BatchMoveResult (1:1) result of batch

TransactionContext
    → MoveOperation (1:N) operations in transaction
    → DatabaseManager (1:1) for database coordination
```

---

## Database Schema Considerations

**Tables to create/update**:
- `move_operations`: Track all move operations
- `quarantine_records`: Track quarantined files
- `duplicate_records`: Track duplicate relationships
- `batch_operations`: Track batch operation metadata

**Indexes needed**:
- Index on `file_hash` for duplicate detection
- Index on `operation_id` for lookup
- Index on `quarantine_id` for recovery queries
- Index on `created_at` / `quarantined_at` for time-based queries

---

## Constitution Compliance

- ✅ **Simplicity First**: Simple dataclasses, no complex ORM
- ✅ **Dependency Minimalism**: Only standard library (dataclasses, datetime, pathlib, enum)
- ✅ **Test-Driven**: All entities easily testable with clear validation rules
- ✅ **Strategic Documentation**: Self-documenting with type hints and docstrings
- ✅ **Readability Priority**: Clear naming, single responsibility per entity

---

**Data Model Status**: ✅ Complete
**Next Phase**: Contracts (contracts/*.py) and Quickstart (quickstart.md)
