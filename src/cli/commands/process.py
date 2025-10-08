"""
Process command implementation.

Main processing command that executes the complete vault pipeline.
"""

import logging
import sys
from pathlib import Path

from src.models import CommandOptions, ProcessingContext
from src.services import PipelineOrchestrator, ProgressMonitor
from src.cli.formatters.summary_formatter import SummaryFormatter
from src.cli.formatters.progress_formatter import ProgressFormatter

logger = logging.getLogger(__name__)


class ProcessCommand:
    """
    Main processing command: vault process <source>

    Executes the complete vault processing pipeline on source files.
    """

    def __init__(
        self,
        orchestrator: PipelineOrchestrator,
        progress_monitor: ProgressMonitor,
        formatter: SummaryFormatter
    ):
        """
        Initialize process command.

        Args:
            orchestrator: Pipeline orchestrator instance
            progress_monitor: Progress monitor instance
            formatter: Summary formatter instance
        """
        self.orchestrator = orchestrator
        self.progress_monitor = progress_monitor
        self.formatter = formatter
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

        if not options.source:
            errors.append("Source path is required for process command")
        elif not options.source.exists():
            errors.append(f"Source path does not exist: {options.source}")

        return errors

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the process command.

        Args:
            options: Command options (must include source)

        Returns:
            Exit code:
            - 0: All files processed successfully
            - 1: Some files failed (check summary)
            - 2: Invalid arguments
            - 65: Source not found
            - 73: Cannot write to vault
        """
        # Validate options
        errors = self.validate(options)
        if errors:
            for error in errors:
                logger.error(error)
            return 2

        # Create processing context
        try:
            context = ProcessingContext(
                source_path=options.source,
                vault_root=options.vault_root,
                config={},  # TODO: Load from config file if specified
                dry_run=options.dry_run,
                verbose=options.verbose,
                max_workers=options.workers,
                batch_size=options.batch_size
            )
        except Exception as e:
            logger.error(f"Failed to create processing context: {e}")
            return 2

        # Display dry-run notice
        if options.dry_run:
            print(self.formatter.colors.warning("DRY RUN - No files will be modified"))
            print()

        # Setup progress callback (unless quiet)
        if not options.quiet:
            def progress_callback(state):
                progress_line = self.progress_formatter.format(state, detailed=False)
                print(f"\r{progress_line}", end="", flush=True)

            self.progress_monitor.subscribe(progress_callback)

        # Execute pipeline
        try:
            logger.info(f"Starting processing: {options.source}")
            result = self.orchestrator.execute(context, progress_callback=None)

            # Clear progress line
            if not options.quiet:
                print()  # New line after progress

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
            logger.info("\nProcessing interrupted by user")
            return 130
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return 73
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return 65
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return 1

    def get_help(self) -> str:
        """
        Get command-specific help text.

        Returns:
            Help text with usage examples
        """
        return """
Process files into the vault.

Usage:
  vault process <source> [options]

Arguments:
  source              Source file or directory to process

Options:
  --vault-root PATH   Vault root directory (default: ./vault)
  --dry-run          Preview without making changes
  --verbose          Show detailed progress
  --quiet            Suppress output except errors
  --workers N        Number of parallel workers (default: 1)
  --batch-size N     Files per batch (default: 100)

Examples:
  # Process a single file
  vault process photo.jpg

  # Process a directory
  vault process /media/photos --verbose

  # Preview without changes
  vault process /media/photos --dry-run

  # Use custom vault location
  vault process photo.jpg --vault-root /backup/vault
"""
