# Quickstart Test Scenarios: CLI Interface

**Feature**: #013 CLI Interface
**Date**: 2025-10-08
**Purpose**: Integration test scenarios that validate user stories

---

## Overview

This document contains executable integration test scenarios that validate the CLI Interface feature against the acceptance criteria from the feature spec. Each scenario follows the Given-When-Then pattern and can be automated.

---

## Test Scenario 1: Process Single File

**User Story**: Process a single image file through the complete pipeline

**Given**: A single JPEG image with EXIF metadata
**When**: User runs `vault process image.jpg`
**Then**: File is processed and moved to vault with proper organization

### Setup
```python
# Create test file
test_file = tmp_path / "photo.jpg"
create_test_image_with_exif(
    test_file,
    date="2024-01-15 14:30:00",
    camera="Canon EOS R5"
)

vault_root = tmp_path / "vault"
```

### Execute
```python
from src.cli.main import main
import sys

# Simulate command-line args
sys.argv = ['vault', 'process', str(test_file), '--vault-root', str(vault_root)]

# Run CLI
exit_code = main()
```

### Assert
```python
# Check exit code
assert exit_code == 0, "Should succeed"

# Check file was moved to vault
expected_path = vault_root / "photos" / "2024" / "2024-01" / "2024-01-15"
assert any(expected_path.glob("*.jpg")), "File should be in vault"
assert not test_file.exists(), "Original file should be moved"

# Check database record
db = DatabaseManager(vault_root / "vault.db")
records = db.query_files()
assert len(records) == 1, "Should have one database record"

# Check summary output
# Should print: "✓ Processed 1 file successfully"
```

---

## Test Scenario 2: Process Directory with Mixed Files

**User Story**: Process a folder of mixed media files

**Given**: A directory with photos, videos, and documents
**When**: User runs `vault process /media`
**Then**: All files are processed and organized by type

### Setup
```python
# Create test directory
media_dir = tmp_path / "media"
media_dir.mkdir()

# Create mixed files
files = {
    'photo.jpg': create_test_image,
    'video.mp4': create_test_video,
    'document.pdf': create_test_pdf,
    'receipt.png': create_test_image,
    'vacation.mov': create_test_video
}

for filename, creator in files.items():
    creator(media_dir / filename)

vault_root = tmp_path / "vault"
```

### Execute
```python
sys.argv = ['vault', 'process', str(media_dir), '--vault-root', str(vault_root), '--verbose']
exit_code = main()
```

### Assert
```python
# Check exit code
assert exit_code == 0

# Check files organized by type
photos = list((vault_root / "photos").rglob("*.jpg")) + list((vault_root / "photos").rglob("*.png"))
videos = list((vault_root / "videos").rglob("*.mp4")) + list((vault_root / "videos").rglob("*.mov"))
documents = list((vault_root / "documents").rglob("*.pdf"))

assert len(photos) == 2, "Should have 2 photos"
assert len(videos) == 2, "Should have 2 videos"
assert len(documents) == 1, "Should have 1 document"

# Check original directory is empty (files moved)
assert len(list(media_dir.iterdir())) == 0

# Check progress output
# Should show: "Progress: 100%"
# Should show: "✓ Processed 5 files successfully"
```

---

## Test Scenario 3: Handle Errors and Quarantine

**User Story**: Gracefully handle problematic files

**Given**: Mix of good and corrupted files
**When**: User runs processing command
**Then**: Good files processed, bad files quarantined, user informed

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()

# Create good files
create_test_image(source_dir / "good1.jpg")
create_test_image(source_dir / "good2.jpg")

# Create corrupted file
corrupted = source_dir / "corrupted.jpg"
corrupted.write_bytes(b"Not a real JPEG")

# Create unsupported file
unsupported = source_dir / "unknown.xyz"
unsupported.write_text("Unsupported format")

vault_root = tmp_path / "vault"
```

### Execute
```python
sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root)]
exit_code = main()
```

### Assert
```python
# Should complete with partial success
assert exit_code == 1, "Should indicate some failures"

# Check good files processed
photos = list((vault_root / "photos").rglob("*.jpg"))
assert len(photos) == 2, "Good files should be processed"

# Check bad files quarantined
quarantine_dir = vault_root / "quarantine"
assert quarantine_dir.exists(), "Quarantine directory should exist"

corrupted_files = list(quarantine_dir.rglob("corrupted.jpg"))
unsupported_files = list(quarantine_dir.rglob("unknown.xyz"))

assert len(corrupted_files) == 1, "Corrupted file should be quarantined"
assert len(unsupported_files) == 1, "Unsupported file should be quarantined"

