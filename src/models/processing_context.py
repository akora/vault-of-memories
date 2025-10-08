"""
Processing context model.

Configuration and state container for pipeline execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ProcessingContext:
    """
    Configuration and state for processing pipeline execution.

    Attributes:
        source_path: Path to source files or directory
        vault_root: Path to vault root directory
        config: Configuration settings from ConfigurationManager
        dry_run: If True, simulate operations without making changes
        verbose: Enable detailed logging
        max_workers: Number of parallel workers (future use)
        batch_size: Number of files to process per batch
        created_at: Timestamp when context was created
    """

    source_path: Path
    vault_root: Path
    config: dict
    dry_run: bool = False
    verbose: bool = False
    max_workers: int = 1
    batch_size: int = 100
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        if self.batch_size < 1:
            raise ValueError("batch_size must be > 0")
