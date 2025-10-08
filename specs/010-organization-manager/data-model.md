# Data Model: Organization Manager

**Feature**: 010-organization-manager
**Created**: 2025-10-08
**Source**: Derived from feature specification and research findings

---

## Core Entities

### 1. VaultPath
**Purpose**: Represents the complete target path for organizing a file in the vault

**Fields**:
- `base_path`: Path - Vault root directory
- `primary_category`: str - Main content category (photos, documents, videos, audio, archives, other)
- `subcategory`: Optional[str] - Content subcategory (raw, processed, family, office, etc.)
- `year`: str - Four-digit year (YYYY)
- `month`: str - Year-month (YYYY-MM)
- `day`: str - Full date (YYYY-MM-DD)
- `full_path`: Path - Complete resolved path

**Relationships**:
- Constructed from Classification and DateInfo
- Used by FolderCreator to create directory structure

**Validation Rules**:
- `primary_category` must be one of: photos, documents, videos, audio, archives, other
- `subcategory` is optional, validated against category-specific allowed values
- Date components must form valid date (year: 1900-2100, month: 01-12, day: 01-31)
- `full_path` must be platform-safe (validated by filename sanitizer)
- Windows path length must not exceed 260 chars without extended prefix

**Example**:
```python
VaultPath(
    base_path=Path("/vault"),
    primary_category="photos",
    subcategory="family",
    year="2024",
    month="2024-01",
    day="2024-01-15",
    full_path=Path("/vault/photos/family/2024/2024-01/2024-01-15")
)
```

---

### 2. Classification
**Purpose**: Result of content classification determining file category and subcategory

**Fields**:
- `primary_category`: str - Main content category
- `subcategory`: Optional[str] - Content subcategory
- `confidence`: float - Classification confidence (0.0-1.0)
- `reasoning`: str - Explanation of classification decision
- `mime_type`: str - Detected MIME type
- `detection_method`: str - How MIME was detected (libmagic, extension, header, fallback)

**Relationships**:
- Created by ClassificationEngine
- Used to construct VaultPath

**Validation Rules**:
- `confidence` must be between 0.0 and 1.0
- `primary_category` must be valid category enum value
- `detection_method` must be: libmagic, extension, header_inspection, fallback

**State Transitions**:
- Initial: Created with low confidence, fallback detection
- Refined: Updated with higher confidence when better detection method succeeds
- Finalized: Locked after manual review or high-confidence automatic classification

**Example**:
```python
Classification(
    primary_category="photos",
    subcategory="raw",
    confidence=0.95,
    reasoning="MIME: image/x-canon-cr2 → photos → raw",
    mime_type="image/x-canon-cr2",
    detection_method="libmagic"
)
```

---

### 3. DateInfo
**Purpose**: Extracted date information with source and timezone details

**Fields**:
- `datetime_utc`: datetime - Date/time in UTC
- `source`: str - Where date was extracted from
- `timezone_info`: Optional[str] - Original timezone information
- `original_local_date`: date - Date in original timezone (for folder organization)
- `confidence`: float - Confidence in date accuracy (0.0-1.0)

**Relationships**:
- Created by DateExtractor
- Used to construct VaultPath date hierarchy

**Validation Rules**:
- `datetime_utc` must have UTC timezone
- `source` must be: exif_datetime_original, file_creation_time, file_modification_time, filename_parsing, fallback_current_time
- `original_local_date` used for folder names, `datetime_utc` for storage/sorting
- `confidence` reflects reliability: exif (0.95), creation (0.8), modification (0.6), filename (0.7), fallback (0.0)

**Example**:
```python
DateInfo(
    datetime_utc=datetime(2024, 1, 15, 9, 30, 22, tzinfo=timezone.utc),
    source="exif_datetime_original",
    timezone_info="offset_+05:30",
    original_local_date=date(2024, 1, 15),
    confidence=0.95
)
```

---

