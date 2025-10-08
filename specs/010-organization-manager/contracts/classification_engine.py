"""
Contract: ClassificationEngine

Content classification with fallback strategies.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Classification:
    """Result of file classification."""
    primary_category: str
    subcategory: str | None
    confidence: float
    reasoning: str
    mime_type: str
    detection_method: str


class ClassificationEngine:
    """
    Classifies files into vault categories using configurable rules.

    Responsibilities:
    - Detect file MIME type with fallback strategies
    - Apply classification rules based on content type
    - Handle ambiguous files with priority rules
    - Provide classification confidence and reasoning
    """

    def classify(self, file_path: Path, metadata: Dict[str, Any]) -> Classification:
        """
        Classify file into primary category and subcategory.

        Args:
            file_path: Path to file
            metadata: File metadata including type information

        Returns:
            Classification with category, confidence, and reasoning

        Raises:
            ValueError: If file_path is invalid
            OSError: If file cannot be read for classification

        Contract:
            - MUST return valid primary category (photos, documents, videos, audio, archives, other)
            - MUST attempt multiple detection methods: libmagic, extension, header inspection
            - MUST handle files with wrong/missing extensions
            - MUST apply priority rules for files matching multiple categories
            - Confidence MUST be 0.0-1.0 (0.95 for libmagic, 0.7 for extension, etc.)
            - MUST default to "other" category for unclassifiable files
            - MUST include reasoning for audit trail
        """
        raise NotImplementedError

    def classify_batch(
        self,
        file_paths: list[Path],
        metadata_dict: Dict[Path, Dict[str, Any]]
    ) -> Dict[Path, Classification]:
        """
        Classify multiple files efficiently.

        Args:
            file_paths: List of files to classify
            metadata_dict: Metadata for each file

        Returns:
            Dictionary mapping file paths to classifications

        Contract:
            - MUST handle batch processing efficiently
            - MUST NOT fail entire batch if one file fails
            - Failed files MUST return Classification with category="other", confidence=0.0
        """
        raise NotImplementedError

    def get_ambiguous_files(self) -> list[tuple[Path, Classification]]:
        """
        Get files flagged as ambiguous during classification.

        Returns:
            List of (file_path, classification) for files with confidence < 0.5

        Contract:
            - MUST track files classified with low confidence
            - MUST provide for manual review
        """
        raise NotImplementedError
