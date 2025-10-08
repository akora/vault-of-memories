"""
Recover command implementation.

Reprocesses quarantined files through the pipeline.
"""

import logging
from pathlib import Path
from typing import Optional

from src.models import CommandOptions, ProcessingContext
from src.services import PipelineOrchestrator, ProgressMonitor
from src.cli.formatters.summary_formatter import SummaryFormatter
from src.cli.formatters.progress_formatter import ProgressFormatter

logger = logging.getLogger(__name__)


class RecoverCommand:
    """
    Recovery command: vault recover

    Reprocesses files from quarantine through the pipeline.
    """

    def __init__(
        self,
        orchestrator: PipelineOrchestrator = None,
        quarantine_manager=None,
        progress_monitor: ProgressMonitor = None,
        formatter: SummaryFormatter = None
    ):
        """
        Initialize recover command.

        Args:
            orchestrator: Pipeline orchestrator instance (optional, will create default)
            quarantine_manager: Quarantine manager instance (optional, for future use)
            progress_monitor: Progress monitor instance (optional, will create default)
            formatter: Summary formatter instance (optional, will create default)
        """
        self.orchestrator = orchestrator
        self.quarantine_manager = quarantine_manager
        self.progress_monitor = progress_monitor
        self.formatter = formatter or SummaryFormatter()
        self.progress_formatter = ProgressFormatter()

    def validate(self, options: CommandOptions) -> list[str]:
        """
        Validate command-specific options.

        Args:
            options: Parsed command-line options

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not options.vault_root.exists():
            errors.append(f"Vault root does not exist: {options.vault_root}")

        return errors

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the recover command.

        Args:
            options: Command options (may include quarantine_type filter)

        Returns:
            Exit code:
            - 0: All files recovered successfully
            - 1: Some files failed recovery
            - 2: Invalid arguments
            - 65: Vault/quarantine not found
            - 130: User cancelled
        """
        # Validate options
        errors = self.validate(options)
        if errors:
            for error in errors:
                logger.error(error)
            return 65 if "does not exist" in errors[0] else 2

        quarantine_dir = options.vault_root / 'quarantine'

        # Check if quarantine exists
        if not quarantine_dir.exists():
            print(self.formatter.colors.success("✓ No quarantine directory found - nothing to recover"))
            return 0

        # Find quarantined files
        try:
            quarantined_files = self._find_quarantined_files(
                quarantine_dir,
                options.quarantine_type
            )
        except Exception as e:
            logger.error(f"Failed to list quarantined files: {e}")
            return 1

        if not quarantined_files:
            qtype_msg = f" of type '{options.quarantine_type}'" if options.quarantine_type else ""
            print(self.formatter.colors.success(f"✓ No quarantined files{qtype_msg} found"))
            return 0

        # Display summary
        print(self.formatter.colors.colorize("Quarantined Files:", 'yellow', bold=True))
        print(f"  Found: {len(quarantined_files)} files")
        if options.quarantine_type:
            print(f"  Type: {options.quarantine_type}")
        print()

        # Ask for confirmation unless --force
        if not options.force:
            response = input("Reprocess these files through the pipeline? [y/N]: ")
            if response.lower() not in ('y', 'yes'):
                print("Recovery cancelled")
                return 130

        # Create processing context for quarantine directory
        try:
            context = ProcessingContext(
                source_path=quarantine_dir,
                vault_root=options.vault_root,
                config={},
                dry_run=options.dry_run,
                verbose=options.verbose,
                max_workers=options.workers,
                batch_size=options.batch_size
            )
        except Exception as e:
            logger.error(f"Failed to create processing context: {e}")
            return 2

        # Setup progress callback (unless quiet)
        if not options.quiet:
            def progress_callback(state):
                progress_line = self.progress_formatter.format(state, detailed=False)
                print(f"\r{progress_line}", end="", flush=True)

            self.progress_monitor.subscribe(progress_callback)

        # Execute recovery
        try:
            logger.info(f"Starting recovery of {len(quarantined_files)} files")
            result = self.orchestrator.execute(context, progress_callback=None)

            # Clear progress line
            if not options.quiet:
                print()

            # Display summary
            summary = self.formatter.format_result(
                result,
                verbose=options.verbose,
                use_colors=not options.quiet
            )
            print(summary)

            # Return appropriate exit code
            if result.success:
                return 0
            else:
                return 1

        except KeyboardInterrupt:
            logger.info("\nRecovery interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"Recovery failed: {e}", exc_info=True)
            return 1

    def _find_quarantined_files(
        self,
        quarantine_dir: Path,
        quarantine_type: Optional[str] = None
    ) -> list[Path]:
        """
        Find quarantined files, optionally filtered by type.

        Args:
            quarantine_dir: Quarantine directory
            quarantine_type: Optional type filter (e.g., 'corrupt', 'unreadable')

        Returns:
            List of quarantined file paths
        """
        files = []

        if quarantine_type:
            # Search specific type directory
            type_dir = quarantine_dir / quarantine_type
            if type_dir.exists():
                files = [f for f in type_dir.rglob('*') if f.is_file()]
        else:
            # Search all quarantine subdirectories
            files = [f for f in quarantine_dir.rglob('*') if f.is_file()]

        return files

    def get_help(self) -> str:
        """
        Get command-specific help text.

        Returns:
            Help text with usage examples
        """
        return """
Recover quarantined files.

Usage:
  vault recover [options]

Options:
  --vault-root PATH         Vault root directory (default: ./vault)
  --quarantine-type TYPE    Only recover specific type (e.g., 'corrupt')
  --force                   Skip confirmation prompt
  --dry-run                Preview without making changes
  --verbose                 Show detailed progress
  --quiet                   Suppress output except errors

Examples:
  # Recover all quarantined files
  vault recover

  # Recover only corrupt files
  vault recover --quarantine-type corrupt

  # Preview recovery without changes
  vault recover --dry-run

  # Recover without confirmation
  vault recover --force
"""
