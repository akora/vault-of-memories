"""
ExifTool Wrapper
Provides a Python interface to the exiftool command-line tool.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


class ExifToolWrapper:
    """
    Wrapper for exiftool command-line tool.

    Provides a clean interface for extracting metadata from image files
    using the exiftool external dependency.
    """

    def __init__(self, exiftool_path: str = "exiftool"):
        """
        Initialize the ExifTool wrapper.

        Args:
            exiftool_path: Path to exiftool executable (default: "exiftool" in PATH)
        """
        self.logger = logging.getLogger(__name__)
        self.exiftool_path = exiftool_path
        self._version: Optional[str] = None

    def is_available(self) -> bool:
        """
        Check if exiftool is available on the system.

        Returns:
            True if exiftool can be executed, False otherwise
        """
        try:
            result = subprocess.run(
                [self.exiftool_path, "-ver"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_version(self) -> Optional[str]:
        """
        Get the version of exiftool.

        Returns:
            Version string or None if not available
        """
        if self._version:
            return self._version

        try:
            result = subprocess.run(
                [self.exiftool_path, "-ver"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            self._version = result.stdout.strip()
            return self._version
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.logger.error(f"Failed to get exiftool version: {e}")
            return None

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract all metadata from a file using exiftool.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary of metadata tags and values

        Raises:
            FileNotFoundError: If the file does not exist
            RuntimeError: If exiftool is not available or fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.is_available():
            raise RuntimeError("exiftool is not available on this system")

        try:
            # Run exiftool with JSON output for easy parsing
            result = subprocess.run(
                [
                    self.exiftool_path,
                    "-json",
                    "-G",  # Group names
                    "-n",  # Numeric output for some fields
                    "-coordFormat", "%.8f",  # GPS coordinate format
                    str(file_path)
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            # Parse JSON output
            metadata_list = json.loads(result.stdout)

            if not metadata_list:
                self.logger.warning(f"No metadata extracted from {file_path}")
                return {}

            # exiftool returns a list with one element
            return metadata_list[0]

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"exiftool timed out processing {file_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"exiftool failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse exiftool output: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error running exiftool: {e}")

    def extract_metadata_batch(self, file_paths: List[Path]) -> Dict[Path, Dict[str, Any]]:
        """
        Extract metadata from multiple files in a single exiftool invocation.

        This is more efficient than calling extract_metadata multiple times.

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping file paths to their metadata

        Raises:
            RuntimeError: If exiftool is not available or fails
        """
        if not self.is_available():
            raise RuntimeError("exiftool is not available on this system")

        # Filter out non-existent files
        existing_paths = [p for p in file_paths if p.exists()]
        if not existing_paths:
            return {}

        try:
            result = subprocess.run(
                [
                    self.exiftool_path,
                    "-json",
                    "-G",
                    "-n",
                    "-coordFormat", "%.8f",
                ] + [str(p) for p in existing_paths],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )

            metadata_list = json.loads(result.stdout)

            # Map results back to file paths
            result_dict = {}
            for metadata in metadata_list:
                source_file = metadata.get("SourceFile")
                if source_file:
                    result_dict[Path(source_file)] = metadata

            return result_dict

        except subprocess.TimeoutExpired:
            raise RuntimeError("exiftool batch processing timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"exiftool batch processing failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse exiftool batch output: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in batch processing: {e}")

    def get_tag(self, metadata: Dict[str, Any], tag_name: str, group: Optional[str] = None) -> Optional[Any]:
        """
        Get a specific tag value from metadata dictionary.

        Args:
            metadata: Metadata dictionary from extract_metadata
            tag_name: Name of the tag to retrieve
            group: Optional group name (e.g., "EXIF", "File")

        Returns:
            Tag value or None if not found
        """
        if group:
            key = f"{group}:{tag_name}"
            return metadata.get(key)

        # Try with common groups
        for group_name in ["EXIF", "XMP", "IPTC", "File", "Composite"]:
            key = f"{group_name}:{tag_name}"
            if key in metadata:
                return metadata[key]

        # Try without group
        return metadata.get(tag_name)

    def has_tag(self, metadata: Dict[str, Any], tag_name: str, group: Optional[str] = None) -> bool:
        """
        Check if a tag exists in metadata.

        Args:
            metadata: Metadata dictionary
            tag_name: Tag name to check
            group: Optional group name

        Returns:
            True if tag exists, False otherwise
        """
        return self.get_tag(metadata, tag_name, group) is not None
