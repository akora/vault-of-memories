"""
Main CLI entry point.

Coordinates argument parsing and command execution.
"""

import sys
import logging
from pathlib import Path

from src.cli.arg_parser import parse_args
from src.models import CommandOptions
from src.cli.commands import (
    ProcessCommand,
    StatusCommand,
    RecoverCommand,
    ValidateCommand
)
from src.cli.service_factory import ServiceFactory
from src.cli.formatters.summary_formatter import SummaryFormatter

logger = logging.getLogger(__name__)


def setup_logging(log_file: Path = None, verbose: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        log_file: Optional log file path
        verbose: Whether to use DEBUG level
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def create_command_options(args) -> CommandOptions:
    """
    Create CommandOptions from parsed arguments.

    Args:
        args: Parsed argparse.Namespace

    Returns:
        CommandOptions instance
    """
    return CommandOptions(
        command=args.command or 'help',
        source=getattr(args, 'source', None),
        vault_root=args.vault_root,
        config_file=args.config,
        log_file=args.log_file,
        dry_run=getattr(args, 'dry_run', False),
        verbose=getattr(args, 'verbose', False),
        quiet=getattr(args, 'quiet', False),
        workers=args.workers,
        batch_size=args.batch_size,
        quarantine_type=getattr(args, 'quarantine_type', None),
        force=getattr(args, 'force', False),
        timezone=getattr(args, 'timezone', None)
    )


def execute_command(options: CommandOptions) -> int:
    """
    Execute the specified command.

    Args:
        options: Command options

    Returns:
        Exit code
    """
    # Create shared services
    formatter = SummaryFormatter()

    # Route to appropriate command
    if options.command == 'process':
        # Create command first to validate options before creating expensive services
        command = ProcessCommand(
            orchestrator=None,  # Will be created on-demand
            progress_monitor=None,
            formatter=formatter
        )

        # Validate before creating services
        errors = command.validate(options)
        if errors:
            for error in errors:
                logger.error(error)
            return 2

        # Create services after validation passes
        orchestrator = ServiceFactory.create_pipeline_orchestrator(
            options.vault_root,
            timezone=options.timezone
        )
        progress_monitor = ServiceFactory.create_progress_monitor()
        command.orchestrator = orchestrator
        command.progress_monitor = progress_monitor

        return command.execute(options)

    elif options.command == 'status':
        command = StatusCommand(formatter=formatter)
        return command.execute(options)

    elif options.command == 'recover':
        orchestrator = ServiceFactory.create_pipeline_orchestrator(
            options.vault_root,
            timezone=options.timezone
        )
        progress_monitor = ServiceFactory.create_progress_monitor()
        command = RecoverCommand(
            orchestrator=orchestrator,
            progress_monitor=progress_monitor,
            formatter=formatter
        )
        return command.execute(options)

    elif options.command == 'validate':
        command = ValidateCommand(formatter=formatter)
        return command.execute(options)

    elif options.command == 'help':
        # Show general help
        from src.cli.arg_parser import create_parser
        parser = create_parser()
        parser.print_help()
        return 0

    else:
        logger.error(f"Unknown command: {options.command}")
        return 2


def main(argv=None) -> int:
    """
    Main entry point for vault CLI.

    Args:
        argv: Command-line arguments (None to use sys.argv)

    Returns:
        Exit code:
        - 0: Success
        - 1: General error
        - 2: Invalid arguments
        - 65: File/directory not found
        - 73: Permission denied
        - 130: Interrupted by user
    """
    try:
        # Parse arguments
        args = parse_args(argv)

        # Setup logging
        verbose = getattr(args, 'verbose', False)
        setup_logging(
            log_file=args.log_file,
            verbose=verbose
        )

        # Show help if no command specified
        if not args.command:
            from src.cli.arg_parser import create_parser
            parser = create_parser()
            parser.print_help()
            return 0

        # Create command options
        options = create_command_options(args)

        # Execute command
        exit_code = execute_command(options)

        return exit_code

    except KeyboardInterrupt:
        logger.info("\nOperation interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
