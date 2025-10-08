# Quickstart: File Mover Test Scenarios

**Feature**: 011-file-mover | **Date**: 2025-10-08
**Purpose**: Integration test scenarios derived from acceptance criteria

## Overview

These scenarios test the File Mover's core functionality: moving files to vault locations, handling duplicates, managing quarantine, and ensuring atomic operations.

---

## Scenario 1: Successful Single File Move

**Goal**: Verify successful file move to vault with database update

**Setup**:
```python
# Given: A processed file ready for vault placement
source_file = temp_dir / "IMG_1234.jpg"
source_file.write_bytes(b"test image content")

metadata = {
    "file_hash": calculate_hash(source_file),
    "file_type": "image/jpeg",
    "capture_date": "2024-01-15"
}

destination = vault_path / "photos/2024/2024-01/2024-01-15/IMG_1234.jpg"
```

**Execution**:
```python
# When: FileMover executes move operation
file_mover = FileMover(db_manager, duplicate_handler, quarantine_manager)
result = file_mover.move_file(source_file, destination, metadata)
```

**Assertions**:
```python
# Then: File moved successfully and database updated
assert result.success is True
assert result.actual_destination == destination
assert destination.exists()
assert not source_file.exists()
assert result.is_duplicate is False
assert result.is_quarantined is False

# Verify database record created
db_record = db_manager.get_file_record_by_path(destination)
assert db_record is not None
assert db_record['file_hash'] == metadata['file_hash']

# Verify file integrity
actual_hash = calculate_hash(destination)
assert actual_hash == metadata['file_hash']
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Scenario 2: Duplicate File Handling

**Goal**: Verify duplicate files are moved to duplicates folder

**Setup**:
```python
# Given: An original file already in vault
original_file = vault_path / "photos/2024/2024-01/original.jpg"
original_file.parent.mkdir(parents=True, exist_ok=True)
original_file.write_bytes(b"unique content")
file_hash = calculate_hash(original_file)

# Store in database
db_manager.add_file_record(original_file, file_hash, metadata)

# Given: A duplicate file (same content, different name)
duplicate_source = temp_dir / "duplicate.jpg"
duplicate_source.write_bytes(b"unique content")
assert calculate_hash(duplicate_source) == file_hash

destination = vault_path / "photos/2024/2024-02/duplicate.jpg"
```

**Execution**:
```python
# When: FileMover processes duplicate
result = file_mover.move_file(duplicate_source, destination, metadata)
```

**Assertions**:
```python
# Then: File moved to duplicates folder with cross-reference
assert result.success is True
assert result.is_duplicate is True
assert result.is_quarantined is False

# Verify duplicate stored in correct location
expected_duplicate_path = vault_path / f"duplicates/{today_str}/{file_hash[:4]}/duplicate.jpg"
assert result.actual_destination == expected_duplicate_path
assert result.actual_destination.exists()

# Verify original file unchanged
assert original_file.exists()

# Verify duplicate record in database
duplicate_record = db_manager.get_duplicate_record(file_hash)
assert duplicate_record is not None
assert duplicate_record['original_file_id'] is not None
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Scenario 3: File Quarantine on Checksum Mismatch

**Goal**: Verify files with integrity issues are quarantined

**Setup**:
```python
# Given: A file that will fail integrity check
source_file = temp_dir / "corrupted.jpg"
source_file.write_bytes(b"original content")
original_hash = calculate_hash(source_file)

destination = vault_path / "photos/2024/2024-01/corrupted.jpg"

# Mock IntegrityVerifier to simulate corruption
mock_verifier = Mock(IntegrityVerifier)
mock_verifier.verify_integrity.return_value = IntegrityCheckResult(
    file_path=destination,
    expected_hash=original_hash,
    actual_hash="different_hash",
    match=False,
    check_time_ms=50.0,
    algorithm="sha256",
    file_size=100,
    checked_at=datetime.now()
)
```

**Execution**:
```python
# When: FileMover attempts move and detects corruption
file_mover = FileMover(
    db_manager,
    duplicate_handler,
    quarantine_manager,
    integrity_verifier=mock_verifier
)
result = file_mover.move_file(source_file, destination, metadata)
```

