# Research: File Ingestion System

**Phase**: 0 - Outline & Research
**Date**: 2025-09-19
**Status**: Complete

## Technical Decisions

### Checksum Algorithm Choice
**Decision**: SHA-256
**Rationale**: Industry standard cryptographic hash, excellent collision resistance, available in Python stdlib
**Alternatives considered**: MD5 (deprecated), SHA-1 (security concerns), Blake2 (not stdlib)

### Database Choice
**Decision**: SQLite
**Rationale**: Zero-configuration, ACID compliance, excellent for file tracking, Python stdlib
**Alternatives considered**: PostgreSQL (overkill), JSON files (no concurrency), CSV (no relationships)

### File Processing Strategy
**Decision**: Streaming with fixed-size chunks
**Rationale**: Memory-efficient for large files, consistent performance, standard practice
**Alternatives considered**: Full file reading (memory issues), variable chunks (complexity)

### Directory Traversal Method
**Decision**: os.walk() with pathlib.Path
**Rationale**: Efficient recursive traversal, cross-platform compatibility, stdlib
**Alternatives considered**: glob (limited recursion), manual recursion (reinventing wheel)

## Performance Research

### Chunk Size Optimization
- **64KB chunks**: Optimal balance for I/O performance based on filesystem research
- **Memory usage**: Constant memory footprint regardless of file size
- **Throughput**: ~500MB/s on modern SSDs with this chunk size

### Database Performance
- **Indexed checksums**: B-tree index on checksum field for O(log n) duplicate lookup
- **Batch operations**: Transaction-based batching for bulk inserts
- **Connection pooling**: Single connection per process for simplicity

### File System Considerations
- **Permission handling**: Graceful degradation on access denied
- **Symbolic link handling**: Follow links but detect cycles
- **Large directory handling**: Generator patterns to avoid memory issues

## Integration Patterns

### Error Handling Strategy
- **Continue on error**: Individual file failures don't stop batch processing
- **Comprehensive logging**: All errors logged with context for troubleshooting
- **Status tracking**: Database records track processing status per file

### System File Filtering
- **Pattern-based filtering**: Configurable patterns for system files
- **Common patterns**: .DS_Store, Thumbs.db, *.tmp, desktop.ini
- **Case-insensitive matching**: Cross-platform compatibility

### Concurrent Processing
- **Single-threaded design**: Simplicity over performance for initial implementation
- **Future scalability**: Architecture supports threading in later versions
- **Database safety**: SQLite handles concurrent reads efficiently

## Dependencies Validation

### Standard Library Dependencies
- `hashlib`: SHA-256 implementation ✓
- `sqlite3`: Database operations ✓
- `pathlib`: Modern path handling ✓
- `os`: Directory traversal ✓
- `logging`: Error and audit logging ✓

### No External Dependencies Required
All functionality achievable with Python standard library, meeting Dependency Minimalism principle.

## Compliance Verification

### Constitution Alignment
- **Simplicity First**: Standard library approach, minimal complexity
- **Dependency Minimalism**: Zero external dependencies
- **Industry Standards**: SHA-256, SQLite both industry standards
- **Test-Driven Design**: All interfaces designed for testability
- **Readability**: Clear separation of concerns, descriptive naming

### Digital Preservation Standards
- **Data integrity**: Checksum verification ensures file integrity
- **Non-destructive**: Read-only operations, no source file modification
- **Audit trail**: Complete logging of all operations
- **Reversible**: Database operations can be undone if needed