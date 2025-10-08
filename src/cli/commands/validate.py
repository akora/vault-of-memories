"""
Validate command implementation.

Pre-processes validation of source files without modifications.
"""

import logging
from pathlib import Path
from collections import defaultdict

from src.models import CommandOptions
from src.cli.formatters.summary_formatter import SummaryFormatter
from src.services import MimeDetector

logger = logging.getLogger(__name__)


class ValidateCommand:
    """
    Validation command: vault validate <source>

    Validates source files before processing, without making any modifications.
    This is like a super-dry-run that only checks file readability and types.
    """

    def __init__(self, formatter: SummaryFormatter = None):
        """
        Initialize validate command.

        Args:
            formatter: Summary formatter instance (optional, will create default)
        """
        self.formatter = formatter or SummaryFormatter()
        self.mime_detector = MimeDetector()

    def validate(self, options: CommandOptions) -> list[str]:
        """
        Validate command-specific options.

        Args:
            options: Parsed command-line options

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not options.source:
            errors.append("Source path is required for validate command")
        elif not options.source.exists():
            errors.append(f"Source path does not exist: {options.source}")

        return errors

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the validate command.

        Args:
            options: Command options (must include source)

        Returns:
            Exit code:
            - 0: All files valid
            - 1: Some files invalid or unsupported
            - 2: Invalid arguments
            - 65: Source not found
        """
        # Validate options
        errors = self.validate(options)
        if errors:
            for error in errors:
                logger.error(error)
            return 65 if "does not exist" in errors[0] else 2

        source = options.source

        try:
            # Discover files
            if source.is_file():
                files = [source]
            else:
                files = [f for f in source.rglob('*') if f.is_file()]

            if not files:
                print(self.formatter.colors.warning("No files found in source"))
                return 1

            # Validate files
            results = self._validate_files(files, options.verbose)

            # Display results
            self._display_results(results, options.verbose)

            # Return appropriate exit code
            if results['errors'] or results['unsupported']:
                return 1
            return 0

        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return 73
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return 1

    def _validate_files(self, files: list[Path], verbose: bool) -> dict:
        """
        Validate a list of files.

        Args:
            files: List of file paths to validate
            verbose: Whether to include detailed info

        Returns:
            Dictionary with validation results
        """
        results = {
            'total': len(files),
            'readable': [],
            'unreadable': [],
            'unsupported': [],
            'errors': [],
            'by_type': defaultdict(int),
            'total_size_bytes': 0,
            'estimated_vault_size_bytes': 0
        }

        for file_path in files:
            try:
                # Check if readable
                if not file_path.is_file():
                    results['errors'].append((file_path, "Not a regular file"))
                    continue

                # Try to read first byte
                try:
                    with file_path.open('rb') as f:
                        _ = f.read(1)
                    results['readable'].append(file_path)
                except Exception as e:
                    results['unreadable'].append((file_path, str(e)))
                    continue

                # Detect MIME type
                try:
                    mime_type = self.mime_detector.detect(file_path)
                    results['by_type'][mime_type] += 1

                    # Check if supported (basic check)
                    if not self._is_supported_type(mime_type):
                        results['unsupported'].append((file_path, mime_type))

                except Exception as e:
                    results['errors'].append((file_path, f"MIME detection failed: {e}"))
                    continue

                # Calculate sizes
                size = file_path.stat().st_size
                results['total_size_bytes'] += size
                results['estimated_vault_size_bytes'] += size

            except Exception as e:
                results['errors'].append((file_path, str(e)))

        return results

    def _is_supported_type(self, mime_type: str) -> bool:
        """
        Check if MIME type is supported.

        Args:
            mime_type: MIME type string

        Returns:
            True if supported, False otherwise
        """
        supported_prefixes = [
            'image/',
            'video/',
            'audio/',
            'application/pdf',
            'application/zip',
            'application/x-rar',
            'application/x-tar',
            'application/gzip',
            'text/'
        ]

        return any(mime_type.startswith(prefix) for prefix in supported_prefixes)

    def _display_results(self, results: dict, verbose: bool) -> None:
        """
        Display validation results.

        Args:
            results: Validation results dictionary
            verbose: Whether to show detailed information
        """
        colors = self.formatter.colors

        print(colors.colorize("Validation Results", 'blue', bold=True))
        print("=" * 60)
        print()

        # Summary counts
        print(colors.colorize("Summary:", 'blue'))
        print(f"  Total files: {results['total']}")
        print(f"  Readable: {len(results['readable'])}")
        print(f"  Unreadable: {len(results['unreadable'])}")
        print(f"  Unsupported: {len(results['unsupported'])}")
        print(f"  Errors: {len(results['errors'])}")
        print()

        # Size estimates
        size_mb = results['total_size_bytes'] / (1024 * 1024)
        vault_size_mb = results['estimated_vault_size_bytes'] / (1024 * 1024)
        print(colors.colorize("Storage:", 'blue'))
        print(f"  Total size: {size_mb:.2f} MB")
        print(f"  Estimated vault size: {vault_size_mb:.2f} MB")
        print()

        # By type
        if verbose and results['by_type']:
            print(colors.colorize("By Type:", 'blue'))
            for mime_type, count in sorted(results['by_type'].items(), key=lambda x: -x[1]):
                print(f"  {mime_type}: {count}")
            print()

        # Issues
        if results['unreadable']:
            print(colors.colorize("Unreadable Files:", 'yellow', bold=True))
            for path, error in results['unreadable'][:10]:  # Show first 10
                print(f"  {path}: {error}")
            if len(results['unreadable']) > 10:
                print(f"  ... and {len(results['unreadable']) - 10} more")
            print()

        if results['unsupported']:
            print(colors.colorize("Unsupported Files:", 'yellow', bold=True))
            for path, mime_type in results['unsupported'][:10]:  # Show first 10
                print(f"  {path}: {mime_type}")
            if len(results['unsupported']) > 10:
                print(f"  ... and {len(results['unsupported']) - 10} more")
            print()

        if results['errors']:
            print(colors.colorize("Errors:", 'red', bold=True))
            for path, error in results['errors'][:10]:  # Show first 10
                print(f"  {path}: {error}")
            if len(results['errors']) > 10:
                print(f"  ... and {len(results['errors']) - 10} more")
            print()

        # Final verdict
        if not results['errors'] and not results['unreadable'] and not results['unsupported']:
            print(colors.success("✓ All files are valid and supported"))
        else:
            issues = len(results['errors']) + len(results['unreadable']) + len(results['unsupported'])
            print(colors.warning(f"⚠ {issues} file(s) may have issues"))

    def get_help(self) -> str:
        """
        Get command-specific help text.

        Returns:
            Help text with usage examples
        """
        return """
Validate source files before processing.

Usage:
  vault validate <source> [options]

Arguments:
  source              Source file or directory to validate

Options:
  --verbose          Show detailed information

Examples:
  # Validate a single file
  vault validate photo.jpg

  # Validate a directory
  vault validate /media/photos

  # Validate with detailed output
  vault validate /media/photos --verbose
"""
