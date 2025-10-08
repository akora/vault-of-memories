# File Mover - Feature 011

## Overview

The File Mover feature handles final file operations including moving files to vault locations, creating destination directories, handling duplicates and quarantine files, updating database records, and ensuring atomic operations to prevent data loss.

## Architecture

### Core Components

#### 1. **FileMover** (Orchestration)
Main service that coordinates all file move operations.

```python
from src.services import FileMover
from pathlib import Path

# Initialize
file_mover = FileMover(
    database_manager=db_manager,
    duplicate_handler=dup_handler,
    quarantine_manager=quar_manager
)

# Move single file
result = file_mover.move_file(
    source_path=Path("/source/file.jpg"),
    destination_path=Path("/vault/photos/2024/file.jpg"),
    metadata={"file_type": "image/jpeg"}
)

# Check result
if result.success:
    print(f"Moved to: {result.actual_destination}")
elif result.is_duplicate:
    print(f"Duplicate stored at: {result.actual_destination}")
elif result.is_quarantined:
    print(f"Quarantined at: {result.actual_destination}")
```

#### 2. **IntegrityVerifier** (File Validation)
Calculates and verifies file checksums using SHA256.

```python
from src.services import IntegrityVerifier

verifier = IntegrityVerifier()

# Calculate hash
file_hash = verifier.calculate_hash(Path("/path/to/file.jpg"))

# Verify integrity
result = verifier.verify_integrity(
    file_path=Path("/vault/file.jpg"),
    expected_hash=file_hash
)

if result.match:
    print("Integrity verified")
```

**Features:**
- SHA256, SHA1, MD5 support
- Streaming for large files (64KB chunks)
- Batch verification
- Performance metrics (throughput MB/s)

#### 3. **AtomicMover** (Atomic Operations)
Handles low-level file moves with rollback capability.

```python
from src.services import AtomicMover, IntegrityVerifier
from src.models import MoveOperation

atomic_mover = AtomicMover(IntegrityVerifier())

# Execute atomic move
result = atomic_mover.execute_move(operation)

if result.success:
    print(f"File moved to {result.actual_destination}")
else:
    # Rollback performed automatically
    print(f"Move failed: {result.error}")
```

**Features:**
- Cross-device moves (uses shutil.move)
- Automatic integrity verification
- Rollback on failure
- Timestamp preservation

#### 4. **QuarantineManager** (Error Handling)
Manages problematic files with structured error classification.

```python
from src.services import QuarantineManager
from pathlib import Path

quar_manager = QuarantineManager(quarantine_root=Path("/vault/quarantine"))

# Quarantine file
record = quar_manager.quarantine_file(
    source_path=Path("/source/corrupted.jpg"),
    intended_destination=Path("/vault/photos/corrupted.jpg"),
    error=Exception("Checksum mismatch"),
    metadata={}
)

print(f"Quarantined: {record.file_path}")
print(f"Reason: {record.error_type.value}")
```

**Error Types:**
- `checksum_mismatch` - Integrity verification failed
- `permission_error` - Access/permission issues
- `disk_space_error` - Out of disk space
- `path_too_long` - Path exceeds OS limits
- `invalid_characters` - Invalid chars in path
- `destination_exists` - Destination already exists
- `network_error` - Network storage issue
- `corruption_detected` - File appears corrupted
- `unknown_error` - Unclassified error

#### 5. **DuplicateHandler** (Deduplication)
Detects and handles duplicate files using content hashing.

```python
from src.services import DuplicateHandler

dup_handler = DuplicateHandler(duplicate_db, vault_root)

# Check for duplicate
is_duplicate, original_id = dup_handler.check_duplicate(file_hash, metadata)

if is_duplicate:
    # Handle duplicate
    record = dup_handler.handle_duplicate(source, file_hash, original_id, metadata)
    print(f"Duplicate stored at: {record.duplicate_path}")
```

**Features:**
- Content-based deduplication (SHA256)
- Structured storage: `duplicates/YYYY-MM-DD/{hash_prefix}/filename`
- Metadata diff tracking
- Collision detection

## Data Models

### MoveOperation
Tracks individual file move operations.

