# Quickstart: Organization Manager

**Feature**: 010-organization-manager
**Purpose**: Validate organization manager implementation with real-world scenarios
**Estimated Time**: 10-15 minutes

---

## Prerequisites

- Organization Manager implementation complete
- MetadataConsolidator available (feature 008)
- Test vault directory configured
- Sample files with metadata available

---

## Test Scenarios

### Scenario 1: Family Photo Organization

**Given**: A family photo with complete EXIF data
```
File: /inbox/IMG_20240115_143022.CR2
EXIF:
  - DateTimeOriginal: 2024:01:15 14:30:22
  - OffsetTimeOriginal: +05:30
  - Make: Canon
  - Model: EOS R5
Type: image/x-canon-cr2
```

**When**: Run organization manager
```python
from pathlib import Path
from src.services.organization_manager import OrganizationManager

manager = OrganizationManager(vault_root=Path("/vault"))
vault_path = manager.determine_path(
    file_path=Path("/inbox/IMG_20240115_143022.CR2"),
    metadata={
        'datetime_original': '2024:01:15 14:30:22',
        'offset_time_original': '+05:30',
        'mime_type': 'image/x-canon-cr2',
        'make': 'Canon',
        'model': 'EOS R5'
    }
)
```

**Then**: Verify organization decision
```python
assert vault_path.primary_category == "photos"
assert vault_path.subcategory == "raw"
assert vault_path.year == "2024"
assert vault_path.month == "2024-01"
assert vault_path.day == "2024-01-15"
assert vault_path.full_path == Path("/vault/photos/raw/2024/2024-01/2024-01-15")
```

**Expected Output**:
```
✓ Classified as: photos/raw (confidence: 0.95, method: libmagic)
✓ Date extracted: 2024-01-15 (source: exif_datetime_original, tz: +05:30)
✓ Target path: /vault/photos/raw/2024/2024-01/2024-01-15
```

---

### Scenario 2: Office Document with No EXIF

**Given**: A PDF document without metadata
```
File: /inbox/quarterly_report.pdf
File creation time: 2024-01-15 09:00:00 UTC
File modification time: 2024-01-16 14:30:00 UTC
Type: application/pdf
```

**When**: Run organization manager
```python
vault_path = manager.determine_path(
    file_path=Path("/inbox/quarterly_report.pdf"),
    metadata={
        'mime_type': 'application/pdf',
        'file_creation_time': 1705309200,  # 2024-01-15 09:00:00 UTC
        'file_modification_time': 1705416600  # 2024-01-16 14:30:00 UTC
    }
)
```

**Then**: Verify organization decision
```python
assert vault_path.primary_category == "documents"
assert vault_path.subcategory == "pdf"
assert vault_path.year == "2024"
assert vault_path.month == "2024-01"
assert vault_path.day == "2024-01-15"  # Uses creation time, not modification
assert vault_path.full_path == Path("/vault/documents/pdf/2024/2024-01/2024-01-15")
```

**Expected Output**:
```
✓ Classified as: documents/pdf (confidence: 0.95, method: libmagic)
✓ Date extracted: 2024-01-15 (source: file_creation_time, confidence: 0.8)
✓ Target path: /vault/documents/pdf/2024/2024-01/2024-01-15
```

---

### Scenario 3: Video with Unclear Classification

**Given**: A video file with ambiguous metadata
```
File: /inbox/family_vacation.mp4
File creation time: 2024-01-15 12:00:00 UTC
Type: video/mp4
Bitrate: 3.5 Mbps (compressed)
```

**When**: Run organization manager with fallback
```python
vault_path = manager.determine_path(
    file_path=Path("/inbox/family_vacation.mp4"),
    metadata={
        'mime_type': 'video/mp4',
        'bitrate': 3500000,  # 3.5 Mbps
        'file_creation_time': 1705320000
    }
)
```

