"""
T025: OrganizationDecision data model.
"""

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from .vault_path import VaultPath
from .classification import Classification
from .date_info import DateInfo


@dataclass
class OrganizationDecision:
    """Complete record of file organization decision with full audit trail."""

    file_path: Path
    vault_path: VaultPath
    classification: Classification
    date_info: DateInfo
    decision_timestamp: datetime
    preview_mode: bool
    execution_status: str
    error_message: str | None = None

    def __post_init__(self):
        """Validate organization decision after initialization."""
        valid_statuses = {"pending", "success", "failed"}
        if self.execution_status not in valid_statuses:
            raise ValueError(f"Invalid execution_status: {self.execution_status}")

        # Error message required when status is failed
        if self.execution_status == "failed" and self.error_message is None:
            raise ValueError("error_message required when status is 'failed'")

        # Preview mode should stay in pending
        if self.preview_mode and self.execution_status != "pending":
            raise ValueError("Preview mode must have 'pending' status")