**Assertions**:
```python
# Then: File quarantined with detailed error information
assert result.success is False
assert result.is_quarantined is True
assert result.is_duplicate is False

# Verify file in quarantine
quarantine_path = vault_path / "quarantine/checksum_mismatch/corrupted.jpg"
assert quarantine_path.exists()

# Verify quarantine record
quarantine_record = db_manager.get_quarantine_record_by_path(quarantine_path)
assert quarantine_record is not None
assert quarantine_record['error_type'] == 'checksum_mismatch'
assert quarantine_record['original_path'] == str(source_file)
assert quarantine_record['intended_destination'] == str(destination)

# Verify metadata JSON created
metadata_json = quarantine_path.with_suffix('.json')
assert metadata_json.exists()
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Scenario 4: Transaction Rollback on Database Failure

**Goal**: Verify file operations rollback when database update fails

**Setup**:
```python
# Given: A valid file ready to move
source_file = temp_dir / "test.jpg"
source_file.write_bytes(b"test content")
file_hash = calculate_hash(source_file)
destination = vault_path / "photos/2024/2024-01/test.jpg"

# Mock DatabaseManager to fail on update
mock_db = Mock(DatabaseManager)
mock_db.begin.return_value = None
mock_db.commit.side_effect = Exception("Database connection lost")
mock_db.rollback.return_value = None
```

**Execution**:
```python
# When: FileMover executes but database fails
file_mover = FileMover(mock_db, duplicate_handler, quarantine_manager)
result = file_mover.move_file(source_file, destination, metadata)
```

**Assertions**:
```python
# Then: File operation rolled back, source unchanged
assert result.success is False
assert result.error is not None
assert "Database" in str(result.error)

# Verify file moved back to source (rollback succeeded)
assert source_file.exists()
assert not destination.exists()

# Verify database rollback was called
mock_db.rollback.assert_called_once()

# Verify no partial records in database
assert db_manager.get_file_record_by_path(destination) is None
```

**Cleanup**:
```python
# Remove test files
```

---

## Scenario 5: Batch Move with Mixed Outcomes

**Goal**: Verify batch operations handle success, duplicates, and failures

**Setup**:
```python
# Given: Multiple files with different outcomes
files = [
    (temp_dir / "success.jpg", "will succeed"),
    (temp_dir / "duplicate.jpg", "duplicate content"),
    (temp_dir / "quarantine.jpg", "will fail verification")
]

for file_path, content in files:
    file_path.write_bytes(content.encode())

# Setup duplicate
original = vault_path / "photos/2024/original.jpg"
original.parent.mkdir(parents=True, exist_ok=True)
original.write_bytes(b"duplicate content")
db_manager.add_file_record(original, calculate_hash(original), {})

# Create batch request
operations = [
    MoveOperation(
        operation_id=str(uuid.uuid4()),
        source_path=file_path,
        destination_path=vault_path / f"photos/2024/{file_path.name}",
        file_hash=calculate_hash(file_path),
        file_size=file_path.stat().st_size
    )
    for file_path, _ in files
]

batch_request = BatchMoveRequest(
    batch_id=str(uuid.uuid4()),
    operations=operations,
    validate_space=True,
    parallel=False,
    max_workers=1,
    stop_on_error=False
)
```

**Execution**:
```python
# When: FileMover processes batch
result = file_mover.move_batch(batch_request)
```

**Assertions**:
```python
# Then: Batch completes with detailed results
assert result.total_operations == 3
assert result.successful_count == 1  # success.jpg
assert result.duplicate_count == 1   # duplicate.jpg
assert result.quarantine_count == 1  # quarantine.jpg (or failed_count)

# Verify individual results
success_result = next(r for r in result.results if "success" in r.operation.source_path.name)
assert success_result.success is True
assert success_result.is_duplicate is False

duplicate_result = next(r for r in result.results if "duplicate" in r.operation.source_path.name)
assert duplicate_result.is_duplicate is True

quarantine_result = next(r for r in result.results if "quarantine" in r.operation.source_path.name)
assert quarantine_result.is_quarantined is True or not quarantine_result.success
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Scenario 6: Storage Space Validation

**Goal**: Verify batch operations validate storage space before execution

**Setup**:
```python
# Given: Large batch of files
large_files = []
for i in range(100):
    file_path = temp_dir / f"large_{i}.dat"
    file_path.write_bytes(b"x" * (10 * 1024 * 1024))  # 10MB each
    large_files.append(file_path)

operations = [
    MoveOperation(
        operation_id=str(uuid.uuid4()),
        source_path=fp,
        destination_path=vault_path / fp.name,
        file_hash=calculate_hash(fp),
        file_size=fp.stat().st_size
    )
    for fp in large_files
]

batch_request = BatchMoveRequest(
    batch_id=str(uuid.uuid4()),
    operations=operations,
    validate_space=True,  # Enable validation
    parallel=False
)

# Mock filesystem to report insufficient space
mock_statvfs = Mock()
mock_statvfs.f_bavail = 100  # Very low available blocks
mock_statvfs.f_frsize = 4096
```

