"""
Argument parser for vault CLI.

Provides argparse-based command-line argument parsing.
"""

import argparse
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main CLI argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='vault',
        description='Vault - Personal file archive and organization system',
        epilog='Use "vault <command> --help" for command-specific help'
    )

    # Global options
    parser.add_argument(
        '--vault-root',
        type=Path,
        default=Path('./vault'),
        help='Vault root directory (default: ./vault)'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Configuration file path'
    )

    parser.add_argument(
        '--log-file',
        type=Path,
        help='Log file path'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Files per batch (default: 100)'
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=False
    )

    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process files into the vault'
    )
    process_parser.add_argument(
        'source',
        type=Path,
        help='Source file or directory to process'
    )
    process_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without making changes'
    )
    process_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )
    process_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output except errors'
    )

    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Display vault status'
    )
    status_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed statistics'
    )

    # Recover command
    recover_parser = subparsers.add_parser(
        'recover',
        help='Recover quarantined files'
    )
    recover_parser.add_argument(
        '--quarantine-type',
        type=str,
        help='Only recover specific type (e.g., "corrupt")'
    )
    recover_parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    recover_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without making changes'
    )
    recover_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )
    recover_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output except errors'
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate source files before processing'
    )
    validate_parser.add_argument(
        'source',
        type=Path,
        help='Source file or directory to validate'
    )
    validate_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    # Help command (manual handler)
    help_parser = subparsers.add_parser(
        'help',
        help='Show help for commands'
    )
    help_parser.add_argument(
        'help_command',
        nargs='?',
        help='Command to get help for'
    )

    return parser


def parse_args(args=None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of arguments (None to use sys.argv)

    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    return parser.parse_args(args)
