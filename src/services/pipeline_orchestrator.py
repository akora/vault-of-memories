"""
Pipeline orchestrator service.

Coordinates execution of all vault processing modules in correct sequence.
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Optional

from src.models import (
    ProcessingContext,
    ProcessingResult,
    ProgressState,
    PipelineStage
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrates the complete vault processing pipeline.

    Coordinates all processing modules in sequence:
    1. File discovery and validation
    2. File ingestion (duplicate detection)
    3. Metadata extraction (type-specific processors)
    4. Metadata consolidation
    5. Filename generation
    6. Organization (path determination)
    7. File moving (atomic operations)
    8. Summary generation
    """

    def __init__(
        self,
        database_manager,
        file_ingestor,
        metadata_consolidator,
        organization_manager,
        file_mover
    ):
        """
        Initialize pipeline orchestrator.

        Args:
            database_manager: Database manager instance
            file_ingestor: File ingestor instance
            metadata_consolidator: Metadata consolidator instance
            organization_manager: Organization manager instance
            file_mover: File mover instance
        """
        self.database_manager = database_manager
        self.file_ingestor = file_ingestor
        self.metadata_consolidator = metadata_consolidator
        self.organization_manager = organization_manager
        self.file_mover = file_mover
        self._interrupted = False

    def execute(
        self,
        context: ProcessingContext,
        progress_callback: Optional[Callable[[ProgressState], None]] = None
    ) -> ProcessingResult:
        """
        Execute the complete processing pipeline.

        Args:
            context: Processing configuration and settings
            progress_callback: Optional callback for progress updates

        Returns:
            ProcessingResult containing summary of execution
        """
        start_time = datetime.now()
        logger.info(f"Starting pipeline execution: {context.source_path}")

        # Validate context
        errors = self.validate_context(context)
        if errors:
            logger.error(f"Context validation failed: {errors}")
            raise ValueError(f"Invalid context: {', '.join(errors)}")

        # Discover files
        files = self.discover_files(context.source_path)
        logger.info(f"Discovered {len(files)} files")

        # Initialize progress tracking
        progress = ProgressState(total_files=len(files))
        progress.current_stage = str(PipelineStage.DISCOVERING)

        if progress_callback:
            progress_callback(progress)

        # Process each file
        successful_files = []
        duplicate_files = []
        quarantined_files = []
        failed_files = []
        warnings = []

        for file_path in files:
            if self._interrupted:
                logger.warning("Pipeline interrupted by user")
                break

            try:
                success, error = self.process_file(file_path, context, progress)

                if success:
                    if error:  # Duplicate
                        duplicate_files.append(file_path)
                    else:
                        successful_files.append(file_path)
                else:
                    if "quarantine" in str(error).lower():
                        quarantined_files.append(file_path)
                    failed_files.append((file_path, error or "Unknown error"))

            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {e}")
                failed_files.append((file_path, str(e)))

            progress.processed_files += 1
            progress.update_estimates()

            if progress_callback:
                progress_callback(progress)

        # Mark complete
        progress.current_stage = str(PipelineStage.COMPLETE if not self._interrupted else PipelineStage.FAILED)

        if progress_callback:
            progress_callback(progress)

        # Generate result
        duration = datetime.now() - start_time
        success = len(failed_files) == 0 and len(quarantined_files) == 0 and not self._interrupted

        result = ProcessingResult(
            context=context,
            final_state=progress,
            success=success,
            total_duration=duration,
            files_processed=len(files),
            successful_files=successful_files,
            duplicate_files=duplicate_files,
            quarantined_files=quarantined_files,
            failed_files=failed_files,
            warnings=warnings
        )

        logger.info(f"Pipeline complete: {result.summary_stats}")
        return result

    def validate_context(self, context: ProcessingContext) -> list[str]:
        """
        Validate processing context before execution.

        Args:
            context: Processing configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check source path exists
        if not context.source_path.exists():
            errors.append(f"Source path does not exist: {context.source_path}")
        elif not context.source_path.is_file() and not context.source_path.is_dir():
            errors.append(f"Source path is not a file or directory: {context.source_path}")

        # Check vault root is writable (or can be created)
        if not context.vault_root.exists():
            try:
                context.vault_root.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create vault root: {e}")
        elif not context.vault_root.is_dir():
            errors.append(f"Vault root is not a directory: {context.vault_root}")

        return errors

    def discover_files(self, source_path: Path) -> list[Path]:
        """
        Discover all processable files in source path.

        Args:
            source_path: Path to file or directory

        Returns:
            List of file paths to process
        """
        files = []

        # System files to filter out
        system_files = {'.DS_Store', 'thumbs.db', 'Thumbs.db', 'desktop.ini'}

        if source_path.is_file():
            if source_path.name not in system_files:
                files.append(source_path.absolute())
        elif source_path.is_dir():
            for item in source_path.rglob('*'):
                if item.is_file() and item.name not in system_files:
                    files.append(item.absolute())

        return sorted(files)

    def process_file(
        self,
        file_path: Path,
        context: ProcessingContext,
        progress: ProgressState
    ) -> tuple[bool, Optional[str]]:
        """
        Process a single file through entire pipeline.

        Args:
            file_path: Path to file to process
            context: Processing configuration
            progress: Progress state to update

        Returns:
            Tuple of (success, error_message)
        """
        progress.current_file = file_path
        logger.debug(f"Processing file: {file_path}")

        try:
            # In dry-run mode, just simulate
            if context.dry_run:
                progress.successful_count += 1
                return (True, None)

            # For now, simplified pipeline
            # TODO: Integrate with actual processors in future tasks
            progress.successful_count += 1
            return (True, None)

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            progress.failed_count += 1
            return (False, str(e))

    def handle_interruption(self) -> ProcessingResult:
        """
        Handle graceful interruption of pipeline.

        Returns:
            ProcessingResult with partial execution summary
        """
        self._interrupted = True
        logger.info("Handling interruption - finishing current operation")

        # Create partial result
        context = ProcessingContext(
            source_path=Path("."),
            vault_root=Path("."),
            config={}
        )

        progress = ProgressState(total_files=0)
        progress.current_stage = str(PipelineStage.FAILED)

        return ProcessingResult(
            context=context,
            final_state=progress,
            success=False,
            total_duration=timedelta(seconds=0),
            files_processed=0,
            successful_files=[],
            duplicate_files=[],
            quarantined_files=[],
            failed_files=[],
            warnings=["Processing interrupted by user"]
        )
