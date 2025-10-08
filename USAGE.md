# Vault of Memories - Usage Guide

## Quick Start

The Vault of Memories CLI processes your files into an organized vault structure with intelligent metadata-based naming and date hierarchies.

## Command Syntax

```bash
python3 -m src.cli.main [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

**Important:** Global options (like `--vault-root`) must come **before** the command name.

---

## Commands

### Process Files

Process files from a source directory into your vault.

```bash
# Basic usage
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads

# Process a single file
python3 -m src.cli.main --vault-root ~/vault process ~/Documents/report.pdf

# Process with dry-run (preview without moving files)
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --dry-run

# Process with verbose output
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --verbose

# Combine options
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --dry-run --verbose
```

**What it does:**
- Recursively scans source directory
- Computes SHA256 checksums
- Detects duplicates
- Extracts metadata (EXIF, PDF properties, ID3 tags)
- Generates intelligent filenames with metadata
- Organizes files by type and date (YYYY/YYYY-MM/YYYY-MM-DD)
- Moves files atomically with integrity verification
- Reports comprehensive statistics

---

### Check Vault Status

Display vault statistics and health information.

```bash
# Check vault status
python3 -m src.cli.main --vault-root ~/vault status

# With verbose details
python3 -m src.cli.main --vault-root ~/vault status --verbose
```

**Output includes:**
- Total files in vault
- Total storage size
- Quarantined files count (if any)
- Vault health status

---

### Validate Files

Pre-validate files before processing (dry-run on steroids).

```bash
# Validate a directory
python3 -m src.cli.main validate ~/Downloads

# Validate a single file
python3 -m src.cli.main validate ~/Documents/report.pdf
```

**What it does:**
- Checks file readability
- Detects file types (MIME)
- Reports unsupported files
- Estimates vault storage requirements
- **Does not modify anything**

---

### Recover Quarantined Files

Reprocess files that were quarantined during previous runs.

```bash
# Recover all quarantined files
python3 -m src.cli.main --vault-root ~/vault recover

# Recover specific quarantine type
python3 -m src.cli.main --vault-root ~/vault recover --quarantine-type corruption

# With verbose output
python3 -m src.cli.main --vault-root ~/vault recover --verbose
```

**Quarantine types:**
- `corruption` - Corrupted files
- `permission` - Permission errors
- `checksum` - Checksum mismatches
- `path` - Path too long
- `disk` - Disk space errors
- `network` - Network errors
- `invalid` - Invalid characters
- `exists` - Destination exists
- `unknown` - Unknown errors

---

## Global Options

Available for all commands (must come **before** the command name):

```bash
--vault-root PATH        # Vault root directory (default: ./vault)
--config FILE           # Configuration file path
--log-file FILE         # Log file path
--workers N             # Number of parallel workers (default: 1)
--batch-size N          # Files per batch (default: 100)
```

**Examples:**

```bash
# Use custom vault location
python3 -m src.cli.main --vault-root /Volumes/Archive/vault process ~/Downloads

# Save logs to file
python3 -m src.cli.main --vault-root ~/vault --log-file processing.log process ~/Downloads

# Use custom config
python3 -m src.cli.main --config my-config.json --vault-root ~/vault process ~/Downloads

# Process with multiple workers (faster for large batches)
python3 -m src.cli.main --vault-root ~/vault --workers 4 process ~/Downloads
```

---

## Command-Specific Options

### Process Command

```bash
--dry-run              # Preview without making changes
--verbose              # Show detailed progress information
--quiet                # Suppress non-error output
```

### Status Command

```bash
--verbose              # Show detailed vault statistics
```

### Recover Command

```bash
--quarantine-type TYPE # Only recover specific error type
--force                # Skip confirmation prompts
--verbose              # Show detailed recovery information
```

### Validate Command

```bash
--verbose              # Show detailed validation information
```

---

## Common Workflows

### Initial Setup

```bash
# 1. Validate your files first
python3 -m src.cli.main validate ~/Downloads

# 2. Do a dry-run to see what would happen
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --dry-run

# 3. Process for real
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads

# 4. Check vault status
python3 -m src.cli.main --vault-root ~/vault status
```

### Regular Maintenance

```bash
# Process new files
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads

# Check for quarantined files
python3 -m src.cli.main --vault-root ~/vault status

# Recover quarantined files if any
python3 -m src.cli.main --vault-root ~/vault recover
```

### Bulk Processing

```bash
# Process multiple sources one by one
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads
python3 -m src.cli.main --vault-root ~/vault process ~/Desktop
python3 -m src.cli.main --vault-root ~/vault process ~/Documents

# Or create a script
#!/bin/bash
VAULT=~/vault
for dir in ~/Downloads ~/Desktop ~/Documents; do
    python3 -m src.cli.main --vault-root $VAULT process "$dir"
done
```

---

## Vault Structure

After processing, your vault will look like this:

```
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

---

## Understanding Filenames

The system generates intelligent filenames based on metadata:

### Images (with EXIF)
```
2025-10-08-143022-Nikon-D5100-4928x3264.jpg
│          │      │     │      │
│          │      │     │      └─ Resolution (width x height)
│          │      │     └─ Camera model
│          │      └─ Camera make
│          └─ Time (HHMMSS)
└─ Date (YYYY-MM-DD)
```

### Documents (with metadata)
```
2025-10-04-095209-p24-s447.pdf
│          │      │   │
│          │      │   └─ Size in KB
│          │      └─ Page count
│          └─ Time
└─ Date
```

