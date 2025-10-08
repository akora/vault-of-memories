# Research: File Mover Technical Decisions

**Feature**: 011-file-mover | **Date**: 2025-10-08
**Input**: Technical unknowns from plan.md

## Research Questions

1. How to implement atomic file move operations across platforms?
2. How to coordinate file operations with database transactions?
3. What file integrity verification strategies are appropriate?
4. How to handle duplicate files efficiently?
5. How to manage quarantine operations?
6. How to implement rollback for failed operations?
7. How to validate storage space before operations?

---

## Decision 1: Atomic File Move Operations

**Decision**: Use `shutil.move()` with explicit error handling and verification, not `os.rename()`

**Rationale**:
- `shutil.move()` handles cross-device moves automatically (falls back to copy + delete)
- `os.rename()` fails when source and destination are on different filesystems
- Need explicit verification after move to ensure integrity
- Use atomic directory creation with `pathlib.Path.mkdir(parents=True, exist_ok=True)`

**Alternatives Considered**:
- `os.rename()`: Fast but fails across devices, not robust enough
- `shutil.move2()`: Preserves metadata but not available in all Python versions
- Custom copy + verify + delete: More control but reinvents wheel

**Implementation Approach**:
```
1. Verify source file exists and is readable
2. Calculate source file checksum (SHA256)
3. Ensure destination directory exists
4. Use shutil.move() to move file
5. Verify destination file checksum matches source
6. If verification fails, attempt rollback
```

**Cross-Platform Considerations**:
- Windows: Handle MAX_PATH limitations (260 chars) using \\?\ prefix
- Windows: Handle reserved names (CON, PRN, AUX, etc.)
- macOS/Linux: Handle case-sensitivity differences
- All platforms: Preserve file timestamps using os.utime() after move

---

## Decision 2: Transaction Coordination (File + Database)

**Decision**: Use Python context manager with explicit rollback tracking

**Rationale**:
- SQLite supports transactions via connection.begin() / commit() / rollback()
- Filesystem operations cannot be transactional like database operations
- Need compensation pattern: track operations and undo on failure
- Use context manager to ensure cleanup happens even on exceptions

**Alternatives Considered**:
- Two-phase commit: Overly complex for this use case
- Write-ahead log: Requires persistent state management
- No coordination: Risk of inconsistency between filesystem and database

**Implementation Approach**:
```python
class TransactionManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.operations = []  # Track for rollback

    def execute(self, file_operation, db_operation):
        try:
            # Start database transaction
            self.db_manager.begin()

            # Execute file operation
            result = file_operation()
            self.operations.append(('file', result))

            # Execute database operation
            db_operation()

            # Commit database transaction
            self.db_manager.commit()

            return Result(success=True, data=result)
        except Exception as e:
            # Rollback database
            self.db_manager.rollback()

            # Rollback file operations
            self._rollback_file_operations()

            return Result(success=False, error=e)
```

**Edge Cases**:
- Database commit succeeds but file move fails: Rollback database
- File move succeeds but database commit fails: Move file back to source
- Multiple failures during rollback: Log all errors, leave in consistent state

---

## Decision 3: File Integrity Verification

**Decision**: Use SHA256 checksums with optional fast-path for small files

**Rationale**:
- SHA256 provides strong collision resistance (better than MD5/SHA1)
- Standard library support via hashlib (no external dependencies)
- Reasonable performance for typical file sizes in vault
- Fast-path: For files <1MB, can use size + mtime as quick check

**Alternatives Considered**:
- MD5: Faster but cryptographically broken
- CRC32: Fast but too many collisions for integrity verification
- No verification: Unacceptable risk of silent corruption
- xxHash: Faster but requires external dependency

**Implementation Approach**:
```python
def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum using streaming for large files"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def verify_move(source_hash, dest_path):
    """Verify file integrity after move"""
    dest_hash = calculate_checksum(dest_path)
    return source_hash == dest_hash
```

**Performance Considerations**:
- 65KB chunk size balances memory and I/O efficiency
- For files >100MB, show progress or run async
- Cache checksums in database to avoid recalculation

---

## Decision 4: Duplicate File Handling

**Decision**: Use content-based deduplication with hash-based identification

**Rationale**:
- Already have DuplicateDatabase from feature 008
- Content hash (SHA256) is authoritative duplicate identifier
- Filename/metadata can vary but content is identical
- Store duplicates in structured folder: vault/duplicates/YYYY-MM-DD/hash-prefix/

**Alternatives Considered**:
- Metadata-only matching: Misses true duplicates with different metadata
- Filename-only matching: Too many false positives
- No duplicate handling: Wastes storage space

**Implementation Approach**:
```
1. Calculate file hash before move
2. Check DuplicateDatabase for existing file with same hash
3. If duplicate found:
   a. Move to duplicates folder: duplicates/YYYY-MM-DD/{hash[:4]}/{filename}
   b. Record relationship in database (original_id, duplicate_id)
   c. Store duplicate metadata separately
4. If not duplicate:
   a. Proceed with normal move
   b. Store hash in database for future duplicate checks
```

**Duplicate Folder Structure**:
```
vault/
└── duplicates/
    └── YYYY-MM-DD/          # Date duplicate was found
        └── {hash_prefix}/   # First 4 chars of hash
            └── filename_TIMESTAMP.ext
```

---

## Decision 5: Quarantine Management

**Decision**: Use structured quarantine folder with error classification

**Rationale**:
- Quarantine prevents problematic files from blocking workflow
- Structured error classification enables automated recovery
- Detailed logging helps troubleshooting
- Recovery workflow allows retrying after fixes

**Alternatives Considered**:
- Fail entire batch on single error: Too disruptive
- Skip problematic files silently: Risk of data loss
- Manual intervention only: Doesn't scale