**Then**: Verify fallback classification
```python
assert vault_path.primary_category == "videos"
assert vault_path.subcategory is None  # No specific subcategory
assert vault_path.year == "2024"
assert vault_path.month == "2024-01"
assert vault_path.day == "2024-01-15"
assert vault_path.full_path == Path("/vault/videos/2024/2024-01/2024-01-15")
```

**Expected Output**:
```
✓ Classified as: videos (confidence: 0.95, method: libmagic)
⚠ No subcategory determined (bitrate below professional threshold)
✓ Date extracted: 2024-01-15 (source: file_creation_time, confidence: 0.8)
✓ Target path: /vault/videos/2024/2024-01/2024-01-15
```

---

### Scenario 4: File with Date in Filename

**Given**: File without metadata, date in filename
```
File: /inbox/scan_2024-01-15_invoice.pdf
Type: application/pdf
No EXIF, no reliable filesystem times
```

**When**: Run organization manager with filename parsing
```python
vault_path = manager.determine_path(
    file_path=Path("/inbox/scan_2024-01-15_invoice.pdf"),
    metadata={
        'mime_type': 'application/pdf',
        # No creation/modification times available
    }
)
```

**Then**: Verify filename date parsing
```python
assert vault_path.primary_category == "documents"
assert vault_path.subcategory == "pdf"
assert vault_path.year == "2024"
assert vault_path.month == "2024-01"
assert vault_path.day == "2024-01-15"
assert vault_path.full_path == Path("/vault/documents/pdf/2024/2024-01/2024-01-15")
```

**Expected Output**:
```
✓ Classified as: documents/pdf (confidence: 0.95, method: libmagic)
✓ Date extracted: 2024-01-15 (source: filename_parsing, confidence: 0.7)
ℹ Parsed date from filename pattern: YYYY-MM-DD
✓ Target path: /vault/documents/pdf/2024/2024-01/2024-01-15
```

---

### Scenario 5: Batch Organization with Preview

**Given**: Multiple files to organize
```
Files:
  - /inbox/photo1.jpg
  - /inbox/photo2.CR2
  - /inbox/document.pdf
  - /inbox/video.mp4
```

**When**: Run preview mode
```python
file_paths = [
    Path("/inbox/photo1.jpg"),
    Path("/inbox/photo2.CR2"),
    Path("/inbox/document.pdf"),
    Path("/inbox/video.mp4")
]

preview = manager.preview_organization(
    file_paths=file_paths,
    metadata_dict={
        Path("/inbox/photo1.jpg"): {'mime_type': 'image/jpeg', ...},
        Path("/inbox/photo2.CR2"): {'mime_type': 'image/x-canon-cr2', ...},
        Path("/inbox/document.pdf"): {'mime_type': 'application/pdf', ...},
        Path("/inbox/video.mp4"): {'mime_type': 'video/mp4', ...}
    }
)
```

**Then**: Verify preview results
```python
assert len(preview) == 4
assert preview[Path("/inbox/photo1.jpg")].primary_category == "photos"
assert preview[Path("/inbox/photo2.CR2")].primary_category == "photos"
assert preview[Path("/inbox/photo2.CR2")].subcategory == "raw"
assert preview[Path("/inbox/document.pdf")].primary_category == "documents"
assert preview[Path("/inbox/video.mp4")].primary_category == "videos"

# Verify no directories were created
assert not Path("/vault/photos/2024").exists()
```

**Expected Output**:
```
Preview Mode - No changes will be made

✓ /inbox/photo1.jpg → /vault/photos/processed/2024/2024-01/2024-01-15
✓ /inbox/photo2.CR2 → /vault/photos/raw/2024/2024-01/2024-01-15
✓ /inbox/document.pdf → /vault/documents/pdf/2024/2024-01/2024-01-15
✓ /inbox/video.mp4 → /vault/videos/2024/2024-01/2024-01-15

Summary: 4 files analyzed, 0 errors, 0 warnings
```

---

### Scenario 6: Parallel Batch Organization

