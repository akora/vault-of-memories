# Research Findings: Organization Manager

**Research Date**: 2025-10-08
**Feature**: 010-organization-manager
**Purpose**: Technical decisions for cross-platform vault organization

---

## 1. Cross-Platform Filesystem Compatibility

### Decision: Path Length Handling
**Chosen**: Use `pathlib` with conditional `\\?\` prefix for Windows long paths (>260 chars)

**Rationale**:
- Windows MAX_PATH limit of 260 characters affects vault hierarchies
- Date-based folders (YYYY/YYYY-MM/YYYY-MM-DD) plus metadata-rich filenames easily exceed limit
- Python's pathlib can handle long paths using `\\?\` prefix on Windows
- Proactive validation prevents user confusion

**Implementation**:
```python
from pathlib import Path
import platform

def create_long_path_safe(path_str: str) -> Path:
    path = Path(path_str).resolve()
    if platform.system() == 'Windows' and len(str(path)) > 260:
        if not str(path).startswith('\\\\?\\'):
            path = Path(f'\\\\?\\{path}')
    return path
```

**Alternatives Considered**:
- Require registry modification: Rejected (too invasive, requires admin)
- Shorten filenames: Rejected (defeats metadata-rich naming)
- Flat structure: Rejected (poor organization for large collections)

---

### Decision: Reserved Filename Handling
**Chosen**: Use `pathvalidate` library for universal filename validation

**Rationale**:
- Windows reserves: CON, PRN, AUX, NUL, COM1-9, LPT1-9 (case-insensitive)
- Library handles all platform-specific reserved names automatically
- "Universal" mode ensures filenames work across all platforms
- Actively maintained, no external dependencies

**Implementation**:
```python
from pathvalidate import sanitize_filename

def validate_filename(filename: str) -> str:
    return sanitize_filename(
        filename,
        platform='universal',
        replacement_text='_'
    )
```

**Alternatives Considered**:
- Custom regex: Rejected (error-prone, doesn't cover all edge cases)
- Platform-specific: Rejected (vault not portable across systems)

---

### Decision: Special Character Handling
**Chosen**: Use `pathvalidate.sanitize_filename()` with universal mode, replace invalid chars with underscores

**Rationale**:
- Different platforms have different invalid character sets
- Universal mode ensures maximum compatibility
- Underscore replacement maintains readability
- Preserves as much original metadata as possible

**Platform-Specific Invalid Characters**:
- Windows: `\ / : * ? " < > |` + control chars (0-31)
- Unix/Linux: `/` + null
- macOS: `/` and `:` (HFS+ legacy)

**Alternatives Considered**:
- Remove characters: Rejected (loses information, creates collisions)
- URL encoding: Rejected (unreadable filenames)
- Allow platform-native: Rejected (vault not portable)

---

### Decision: Case Sensitivity Handling
**Chosen**: Case-insensitive duplicate detection using normalized lowercase comparison, preserve original casing

**Rationale**:
- Windows/macOS: Case-insensitive by default
- Linux: Case-sensitive
- Duplicate detection must work consistently across platforms
- Preserving case maintains metadata fidelity

**Implementation**:
```python
def paths_equal(path1: Path, path2: Path) -> bool:
    return str(path1.resolve()).lower() == str(path2.resolve()).lower()
```

**Alternatives Considered**:
- Platform-native behavior: Rejected (inconsistent vault behavior)
- Force lowercase: Rejected (loses metadata and readability)
- Case-sensitive only: Rejected (creates duplicates when vault is moved)

---

## 2. Atomic Folder Creation Patterns

### Decision: Race Condition Prevention
**Chosen**: Use `Path.mkdir(parents=True, exist_ok=True)` without explicit locking for create-only operations

**Rationale**:
- `exist_ok=True` prevents errors when multiple threads create same directory
- Vault organization is create-only (no deletion during processing)
- Python 3.6+ has resolved critical race conditions in pathlib.mkdir()
- Thread-local locks available for critical sections if needed

