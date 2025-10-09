# 🗄️ Vault of Memories

An intelligent file processing system that transforms scattered digital files into an organized, searchable vault with metadata-rich filenames and standardized folder structures - designed to stand the test of time.

## 🎯 Project Vision

The goal is to build a `pre-processor` for digital vaults that ensures digital assets stand the test of time. Rather than focusing on specific DAM (Digital Asset Management) systems that come and go, we focus on the source files themselves.

*Always focus on the source!*

Following core Unix design principles like "[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)" and *"make each program do one thing well"*, longevity is strengthened by focusing on the most basic, widespread formats:

- Plain text (markdown is also fine)
- Most popular image formats (JPEG, PNG, GIF, WebP)
- Most popular video formats (MP4, WebM)
- Most popular audio formats (MP3, FLAC)
- Most popular document formats (PDF, DOCX, ODT)
- Most popular archive formats (ZIP, TAR, 7Z)

## 🚀 Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Process files into your vault
python3 -m src.cli --vault-root ~/vault process ~/Downloads

# See all available commands
python3 -m src.cli --help
```

Upon the first run an SQLite database will be created (as a hidden file).
This database is local and stores key attributes of each processed file, to manage identifying duplicates and to serve as the source for any processing statistics.

For more details on usage patterns please check [USAGE.md](./USAGE.md)

## Example Vault Structure

After processing, your vault will look like this:

```text
vault/
├── .vault.db                    # SQLite database for tracking
├── documents/
│   ├── pdf/
│   │   └── 2025/
│   │       └── 2025-10/
│   │           └── 2025-10-08/
│   │               └── 2025-10-04-095209-p447-s447.pdf
│   ├── text/
│   │   └── 2025/...
│   └── office/
│       └── 2025/...
├── images/
│   ├── photos/
│   │   └── 2025/
│   │       └── 2025-10/
│   │           └── 2025-10-08/
│   │               └── 2025-10-08-143022-Nikon-D5100-4928x3264.jpg
│   └── graphics/
│       └── 2025/...
├── videos/
│   └── 2025/...
├── audio/
│   └── 2025/...
├── other/
│   └── 2025/...
├── duplicates/                  # Duplicate files moved here
└── quarantine/                  # Problematic files moved here
    ├── corruption/
    ├── permission/
    ├── checksum/
    └── ...
```

## 🏗️ Architecture Overview

The system follows a modular pipeline architecture:

1. **File Ingestion** → Checksum calculation and duplicate detection
2. **File Type Analysis** → Content-based file type detection
3. **Specialized Processing** → Type-specific metadata extraction
4. **Metadata Consolidation** → Priority-based metadata merging
5. **Filename Generation** → Rule-based naming with metadata
6. **Organization** → Content classification and folder placement
7. **File Operations** → Atomic moves to vault structure

### Key Features

- **Modular Design**: Each component has single responsibility
- **Configuration-Driven**: JSON files for all rules and settings
- **Extensible**: Easy to add new file types without code changes
- **Reliable**: Comprehensive error handling and quarantine system
- **Preserves History**: SQLite database tracks all operations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📚 Documentation

- [Project Constitution](./.specify/memory/constitution.md) - Core principles and standards
- [Spec-Kit Workflow Guide](./SPEC-KIT-WORKFLOW.md) - Step-by-step modular specification process
- [Feature Specifications](./specs/) - Detailed feature requirements (modular components)
- [Complete Technical Documentation](./README-detailed.md) - Full system architecture, rule storage, and implementation details

## 🤝 Contributing

This project follows Spec-Driven Development principles:

1. **Establish Principles**: Review the [constitution](./.specify/memory/constitution.md)
2. **Create Specifications**: Use `/specify` for new features
3. **Plan Implementation**: Use `/plan` for technical approach
4. **Break Down Tasks**: Use `/tasks` for actionable items
5. **Execute**: Use `/implement` or manual development

## 🙏 Acknowledgments

- Built with [spec-kit](https://github.com/github/spec-kit) for Spec-Driven Development
- Inspired by Unix philosophy and digital preservation principles