**Given**: Large batch of files (100+)
**When**: Run batch organization with parallel processing
```python
results = manager.organize_batch(
    file_paths=large_file_list,  # 100+ files
    metadata_dict=metadata_for_all_files,
    preview_only=False
)
```

**Then**: Verify thread-safe execution
```python
assert len(results) == len(large_file_list)
assert all(r['execution_status'] == 'success' for r in results.values())

# Verify all folders created without race conditions
for path, result in results.items():
    assert result['vault_path'].full_path.exists()
    assert result['vault_path'].full_path.is_dir()
```

**Expected Output**:
```
Organizing 100 files with 4 worker threads...

✓ 100/100 files organized successfully
✓ Created 15 new date folders
✓ 0 errors, 0 warnings
✓ Processing time: 3.2 seconds (31 files/sec)
```

---

### Scenario 7: Cross-Platform Path Validation

**Given**: Files with problematic names
```
Files:
  - /inbox/CON.jpg (Windows reserved name)
  - /inbox/file:with:colons.pdf (invalid on Windows)
  - /inbox/very_long_filename_that_exceeds_260_characters...jpg
```

**When**: Run organization with sanitization
```python
vault_path1 = manager.determine_path(
    Path("/inbox/CON.jpg"),
    {'mime_type': 'image/jpeg', ...}
)

vault_path2 = manager.determine_path(
    Path("/inbox/file:with:colons.pdf"),
    {'mime_type': 'application/pdf', ...}
)
```

**Then**: Verify sanitized paths
```python
# CON is reserved on Windows
assert "CON" not in str(vault_path1.full_path)

# Colons replaced with underscores
assert ":" not in str(vault_path2.full_path)

# Path length validated
assert len(str(vault_path2.full_path)) <= 260  # Windows limit
```

**Expected Output**:
```
⚠ Sanitized reserved filename: CON.jpg → CON_file.jpg
⚠ Sanitized invalid characters: file:with:colons.pdf → file_with_colons.pdf
✓ All paths validated for cross-platform compatibility
```

---

## Success Criteria

### Must Complete Successfully:
- [ ] Scenario 1: Photo with EXIF organized correctly
- [ ] Scenario 2: Document uses file creation time for date
- [ ] Scenario 3: Ambiguous video classified with fallback
- [ ] Scenario 4: Date parsed from filename when metadata missing
- [ ] Scenario 5: Preview mode shows decisions without executing
- [ ] Scenario 6: Batch processing with thread-safe folder creation
- [ ] Scenario 7: Cross-platform path sanitization works

### Performance Benchmarks:
- [ ] Single file organization: < 100ms
- [ ] Batch (100 files): < 5 seconds (>20 files/sec)
- [ ] Parallel processing: No race conditions or errors

### Quality Checks:
- [ ] All dates stored in UTC
- [ ] Folder dates match original local time (user-friendly)
- [ ] Classification confidence logged for audit
- [ ] Low confidence files flagged for review
- [ ] All paths cross-platform compatible

---

## Troubleshooting

### Issue: Date in wrong timezone
- **Check**: `DateInfo.timezone_info` field
- **Expected**: EXIF offset used, UTC for storage, local for folders

### Issue: Wrong classification
- **Check**: `Classification.reasoning` field
- **Expected**: Shows detection method and rule applied

### Issue: Path too long on Windows
- **Check**: Path length and `\\?\` prefix handling
- **Expected**: Paths > 260 chars use extended syntax

### Issue: Race condition in batch processing
- **Check**: Folder creation logs for conflicts
- **Expected**: `mkdir(exist_ok=True)` prevents errors

---

## Next Steps

After quickstart validation:
1. Review ambiguous files report
2. Adjust classification rules if needed
3. Run full vault organization with preview mode
4. Verify folder structure consistency
5. Execute actual organization
6. Validate audit logs

---

*Quickstart complete - Implementation validated with real-world scenarios*