**Implementation**:
```python
def create_directory_atomic(path: Path, mode: int = 0o755) -> bool:
    abs_path = path.resolve()
    abs_path.mkdir(parents=True, exist_ok=True, mode=mode)
    if not abs_path.is_dir():
        raise OSError(f"Path exists but is not a directory: {abs_path}")
    return True
```

**Alternatives Considered**:
- Global file locks: Rejected (too slow, creates contention)
- Check-then-create: Rejected (classic race condition)
- Process-level locking: Rejected (single application instance)

---

### Decision: Permission Handling
**Chosen**: Use `mode=0o755` as default on Unix, accept Windows defaults, avoid umask manipulation

**Rationale**:
- Windows ignores Unix mode, uses NTFS ACLs
- Manipulating umask is not thread-safe (affects entire process)
- Most users have standard umask (0o022) producing sensible defaults
- `0o755` (rwxr-xr-x) is standard for shared directories

**Permission Modes**:
- Standard vault: `0o755` (rwxr-xr-x)
- Private vault: `0o700` (rwx------)
- Windows: Inherits from parent (NTFS ACLs)

**Alternatives Considered**:
- Temporarily set umask to 0: Rejected (not thread-safe, security issue)
- Platform-specific handling: Rejected (unnecessary complexity)

---

## 3. Content Classification Strategies

### Decision: Hierarchical Classification System
**Chosen**: Primary categories (photos, documents, videos, audio, archives) with metadata-based subcategories

**Rationale**:
- Industry-standard DAM systems use hierarchical taxonomy
- Content-based classification more meaningful than format-based
- Configurable rules allow customization without code changes
- Aligns with user mental models

**Primary Categories**:
- PHOTOS: images, screenshots, raw photos
- DOCUMENTS: PDFs, office files, text files
- VIDEOS: movies, family videos, professional footage
- AUDIO: music, podcasts, recordings
- ARCHIVES: zips, tars, compressed files
- OTHER: fallback for unclassifiable files

**Classification Priority**:
1. MIME type detection (most reliable)
2. File extension (fallback)
3. Content inspection (file headers)
4. Default to OTHER category

