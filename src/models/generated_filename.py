"""
Generated filename model.

Defines data structure for filename generation results with metadata about
the generation process.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class GeneratedFilename:
    """
    Result of filename generation.

    Contains the generated filename, component mapping, and metadata about
    the generation process.
    """
    filename: str  # Generated filename with extension
    original_filename: str  # Original filename
    components_used: Dict[str, Any]  # Metadata components used in generation
    pattern_applied: str  # Pattern template that was used
    collision_counter: Optional[int] = None  # Counter if collision occurred (1-based)
    truncated: bool = False  # Whether filename was truncated
    sanitized_chars: int = 0  # Number of characters sanitized
    generation_timestamp: Optional[datetime] = None  # When generated
    warnings: List[str] = field(default_factory=list)  # Any warnings during generation
