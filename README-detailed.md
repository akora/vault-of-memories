# Vault of Digital Memories

Me:

> *Hey, my dear AI assistant!\
>\
> I'm planning to build a digital vault. The purpose of this project is to collect and package all digital memories, photos, videos, digitised documents into a digital vault so that my family can inherit it later in life. Please suggest methods, technologies, equipment that should be used. Also suggest digital formats that stand the test of time.*

AI:

> *Building a digital vault for preserving digital memories, photos, videos, and digitized documents is a thoughtful and lasting gift. Here are some methods, technologies, equipment, and digital formats that can help you ensure the longevity and accessibility of your digital vault: ...*

:)

Not so fast! Let's pause for a moment.

The REAL goal of this project is to build a `pre-processor` for the digital vault.

## What's a pre-processor, and why do we need one?

To be able to build a succesful digital vault, we need to ensure that the digital assets stored in the vault stand the test of time. Various DAM (Digital Asset Management) systems will come and go, instead of focusing on those, let's focus on the source.

*Always focus on the source!*

Similarly to some of the core Unix design principles and [philosophy](https://en.wikipedia.org/wiki/Unix_philosophy), like "[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)", or "make each program do one thing well", longevity can only be strengthened by focusing on the most basic formats:

- plain text (markdown is also fine)
- most popular and widespread image formats (JPEG, PNG, GIF, WebP)
- most popular and widespread video formats (MP4, WebM)
- most popular and widespread audio formats (MP3, FLAC)
- most popular and widespread document formats (PDF, DOCX, ODT)
- most popular and widespread archive formats (ZIP, TAR, 7Z)
- ...

The list goes on.

Will these formats be around in 100 years? I cannot tell.

Pre-processing is required to ensure that BEFORE a digital vault is built "inside" a DAM system, all digital assets are kept organized in the most basic formats. This also ensures portability (any DAM system can import these formats).

This is the goal of this project:

To

- collect
- organize
- deduplicate
- enrich (with metadata)
- rename
- package

digital files into a vault that can be easily imported into ANY DAM system.

As an end result, we will have a digital vault that's organized (based on time), deduplicated, all files renamed to have human-readable, understandable names, enriched with metadata, and ready to be imported into ANY DAM system.

---

## Acceptable Input

Files/content types to be accepted for processing:

- documents
  - plain text (or markdown)
    - notes
  - RTF
  - DOC / DOCX
  - ODT
  - Pages (macOS)
  - scanned
    - PDF
    - as image
    - scanned-content (OCR extracted content of scanned documents with matching file name of the original file but with .txt or .md file extension)
  - bookmarks (exported bookmarks from web browsers in HTML format)
  - mindmaps
  - brochures (PDFs with a length of maximum 5 pages)
  - presentations
  - spreadsheets
- ebooks (PDFs or other ebook formats longer than 5 pages)
- fonts
- audio files
- images (NOT photos)
  - screenshots
  - icons
  - SVG files
  - other images
- photos
  - raw (NEF, ARW, etc.)
  - processed (JPG)
- videos
  - family videos
  - downloaded
    - music videos
    - tutorials
    - work related
    - tech
    - YT other

Hidden and system files (e.g. `.DS_Store`, `Thumbs.db`) should be ignored and removed from the input folder during clean-up.

## System Components

The processing pipeline should be built based on the following requirements:

Processing pipeline with distinct, interchangeable modules. Allowing to easily add new file types without rewriting the entire system.

1. **Ingestion & Duplicate Check Module:** This is the entry point. It receives files and performs a checksum-based duplicate check against both the existing vault and the current batch. This module doesn't care about the file type; it just needs the file content to generate the hash.
2. **File Type Analyzer Module:** This module reads the file's content (e.g., magic numbers) to definitively identify its type. Based on this, it routes the file to the appropriate specialized processing module.
3. **Specialized Processing Modules:** Create a separate module for each file type. For example:
    - **Text File Processor:** Extracts text and basic metadata.
    - **Image File Processor:** Extracts EXIF data (date, time, camera model) from images.
    - **Audio File Processor:** Extracts ID3 tags (artist, album, date) from audio files.
    - **Video File Processor:** Extracts creation date and other metadata from video files.
4. **Renaming & Organization Module:** This module takes the file and the extracted metadata, applies a standardized naming convention, and determines the final destination folder based on your organizational rules.
5. **Finalization Module:** This module performs the final copy to the vault and removes the original from the input folder.
6. **Error Handling & Reporting Module:** This is a crucial, overarching module that monitors every step. If any module fails, it logs the error, moves the file to a quarantine folder, and sends an alert.

## Processing Requirements

No need to supports parallel processing, batch processing is acceptable.
The processing can be triggered manually, by running a script, no need to continuously watch a folder for changes.

The goal of the output filenames is to produce

- unique file names (no possible collision across the entire digital vault)
- human readable file names (using dashes between values to make it more readable)
- metadata rich file names (containing meaningful values, e.g. the size of the image in pixels, the length of a video file in minutes and seconds, the number of pages of a PDF file)
- original creation date and original creation time sortable file names

General rules for output file names:

- no spaces: each space must be replaced with a dash "-"
- multiple consecutive spaces must be replaced with a single dash "-"
- each section of the file name must be separated by a dash "-"
- the file extensions must always be all lowercase
- the file extensions must always be normalized (e.g. either all ".jpg" or all ".jpeg")
- where a counter is used (e.g. for the shutter count value extracted from cameras) always use padding, either up to 6 digits or to 8 digits

Metadata to be used in file names:

- d: original creation date in the format of YYYYMMDD
- t: original creation time in the format of HHMMSS
- sc: shutter count for digital photos if available padded to 6 or 8 digits
- s: file size in bytes
- p: number of pages in PDFs, documents etc. where applicable
- ir: resolution of images in pixels in the format of XXXXxYYYY
- vr: resolution of video files in the format of p (progressive scan), e.g. 1080p
- fps: frames per seconds of video files
- l: length of video files in the format of XXXmYYYs (minutes and seconds)
- camera/scanner/drone etc. manufacturer's name (e.g. Nikon, Sony, Canon-LiDE, iPhone, DJI etc.)
- camera/scanner/drone etc. manufacturer's model/version indicator (e.g. D5100, ILCE-7M4)

Photos can be distinguished from other digital image files based on any metadata that can identify a camera.

Manufacturer and model names must be standardized.

The output files are organized in folders, based on content type and original creation date and time (in the structure of YYYY/YYYY-MM/YYYY-MM-DD).

---

## System Architecture

### Overview

The system follows a modular pipeline architecture where each component has a single responsibility and can be easily extended or replaced. The pipeline processes files sequentially through distinct stages, with comprehensive error handling and logging at each step.

### Core Components

#### 1. Main Controller (`vault_processor.py`)

- **Purpose**: Orchestrates the entire processing pipeline
- **Responsibilities**:
  - Initialize configuration and database
  - Scan input directory/files
  - Coordinate processing modules
  - Handle global error reporting
  - Generate processing summary

#### 2. Configuration Manager (`config/config_manager.py`)

- **Purpose**: Centralized configuration management
- **Responsibilities**:
  - Load and validate JSON configuration files
  - Provide configuration access to all modules
  - Handle configuration file updates
  - Validate configuration integrity

#### 3. Database Manager (`database/db_manager.py`)

- **Purpose**: SQLite database operations for duplicate detection and history
- **Responsibilities**:
  - Initialize database schema
  - Store and retrieve file checksums
  - Track processing history
  - Manage duplicate records

#### 4. File Ingestion Module (`modules/ingestion.py`)

- **Purpose**: Entry point for file processing
- **Responsibilities**:
  - Calculate SHA-256 checksums
  - Check for duplicates against database
  - Clean up system/hidden files
  - Route files to appropriate processors

#### 5. File Type Analyzer (`modules/file_analyzer.py`)

- **Purpose**: Determine file types using content analysis
- **Responsibilities**:
  - Use `python-magic` for MIME type detection
  - Validate file extensions against content
  - Route files to specialized processors
  - Handle unknown/corrupted files

#### 6. Specialized Processing Modules

##### Image Processor (`modules/processors/image_processor.py`)

- **Purpose**: Handle image files (photos and graphics)
- **Responsibilities**:
  - Extract EXIF data using Pillow
  - Distinguish photos from images (camera metadata)
  - Extract resolution, camera info, timestamps
  - Determine raw vs processed classification

##### Document Processor (`modules/processors/document_processor.py`)

- **Purpose**: Handle document files
- **Responsibilities**:
  - Count PDF pages to classify brochures vs ebooks
  - Extract document metadata (creation date, author)
  - Handle OCR content matching
  - Process various document formats

##### Audio Processor (`modules/processors/audio_processor.py`)

- **Purpose**: Handle audio files
- **Responsibilities**:
  - Extract ID3 tags using mutagen
  - Get duration, bitrate, format info
  - Extract artist, album, creation date

##### Video Processor (`modules/processors/video_processor.py`)

- **Purpose**: Handle video files
- **Responsibilities**:
  - Extract metadata using pymediainfo
  - Get duration, resolution, fps
  - Extract creation date and camera info
  - Determine video category (family, tutorials, etc.)

#### 7. Metadata Extractor (`modules/metadata_extractor.py`)

- **Purpose**: Centralized metadata extraction coordination
- **Responsibilities**:
  - Coordinate between specialized processors
  - Apply metadata priority rules (EXIF > filename > filesystem)
  - Handle timezone preservation
  - Standardize manufacturer names

#### 8. File Renamer (`modules/file_renamer.py`)

- **Purpose**: Generate standardized filenames
- **Responsibilities**:
  - Apply naming convention rules
  - Format metadata components (padding, dashes)
  - Ensure filename uniqueness
  - Handle filename length limits

#### 9. Organization Manager (`modules/organization_manager.py`)

- **Purpose**: Determine final file placement
- **Responsibilities**:
  - Apply content classification rules
  - Create date-based folder hierarchy
  - Ensure folder structure consistency
  - Handle edge cases in classification

#### 10. File Mover (`modules/file_mover.py`)

- **Purpose**: Handle final file operations
- **Responsibilities**:
  - Create destination directories
  - Move files to vault locations
  - Handle duplicates and quarantine files
  - Update database records

#### 11. Error Handler (`modules/error_handler.py`)

- **Purpose**: Centralized error management
- **Responsibilities**:
  - Log errors with context
  - Move problematic files to quarantine
  - Generate error reports
  - Handle recovery scenarios

### Data Flow

```text
Input Files
    ↓
[File Ingestion] → Check duplicates → Route to quarantine if duplicate
    ↓
[File Type Analyzer] → Determine MIME type → Route to appropriate processor
    ↓
[Specialized Processor] → Extract metadata → Apply classification rules
    ↓
[Metadata Extractor] → Consolidate metadata → Apply priority rules
    ↓
[File Renamer] → Generate filename → Apply naming conventions
    ↓
[Organization Manager] → Determine destination → Apply folder structure
    ↓
[File Mover] → Move to vault → Update database
    ↓
Processed Files in Vault
```

### Error Handling Strategy

- **Graceful Degradation**: If metadata extraction fails, continue with available data
- **Quarantine System**: Move problematic files to categorized quarantine folders
- **Comprehensive Logging**: Log all operations with timestamps and context
- **Recovery Mechanisms**: Allow reprocessing of quarantined files
- **Rollback Capability**: Track operations for potential rollback

### Configuration Structure

```json
{
  "vault": {
    "base_path": "/path/to/vault",
    "create_structure": true
  },
  "processing": {
    "batch_size": 100,
    "filename_max_length": 200,
    "counter_padding": 8
  },
  "database": {
    "path": "vault_database.sqlite",
    "backup_interval": 1000
  },
  "logging": {
    "level": "INFO",
    "file": "vault_processor.log"
  }
}
```

### Database Schema

```sql
CREATE TABLE processed_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT NOT NULL,
    checksum TEXT UNIQUE NOT NULL,
    vault_path TEXT,
    file_type TEXT,
    metadata JSON,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'processed'
);

CREATE TABLE duplicates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checksum TEXT NOT NULL,
    duplicate_path TEXT NOT NULL,
    original_file_id INTEGER,
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_file_id) REFERENCES processed_files (id)
);
```

---

## Technical Specifications

### Technology Stack

- **Programming Language:** Python
- **Configuration Management:** JSON configuration files
- **Database:** SQLite for duplicate detection and processing history
- **Metadata Extraction Libraries:**
  - `python-magic` for file type detection
  - `Pillow` for image EXIF data
  - `mutagen` for audio metadata
  - `pymediainfo` for video metadata

### Duplicate Detection

- **Algorithm:** SHA-256 checksums for content-based duplicate detection
- **Handling:** Duplicates moved to separate `duplicates/` folder with original path preserved
- **Database:** SQLite database to track processed files and checksums for faster duplicate detection

### Metadata Priority Order

1. **EXIF data** (for images/videos)
2. **Original filename** (if contains usable information like dates)
3. **Filesystem timestamps** (creation/modification time)
4. **Fallback:** Skip metadata component if unavailable

### File Processing Rules

- **File Size:** No limits imposed
- **Counter Padding:** 8 digits for all counters (e.g., shutter count: `00012345`)
- **Filename Length:** Reasonable defaults (~200 characters max for compatibility)
- **Timezone:** Preserve original creation timestamps from metadata (no UTC conversion)

### Error Handling

- **Corrupted Files:** Moved to `quarantine/corrupted/` folder
- **Unsupported Formats:** Moved to `quarantine/unsupported/` folder
- **Processing Errors:** Moved to `quarantine/processing-errors/` folder
- **Missing Metadata:** Fallback mechanisms in place, skip unavailable components

### Manufacturer Standardization

- **Mapping File:** `config/manufacturer-mapping.json` for standardizing device names
- **Examples:**
  - `"NIKON CORPORATION"` → `"Nikon"`
  - `"SONY"` → `"Sony"`
  - `"Apple"` → `"iPhone"` (for phone cameras)

### Configuration Files

- `config/settings.json` - Main system settings
- `config/manufacturer-mapping.json` - Device name standardization
- `config/file-types.json` - Supported file extensions and processing rules

### Folder Structure

The vault organizes files by content type, then by date hierarchy. The complete structure follows this pattern:

```text
vault/
├── documents/
│   ├── notes/2023/2023-12/2023-12-25/           # plain text, markdown
│   ├── office/2023/2023-12/2023-12-25/          # DOC, DOCX, ODT, Pages, RTF
│   ├── scanned/2023/2023-12/2023-12-25/         # PDF scans, OCR content
│   ├── bookmarks/2023/2023-12/2023-12-25/       # exported browser bookmarks
│   ├── mindmaps/2023/2023-12/2023-12-25/        # mindmap files
│   ├── brochures/2023/2023-12/2023-12-25/       # PDFs ≤5 pages
│   ├── presentations/2023/2023-12/2023-12-25/   # presentation files
│   └── spreadsheets/2023/2023-12/2023-12-25/    # spreadsheet files
├── ebooks/2023/2023-12/2023-12-25/              # PDFs >5 pages, ebook formats
├── fonts/2023/2023-12/2023-12-25/               # font files
├── audio/2023/2023-12/2023-12-25/               # all audio files
├── images/                                       # non-photo images
│   ├── screenshots/2023/2023-12/2023-12-25/     # screen captures
│   ├── icons/2023/2023-12/2023-12-25/           # icon files
│   ├── svg/2023/2023-12/2023-12-25/             # SVG files
│   └── other/2023/2023-12/2023-12-25/           # other images
├── photos/                                       # camera photos
│   ├── raw/2023/2023-12/2023-12-25/             # NEF, ARW, etc.
│   └── processed/2023/2023-12/2023-12-25/       # JPG, edited photos
├── videos/
│   ├── family/2023/2023-12/2023-12-25/          # family videos
│   ├── music-videos/2023/2023-12/2023-12-25/    # downloaded music videos
│   ├── tutorials/2023/2023-12/2023-12-25/       # tutorial videos
│   ├── work/2023/2023-12/2023-12-25/            # work-related videos
│   ├── tech/2023/2023-12/2023-12-25/            # tech videos
│   └── other/2023/2023-12/2023-12-25/           # YT other, misc
├── duplicates/                                   # duplicate files with original path preserved
└── quarantine/                                   # files that couldn't be processed
    ├── corrupted/
    ├── unsupported/
    └── processing-errors/
```

### Content Classification Rules

- **Documents vs Ebooks**: PDFs with ≤5 pages go to `documents/brochures/`, PDFs with >5 pages go to `ebooks/`
- **Photos vs Images**: Files with camera EXIF data go to `photos/`, others go to `images/`
- **Raw vs Processed Photos**: Determined by file extension (NEF, ARW, CR2, etc. = raw; JPG, PNG = processed)

### Rule Storage System

The system uses JSON-based configuration files to store all processing and naming rules, making them easily editable without code changes.

#### Filename Assembly Rules (`config/filename-rules.json`)

```json
{
  "naming_patterns": {
    "photos": {
      "raw": "{d}-{t}-{manufacturer}-{model}-sc{sc}-ir{ir}-s{s}.{ext}",
      "processed": "{d}-{t}-{manufacturer}-{model}-ir{ir}-s{s}.{ext}"
    },
    "videos": {
      "family": "{d}-{t}-{manufacturer}-{model}-vr{vr}-fps{fps}-l{l}-s{s}.{ext}",
      "tutorials": "{d}-{t}-l{l}-s{s}.{ext}",
      "other": "{d}-{t}-vr{vr}-l{l}-s{s}.{ext}"
    },
    "documents": {
      "office": "{d}-{t}-p{p}-s{s}.{ext}",
      "scanned": "{d}-{t}-p{p}-s{s}.{ext}",
      "brochures": "{d}-{t}-p{p}-s{s}.{ext}"
    },
    "ebooks": "{d}-{t}-p{p}-s{s}.{ext}",
    "audio": "{d}-{t}-l{l}-s{s}.{ext}",
    "images": {
      "screenshots": "{d}-{t}-ir{ir}-s{s}.{ext}",
      "icons": "{d}-{t}-ir{ir}-s{s}.{ext}",
      "svg": "{d}-{t}-s{s}.{ext}",
      "other": "{d}-{t}-ir{ir}-s{s}.{ext}"
    },
    "fonts": "{d}-{t}-s{s}.{ext}"
  },
  "metadata_components": {
    "d": {
      "description": "Original creation date",
      "format": "YYYYMMDD",
      "required": true,
      "fallback_order": ["exif_date", "filename_date", "filesystem_created", "filesystem_modified"]
    },
    "t": {
      "description": "Original creation time", 
      "format": "HHMMSS",
      "required": true,
      "fallback_order": ["exif_time", "filename_time", "filesystem_created", "filesystem_modified"]
    },
    "sc": {
      "description": "Shutter count",
      "format": "00000000",
      "required": false,
      "applies_to": ["photos"],
      "padding": 8
    },
    "s": {
      "description": "File size in bytes",
      "format": "numeric",
      "required": true,
      "padding": 0
    },
    "p": {
      "description": "Number of pages",
      "format": "000",
      "required": false,
      "applies_to": ["documents", "ebooks"],
      "padding": 3
    },
    "ir": {
      "description": "Image resolution",
      "format": "XXXXxYYYY",
      "required": false,
      "applies_to": ["photos", "images"]
    },
    "vr": {
      "description": "Video resolution",
      "format": "XXXXp",
      "required": false,
      "applies_to": ["videos"]
    },
    "fps": {
      "description": "Frames per second",
      "format": "00",
      "required": false,
      "applies_to": ["videos"],
      "padding": 2
    },
    "l": {
      "description": "Length/duration",
      "format": "XXXmYYs",
      "required": false,
      "applies_to": ["videos", "audio"]
    },
    "manufacturer": {
      "description": "Device manufacturer",
      "format": "text",
      "required": false,
      "standardize": true,
      "applies_to": ["photos", "videos"]
    },
    "model": {
      "description": "Device model",
      "format": "text",
      "required": false,
      "standardize": true,
      "applies_to": ["photos", "videos"]
    },
    "ext": {
      "description": "File extension",
      "format": "lowercase",
      "required": true,
      "normalize": true
    }
  },
  "formatting_rules": {
    "separator": "-",
    "space_replacement": "-",
    "multiple_spaces": "single_dash",
    "max_filename_length": 200,
    "invalid_chars_replacement": "_",
    "case_handling": {
      "extensions": "lowercase",
      "manufacturer": "title_case",
      "model": "preserve"
    }
  }
}
```

#### Content Classification Rules (`config/classification-rules.json`)

```json
{
  "file_type_detection": {
    "photos": {
      "criteria": [
        {"type": "exif_data", "required_fields": ["camera_make", "camera_model"]},
        {"type": "exif_data", "required_fields": ["datetime_original"]},
        {"type": "mime_type", "patterns": ["image/jpeg", "image/tiff", "image/raw"]}
      ],
      "extensions": {
        "raw": [".nef", ".arw", ".cr2", ".cr3", ".dng", ".raf", ".orf", ".rw2"],
        "processed": [".jpg", ".jpeg", ".png", ".tiff", ".tif"]
      }
    },
    "images": {
      "criteria": [
        {"type": "mime_type", "patterns": ["image/*"]},
        {"type": "not", "condition": "photos"}
      ],
      "subcategories": {
        "screenshots": {
          "criteria": [
            {"type": "filename_pattern", "patterns": ["*screenshot*", "*screen*shot*", "*capture*"]},
            {"type": "exif_data", "software_patterns": ["screenshot", "snipping", "capture"]}
          ]
        },
        "icons": {
          "criteria": [
            {"type": "filename_pattern", "patterns": ["*icon*", "*ico*"]},
            {"type": "dimensions", "max_width": 512, "max_height": 512}
          ]
        },
        "svg": {
          "criteria": [
            {"type": "extension", "patterns": [".svg"]}
          ]
        }
      }
    },
    "documents": {
      "criteria": [
        {"type": "mime_type", "patterns": ["application/pdf", "application/msword", "text/*"]}
      ],
      "subcategories": {
        "brochures": {
          "criteria": [
            {"type": "pdf_pages", "max_pages": 5}
          ]
        },
        "office": {
          "criteria": [
            {"type": "extension", "patterns": [".doc", ".docx", ".odt", ".rtf", ".pages"]}
          ]
        },
        "scanned": {
          "criteria": [
            {"type": "filename_pattern", "patterns": ["*scan*", "*scanned*"]},
            {"type": "ocr_companion", "exists": true}
          ]
        }
      }
    },
    "ebooks": {
      "criteria": [
        {"type": "pdf_pages", "min_pages": 6},
        {"type": "extension", "patterns": [".epub", ".mobi", ".azw", ".azw3"]}
      ]
    }
  },
  "folder_mapping": {
    "photos": {
      "raw": "photos/raw/{year}/{year}-{month}/{year}-{month}-{day}/",
      "processed": "photos/processed/{year}/{year}-{month}/{year}-{month}-{day}/"
    },
    "videos": {
      "family": "videos/family/{year}/{year}-{month}/{year}-{month}-{day}/",
      "tutorials": "videos/tutorials/{year}/{year}-{month}/{year}-{month}-{day}/",
      "music-videos": "videos/music-videos/{year}/{year}-{month}/{year}-{month}-{day}/",
      "work": "videos/work/{year}/{year}-{month}/{year}-{month}-{day}/",
      "tech": "videos/tech/{year}/{year}-{month}/{year}-{month}-{day}/",
      "other": "videos/other/{year}/{year}-{month}/{year}-{month}-{day}/"
    },
    "documents": {
      "office": "documents/office/{year}/{year}-{month}/{year}-{month}-{day}/",
      "scanned": "documents/scanned/{year}/{year}-{month}/{year}-{month}-{day}/",
      "brochures": "documents/brochures/{year}/{year}-{month}/{year}-{month}-{day}/",
      "notes": "documents/notes/{year}/{year}-{month}/{year}-{month}-{day}/",
      "bookmarks": "documents/bookmarks/{year}/{year}-{month}/{year}-{month}-{day}/",
      "mindmaps": "documents/mindmaps/{year}/{year}-{month}/{year}-{month}-{day}/",
      "presentations": "documents/presentations/{year}/{year}-{month}/{year}-{month}-{day}/",
      "spreadsheets": "documents/spreadsheets/{year}/{year}-{month}/{year}-{month}-{day}/"
    }
  }
}
```

#### Processing Rules (`config/processing-rules.json`)

```json
{
  "duplicate_handling": {
    "strategy": "move_to_duplicates",
    "preserve_path": true,
    "folder_structure": "duplicates/{original_date}/{checksum}/"
  },
  "quarantine_rules": {
    "corrupted": {
      "folder": "quarantine/corrupted/{date}/",
      "triggers": ["file_read_error", "metadata_extraction_failed", "invalid_format"]
    },
    "unsupported": {
      "folder": "quarantine/unsupported/{date}/",
      "triggers": ["unknown_mime_type", "unsupported_extension"]
    },
    "processing_errors": {
      "folder": "quarantine/processing-errors/{date}/",
      "triggers": ["naming_failed", "move_failed", "database_error"]
    }
  },
  "metadata_extraction": {
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "fallback_enabled": true,
    "required_fields": ["creation_date", "file_size"],
    "optional_fields": ["camera_info", "resolution", "duration"]
  },
  "file_operations": {
    "verify_checksums": true,
    "create_backups": false,
    "atomic_moves": true,
    "preserve_timestamps": true
  }
}
```

### Rule Processing Logic

The system processes rules in this order:

1. **File Type Detection**: Use `classification-rules.json` to determine content type and subcategory
2. **Metadata Extraction**: Extract available metadata based on file type
3. **Filename Assembly**: Use appropriate pattern from `filename-rules.json` based on detected type
4. **Component Formatting**: Apply formatting rules for each metadata component
5. **Folder Determination**: Use folder mapping to determine destination path
6. **Validation**: Ensure filename meets length and character requirements
7. **Uniqueness Check**: Append counter if filename collision detected