```python
from src.models import MoveOperation, OperationStatus
from datetime import datetime

operation = MoveOperation(
    operation_id="uuid",
    source_path=Path("/source/file.jpg"),
    destination_path=Path("/vault/file.jpg"),
    file_hash="abc123...",
    file_size=1024000,
    status=OperationStatus.PENDING,
    created_at=datetime.now()
)
```

**Status Lifecycle:**
1. `PENDING` - Not yet started
2. `IN_PROGRESS` - Currently executing
3. `VERIFYING` - Verifying integrity
4. `COMPLETED` - Successfully completed
5. `FAILED` - Failed with error
6. `ROLLED_BACK` - Rolled back after failure
7. `QUARANTINED` - File moved to quarantine

### MoveResult
Result of move operation.

```python
from src.models import MoveResult

result = MoveResult(
    success=True,
    operation=operation,
    actual_destination=Path("/vault/file.jpg"),
    is_duplicate=False,
    is_quarantined=False,
    execution_time_ms=150.5
)

# Derived properties
print(result.moved_to_vault)  # True if successful normal move
print(result.needs_attention)  # True if quarantined or failed
```

### Batch Operations

```python
from src.models import BatchMoveRequest, BatchMoveResult

# Create batch request
batch = BatchMoveRequest(
    batch_id="batch-123",
    operations=[op1, op2, op3],
    validate_space=True,
    parallel=False,
    max_workers=1
)

# Execute batch
result = file_mover.move_batch(batch)

print(f"Success rate: {result.success_rate}%")
print(f"Successful: {result.successful_count}")
print(f"Duplicates: {result.duplicate_count}")
print(f"Quarantined: {result.quarantine_count}")
print(f"Failed: {result.failed_count}")
```

## Database Schema

The File Mover extends the database with 4 new tables:

### move_operations
```sql
CREATE TABLE move_operations (
    operation_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    destination_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at REAL NOT NULL,
    started_at REAL,
    completed_at REAL,
    error_message TEXT,
    rollback_attempted INTEGER DEFAULT 0,
    rollback_success INTEGER
);
```

### quarantine_records
```sql
CREATE TABLE quarantine_records (
    quarantine_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    original_path TEXT NOT NULL,
    intended_destination TEXT NOT NULL,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    quarantined_at REAL NOT NULL,
    recovery_attempts INTEGER DEFAULT 0,
    file_hash TEXT,
    file_size INTEGER NOT NULL,
    can_retry INTEGER DEFAULT 1
);
```

### duplicate_records
```sql
CREATE TABLE duplicate_records (
    duplicate_id TEXT PRIMARY KEY,
    original_file_id TEXT NOT NULL,
    duplicate_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    detected_at REAL NOT NULL,
    duplicate_size INTEGER NOT NULL
);
```

### batch_operations
```sql
CREATE TABLE batch_operations (
    batch_id TEXT PRIMARY KEY,
    total_operations INTEGER NOT NULL,
    successful_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    quarantine_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    total_time_ms REAL
);
```

## Configuration

### Quarantine Settings
Located at `config/quarantine_settings.json`:

```json
{
  "quarantine_root": "quarantine",
  "folder_structure": {
    "checksum_mismatch": {
      "description": "Files with integrity verification failures",
      "auto_retry": false,
      "max_recovery_attempts": 0
    },
    "permission_error": {
      "auto_retry": true,
      "max_recovery_attempts": 3
    }
  },
  "recovery_policies": {
    "retry_delay_seconds": 60,
    "exponential_backoff": true,
    "max_backoff_seconds": 3600
  }
}
```

## Usage Examples

### Single File Move with Error Handling

```python
from src.services import FileMover
from src.models import OperationStatus

try:
    result = file_mover.move_file(source, destination, metadata)

    if result.success:
        if result.is_duplicate:
            print(f"✓ Duplicate: {result.actual_destination}")
        else:
            print(f"✓ Moved: {result.actual_destination}")
    else:
        if result.is_quarantined:
            print(f"⚠ Quarantined: {result.actual_destination}")
        else:
            print(f"✗ Failed: {result.error}")

except FileNotFoundError as e:
    print(f"Source not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Batch Move with Progress Tracking

```python
from src.models import BatchMoveRequest, MoveOperation
import uuid

operations = []
for source in source_files:
    op = MoveOperation(
        operation_id=str(uuid.uuid4()),
        source_path=source,
        destination_path=vault_path / source.name,
        file_hash=calculate_hash(source),
        file_size=source.stat().st_size,
        status=OperationStatus.PENDING,
        created_at=datetime.now()
    )
    operations.append(op)

