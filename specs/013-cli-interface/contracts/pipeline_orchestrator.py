"""
Service Contract: PipelineOrchestrator

Coordinates execution of all vault processing modules in correct sequence.
Manages progress tracking, error handling, and result aggregation.
"""

from pathlib import Path
from typing import Protocol, Callable
from src.models import ProcessingContext, ProcessingResult, ProgressState


class PipelineOrchestrator(Protocol):
    """
    Orchestrates the complete vault processing pipeline.

    The orchestrator coordinates all processing modules in sequence:
    1. File discovery and validation
    2. File ingestion (duplicate detection)
    3. Metadata extraction (type-specific processors)
    4. Metadata consolidation
    5. Filename generation
    6. Organization (path determination)
    7. File moving (atomic operations)
    8. Summary generation

    Responsibilities:
    - Execute pipeline stages in correct order
    - Track progress through all stages
    - Handle errors gracefully (quarantine files)
    - Aggregate results from all stages
    - Support dry-run mode (simulation)
    - Enable graceful interruption
    """

    def execute(
        self,
        context: ProcessingContext,
        progress_callback: Callable[[ProgressState], None] | None = None
    ) -> ProcessingResult:
        """
        Execute the complete processing pipeline.

        Args:
            context: Processing configuration and settings
            progress_callback: Optional callback for progress updates

        Returns:
            ProcessingResult containing summary of execution

        Raises:
            ValueError: If context validation fails
            FileNotFoundError: If source path doesn't exist
            PermissionError: If vault_root is not writable

        Contract:
            - MUST validate context before starting
            - MUST discover all files before processing
            - MUST execute stages in defined order
            - MUST update progress after each file
            - MUST handle errors without stopping pipeline
            - MUST respect dry_run mode (no modifications)
            - MUST generate result even on partial failure
            - SHOULD call progress_callback every 100ms or per file
        """
        ...

    def validate_context(self, context: ProcessingContext) -> list[str]:
        """
        Validate processing context before execution.

        Args:
            context: Processing configuration to validate

        Returns:
            List of validation errors (empty if valid)

        Contract:
            - MUST check source_path exists and is readable
            - MUST check vault_root is writable (or creatable)
            - MUST validate configuration settings
            - MUST return specific error messages
        """
        ...

    def discover_files(self, source_path: Path) -> list[Path]:
        """
        Discover all processable files in source path.

        Args:
            source_path: Path to file or directory

        Returns:
            List of file paths to process

        Contract:
            - MUST handle both files and directories
            - MUST recurse into subdirectories
            - MUST filter out system files (.DS_Store, thumbs.db)
            - MUST return absolute paths
            - MUST handle symbolic links safely
        """
        ...

    def process_file(
        self,
        file_path: Path,
        context: ProcessingContext,
        progress: ProgressState
    ) -> tuple[bool, str | None]:
        """
        Process a single file through entire pipeline.

        Args:
            file_path: Path to file to process
            context: Processing configuration
            progress: Progress state to update

        Returns:
            Tuple of (success, error_message)
            success=True, error=None: File processed successfully
            success=True, error=None: File is duplicate (success)
            success=False, error=msg: File quarantined or failed

        Contract:
            - MUST update progress.current_file
            - MUST execute all pipeline stages
            - MUST handle errors gracefully (quarantine)
            - MUST update appropriate counters in progress
            - MUST respect context.dry_run mode
            - MUST return specific error message on failure
        """
        ...

    def handle_interruption(self) -> ProcessingResult:
        """
        Handle graceful interruption of pipeline.

        Returns:
            ProcessingResult with partial execution summary

        Contract:
            - MUST finish current file operation
            - MUST save current progress state
            - MUST close database connections
            - MUST generate partial result
            - MUST mark result as interrupted
        """
        ...


class InterruptHandler(Protocol):
    """
    Handles graceful interruption signals (SIGINT, SIGTERM).

    Responsibilities:
    - Register signal handlers
    - Coordinate with orchestrator for cleanup
    - Ensure data integrity during interruption
    """

    def register(self, orchestrator: PipelineOrchestrator) -> None:
        """
        Register signal handlers for graceful interruption.

        Args:
            orchestrator: Pipeline orchestrator to coordinate with

        Contract:
            - MUST register SIGINT handler (Ctrl+C)
            - MUST register SIGTERM handler (kill)
            - MUST coordinate with orchestrator for cleanup
            - SHOULD print user-friendly interruption message
        """
        ...

    def is_interrupted(self) -> bool:
        """
        Check if interruption signal was received.

        Returns:
            True if interrupted, False otherwise

        Contract:
            - MUST return immediately (no blocking)
            - MUST be thread-safe
        """
        ...


# Example Usage
"""
from src.services import PipelineOrchestrator, InterruptHandler
from src.models import ProcessingContext

# Setup
orchestrator = PipelineOrchestrator(
    database_manager=db,
    file_ingestor=ingestor,
    metadata_consolidator=consolidator,
    organization_manager=org_mgr,
    file_mover=mover
)

interrupt_handler = InterruptHandler()
interrupt_handler.register(orchestrator)

# Create context
context = ProcessingContext(
    source_path=Path("/source"),
    vault_root=Path("/vault"),
    config=config,
    dry_run=False
)

# Execute with progress callback
def on_progress(state: ProgressState):
    print(f"Progress: {state.percent_complete:.1f}%")

result = orchestrator.execute(context, progress_callback=on_progress)

# Check result
if result.success:
    print(f"✓ Processed {result.files_processed} files")
else:
    print(f"✗ Completed with errors: {len(result.failed_files)} failed")
"""
