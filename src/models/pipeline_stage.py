"""
Pipeline stage enumeration.

Defines all processing stages in the vault pipeline.
"""

from enum import Enum


class PipelineStage(Enum):
    """Processing pipeline stages."""

    INITIALIZING = "initializing"
    DISCOVERING = "discovering"
    INGESTING = "ingesting"
    EXTRACTING = "extracting"
    CONSOLIDATING = "consolidating"
    RENAMING = "renaming"
    ORGANIZING = "organizing"
    MOVING = "moving"
    SUMMARIZING = "summarizing"
    COMPLETE = "complete"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value
