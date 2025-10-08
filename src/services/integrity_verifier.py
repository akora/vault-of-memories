"""
IntegrityVerifier service.
Verifies file integrity using cryptographic hashes.
"""

import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class IntegrityCheckResult:
    """Result of file integrity check"""
    file_path: Path
    expected_hash: str
    actual_hash: str
    match: bool
    check_time_ms: float
    algorithm: str
    file_size: int
    checked_at: datetime

    @property
    def integrity_valid(self) -> bool:
        """True if integrity check passed"""
        return self.match

    @property
    def throughput_mbps(self) -> float:
        """Throughput in MB/s during check"""
        if self.check_time_ms == 0:
            return 0.0
        size_mb = self.file_size / (1024 * 1024)
        time_s = self.check_time_ms / 1000
        return size_mb / time_s if time_s > 0 else 0.0


class IntegrityVerifier:
    """Verifies file integrity using cryptographic hashes"""

    SUPPORTED_ALGORITHMS = ['sha256', 'sha1', 'md5']

    def calculate_hash(self, file_path: Path, algorithm: str = "sha256") -> str:
        """
        Calculate cryptographic hash of file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hex string of file hash

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If algorithm not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Use one of {self.SUPPORTED_ALGORITHMS}")

        hash_obj = hashlib.new(algorithm)

        # Use streaming for large files (64KB chunks)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def verify_integrity(
        self,
        file_path: Path,
        expected_hash: str,
        algorithm: str = "sha256"
    ) -> IntegrityCheckResult:
        """
        Verify file integrity against expected hash.

        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm (default: sha256)

        Returns:
            IntegrityCheckResult with verification outcome
        """
        import time

        start_time = time.time()
        file_size = file_path.stat().st_size if file_path.exists() else 0

        try:
            actual_hash = self.calculate_hash(file_path, algorithm)
        except Exception:
            actual_hash = ""

        end_time = time.time()
        check_time_ms = (end_time - start_time) * 1000

        # Case-insensitive comparison
        match = actual_hash.lower() == expected_hash.lower()

        return IntegrityCheckResult(
            file_path=file_path,
            expected_hash=expected_hash.lower(),
            actual_hash=actual_hash.lower(),
            match=match,
            check_time_ms=check_time_ms,
            algorithm=algorithm,
            file_size=file_size,
            checked_at=datetime.now()
        )

    def batch_verify(
        self,
        files: List[Tuple[Path, str]],
        algorithm: str = "sha256"
    ) -> List[IntegrityCheckResult]:
        """
        Verify integrity of multiple files.

        Args:
            files: List of (file_path, expected_hash) tuples
            algorithm: Hash algorithm (default: sha256)

        Returns:
            List of IntegrityCheckResult, one per file
        """
        results = []

        for file_path, expected_hash in files:
            try:
                result = self.verify_integrity(file_path, expected_hash, algorithm)
                results.append(result)
            except Exception as e:
                # Create error result
                results.append(IntegrityCheckResult(
                    file_path=file_path,
                    expected_hash=expected_hash,
                    actual_hash="",
                    match=False,
                    check_time_ms=0.0,
                    algorithm=algorithm,
                    file_size=0,
                    checked_at=datetime.now()
                ))

        return results
