"""
Service Contract: CommandHandler

Base interface for CLI command implementations.
Defines the contract all commands must follow.
"""

from typing import Protocol
from src.models import CommandOptions, ProcessingResult


class CommandHandler(Protocol):
    """
    Base interface for CLI command implementations.

    All CLI commands (process, status, recover) implement this interface
    to ensure consistent behavior and error handling.

    Responsibilities:
    - Validate command-specific options
    - Execute command logic
    - Handle errors gracefully
    - Return result or exit code
    """

    def validate(self, options: CommandOptions) -> list[str]:
        """
        Validate command-specific options.

        Args:
            options: Parsed command-line options

        Returns:
            List of validation errors (empty if valid)

        Contract:
            - MUST check command-specific required arguments
            - MUST validate argument types and ranges
            - MUST return specific error messages
            - MUST not modify options
        """
        ...

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the command.

        Args:
            options: Parsed and validated command options

        Returns:
            Exit code (0 for success, non-zero for error)

        Contract:
            - MUST validate options before execution
            - MUST handle errors gracefully (no uncaught exceptions)
            - MUST return appropriate exit code
            - MUST print user-friendly output
            - MUST respect quiet/verbose flags
            - SHOULD log to file if log_file specified
        """
        ...

    def get_help(self) -> str:
        """
        Get command-specific help text.

        Returns:
            Help text with usage examples

        Contract:
            - MUST include command syntax
            - MUST include option descriptions
            - MUST include usage examples
            - SHOULD include common error scenarios
        """
        ...


class ProcessCommand(Protocol):
    """
    Main processing command: vault process <source>

    Executes the complete vault processing pipeline on source files.

    Responsibilities:
    - Validate source path
    - Create processing context
    - Execute pipeline orchestrator
    - Display progress
    - Generate summary
    """

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

        Contract:
            - MUST validate source path exists
            - MUST validate vault_root is writable
            - MUST create ProcessingContext
            - MUST execute PipelineOrchestrator
            - MUST display progress (unless --quiet)
            - MUST generate summary
            - MUST handle interruption gracefully
        """
        ...


class StatusCommand(Protocol):
    """
    Status checking command: vault status

    Displays current vault statistics and health status.

    Responsibilities:
    - Query database for statistics
    - Check vault integrity
    - Display quarantine summary
    - Report any issues
    """

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the status command.

        Args:
            options: Command options

        Returns:
            Exit code:
            - 0: Vault is healthy
            - 1: Vault has issues (quarantined files, etc.)

        Contract:
            - MUST query database for statistics
            - MUST check quarantine folders
            - MUST display file counts by type
            - MUST highlight any issues
            - SHOULD suggest recovery if needed
        """
        ...


class RecoverCommand(Protocol):
    """
    Recovery command: vault recover

    Attempts to reprocess files from quarantine.

    Responsibilities:
    - List quarantined files
    - Filter by quarantine type (if specified)
    - Reprocess through pipeline
    - Move successful files to vault
    - Report recovery results
    """

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the recover command.

        Args:
            options: Command options (may include quarantine_type filter)

        Returns:
            Exit code:
            - 0: All files recovered
            - 1: Some files still quarantined

        Contract:
            - MUST list quarantined files
            - MUST filter by quarantine_type if specified
            - MUST reprocess through pipeline
            - MUST update quarantine records
            - MUST display recovery summary
            - SHOULD ask confirmation unless --force
        """
        ...


class ValidateCommand(Protocol):
    """
    Validation command: vault validate <source>

    Validates files before processing (dry-run with checks).

    Responsibilities:
    - Check file accessibility
    - Detect file types
    - Estimate processing time
    - Report any issues
    """

    def execute(self, options: CommandOptions) -> int:
        """
        Execute the validate command.

        Args:
            options: Command options (must include source)

        Returns:
            Exit code:
            - 0: All files valid
            - 1: Some files have issues

        Contract:
            - MUST check all files are readable
            - MUST detect file types
            - MUST estimate disk space needed
            - MUST report any unsupported formats
            - MUST not modify any files
        """
        ...


# Example Usage
"""
from src.cli.commands import ProcessCommand
from src.models import CommandOptions

# Create command
cmd = ProcessCommand(
    orchestrator=orchestrator,
    progress_monitor=monitor,
    formatter=formatter
)

# Parse options
options = CommandOptions.from_args(args)

# Validate
errors = cmd.validate(options)
if errors:
    for error in errors:
        print(f"Error: {error}")
    sys.exit(2)

# Execute
exit_code = cmd.execute(options)
sys.exit(exit_code)
"""