# Check summary shows errors
# Should print: "✓ Processed 2 files successfully"
# Should print: "⚠ Quarantined 2 files"
# Should print: "See error report for details"
```

---

## Test Scenario 4: Interrupt Processing Gracefully

**User Story**: Handle Ctrl+C interruption safely

**Given**: Processing a large batch of files
**When**: User presses Ctrl+C during processing
**Then**: Current file finishes, state saved, summary printed

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()

# Create 50 test files
for i in range(50):
    create_test_image(source_dir / f"photo_{i:03d}.jpg")

vault_root = tmp_path / "vault"
```

### Execute
```python
import signal
import threading

# Start processing in thread
def run_processing():
    sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root)]
    return main()

# Interrupt after 2 seconds (should process ~10 files)
def send_interrupt():
    time.sleep(2)
    os.kill(os.getpid(), signal.SIGINT)

interrupt_thread = threading.Thread(target=send_interrupt)
interrupt_thread.start()

exit_code = run_processing()
interrupt_thread.join()
```

### Assert
```python
# Should exit with interrupt code
assert exit_code == 130, "Should indicate interruption"

# Check some files were processed
processed = list((vault_root / "photos").rglob("*.jpg"))
assert len(processed) > 0, "Some files should be processed"
assert len(processed) < 50, "Not all files should be processed"

# Check source still has unprocessed files
remaining = list(source_dir.glob("*.jpg"))
assert len(remaining) > 0, "Some files should remain"

# Check summary printed
# Should print: "Interrupted. Cleaning up..."
# Should print: "✓ Processed {N} of 50 files before interruption"
```

---

## Test Scenario 5: Dry-Run Mode (Preview)

**User Story**: Preview processing without making changes

**Given**: Directory with files to process
**When**: User runs with `--dry-run` flag
**Then**: Full simulation runs, no files modified, report shows what would happen

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()

for i in range(5):
    create_test_image(source_dir / f"photo_{i}.jpg")

vault_root = tmp_path / "vault"
```

### Execute
```python
sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root), '--dry-run']
exit_code = main()
```

### Assert
```python
# Should succeed
assert exit_code == 0

# Check NO files were moved
assert len(list(source_dir.glob("*.jpg"))) == 5, "All files should remain"
assert not (vault_root / "photos").exists(), "Vault should not be created"

# Check database not modified
assert not (vault_root / "vault.db").exists(), "Database should not be created"

# Check preview output
# Should print: "DRY RUN - No files will be modified"
# Should print: "Would process 5 files"
# Should print: "Estimated duration: ~1.0s"
# Should print: "Estimated space needed: ~2.5 MB"
```

---

## Test Scenario 6: Duplicate Detection

**User Story**: Detect and handle duplicate files

**Given**: Same file in multiple locations
**When**: User processes both
**Then**: First file goes to vault, second detected as duplicate

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()

# Create original file
original = source_dir / "original.jpg"
create_test_image(original)

# Create duplicate (same content)
duplicate_dir = tmp_path / "duplicates_source"
duplicate_dir.mkdir()
duplicate = duplicate_dir / "copy.jpg"
shutil.copy(original, duplicate)

vault_root = tmp_path / "vault"
```

### Execute
```python
# Process original first
sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root)]
exit_code1 = main()

# Process duplicate
sys.argv = ['vault', 'process', str(duplicate_dir), '--vault-root', str(vault_root)]
exit_code2 = main()
```

### Assert
```python
# Both should succeed
assert exit_code1 == 0
assert exit_code2 == 0

# Check vault has only one file
vault_files = list((vault_root / "photos").rglob("*.jpg"))
assert len(vault_files) == 1, "Should have only one file in vault"

# Check duplicate is in duplicates folder
duplicates = list((vault_root / "duplicates").rglob("*.jpg"))
assert len(duplicates) == 1, "Should have one duplicate"

# Check summary for second run
# Should print: "⊕ Detected 1 duplicate file"
# Should print: "See: vault/duplicates/..."
```

---

## Test Scenario 7: Status Command

**User Story**: Check vault status

**Given**: Processed vault with some files
**When**: User runs `vault status`
**Then**: Statistics and health report displayed

### Setup
```python
# Process some files first
source_dir = tmp_path / "source"
source_dir.mkdir()

for i in range(10):
    create_test_image(source_dir / f"photo_{i}.jpg")

vault_root = tmp_path / "vault"

sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root)]
main()
```

### Execute
```python
sys.argv = ['vault', 'status', '--vault-root', str(vault_root)]
exit_code = main()
```

### Assert
```python
# Should succeed
assert exit_code == 0

# Check output contains statistics
# Should print: "Vault Statistics:"
# Should print: "Total files: 10"
# Should print: "Photos: 10"
# Should print: "Videos: 0"
# Should print: "Documents: 0"
# Should print: "Quarantined: 0"
# Should print: "✓ Vault is healthy"
```