**Alternatives Considered**:
- Flat categories: Rejected (doesn't scale)
- Format-based: Rejected (less meaningful than content-based)
- AI classification: Rejected (unnecessary complexity)

---

### Decision: Fallback Strategy for Ambiguous Files
**Chosen**: Multi-level fallback: MIME → extension → header inspection → default

**Rationale**:
- MIME detection (libmagic) most reliable but can fail
- Extension provides fallback when MIME fails
- Header inspection catches disguised files
- Default prevents processing failures
- Audit logging helps improve rules

**Implementation**:
- Level 1: libmagic MIME detection (confidence: 0.95)
- Level 2: Extension-based MIME (confidence: 0.7)
- Level 3: File header inspection (confidence: 0.8)
- Level 4: Default fallback (confidence: 0.0)

**Alternatives Considered**:
- Fail on ambiguous: Rejected (too strict for batch processing)
- Trust extension only: Rejected (unreliable)
- Prompt user: Rejected (doesn't scale)

---

### Decision: Priority Rules for Multiple Categories
**Chosen**: Explicit priority: Raw > Source > Processed > Derivative > Compressed

**Rationale**:
- Some files fit multiple categories legitimately
- Content fidelity (raw/original) more valuable for preservation
- Priority ensures consistent classification
- Quality indicators help classify professional vs casual

**Priority Levels**:
- RAW_MEDIA (100): RAW photos, lossless audio
- SOURCE (80): Original files
- PROCESSED (60): Edited versions
- DERIVATIVE (40): Generated from others
- COMPRESSED (20): Heavily compressed
- UNKNOWN (0): Unclassified

**Alternatives Considered**:
- First-match wins: Rejected (inconsistent results)
- User prompt: Rejected (doesn't scale)
- Always primary only: Rejected (loses subcategory info)

---

## 4. Date Extraction Strategies

### Decision: Prioritized Date Source Cascade
**Chosen**: EXIF DateTimeOriginal → File creation → Modification → Filename parsing → Current time

**Rationale**:
- EXIF DateTimeOriginal most accurate for photos/videos
- File creation time reliable when EXIF unavailable
- Modification time changes with edits (last resort)
- Filename parsing useful for user-organized files
- Logging source enables verification

**Date Source Priority**:

| Priority | Source | Reliability | Use Case |
|----------|--------|-------------|----------|
| 1 | EXIF DateTimeOriginal | High | When photo taken |
| 2 | File creation time | Medium | When file created |
| 3 | File modification | Low | Last edit time |
| 4 | Filename parsing | Variable | User-organized |
| 5 | Current time | Fallback | Last resort |

**Alternatives Considered**:
- EXIF only: Rejected (fails for non-photos)
- Modification first: Rejected (changes with edits)
- Filename only: Rejected (not always present)
- Fail on missing: Rejected (too strict)

---

### Decision: Filename Date Parsing
**Chosen**: Support multiple formats with precedence: ISO 8601 (YYYY-MM-DD) > compact (YYYYMMDD) > ambiguous with logging

**Rationale**:
- ISO 8601 is unambiguous international standard
- YYYYMMDD common in technical contexts
- DD-MM-YYYY vs MM-DD-YYYY ambiguous (prefer European, log warning)
- Multiple formats maximize successful extraction

**Supported Formats** (priority order):
1. ISO 8601: YYYY-MM-DD (unambiguous)
2. Compact ISO: YYYYMMDD (unambiguous)
3. ISO with time: YYYY-MM-DD_HH-MM-SS
4. European: DD-MM-YYYY (ambiguous warning)
5. US: MM/DD/YYYY (ambiguous warning)
6. Underscore: YYYY_MM_DD
7. Dot: YYYY.MM.DD

**Alternatives Considered**:
- ISO only: Rejected (too restrictive)
- Assume US format: Rejected (not international)
- ML extraction: Rejected (overkill)

---

### Decision: Timezone Handling
**Chosen**: Store in UTC, extract from EXIF OffsetTimeOriginal when available, use EXIF/local date for folders

**Rationale**:
- UTC storage eliminates conversion errors
- EXIF OffsetTimeOriginal available in modern cameras (2016+)
- Legacy files lack timezone (assume UTC)
- Folder date uses original local time (user-friendly)
- Audit logging enables verification

**Implementation**:
- Store all dates in UTC internally
- Extract timezone from EXIF when available
- Use original local date for folder organization
- Log timezone source for auditability

**Folder Date Strategy**:
- Use EXIF/local date (user mental model: "photos from Dec 25")
- Even though stored as UTC, organize by original date
- Prevents confusion from timezone conversions

**Alternatives Considered**:
- Store in local timezone: Rejected (which timezone?)
- Ignore timezones: Rejected (date boundary issues)
- Always UTC folders: Rejected (user-unfriendly)
- Detect from GPS: Rejected (complex, not always available)

---

## Summary

### Key Technical Decisions

1. **Dependencies**:
   - `pathvalidate` (v3.3.1+): Filename validation
   - `python-magic`: MIME detection
   - Python standard library: pathlib, datetime, threading

2. **Cross-Platform Strategy**:
   - Universal filename validation
   - Long path support for Windows
   - Case-insensitive duplicate detection
   - Platform-appropriate permissions

3. **Classification Approach**:
   - Hierarchical taxonomy
   - Multi-level fallback
   - Priority-based rules
   - Audit logging

4. **Date Handling**:
   - EXIF-first cascade
   - UTC storage
   - Local date for folders
   - Timezone awareness

All decisions align with constitutional principles: **Simplicity First**, **Dependency Minimalism**, **Industry Standards Adherence**.

---
*Research complete - Ready for Phase 1 (Design & Contracts)*
