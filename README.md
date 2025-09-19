# 🗄️ Vault of Memories

## Build a future-proof digital vault pre-processor for preserving family memories

An intelligent file processing system that transforms scattered digital files into an organized, searchable vault with metadata-rich filenames and standardized folder structures - designed to stand the test of time.

## 🎯 Project Vision

The goal is to build a `pre-processor` for digital vaults that ensures digital assets stand the test of time. Rather than focusing on specific DAM (Digital Asset Management) systems that come and go, we focus on the source files themselves.

*Always focus on the source!*

Following core Unix design principles like "[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)" and "make each program do one thing well", longevity is strengthened by focusing on the most basic, widespread formats:

- Plain text (markdown is also fine)
- Most popular image formats (JPEG, PNG, GIF, WebP)
- Most popular video formats (MP4, WebM)
- Most popular audio formats (MP3, FLAC)
- Most popular document formats (PDF, DOCX, ODT)
- Most popular archive formats (ZIP, TAR, 7Z)

## 🚀 Quick Start

This project uses [spec-kit](https://github.com/github/spec-kit) for Spec-Driven Development.

### Prerequisites

- Python 3.11+
- Git
- [spec-kit](https://github.com/github/spec-kit) installed

### Initialize Development

```bash
# Clone the repository
git clone <repository-url>
cd vault-of-memories

# Initialize spec-kit (if not already done)
uvx --from git+https://github.com/github/spec-kit.git specify init vault-of-memories

# Start development with Claude (or your preferred AI agent)
claude
```

### Available Commands

Once in your AI agent with spec-kit loaded:

- `/constitution` - View/update project principles
- `/specify` - Create feature specifications
- `/plan` - Generate implementation plans
- `/tasks` - Break down features into tasks
- `/implement` - Execute implementation

## 📋 Current Status

### Project Setup Complete

- **[Project Constitution](./memory/constitution.md)** - Core principles and development standards
- **[Spec-Kit Workflow Guide](./SPEC-KIT-WORKFLOW.md)** - Modular specification process
- **[Technical Architecture](./README-detailed.md)** - Complete system design and rule storage

### Ready for Modular Specification

Following the spec-kit workflow, we're ready to create focused specifications for each component:

1. **001-file-ingestion** - File input, checksums, duplicate detection
2. **002-configuration-system** - JSON configuration management  
3. **003-file-type-analyzer** - MIME type detection and routing
4. **004-007** - Specialized processors (image, document, audio, video)
5. **008-011** - Organization and output systems
6. **012-013** - Error handling and CLI integration

### Next Steps

Run the `/specify` commands from the workflow guide to create modular specifications.

### What the System Does

The Vault of Memories pre-processor:

1. **Collects** - Accepts single files, multiple files, or nested folder structures
2. **Organizes** - Creates content-type folders with date-based hierarchy (YYYY/YYYY-MM/YYYY-MM-DD)
3. **Deduplicates** - Uses SHA-256 checksums to identify and handle duplicate files
4. **Enriches** - Extracts metadata from EXIF, ID3 tags, document properties, etc.
5. **Renames** - Generates human-readable, metadata-rich filenames
6. **Packages** - Creates a structured vault ready for any DAM system

### Example Output Structure

```text
vault/
├── photos/
│   ├── raw/2023/2023-12/2023-12-25/
│   │   └── 20231225-143022-Nikon-D5100-sc00012345-ir4928x3264-s2847291.nef
│   └── processed/2023/2023-12/2023-12-25/
│       └── 20231225-143022-Nikon-D5100-ir4928x3264-s1847291.jpg
├── documents/
│   ├── office/2023/2023-12/2023-12-25/
│   └── brochures/2023/2023-12/2023-12-25/
├── videos/
│   ├── family/2023/2023-12/2023-12-25/
│   └── tutorials/2023/2023-12/2023-12-25/
├── duplicates/
└── quarantine/
    ├── corrupted/
    ├── unsupported/
    └── processing-errors/
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

## 🔧 Technical Stack

- **Language**: Python 3.11+
- **Dependencies**: python-magic, Pillow, mutagen, pymediainfo
- **Database**: SQLite for duplicate detection and history
- **Configuration**: JSON files for rules and settings
- **Testing**: pytest with comprehensive coverage
- **Documentation**: Markdown with spec-kit structure

## 📚 Documentation

- [Project Constitution](./memory/constitution.md) - Core principles and standards
- [Spec-Kit Workflow Guide](./SPEC-KIT-WORKFLOW.md) - Step-by-step modular specification process
- [Feature Specifications](./specs/) - Detailed feature requirements (modular components)
- [Complete Technical Documentation](./README-detailed.md) - Full system architecture, rule storage, and implementation details

## 🤝 Contributing

This project follows Spec-Driven Development principles:

1. **Establish Principles**: Review the [constitution](./memory/constitution.md)
2. **Create Specifications**: Use `/specify` for new features
3. **Plan Implementation**: Use `/plan` for technical approach
4. **Break Down Tasks**: Use `/tasks` for actionable items
5. **Execute**: Use `/implement` or manual development

### Development Principles

- **Simplicity First (SF)**: Choose the simplest solution
- **Dependency Minimalism (DM)**: Minimal external dependencies
- **Industry Standards Adherence (ISA)**: Follow established conventions
- **Test-Driven Thinking (TDT)**: Design for testability
- **Strategic Documentation (SD)**: Self-documenting code
- **Readability Priority (RP)**: Code must be immediately understandable

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [spec-kit](https://github.com/github/spec-kit) for Spec-Driven Development
- Inspired by Unix philosophy and digital preservation principles