### 4. OrganizationDecision
**Purpose**: Complete record of file organization decision with full audit trail

**Fields**:
- `file_path`: Path - Source file path
- `vault_path`: VaultPath - Target organization path
- `classification`: Classification - Content classification result
- `date_info`: DateInfo - Date extraction result
- `decision_timestamp`: datetime - When decision was made
- `preview_mode`: bool - Whether this is preview-only (not executed)
- `execution_status`: str - Status: pending, success, failed
- `error_message`: Optional[str] - Error details if failed

**Relationships**:
- Aggregates Classification, DateInfo, and VaultPath
- Created by OrganizationManager
- Logged to OrganizationAuditLog

**Validation Rules**:
- `execution_status` must be: pending, success, failed
- `error_message` required when status is failed
- `preview_mode` cannot have status other than pending

**State Transitions**:
- `pending` → `success`: Successfully organized file
- `pending` → `failed`: Error during organization
- Preview mode stays in `pending` (not executed)

**Example**:
```python
OrganizationDecision(
    file_path=Path("/inbox/IMG_2024.CR2"),
    vault_path=VaultPath(...),
    classification=Classification(...),
    date_info=DateInfo(...),
    decision_timestamp=datetime.now(timezone.utc),
    preview_mode=False,
    execution_status="success",
    error_message=None
)
```

---

### 5. ClassificationRule
**Purpose**: Configurable rule for determining file category/subcategory

**Fields**:
- `name`: str - Rule identifier
- `priority`: int - Rule priority (higher = higher priority)
- `primary_category`: str - Category this rule assigns
- `subcategory`: Optional[str] - Subcategory this rule assigns
- `mime_patterns`: List[str] - MIME type patterns to match
- `extension_patterns`: List[str] - File extension patterns to match
- `metadata_conditions`: Dict[str, Any] - Additional metadata conditions
- `description`: str - Human-readable rule explanation

**Relationships**:
- Loaded from configuration
- Used by ClassificationEngine to classify files

**Validation Rules**:
- `priority` must be positive integer
- Either `mime_patterns` or `extension_patterns` must be non-empty
- Patterns support wildcards (* and ?)

**Example**:
```python
ClassificationRule(
    name="raw_photo",
    priority=100,
    primary_category="photos",
    subcategory="raw",
    mime_patterns=["image/x-canon-cr2", "image/x-nikon-nef", "image/x-*-raw"],
    extension_patterns=[".cr2", ".nef", ".arw", ".dng"],
    metadata_conditions={},
    description="RAW camera files have highest priority"
)
```

---

### 6. FolderStructure
**Purpose**: Definition of vault organization hierarchy and naming rules

**Fields**:
- `vault_root`: Path - Base vault directory
- `category_folders`: Dict[str, str] - Category to folder name mapping
- `date_hierarchy_format`: str - Format for date folders (YYYY/YYYY-MM/YYYY-MM-DD)
- `max_path_length`: int - Maximum path length (260 for Windows)
- `use_subcategories`: bool - Whether to include subcategory folders
- `folder_permissions`: int - Unix permission mode (e.g., 0o755)

**Relationships**:
- Loaded from configuration
- Used by DateHierarchyBuilder and FolderCreator

**Validation Rules**:
- `vault_root` must exist and be writable
- `max_path_length` typically 260 (Windows) or 4096 (Unix)
- `folder_permissions` must be valid Unix mode (0o000-0o777)

**Example**:
```python
FolderStructure(
    vault_root=Path("/vault"),
    category_folders={
        "photos": "photos",
        "documents": "documents",
        "videos": "videos",
        "audio": "audio",
        "archives": "archives",
        "other": "other"
    },
    date_hierarchy_format="YYYY/YYYY-MM/YYYY-MM-DD",
    max_path_length=260,
    use_subcategories=True,
    folder_permissions=0o755
)
```

---

### 7. CreationResult
**Purpose**: Result of folder creation operation