---

## Test Scenario 8: Recover Quarantined Files

**User Story**: Reprocess quarantined files after fixing issues

**Given**: Some files in quarantine
**When**: User runs `vault recover`
**Then**: Files reprocessed, successful ones moved to vault

### Setup
```python
vault_root = tmp_path / "vault"
quarantine_dir = vault_root / "quarantine" / "corruption_detected"
quarantine_dir.mkdir(parents=True)

# Create "fixed" file in quarantine
fixed_file = quarantine_dir / "fixed.jpg"
create_test_image(fixed_file)

# Create still-broken file
broken_file = quarantine_dir / "still_broken.jpg"
broken_file.write_bytes(b"Still corrupted")
```

### Execute
```python
sys.argv = ['vault', 'recover', '--vault-root', str(vault_root), '--quarantine-type', 'corruption_detected']
exit_code = main()
```

### Assert
```python
# Should complete with partial success
assert exit_code == 1, "Should indicate some files still quarantined"

# Check fixed file moved to vault
vault_files = list((vault_root / "photos").rglob("fixed.jpg"))
assert len(vault_files) == 1, "Fixed file should be in vault"

# Check broken file still quarantined
remaining_quarantine = list(quarantine_dir.glob("still_broken.jpg"))
assert len(remaining_quarantine) == 1, "Broken file should remain quarantined"

# Check summary
# Should print: "Recovery Results:"
# Should print: "✓ Recovered: 1"
# Should print: "✗ Still quarantined: 1"
```

---

## Test Scenario 9: Verbose Output

**User Story**: See detailed processing information

**Given**: Files to process
**When**: User runs with `--verbose` flag
**Then**: Detailed progress and metadata shown

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()
create_test_image(source_dir / "photo.jpg")

vault_root = tmp_path / "vault"
```

### Execute
```python
sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root), '--verbose']

# Capture output
import io
import sys
captured_output = io.StringIO()
sys.stdout = captured_output

exit_code = main()

sys.stdout = sys.__stdout__
output = captured_output.getvalue()
```

### Assert
```python
assert exit_code == 0

# Check detailed output present
assert "Stage: discovering" in output
assert "Stage: ingesting" in output
assert "Stage: extracting" in output
assert "Stage: consolidating" in output
assert "Stage: organizing" in output
assert "Stage: moving" in output

# Should show metadata
assert "Camera:" in output or "Metadata:" in output

# Should show destination path
assert "Destination:" in output
```

---

## Test Scenario 10: Quiet Mode

**User Story**: Suppress output except errors

**Given**: Files to process
**When**: User runs with `--quiet` flag
**Then**: Only errors printed

### Setup
```python
source_dir = tmp_path / "source"
source_dir.mkdir()
create_test_image(source_dir / "good.jpg")

# Add corrupted file to trigger error
corrupted = source_dir / "bad.jpg"
corrupted.write_bytes(b"corrupted")

vault_root = tmp_path / "vault"
```

### Execute
```python
sys.argv = ['vault', 'process', str(source_dir), '--vault-root', str(vault_root), '--quiet']

captured_output = io.StringIO()
sys.stdout = captured_output

exit_code = main()

sys.stdout = sys.__stdout__
output = captured_output.getvalue()
```

### Assert
```python
assert exit_code == 1, "Should indicate errors"

# Output should be minimal - only errors
assert "✓" not in output, "Should not show success messages"
assert "Progress:" not in output, "Should not show progress"

# Should show errors
assert "Error:" in output or "✗" in output
assert "bad.jpg" in output
```

---

## Running Tests

### Manual Testing
```bash
# Run all quickstart scenarios
pytest specs/013-cli-interface/quickstart.md --markdown

# Run specific scenario
pytest specs/013-cli-interface/quickstart.md::test_scenario_1
```

### Automated Testing
```python
# Integration test suite
pytest tests/integration/test_cli_interface.py -v

# With coverage
pytest tests/integration/test_cli_interface.py --cov=src.cli
```

---

## Success Criteria

All scenarios must pass for feature to be considered complete:

- [x] Scenario 1: Single file processing
- [x] Scenario 2: Directory processing
- [x] Scenario 3: Error handling and quarantine
- [x] Scenario 4: Graceful interruption
- [x] Scenario 5: Dry-run mode
- [x] Scenario 6: Duplicate detection
- [x] Scenario 7: Status command
- [x] Scenario 8: Recovery command
- [x] Scenario 9: Verbose output
- [x] Scenario 10: Quiet mode

---

**Status**: ✅ All scenarios defined
**Next Step**: Implement CLI and run scenarios to validate
