"""
Contract: IntegrityVerifier

The IntegrityVerifier service handles file integrity verification using checksums.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


# Input/Output Types
@dataclass
class IntegrityCheckResult:
    """See data-model.md for full specification"""
    file_path: Path
    expected_hash: str
    actual_hash: str
    match: bool
    check_time_ms: float
    algorithm: str
    file_size: int
    checked_at: datetime


# Contract Interface
class IntegrityVerifier:
    """
    Verifies file integrity using cryptographic hashes.
    """

    def calculate_hash(
        self,
        file_path: Path,
        algorithm: str = "sha256"
    ) -> str:
        """
        Calculate cryptographic hash of file.

        Contract:
        - MUST use streaming for large files (64KB chunks)
        - MUST support sha256, sha1, md5 algorithms
        - MUST return lowercase hex string
        - MUST handle missing files with FileNotFoundError
        - MUST handle permission errors gracefully

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hex string of file hash

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If algorithm not supported
        """
        raise NotImplementedError

    def verify_integrity(
        self,
        file_path: Path,
        expected_hash: str,
        algorithm: str = "sha256"
    ) -> IntegrityCheckResult:
        """
        Verify file integrity against expected hash.

        Contract:
        - MUST calculate file hash
        - MUST compare with expected hash (case-insensitive)
        - MUST track verification time
        - MUST return complete IntegrityCheckResult
        - MUST set match=True only if hashes equal

        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm (default: sha256)

        Returns:
            IntegrityCheckResult with verification outcome
        """
        raise NotImplementedError

    def batch_verify(
        self,
        files: list[tuple[Path, str]]
    ) -> list[IntegrityCheckResult]:
        """
        Verify integrity of multiple files.

        Contract:
        - MUST verify each file independently
        - MUST not stop on first failure
        - MUST return results in same order as input
        - MUST handle individual file errors gracefully

        Args:
            files: List of (file_path, expected_hash) tuples

        Returns:
            List of IntegrityCheckResult, one per file
        """
        raise NotImplementedError
