"""
Manufacturer name standardization service.

Normalizes device/camera manufacturer names using configurable mappings
to ensure consistent naming across the vault.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional


logger = logging.getLogger(__name__)


class ManufacturerStandardizer:
    """
    Standardize manufacturer names using configurable mappings.

    Handles case-insensitive matching and supports multiple aliases
    for each manufacturer.
    """

    # Default manufacturer mappings (lowercase key → standard name)
    DEFAULT_MAPPINGS = {
        # Camera manufacturers
        "nikon": "Nikon",
        "nikon corporation": "Nikon",
        "canon": "Canon",
        "canon inc.": "Canon",
        "sony": "Sony",
        "sony corporation": "Sony",
        "fujifilm": "Fujifilm",
        "fuji photo film co., ltd.": "Fujifilm",
        "olympus": "Olympus",
        "olympus corporation": "Olympus",
        "olympus imaging corp.": "Olympus",
        "panasonic": "Panasonic",
        "leica": "Leica",
        "leica camera ag": "Leica",
        "pentax": "Pentax",
        "ricoh": "Ricoh",
        "ricoh imaging company, ltd.": "Ricoh",
        "hasselblad": "Hasselblad",
        "sigma": "Sigma",
        "sigma corporation": "Sigma",

        # Phone manufacturers
        "apple": "Apple",
        "samsung": "Samsung",
        "samsung electronics": "Samsung",
        "google": "Google",
        "huawei": "Huawei",
        "xiaomi": "Xiaomi",
        "oneplus": "OnePlus",
        "motorola": "Motorola",
        "lg": "LG",
        "lg electronics": "LG",

        # Action cameras
        "gopro": "GoPro",
        "dji": "DJI",

        # Other devices
        "microsoft": "Microsoft",
        "adobe": "Adobe",
        "adobe systems": "Adobe",
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize manufacturer standardizer.

        Args:
            config_path: Optional path to manufacturer mappings configuration
        """
        self.mappings = self.DEFAULT_MAPPINGS.copy()

        if config_path and config_path.exists():
            self._load_config(config_path)

    def standardize(self, manufacturer: str) -> str:
        """
        Standardize manufacturer name using mapping rules.

        Performs case-insensitive matching. If no mapping found,
        returns the original name with capitalization cleaned up.

        Args:
            manufacturer: Original manufacturer name

        Returns:
            Standardized manufacturer name

        Raises:
            ValueError: If manufacturer name is invalid (empty or None)
        """
        if not manufacturer:
            raise ValueError("Manufacturer name cannot be empty")

        # Normalize for lookup
        manufacturer_lower = manufacturer.strip().lower()

        # Check for exact match in mappings
        if manufacturer_lower in self.mappings:
            standardized = self.mappings[manufacturer_lower]
            logger.debug(f"Standardized '{manufacturer}' → '{standardized}'")
            return standardized

        # No mapping found - clean up the original name
        cleaned = self._clean_manufacturer_name(manufacturer)
        logger.debug(f"No mapping for '{manufacturer}', using cleaned: '{cleaned}'")
        return cleaned

    def get_mappings(self) -> Dict[str, str]:
        """
        Get all manufacturer mappings.

        Returns:
            Dictionary mapping lowercase original names to standardized names
        """
        return self.mappings.copy()

    def add_mapping(self, original: str, standardized: str) -> None:
        """
        Add a new manufacturer mapping.

        Args:
            original: Original manufacturer name (will be lowercased)
            standardized: Standardized name to map to
        """
        original_lower = original.strip().lower()
        self.mappings[original_lower] = standardized
        logger.info(f"Added manufacturer mapping: '{original}' → '{standardized}'")

    def _clean_manufacturer_name(self, manufacturer: str) -> str:
        """
        Clean up manufacturer name when no mapping exists.

        Removes common suffixes and applies title case.

        Args:
            manufacturer: Original manufacturer name

        Returns:
            Cleaned manufacturer name
        """
        name = manufacturer.strip()

        # Remove common corporate suffixes
        suffixes_to_remove = [
            " corporation",
            " corp.",
            " corp",
            " inc.",
            " inc",
            " ltd.",
            " ltd",
            " limited",
            " co., ltd.",
            " co., ltd",
            " gmbh",
            " ag",
            " llc",
        ]

        name_lower = name.lower()
        for suffix in suffixes_to_remove:
            if name_lower.endswith(suffix):
                name = name[: -len(suffix)]
                break

        # Apply title case
        name = name.strip().title()

        return name

    def _load_config(self, config_path: Path) -> None:
        """
        Load manufacturer mappings from JSON configuration file.

        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Load manufacturer mappings
            if "manufacturer_mappings" in config:
                for original, standardized in config["manufacturer_mappings"].items():
                    original_lower = original.strip().lower()
                    self.mappings[original_lower] = standardized

                logger.info(
                    f"Loaded {len(config['manufacturer_mappings'])} "
                    f"manufacturer mappings from {config_path}"
                )

        except Exception as e:
            logger.error(f"Failed to load manufacturer mappings from {config_path}: {e}")
            raise
