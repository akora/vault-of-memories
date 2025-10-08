# Data Model: File Ingestion System

**Phase**: 1 - Design & Contracts
**Date**: 2025-09-19
**Status**: Complete

## Core Entities

### FileRecord
Represents a processed file with all metadata needed for duplicate detection and processing tracking.

**Attributes**:
- `id`: INTEGER PRIMARY KEY - Unique identifier for database records
- `file_path`: TEXT UNIQUE - Full path to the original file
- `checksum`: TEXT - SHA-256 hash in hexadecimal format (64 characters)
- `file_size`: INTEGER - File size in bytes
- `modification_time`: REAL - Unix timestamp of file's last modification
- `created_at`: REAL - Unix timestamp when record was created
- `status`: TEXT - Processing status: pending, processed, duplicate, error

**Relationships**:
- None (single table design for simplicity)

**Validation Rules**:
- `file_path` must be absolute path
- `checksum` must be valid SHA-256 hex string (64 chars, hex only)
- `file_size` must be non-negative
- `status` must be one of: pending, processed, duplicate, error

### ProcessingStats
Aggregated statistics for batch processing operations.

**Attributes**:
- `total_files`: INTEGER - Total files encountered
- `processed_files`: INTEGER - Successfully processed files
- `duplicate_files`: INTEGER - Files identified as duplicates
- `error_files`: INTEGER - Files that failed processing
- `system_files_removed`: INTEGER - System files filtered out
- `total_size`: INTEGER - Total bytes processed
- `processing_time`: FLOAT - Time taken for operation

**Validation Rules**:
- All counts must be non-negative
- `processed_files + duplicate_files + error_files ≤ total_files`

### SystemFilePattern
Configuration for identifying system/hidden files to filter out.

**Attributes**:
- `pattern`: TEXT - Glob pattern for matching filenames
- `case_sensitive`: BOOLEAN - Whether pattern matching is case-sensitive
- `description`: TEXT - Human-readable description of what pattern matches

**Default Patterns**:
- `.DS_Store` - macOS metadata files
- `Thumbs.db` - Windows thumbnail cache
- `desktop.ini` - Windows folder configuration
- `*.tmp` - Temporary files
- `.*` - Hidden files (Unix convention)

## Database Schema

### SQLite Table Definition
```sql
CREATE TABLE file_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    checksum TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    modification_time REAL NOT NULL,
    created_at REAL NOT NULL DEFAULT (strftime('%s', 'now')),
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE INDEX idx_checksum ON file_records(checksum);
CREATE INDEX idx_status ON file_records(status);
```

### State Transitions
```
File Input → [pending] → Processing → [processed|duplicate|error]
```

**State Descriptions**:
- `pending`: File record created, awaiting processing
- `processed`: File successfully processed and routed to next stage
- `duplicate`: File identified as duplicate of existing file
- `error`: Processing failed (permission denied, corruption, etc.)

## Data Access Patterns

### Primary Operations
1. **Insert new file record** - Add file to processing queue
2. **Check for duplicate** - Query by checksum for existing files
3. **Update processing status** - Mark file as processed/duplicate/error
4. **Get processing statistics** - Aggregate counts and metrics
5. **List duplicates** - Find all files with duplicate status

### Query Patterns
```sql
-- Check for duplicate by checksum
SELECT id, file_path FROM file_records WHERE checksum = ?;

-- Get processing statistics
SELECT
    status,
    COUNT(*) as count,
    SUM(file_size) as total_size
FROM file_records
GROUP BY status;

-- Find all duplicates
SELECT checksum, COUNT(*) as count
FROM file_records
GROUP BY checksum
HAVING COUNT(*) > 1;
```

## Data Integrity Constraints

### Business Rules
- No two files can have the same `file_path`
- Files with identical `checksum` are considered duplicates
- `created_at` timestamp is immutable once set
- Status transitions follow defined workflow

### Data Quality Assurance
- Checksum validation ensures 64-character hex strings
- File size validation prevents negative values
- Path validation ensures absolute paths
- Timestamp validation ensures reasonable date ranges

## Backup and Recovery

### Data Protection
- SQLite database provides ACID compliance
- WAL mode for better concurrent access
- Regular integrity checks via `PRAGMA integrity_check`
- Atomic transactions for batch operations

### Recovery Scenarios
- **Database corruption**: Rebuild from file system scan
- **Partial processing**: Resume from last known state
- **System crash**: Transaction rollback ensures consistency