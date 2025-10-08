"""
Status command implementation.

Displays vault status including file counts and quarantine info.
"""

import logging
from pathlib import Path
from typing import Optional

from src.models import CommandOptions
from src.cli.formatters.summary_formatter import SummaryFormatter

logger = logging.getLogger(__name__)


class StatusCommand:
    """
    Status command: vault status

    Displays current vault status including statistics and quarantine info.
    """

    def __init__(self, database_manager=None, formatter: SummaryFormatter = None):
        """
        Initialize status command.

        Args:
            database_manager: Database manager instance (optional, for future use)
            formatter: Summary formatter instance (optional, will create default)
        """
        self.database_manager = database_manager
        self.formatter = formatter or SummaryFormatter()

    def validate(self, options: CommandOptions) -> list[str]:
        """
        Validate command-specific options.

        Args:
            options: Parsed command-line options

        Returns:
            List of validation errors (empty if valid)
        """
        # Status command doesn't require vault to exist - it can report on empty/missing vault
        return []

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the status command.

        Args:
            options: Command options

        Returns:
            Exit code:
            - 0: Vault is healthy or empty
            - 1: Vault has issues (quarantined files, etc.)
        """
        vault_root = options.vault_root

        try:
            # Gather vault statistics
            stats = self._gather_statistics(vault_root)

            # Format and display status
            status_output = self._format_status(stats, options.verbose)
            print(status_output)

            # Return non-zero if there are issues
            if stats.get('quarantine_count', 0) > 0:
                return 1

            return 0

        except Exception as e:
            logger.error(f"Failed to retrieve vault status: {e}", exc_info=True)
            return 1

    def _gather_statistics(self, vault_root: Path) -> dict:
        """
        Gather statistics about the vault.

        Args:
            vault_root: Vault root directory

        Returns:
            Dictionary with statistics
        """
        stats = {
            'vault_root': vault_root,
            'total_files': 0,
            'by_type': {},
            'quarantine_count': 0,
            'quarantine_by_type': {},
            'vault_size_bytes': 0
        }

        # Check if vault exists
        if not vault_root.exists():
            return stats

        # Count files in vault (excluding quarantine)
        vault_files = [
            f for f in vault_root.rglob('*')
            if f.is_file() and 'quarantine' not in f.parts
        ]
        stats['total_files'] = len(vault_files)

        # Calculate total size
        stats['vault_size_bytes'] = sum(f.stat().st_size for f in vault_files)

        # Count by type (simple extension-based)
        for file_path in vault_files:
            ext = file_path.suffix.lower()
            stats['by_type'][ext] = stats['by_type'].get(ext, 0) + 1

        # Count quarantine files
        quarantine_dir = vault_root / 'quarantine'
        if quarantine_dir.exists():
            for qtype_dir in quarantine_dir.iterdir():
                if qtype_dir.is_dir():
                    qfiles = list(qtype_dir.glob('*'))
                    count = len([f for f in qfiles if f.is_file()])
                    if count > 0:
                        stats['quarantine_by_type'][qtype_dir.name] = count
                        stats['quarantine_count'] += count

        return stats

    def _format_status(self, stats: dict, verbose: bool) -> str:
        """
        Format status output.

        Args:
            stats: Statistics dictionary
            verbose: Whether to show detailed information

        Returns:
            Formatted status string
        """
        lines = []
        colors = self.formatter.colors

        # Header
        lines.append(colors.colorize("Vault Status", 'blue', bold=True))
        lines.append("=" * 60)
        lines.append("")

        # Vault location
        lines.append(f"Vault Root: {stats['vault_root']}")

        # Check if vault exists
        if not Path(stats['vault_root']).exists():
            lines.append(colors.warning("  (Vault does not exist yet)"))
            lines.append("")
            lines.append(colors.colorize("No files in vault", 'blue'))
            return "\n".join(lines)

        lines.append("")

        # File counts
        lines.append(colors.colorize("Files in Vault:", 'blue', bold=True))
        lines.append(f"  Total: {stats['total_files']}")

        # Size
        size_mb = stats['vault_size_bytes'] / (1024 * 1024)
        lines.append(f"  Size: {size_mb:.2f} MB")
        lines.append("")

        # By type (if verbose)
        if verbose and stats['by_type']:
            lines.append(colors.colorize("By File Type:", 'blue'))
            for ext, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
                lines.append(f"  {ext or '(no ext)'}: {count}")
            lines.append("")

        # Quarantine status
        if stats['quarantine_count'] > 0:
            lines.append(colors.colorize("Quarantine:", 'yellow', bold=True))
            lines.append(f"  Total: {stats['quarantine_count']}")

            if stats['quarantine_by_type']:
                for qtype, count in stats['quarantine_by_type'].items():
                    lines.append(f"    {qtype}: {count}")

            lines.append("")
            lines.append(colors.warning("⚠ Some files are in quarantine. Use 'vault recover' to reprocess."))
        else:
            lines.append(colors.success("✓ No files in quarantine"))

        return "\n".join(lines)

    def get_help(self) -> str:
        """
        Get command-specific help text.

        Returns:
            Help text with usage examples
        """
        return """
Display vault status.

Usage:
  vault status [options]

Options:
  --vault-root PATH   Vault root directory (default: ./vault)
  --verbose          Show detailed statistics

Examples:
  # Check vault status
  vault status

  # Check status with details
  vault status --verbose

  # Check custom vault location
  vault status --vault-root /backup/vault
"""
