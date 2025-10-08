"""
QuarantineManager service.
Manages quarantine operations for problematic files.
"""

import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.models.quarantine_record import QuarantineRecord, QuarantineReason


class QuarantineManager:
    """Manages quarantine operations for problematic files"""

    def __init__(self, quarantine_root: Path):
        self.quarantine_root = quarantine_root
        self.quarantine_root.mkdir(parents=True, exist_ok=True)

    def quarantine_file(
        self,
        source_path: Path,
        intended_destination: Path,
        error: Exception,
        metadata: dict
    ) -> QuarantineRecord:
        """
        Move file to quarantine with error classification.

        Args:
            source_path: Path to problematic file
            intended_destination: Where file was supposed to go
            error: Exception that caused quarantine
            metadata: File metadata

        Returns:
            QuarantineRecord with quarantine information

        Raises:
            PermissionError: If cannot access quarantine folder
        """
        # Classify error
        error_type = self.classify_error(error)

        # Generate quarantine path
        quarantine_path = self.get_quarantine_path(error_type, source_path.name)

        # Ensure quarantine subdirectory exists
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file to quarantine
        try:
            shutil.move(str(source_path), str(quarantine_path))
        except Exception as move_error:
            # If move fails, copy instead
            shutil.copy2(str(source_path), str(quarantine_path))

        # Create quarantine record
        quarantine_id = str(uuid.uuid4())
        record = QuarantineRecord(
            quarantine_id=quarantine_id,
            file_path=quarantine_path,
            original_path=source_path,
            intended_destination=intended_destination,
            error_type=error_type,
            error_message=str(error),
            quarantined_at=datetime.now(),
            recovery_attempts=0,
            file_size=quarantine_path.stat().st_size if quarantine_path.exists() else 0,
            error_traceback=self._get_traceback(error),
            metadata_snapshot=metadata,
            can_retry=self._can_retry(error_type)
        )

        # Save metadata JSON
        self._save_metadata_json(quarantine_path, record)

        return record

    def classify_error(self, error: Exception) -> QuarantineReason:
        """
        Classify exception into quarantine reason.

        Args:
            error: Exception to classify

        Returns:
            Appropriate QuarantineReason
        """
        if error is None:
            return QuarantineReason.UNKNOWN_ERROR

        error_type = type(error).__name__
        error_msg = str(error).lower()

        # Map exceptions to reasons
        if "checksum" in error_msg or "integrity" in error_msg or "hash" in error_msg:
            return QuarantineReason.CHECKSUM_MISMATCH
        elif "permission" in error_msg or isinstance(error, PermissionError):
            return QuarantineReason.PERMISSION_ERROR
        elif "disk" in error_msg or "space" in error_msg or isinstance(error, OSError):
            return QuarantineReason.DISK_SPACE_ERROR
        elif "path" in error_msg and "long" in error_msg:
            return QuarantineReason.PATH_TOO_LONG
        elif "invalid" in error_msg and "character" in error_msg:
            return QuarantineReason.INVALID_CHARACTERS
        elif "exists" in error_msg or isinstance(error, FileExistsError):
            return QuarantineReason.DESTINATION_EXISTS
        elif "network" in error_msg or "connection" in error_msg:
            return QuarantineReason.NETWORK_ERROR
        elif "corrupt" in error_msg:
            return QuarantineReason.CORRUPTION_DETECTED
        else:
            return QuarantineReason.UNKNOWN_ERROR

    def get_quarantine_path(self, error_type: QuarantineReason, filename: str) -> Path:
        """
        Calculate path for quarantined file.

        Args:
            error_type: Reason for quarantine
            filename: Original filename

        Returns:
            Path where file should be quarantined
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)

        # Build path: quarantine/{error_type}/{filename}
        quarantine_dir = self.quarantine_root / error_type.value
        quarantine_path = quarantine_dir / safe_filename

        # Handle collisions with timestamp
        if quarantine_path.exists():
            stem = quarantine_path.stem
            suffix = quarantine_path.suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{stem}_{timestamp}{suffix}"
            quarantine_path = quarantine_dir / safe_filename

        return quarantine_path

    def list_quarantined_files(
        self,
        error_type: Optional[QuarantineReason] = None
    ) -> List[QuarantineRecord]:
        """
        List files in quarantine, optionally filtered by error type.

        Args:
            error_type: Optional filter by error type

        Returns:
            List of QuarantineRecord
        """
        records = []

        # Determine directories to scan
        if error_type:
            dirs = [self.quarantine_root / error_type.value]
        else:
            dirs = [self.quarantine_root / reason.value for reason in QuarantineReason]

        # Scan directories
        for dir_path in dirs:
            if not dir_path.exists():
                continue

            for file_path in dir_path.glob("*"):
                if file_path.suffix == ".json":
                    continue  # Skip metadata files

                # Try to load metadata JSON
                json_path = file_path.with_suffix(file_path.suffix + ".json")
                if json_path.exists():
                    try:
                        with open(json_path, 'r') as f:
                            data = json.load(f)
                            # Reconstruct record from JSON
                            # (simplified - would need full deserialization)
                    except Exception:
                        pass

        return records

    def _get_traceback(self, error: Exception) -> Optional[str]:
        """Extract traceback from exception"""
        import traceback
        try:
            return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        except Exception:
            return None

    def _can_retry(self, error_type: QuarantineReason) -> bool:
        """Determine if error type allows retry"""
        retry_allowed = {
            QuarantineReason.PERMISSION_ERROR,
            QuarantineReason.DISK_SPACE_ERROR,
            QuarantineReason.NETWORK_ERROR,
            QuarantineReason.DESTINATION_EXISTS
        }
        return error_type in retry_allowed

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        import re
        # Remove invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Truncate if too long
        if len(safe) > 200:
            stem = safe[:190]
            suffix = Path(filename).suffix
            safe = stem + suffix
        return safe

    def _save_metadata_json(self, quarantine_path: Path, record: QuarantineRecord):
        """Save quarantine metadata as JSON"""
        json_path = quarantine_path.with_suffix(quarantine_path.suffix + ".json")

        metadata = {
            "quarantine_id": record.quarantine_id,
            "original_path": str(record.original_path),
            "intended_destination": str(record.intended_destination),
            "error_type": record.error_type.value,
            "error_message": record.error_message,
            "quarantined_at": record.quarantined_at.isoformat(),
            "recovery_attempts": record.recovery_attempts,
            "file_size": record.file_size,
            "can_retry": record.can_retry
        }

        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
