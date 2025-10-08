"""
Service factory for CLI.

Creates and wires together all services needed for the pipeline.
"""

from pathlib import Path

from src.services import (
    PipelineOrchestrator,
    ProgressMonitor,
    OrganizationManager,
    FileMover,
    QuarantineManager,
)
from src.services.database_manager import DatabaseManager
from src.services.file_ingestor import FileIngestorImpl
from src.services.metadata_consolidator import MetadataConsolidator
from src.services.duplicate_handler import DuplicateHandler
from src.services.integrity_verifier import IntegrityVerifier
from src.services.image_processor import ImageProcessorImpl
from src.services.document_processor import DocumentProcessorImpl
from src.services.audio_processor import AudioProcessorImpl
from src.services.video_processor import VideoProcessor


class ServiceFactory:
    """Factory for creating configured service instances."""

    @staticmethod
    def create_pipeline_orchestrator(vault_root: Path) -> PipelineOrchestrator:
        """
        Create a fully configured PipelineOrchestrator.

        Args:
            vault_root: Vault root directory path

        Returns:
            Configured PipelineOrchestrator instance
        """
        # Ensure vault root exists
        vault_root.mkdir(parents=True, exist_ok=True)

        # Create database path
        db_path = vault_root / ".vault.db"

        # Create database manager
        database_manager = DatabaseManager()

        # Create file ingestor
        file_ingestor = FileIngestorImpl(db_path)

        # Create metadata consolidator
        metadata_consolidator = MetadataConsolidator()

        # Register specialized processors
        metadata_consolidator.register_processor('image', ImageProcessorImpl())
        metadata_consolidator.register_processor('document', DocumentProcessorImpl())
        metadata_consolidator.register_processor('audio', AudioProcessorImpl())
        metadata_consolidator.register_processor('video', VideoProcessor())

        # Create organization manager
        organization_manager = OrganizationManager(vault_root)

        # Create quarantine manager
        quarantine_manager = QuarantineManager(vault_root)

        # Create duplicate handler
        # Note: DuplicateHandler expects (duplicate_database, vault_root)
        # For now, passing database_manager as placeholder for duplicate_database
        duplicate_handler = DuplicateHandler(database_manager, vault_root)

        # Create integrity verifier
        integrity_verifier = IntegrityVerifier()

        # Create file mover
        file_mover = FileMover(
            database_manager=database_manager,
            duplicate_handler=duplicate_handler,
            quarantine_manager=quarantine_manager,
            integrity_verifier=integrity_verifier
        )

        # Create and return orchestrator
        return PipelineOrchestrator(
            database_manager=database_manager,
            file_ingestor=file_ingestor,
            metadata_consolidator=metadata_consolidator,
            organization_manager=organization_manager,
            file_mover=file_mover
        )

    @staticmethod
    def create_progress_monitor() -> ProgressMonitor:
        """
        Create a ProgressMonitor instance.

        Returns:
            ProgressMonitor instance
        """
        return ProgressMonitor()