**Execution**:
```python
# When: FileMover validates space (with mock)
with patch('os.statvfs', return_value=mock_statvfs):
    with pytest.raises(InsufficientStorageError) as exc_info:
        file_mover.move_batch(batch_request)
```

**Assertions**:
```python
# Then: Batch fails fast with clear error
assert "insufficient" in str(exc_info.value).lower()
assert "storage" in str(exc_info.value).lower()

# Verify no files were moved
for fp in large_files:
    assert fp.exists()  # Source still exists
    assert not (vault_path / fp.name).exists()  # Destination doesn't exist
```

**Cleanup**:
```python
# Remove test files
```

---

## Scenario 7: Concurrent File Operations

**Goal**: Verify thread-safe batch operations with parallelism

**Setup**:
```python
# Given: Multiple files for parallel processing
files = []
for i in range(20):
    file_path = temp_dir / f"parallel_{i}.txt"
    file_path.write_bytes(f"content {i}".encode())
    files.append(file_path)

operations = [
    MoveOperation(
        operation_id=str(uuid.uuid4()),
        source_path=fp,
        destination_path=vault_path / "documents" / fp.name,
        file_hash=calculate_hash(fp),
        file_size=fp.stat().st_size
    )
    for fp in files
]

batch_request = BatchMoveRequest(
    batch_id=str(uuid.uuid4()),
    operations=operations,
    validate_space=False,
    parallel=True,        # Enable parallelism
    max_workers=4,        # Use 4 threads
    stop_on_error=False
)
```

**Execution**:
```python
# When: FileMover processes batch in parallel
result = file_mover.move_batch(batch_request)
```

**Assertions**:
```python
# Then: All files moved successfully without conflicts
assert result.total_operations == 20
assert result.successful_count == 20
assert result.failed_count == 0

# Verify all destination files exist
for op in operations:
    assert op.destination_path.exists()
    assert not op.source_path.exists()

# Verify no race conditions (all database records created)
for op in operations:
    record = db_manager.get_file_record_by_path(op.destination_path)
    assert record is not None

# Verify performance benefit (should be faster than sequential)
# This is approximate - parallel should be <50% of sequential time
assert result.total_time_ms < (result.average_time_ms * 20 * 0.5)
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Scenario 8: Preview Mode (Dry Run)

**Goal**: Verify preview functionality shows what would happen without executing

**Setup**:
```python
# Given: A file that would be identified as duplicate
original = vault_path / "photos/original.jpg"
original.parent.mkdir(parents=True, exist_ok=True)
original.write_bytes(b"shared content")
db_manager.add_file_record(original, calculate_hash(original), {})

preview_source = temp_dir / "preview.jpg"
preview_source.write_bytes(b"shared content")
destination = vault_path / "photos/2024/preview.jpg"
```

**Execution**:
```python
# When: FileMover previews move
preview = file_mover.preview_move(preview_source, destination)
```

**Assertions**:
```python
# Then: Preview shows duplicate without moving file
assert preview['will_move'] is True
assert preview['is_duplicate'] is True
assert 'duplicates' in str(preview['actual_destination'])
assert preview['estimated_time_ms'] > 0
assert len(preview['potential_errors']) == 0

# Verify no files were actually moved
assert preview_source.exists()
assert not destination.exists()

# Verify no database changes
assert db_manager.get_file_record_by_path(destination) is None
```

**Cleanup**:
```python
# Remove test files and database records
```

---

## Test Execution Order

For integration testing, run scenarios in this order:
1. Scenario 1 (baseline successful move)
2. Scenario 8 (preview mode - non-destructive)
3. Scenario 2 (duplicate handling)
4. Scenario 3 (quarantine)
5. Scenario 4 (rollback)
6. Scenario 5 (batch with mixed outcomes)
7. Scenario 6 (storage validation)
8. Scenario 7 (parallel operations)

---

## Common Test Utilities

```python
def setup_test_environment():
    """Create clean test environment"""
    temp_dir = Path(tempfile.mkdtemp())
    vault_path = temp_dir / "vault"
    vault_path.mkdir()
    db_path = temp_dir / "test.db"
    db_manager = DatabaseManager(db_path)
    db_manager.initialize()
    return temp_dir, vault_path, db_manager

def cleanup_test_environment(temp_dir):
    """Remove test environment"""
    shutil.rmtree(temp_dir)

def calculate_hash(file_path, algorithm='sha256'):
    """Calculate file hash for tests"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        hash_obj.update(f.read())
    return hash_obj.hexdigest()
```

---

**Quickstart Status**: ✅ Complete
**Next Phase**: Task Generation (/tasks command)
