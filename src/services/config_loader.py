"""
T039: Configuration loader for classification rules.
"""

import json
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads configuration from JSON files."""

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Directory containing config files (defaults to ./config)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"

        self.config_dir = config_dir
        logger.info(f"ConfigLoader initialized with config_dir: {config_dir}")

    def load_classification_rules(self) -> dict:
        """Load classification rules from config/classification_rules.json"""
        config_file = self.config_dir / "classification_rules.json"

        if not config_file.exists():
            logger.warning(f"Classification rules file not found: {config_file}")
            return {"mime_to_category": {}, "fallback": {"default_category": "other"}}

        with open(config_file, 'r') as f:
            config = json.load(f)

        logger.info(f"Loaded {len(config.get('mime_to_category', {}))} classification rules")
        return config

    def load_folder_structure(self) -> dict:
        """Load folder structure configuration from config/folder_structure.json"""
        config_file = self.config_dir / "folder_structure.json"

        if not config_file.exists():
            logger.warning(f"Folder structure file not found: {config_file}")
            return {
                "vault_layout": {"date_hierarchy_format": "YYYY/YYYY-MM/YYYY-MM-DD"},
                "category_folders": {}
            }

        with open(config_file, 'r') as f:
            config = json.load(f)

        logger.info("Loaded folder structure configuration")
        return config