**Fields**:
- `path`: Path - Directory that was created/verified
- `created_new`: bool - True if directory was newly created
- `already_existed`: bool - True if directory already existed
- `permissions_set`: int - Actual permissions set (Unix)
- `timestamp`: datetime - When operation completed
- `error`: Optional[str] - Error message if operation failed

**Relationships**:
- Returned by FolderCreator.create_hierarchy()
- Logged for audit trail

**Validation Rules**:
- Either `created_new` or `already_existed` must be True (unless error)
- `error` is None for successful operations

**Example**:
```python
CreationResult(
    path=Path("/vault/photos/family/2024/2024-01/2024-01-15"),
    created_new=False,
    already_existed=True,
    permissions_set=0o755,
    timestamp=datetime.now(timezone.utc),
    error=None
)
```

---

## Enumerations

### PrimaryCategory
```python
class PrimaryCategory(Enum):
    PHOTOS = "photos"
    DOCUMENTS = "documents"
    VIDEOS = "videos"
    AUDIO = "audio"
    ARCHIVES = "archives"
    OTHER = "other"
```

### DateSource
```python
class DateSource(Enum):
    EXIF_DATETIME_ORIGINAL = "exif_datetime_original"
    FILE_CREATION_TIME = "file_creation_time"
    FILE_MODIFICATION_TIME = "file_modification_time"
    FILENAME_PARSING = "filename_parsing"
    FALLBACK_CURRENT_TIME = "fallback_current_time"
```

### ExecutionStatus
```python
class ExecutionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
```

### DetectionMethod
```python
class DetectionMethod(Enum):
    LIBMAGIC = "libmagic"
    EXTENSION = "extension"
    HEADER_INSPECTION = "header_inspection"
    FALLBACK = "fallback"
```

---

## Entity Relationships

```
OrganizationDecision
├── file_path: Path
├── vault_path: VaultPath
│   ├── primary_category: str
│   ├── subcategory: Optional[str]
│   ├── year/month/day: str
│   └── full_path: Path
├── classification: Classification
│   ├── primary_category: str
│   ├── subcategory: Optional[str]
│   ├── confidence: float
│   ├── mime_type: str
│   └── detection_method: str
└── date_info: DateInfo
    ├── datetime_utc: datetime
    ├── source: str
    ├── timezone_info: Optional[str]
    └── original_local_date: date

FolderStructure
├── vault_root: Path
├── category_folders: Dict[str, str]
├── date_hierarchy_format: str
└── folder_permissions: int

ClassificationRule
├── name: str
├── priority: int
├── primary_category: str
├── mime_patterns: List[str]
└── extension_patterns: List[str]
```

---

## Data Flow

1. **Input**: File path + metadata (from MetadataConsolidator)
2. **Classification**: ClassificationEngine applies ClassificationRules → Classification
3. **Date Extraction**: DateExtractor extracts date from multiple sources → DateInfo
4. **Path Construction**: VaultPath builder combines Classification + DateInfo + FolderStructure → VaultPath
5. **Folder Creation**: FolderCreator creates directory hierarchy → CreationResult
6. **Decision Recording**: OrganizationDecision aggregates all results
7. **Audit Logging**: Decision logged to OrganizationAuditLog

---

## Validation Rules Summary

1. **Path Safety**:
   - All paths validated for cross-platform compatibility
   - Reserved filenames detected and sanitized
   - Path length checked against platform limits

2. **Date Validity**:
   - Year: 1900-2100
   - Month: 01-12
   - Day: 01-31 (validated for specific month/year)
   - All dates stored in UTC with timezone awareness

3. **Classification Confidence**:
   - Values between 0.0-1.0
   - Low confidence (<0.5) flags for review
   - Method-specific confidence thresholds

4. **Category Consistency**:
   - Primary category must be valid enum
   - Subcategory must be valid for primary category
   - Fallback to OTHER for unclassifiable files

---

*Data model complete - Ready for contract definitions*
