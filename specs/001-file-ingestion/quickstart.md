# Quickstart: File Ingestion System

**Phase**: 1 - Design & Contracts
**Date**: 2025-09-19
**Purpose**: Validate implementation through end-to-end scenarios

## Setup Instructions

### Prerequisites
- Python 3.11+
- SQLite3 (included with Python)
- Test data directory with sample files

### Quick Test Setup
```bash
# Navigate to project root
cd vault-of-memories

# Create test data structure
mkdir -p test_data/sample_files
mkdir -p test_data/nested/subfolder

# Add test files (examples)
echo "Test content 1" > test_data/sample_files/file1.txt
echo "Test content 2" > test_data/sample_files/file2.txt
cp test_data/sample_files/file1.txt test_data/sample_files/duplicate.txt
touch test_data/sample_files/.DS_Store
```

## Basic Usage Scenarios

### Scenario 1: Single File Ingestion
```python
from src.services.file_ingestor import FileIngestorImpl
from pathlib import Path

# Initialize ingestor
ingestor = FileIngestorImpl()

# Process single file
file_path = Path("test_data/sample_files/file1.txt")
record = ingestor.ingest_file(file_path)

# Verify results
assert record.checksum is not None
assert record.file_size > 0
assert record.status == ProcessingStatus.PROCESSED
```

### Scenario 2: Directory Processing
```python
# Process entire directory
dir_path = Path("test_data/sample_files")
records = ingestor.ingest_directory(dir_path)

# Verify batch processing
stats = ingestor.get_processing_stats()
assert stats.total_files >= 3  # file1, file2, duplicate
assert stats.duplicate_files >= 1  # duplicate.txt
assert stats.system_files_removed >= 1  # .DS_Store
```

### Scenario 3: Duplicate Detection
```python
# First ingestion
record1 = ingestor.ingest_file(Path("test_data/sample_files/file1.txt"))
assert record1.status == ProcessingStatus.PROCESSED

# Second ingestion of identical file
record2 = ingestor.ingest_file(Path("test_data/sample_files/duplicate.txt"))
assert record2.status == ProcessingStatus.DUPLICATE
assert record1.checksum == record2.checksum
```

### Scenario 4: Error Handling
```python
# Test with non-existent file
try:
    ingestor.ingest_file(Path("non_existent.txt"))
    assert False, "Should have raised FileNotFoundError"
except FileNotFoundError:
    pass  # Expected behavior

# Test with permission denied (if possible in test environment)
# Stats should show error count
stats = ingestor.get_processing_stats()
print(f"Errors encountered: {stats.error_files}")
```

## Validation Checklist

### Functional Validation
- [ ] Single file processing calculates correct SHA-256 checksum
- [ ] Directory processing handles all files recursively
- [ ] Duplicate detection identifies identical files correctly
- [ ] System files (.DS_Store, Thumbs.db) are filtered out
- [ ] File metadata (size, timestamps) preserved accurately
- [ ] Processing statistics provide accurate counts

### Performance Validation
- [ ] Large files (>100MB) process without memory issues
- [ ] Directory with 1000+ files completes in reasonable time
- [ ] Database operations remain responsive during batch processing
- [ ] Memory usage stays constant regardless of file size

### Error Handling Validation
- [ ] Graceful handling of permission denied errors
- [ ] Continued processing when individual files fail
- [ ] Proper error logging with sufficient context
- [ ] Database consistency maintained during errors

### Constitutional Compliance
- [ ] **Simplicity First**: Implementation uses standard library
- [ ] **Dependency Minimalism**: No external dependencies required
- [ ] **Industry Standards**: SHA-256 for checksums, SQLite for storage
- [ ] **Test-Driven**: All interfaces have corresponding tests
- [ ] **Digital Preservation**: Source files remain unmodified

## Expected Results

### Successful Test Run Output
```
Processing Statistics:
- Total Files: 4
- Processed: 2
- Duplicates: 1
- System Files Removed: 1
- Errors: 0
- Total Size: 1,024 bytes
- Processing Time: 0.15 seconds

All validations: PASSED
```

### Performance Benchmarks
- Single file: <10ms average
- 1000 files: <30 seconds total
- Memory usage: <50MB regardless of file sizes
- Database operations: <5ms per query

This quickstart guide ensures the implementation meets all requirements and provides a reliable foundation for the vault processing pipeline.