**Implementation Approach**:
```
Quarantine folder structure:
vault/
└── quarantine/
    ├── checksum_mismatch/    # Integrity verification failures
    ├── permission_error/     # Permission/access issues
    ├── disk_space/           # Out of space errors
    ├── path_too_long/        # Path length violations
    └── unknown/              # Unclassified errors

Each file stored with metadata JSON:
{
    "original_path": "/source/file.jpg",
    "intended_destination": "/vault/2024/2024-01/file.jpg",
    "error_type": "checksum_mismatch",
    "error_message": "...",
    "quarantine_timestamp": "2024-01-15T10:30:00Z",
    "source_hash": "abc123...",
    "recovery_attempts": 0
}
```

**Recovery Workflow**:
1. Periodic scan of quarantine folders
2. Attempt automated recovery based on error type
3. Notify user of unrecoverable files
4. Track recovery attempts to prevent infinite loops

---

## Decision 6: Rollback Strategies

**Decision**: Implement compensation-based rollback with detailed logging

**Rationale**:
- Filesystem operations can't be truly rolled back like database transactions
- Compensation pattern: reverse each operation explicitly
- Detailed logging enables manual recovery if automated rollback fails
- Track rollback state to avoid partial rollbacks

**Alternatives Considered**:
- Snapshot-based rollback: Too storage-intensive
- No rollback: Unacceptable risk of inconsistency
- Lock-based prevention: Doesn't handle crashes/interruptions

**Implementation Approach**:
```python
class RollbackManager:
    def __init__(self):
        self.operations = []  # Stack of completed operations

    def record_move(self, source, destination):
        """Record a completed move operation"""
        self.operations.append({
            'type': 'move',
            'source': source,
            'destination': destination,
            'timestamp': datetime.now()
        })

    def rollback_all(self):
        """Rollback all operations in reverse order"""
        errors = []
        while self.operations:
            op = self.operations.pop()
            try:
                if op['type'] == 'move':
                    # Move file back to source
                    shutil.move(op['destination'], op['source'])
                    logger.info(f"Rolled back: {op['destination']} → {op['source']}")
            except Exception as e:
                errors.append({'operation': op, 'error': str(e)})
                logger.error(f"Rollback failed for {op}: {e}")

        return errors
```

**Rollback Guarantees**:
- Best-effort: Attempt to reverse all operations
- Log all rollback failures for manual intervention
- Leave system in consistent state (either all moved or all at source)
- Don't attempt rollback if destination is also source (duplicate case)

---

## Decision 7: Storage Space Validation

**Decision**: Pre-flight validation with safety margin

**Rationale**:
- Prevent partial batch failures due to disk space exhaustion
- Check available space before starting batch operations
- Use safety margin (10%) to account for metadata, logs, etc.
- Graceful degradation: Continue with smaller batches if space limited

**Alternatives Considered**:
- No validation: Risk of disk full errors mid-batch
- Per-file validation: Too many stat calls, performance impact
- Optimistic approach: Only check on failure

**Implementation Approach**:
```python
def validate_storage_space(files, destination_root):
    """Validate sufficient storage space before batch move"""
    # Calculate total size needed
    total_size = sum(Path(f).stat().st_size for f in files)

    # Get available space on destination
    stat = os.statvfs(destination_root)
    available = stat.f_bavail * stat.f_frsize

    # Require 10% safety margin
    required = total_size * 1.1

    if required > available:
        raise InsufficientStorageError(
            f"Need {required:,} bytes, only {available:,} available"
        )

    return True
```

**Graceful Degradation**:
- If batch too large, split into smaller batches
- Prioritize files by importance (e.g., original > derivative)
- Pause and notify user when space critically low (<5% free)

---

## Implementation Priorities

1. **Critical** (must have for MVP):
   - Atomic file moves with verification
   - Transaction coordination
   - Basic integrity checking
   - Quarantine for failed moves

2. **Important** (needed for production):
   - Duplicate handling
   - Rollback capability
   - Storage space validation
   - Comprehensive error classification

3. **Nice to have** (future enhancements):
   - Async/parallel batch operations
   - Progress reporting for large batches
   - Automated quarantine recovery
   - Performance optimizations (fast-path verification)

---

## Dependencies on Existing Features

- **Feature 008 (Metadata Consolidator)**: Source of file metadata
- **Feature 010 (Organization Manager)**: Determines destination paths
- **Feature 002 (Configuration System)**: Vault root path, quarantine settings
- **Existing DatabaseManager**: Transaction management, record storage

---

## Performance Targets

- **Single file move**: <200ms (including verification)
- **Batch of 100 files**: <20 seconds (200ms/file average)
- **Checksum calculation**: <50ms for files <10MB
- **Database transaction**: <10ms
- **Storage validation**: <100ms for batch

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Disk full during move | Pre-flight space validation |
| Power loss during move | Transaction log for recovery |
| Checksum mismatch | Quarantine file, don't delete source |
| Database corruption | Database backups, transaction rollback |
| Network interruption (network storage) | Retry logic with exponential backoff |
| Permission errors | Quarantine with clear error message |
| Race conditions | File locking, atomic operations |

---

## Constitution Compliance

- ✅ **Simplicity First**: Standard library only (shutil, hashlib, pathlib)
- ✅ **Dependency Minimalism**: No new external dependencies
- ✅ **Industry Standards**: ACID-like properties, standard hash algorithms
- ✅ **Test-Driven**: All scenarios testable with mock filesystem
- ✅ **Strategic Documentation**: Self-documenting code, clear error messages
- ✅ **Readability Priority**: Clear separation of concerns, single responsibility

---

**Research Status**: ✅ Complete
**Next Phase**: Design & Contracts (data-model.md, contracts/)
