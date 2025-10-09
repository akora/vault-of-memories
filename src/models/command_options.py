"""
Command options model.

Parsed CLI arguments and configuration flags.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CommandOptions:
    """
    Parsed command-line arguments and options.

    Attributes:
        command: Subcommand name (process, status, recover)
        source: Source path (for process command)
        vault_root: Vault root directory path
        config_file: Path to configuration file
        dry_run: Preview mode flag
        verbose: Verbose output flag
        quiet: Suppress non-error output
        log_file: Path to log file
        workers: Number of parallel workers
        batch_size: Files per batch
        force: Force operation (skip confirmations)
        quarantine_type: Quarantine category for recovery
    """

    command: str
    source: Optional[Path] = None
    vault_root: Path = None
    config_file: Optional[Path] = None
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    log_file: Optional[Path] = None
    workers: int = 1
    batch_size: int = 100
    force: bool = False
    quarantine_type: Optional[str] = None
    timezone: Optional[str] = None  # e.g., "Asia/Tokyo", "America/New_York"

    def __post_init__(self):
        """Validate and set defaults."""
        # Set default vault_root if not provided
        if self.vault_root is None:
            self.vault_root = Path.cwd() / 'vault'

        # Validate mutually exclusive flags
        if self.verbose and self.quiet:
            raise ValueError("--verbose and --quiet are mutually exclusive")

        # Validate workers and batch_size
        if self.workers < 1:
            raise ValueError("workers must be >= 1")
        if self.batch_size < 1:
            raise ValueError("batch_size must be > 0")

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'CommandOptions':
        """
        Create CommandOptions from argparse.Namespace.

        Args:
            args: Parsed arguments from argparse

        Returns:
            CommandOptions instance
        """
        return cls(
            command=args.command,
            source=Path(args.source) if hasattr(args, 'source') and args.source else None,
            vault_root=Path(args.vault_root) if hasattr(args, 'vault_root') and args.vault_root else None,
            config_file=Path(args.config) if hasattr(args, 'config') and args.config else None,
            dry_run=getattr(args, 'dry_run', False),
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False),
            log_file=Path(args.log_file) if getattr(args, 'log_file', None) else None,
            workers=getattr(args, 'workers', 1),
            batch_size=getattr(args, 'batch_size', 100),
            force=getattr(args, 'force', False),
            quarantine_type=getattr(args, 'quarantine_type', None),
            timezone=getattr(args, 'timezone', None)
        )