### Files without metadata
```
original-filename.txt
└─ Preserves original name when metadata is insufficient
```

---

## Exit Codes

- `0` - Success
- `1` - Processing errors (some files failed)
- `2` - Invalid arguments
- `65` - File/directory not found
- `130` - User cancelled (Ctrl+C)

---

## Tips & Best Practices

### Before Processing

1. **Always validate first:**
   ```bash
   python3 -m src.cli.main validate ~/Downloads
   ```

2. **Use dry-run to preview:**
   ```bash
   python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --dry-run
   ```

3. **Check available disk space:**
   The system needs enough space for the entire source directory.

### During Processing

- **Use verbose mode** for large batches to monitor progress:
  ```bash
  python3 -m src.cli.main --vault-root ~/vault process ~/Downloads --verbose
  ```

- **Interrupt safely** with Ctrl+C - the system handles interruption gracefully and finishes the current file before stopping.

### After Processing

1. **Check for quarantined files:**
   ```bash
   python3 -m src.cli.main --vault-root ~/vault status
   ```

2. **Review and recover** if needed:
   ```bash
   python3 -m src.cli.main --vault-root ~/vault recover
   ```

### Performance

- For large batches (1000+ files), use multiple workers:
  ```bash
  python3 -m src.cli.main --vault-root ~/vault --workers 4 process ~/Downloads
  ```

- For external drives or network storage, use single worker to avoid conflicts:
  ```bash
  python3 -m src.cli.main --vault-root ~/vault --workers 1 process ~/Downloads
  ```

---

## Troubleshooting

### "No such file or directory"
Make sure paths are absolute or use `~` for home directory:
```bash
# Good
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads

# Bad (relative paths may not work)
python3 -m src.cli.main --vault-root ./vault process ./Downloads
```

### "Permission denied"
Ensure you have read access to source files and write access to vault:
```bash
# Check permissions
ls -la ~/Downloads
ls -la ~/vault
```

### Files not moving
Check if dry-run mode is enabled - remove `--dry-run` to actually move files.

### Duplicates detected
This is normal! The system prevents duplicate files from being stored. Check the duplicates folder:
```bash
ls -la ~/vault/duplicates/
```

### Quarantined files
Check what went wrong:
```bash
python3 -m src.cli.main --vault-root ~/vault status --verbose
```

Then recover if safe:
```bash
python3 -m src.cli.main --vault-root ~/vault recover
```

---

## Creating an Alias (Optional)

For easier use, add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias vault='python3 -m src.cli.main'
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Now you can use shorter commands:
```bash
vault --vault-root ~/vault process ~/Downloads
vault --vault-root ~/vault status
vault validate ~/Downloads
```

---

## Getting Help

```bash
# General help
python3 -m src.cli.main --help

# Command-specific help
python3 -m src.cli.main process --help
python3 -m src.cli.main status --help
python3 -m src.cli.main validate --help
python3 -m src.cli.main recover --help
```

---

## Examples by Use Case

### Photographer organizing photos

```bash
# Validate camera card
python3 -m src.cli.main validate /Volumes/SD_CARD/DCIM

# Process with dry-run
python3 -m src.cli.main --vault-root ~/Photos/vault process /Volumes/SD_CARD/DCIM --dry-run

# Process for real
python3 -m src.cli.main --vault-root ~/Photos/vault process /Volumes/SD_CARD/DCIM
```

Result: Photos organized by date with camera info in filenames.

### Archiving documents

```bash
# Process documents folder
python3 -m src.cli.main --vault-root ~/Archive/vault process ~/Documents

# Check status
python3 -m src.cli.main --vault-root ~/Archive/vault status
```

Result: Documents organized by type (PDF, Office) and date with page count in filenames.

### Music library organization

```bash
# Process music folder
python3 -m src.cli.main --vault-root ~/Music/vault process ~/Downloads/Music --verbose

# Verify results
python3 -m src.cli.main --vault-root ~/Music/vault status
```

Result: Audio files organized by date with artist, album, bitrate in filenames.

### Cleaning up Downloads

```bash
# See what's in there
python3 -m src.cli.main validate ~/Downloads

# Process everything
python3 -m src.cli.main --vault-root ~/vault process ~/Downloads

# Check for issues
python3 -m src.cli.main --vault-root ~/vault status --verbose
```

Result: All files categorized and organized, duplicates caught, system files removed.

---

## Advanced Usage

### Custom Configuration

Create a `vault-config.json`:
```json
{
  "naming_patterns": {
    "image": "{date}-{time}-{device_make}-{device_model}-{resolution}",
    "document": "{date}-{title}-p{page_count}",
    "audio": "{artist}-{album}-{title}"
  }
}
```

Use it:
```bash
python3 -m src.cli.main --config vault-config.json --vault-root ~/vault process ~/Downloads
```

### Processing with logs

```bash
# Save detailed logs
python3 -m src.cli.main --vault-root ~/vault --log-file vault-$(date +%Y%m%d).log process ~/Downloads --verbose

# Review logs later
tail -f vault-20251008.log
```

### Scheduled processing (cron)

Add to crontab:
```bash
# Process Downloads daily at 2 AM
0 2 * * * cd /Users/yourusername/vault-of-memories && python3 -m src.cli.main --vault-root ~/vault --log-file ~/vault-logs/daily-$(date +\%Y\%m\%d).log process ~/Downloads
```

---

For more information, see the main [README.md](README.md) or check the [project documentation](docs/).
