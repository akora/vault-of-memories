"""
Metadata quality assessment service.

Evaluates the completeness and confidence of consolidated metadata,
providing scores and metrics for quality assessment.
"""

import logging
from typing import Dict
from collections import Counter

from ..models.consolidated_metadata import (
    ConsolidatedMetadata,
    MetadataQuality,
    MetadataSource,
    MetadataField
)


logger = logging.getLogger(__name__)


class MetadataQualityAssessor:
    """
    Assess the quality and completeness of consolidated metadata.

    Calculates:
    - Completeness score (percentage of fields populated)
    - Confidence score (average confidence from sources)
    - Source breakdown (count of fields from each source)
    """

    # Fields that contribute to quality scoring
    SCOREABLE_FIELDS = [
        "creation_date",
        "modification_date",
        "capture_date",
        "device_make",
        "device_model",
        "software",
        "gps_latitude",
        "gps_longitude",
        "gps_altitude",
        "location_name",
        "title",
        "description",
        "keywords",
        "category",
        "author",
        "copyright",
        "width",
        "height",
        "duration",
        "page_count",
    ]

    def assess_quality(self, metadata: ConsolidatedMetadata) -> MetadataQuality:
        """
        Assess the quality and completeness of consolidated metadata.

        Args:
            metadata: Consolidated metadata to assess

        Returns:
            MetadataQuality with scores and analysis

        Raises:
            ValueError: If metadata is invalid
        """
        if metadata is None:
            raise ValueError("Metadata cannot be None")

        # Count populated fields
        populated_fields = 0
        high_confidence_fields = 0
        total_confidence = 0.0
        confidence_count = 0
        source_counts = Counter()

        for field_name in self.SCOREABLE_FIELDS:
            field_value = getattr(metadata, field_name, None)

            if field_value is not None and isinstance(field_value, MetadataField):
                populated_fields += 1
                source_counts[field_value.source] += 1

                # Track confidence
                total_confidence += field_value.confidence
                confidence_count += 1

                if field_value.confidence > 0.8:
                    high_confidence_fields += 1

        # Calculate scores
        total_fields = len(self.SCOREABLE_FIELDS)
        completeness_score = populated_fields / total_fields if total_fields > 0 else 0.0
        confidence_score = total_confidence / confidence_count if confidence_count > 0 else 0.0

        # Get conflicts count
        conflicts_count = len(metadata.conflicts_detected)

        # Build source breakdown
        source_breakdown = dict(source_counts)

        return MetadataQuality(
            completeness_score=completeness_score,
            confidence_score=confidence_score,
            total_fields=total_fields,
            populated_fields=populated_fields,
            high_confidence_fields=high_confidence_fields,
            conflicts_count=conflicts_count,
            source_breakdown=source_breakdown
        )

    def get_scoreable_fields(self) -> list:
        """
        Get list of fields used in quality scoring.

        Returns:
            List of field names
        """
        return self.SCOREABLE_FIELDS.copy()

    def is_high_quality(self, quality: MetadataQuality, threshold: float = 0.7) -> bool:
        """
        Determine if metadata meets high quality standards.

        Args:
            quality: MetadataQuality assessment
            threshold: Minimum score for high quality (default 0.7)

        Returns:
            True if both completeness and confidence meet threshold
        """
        return (
            quality.completeness_score >= threshold and
            quality.confidence_score >= threshold
        )