batch = BatchMoveRequest(
    batch_id=str(uuid.uuid4()),
    operations=operations,
    validate_space=True,
    parallel=True,
    max_workers=4
)

result = file_mover.move_batch(batch)

print(f"Completed {result.total_operations} operations")
print(f"Success: {result.successful_count}")
print(f"Duplicates: {result.duplicate_count}")
print(f"Quarantined: {result.quarantine_count}")
print(f"Average time: {result.average_time_ms:.2f}ms")
```

### Preview Mode (Dry Run)

```python
# Preview what would happen
preview = file_mover.preview_move(source, destination)

print(f"Will move: {preview['will_move']}")
print(f"Is duplicate: {preview['is_duplicate']}")
print(f"Estimated time: {preview['estimated_time_ms']}ms")
print(f"Potential errors: {preview['potential_errors']}")

# No files modified during preview
assert source.exists()
assert not destination.exists()
```

## Performance

### Targets
- **Single file move**: <200ms (including verification)
- **Batch (100 files)**: <20 seconds (200ms average)
- **Checksum (10MB file)**: <50ms
- **Database transaction**: <10ms

### Optimization Tips
1. **Parallel Execution**: Set `parallel=True` for batch operations
2. **Storage Validation**: Disable with `validate_space=False` for speed
3. **Hash Algorithm**: Use SHA1 instead of SHA256 if security isn't critical
4. **Batch Size**: Process 50-100 files per batch for optimal performance

## Error Handling

### Error Flow
1. **Move fails** → Integrity verification fails → Rollback attempted
2. **Rollback fails** → File quarantined with detailed error
3. **Quarantine fails** → Operation marked as failed, error logged

### Logging
All operations are logged:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs will show:
# 2024-01-15 10:30:00 - src.services.file_mover - INFO - Starting file move: /source/file.jpg -> /vault/file.jpg
# 2024-01-15 10:30:00 - src.services.file_mover - INFO - File moved successfully in 145.23ms
```

## Cross-Platform Compatibility

### Path Handling
- Uses `pathlib.Path` for all file operations
- Handles Windows MAX_PATH (260 chars) limitations
- Sanitizes reserved names (CON, PRN, AUX, etc.)
- Supports cross-device moves

### Platform-Specific Features
- **Windows**: \\?\ prefix for long paths
- **macOS/Linux**: Preserves file permissions
- **All**: Handles case-sensitivity differences

## Integration

### With OrganizationManager
```python
from src.services import OrganizationManager, FileMover

# Get destination from OrganizationManager
org_manager = OrganizationManager()
vault_path = org_manager.determine_path(metadata)

# Execute move
result = file_mover.move_file(source, vault_path, metadata)
```

### With MetadataConsolidator
```python
from src.services import MetadataConsolidator, FileMover

# Get consolidated metadata
consolidator = MetadataConsolidator()
metadata = consolidator.consolidate(processors_metadata)

# Use in move operation
result = file_mover.move_file(source, destination, metadata)
```

## Troubleshooting

### Common Issues

**Integrity Verification Fails**
- Check disk for corruption
- Verify source file exists
- Review quarantine logs

**Permission Errors**
- Ensure write permissions on vault directory
- Check quarantine folder permissions
- Review user/group ownership

**Duplicate Detection Issues**
- Verify DuplicateDatabase is initialized
- Check hash calculation is consistent
- Review duplicate folder structure

## Testing

Run contract tests:
```bash
pytest tests/contract/test_file_mover.py -v
```

Run with coverage:
```bash
pytest tests/contract/test_file_mover.py --cov=src.services.file_mover
```

## Future Enhancements

- [ ] Async/parallel batch operations
- [ ] Progress reporting for large batches
- [ ] Automated quarantine recovery
- [ ] Performance optimizations (fast-path verification)
- [ ] Network storage retry logic
- [ ] Transaction management integration
- [ ] Comprehensive test suite
- [ ] Performance benchmarks

## References

- [Feature Spec](./spec.md)
- [Implementation Plan](./plan.md)
- [Research Findings](./research.md)
- [Data Model](./data-model.md)
- [Task List](./tasks.md)
