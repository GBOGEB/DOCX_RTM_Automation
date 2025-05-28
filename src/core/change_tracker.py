#!/usr/bin/env python3
"""
Track and analyze changes between document versions.
Provides version history management and change reporting.
"""
import os
import sys
import json
import logging
import datetime
from pathlib import Path
import shutil
from typing import Dict, List, Any, Optional

import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ChangeTracker:
    """
    Track and analyze changes between document versions.
    """

    def __init__(self, history_dir: Optional[str] = None):
        """
        Initialize the change tracker.

        Args:
            history_dir: Directory for storing version history
        """
        self.project_root = PROJECT_ROOT
        self.history_dir = history_dir or os.path.join(self.project_root, "history")

        # Create history directory if it doesn't exist
        os.makedirs(self.history_dir, exist_ok=True)

    def record_version(self,
                      document_path: str,
                      version: str,
                      files: Dict[str, str] = None,
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Record a new version of a document."""
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract document base name
        doc_basename = os.path.basename(document_path)
        doc_name, _ = os.path.splitext(doc_basename)

        # Create version directory
        version_dir = os.path.join(self.history_dir, f"{doc_name}_{version}_{timestamp}")
        os.makedirs(version_dir, exist_ok=True)

        # Save main document
        doc_copy_path = os.path.join(version_dir, doc_basename)
        shutil.copy2(document_path, doc_copy_path)

        # Save related files
        saved_files = {}
        if files:
            for file_name, file_path in files.items():
                if os.path.exists(file_path):
                    file_basename = os.path.basename(file_path)
                    target_path = os.path.join(version_dir, file_basename)
                    shutil.copy2(file_path, target_path)
                    saved_files[file_name] = target_path

        # Create version metadata
        version_data = {
            "document_name": doc_name,
            "version": version,
            "timestamp": timestamp,
            "datetime": datetime.datetime.now().isoformat(),
            "original_path": document_path,
            "saved_path": doc_copy_path,
            "related_files": saved_files
        }

        # Add additional metadata
        if metadata:
            version_data["metadata"] = metadata

        # Save version metadata
        metadata_path = os.path.join(version_dir, "version_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)

        logger.info("Recorded version %s of %s in %s", version, doc_name, version_dir)

        return {
            "version": version,
            "timestamp": timestamp,
            "directory": version_dir,
            "document": doc_copy_path,
            "files": saved_files,
            "metadata": metadata_path
        }

    def get_document_versions(self, document_name: str) -> List[Dict[str, Any]]:
        """Get all recorded versions of a document."""
        versions = []

        if not os.path.exists(self.history_dir):
            return versions

        # Find all version directories for this document
        for item in os.listdir(self.history_dir):
            item_path = os.path.join(self.history_dir, item)

            # Check if this is a directory and starts with the document name
            if os.path.isdir(item_path) and item.startswith(f"{document_name}_"):
                metadata_path = os.path.join(item_path, "version_metadata.json")

                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        versions.append(metadata)
                    except Exception as e:  # pylint: disable=broad-except
                        logger.warning("Error reading metadata from %s: %s", metadata_path, e)

        # Sort versions by timestamp
        versions.sort(key=lambda x: x.get("timestamp", ""))

        return versions

    def generate_changelog(self,
                          document_name: str,
                          output_path: Optional[str] = None,
                          format_type: str = "markdown") -> Optional[str]:
        """Generate a changelog for a document."""
        # Get all versions
        versions = self.get_document_versions(document_name)

        if not versions:
            logger.warning(f"No versions found for document: {document_name}")
            return None

        # If no output path specified, create one
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.project_root,
                "output",
                "reports",
                f"{document_name}_changelog_{timestamp}.{format_type.lower()}"
            )

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate content based on format type
        if format_type.lower() == "markdown":
            content = self._generate_markdown_changelog(document_name, versions)
        elif format_type.lower() == "html":
            content = self._generate_html_changelog(
                document_name, versions
            )
        elif format_type.lower() in ["json", "yaml"]:
            content = self._generate_data_changelog(
                document_name, versions, format_type.lower()
            )
        else:
            logger.error("Unsupported format type: %s", format_type)

        # Write changelog
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info("Generated changelog for %s at %s", document_name, output_path)
            return output_path
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error writing changelog: %s", e)
            return None

    def _generate_html_changelog(self, document_name: str, versions: List[Dict[str, Any]]) -> str:
        """Generate HTML changelog."""
        content = f"<html><head><title>Changelog for {document_name}</title></head><body>"
        content += f"<h1>Changelog for {document_name}</h1>"
        content += f"<p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"

        # Add an entry for each version
        for version in versions:
            v_name = version.get("version", "unknown")
            v_time = version.get("timestamp", "unknown")
            content += f"<div><h2>Version: {v_name}</h2><p>Timestamp: {v_time}</p></div>"

        content += "</body></html>"
        return content

    def _generate_data_changelog(self, document_name: str, versions: List[Dict[str, Any]], format_type: str) -> str:
        """Generate JSON or YAML changelog."""
        changelog_data = {
            "document": document_name,
            "generated_at": datetime.datetime.now().isoformat(),
            "versions": versions
        }

        if format_type == "json":
            return json.dumps(changelog_data, indent=2)
        else:  # YAML
            return yaml.dump(changelog_data, default_flow_style=False)

    def _generate_markdown_changelog(self, document_name: str, versions: List[Dict[str, Any]]) -> str:
        """Generate Markdown changelog."""
        content = f"# Changelog for {document_name}\n\n"
        content += f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Add an entry for each version
        for i, version in enumerate(versions):
            v_name = version.get("version", "unknown")
            v_time = version.get("timestamp", "unknown")

            content += f"## Version {i + 1}: {v_name}\n"
            content += f"- Timestamp: {v_time}\n\n"

        # Return the generated content
        return content
