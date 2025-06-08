#!/usr/bin/env python3
"""
RTM Roundtrip Controller - Manages the full Word to RTM roundtrip process:
1. Parse Word/PDF to Markdown
2. Extract structured data (JSON/YAML)
3. Analyze & improve content
4. Generate improved output in both MD and Word formats
5. Track and compare changes
"""

import os
import sys
import json
import yaml
import logging
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.word_to_md import WordToMarkdownConverter
from src.core.md_to_json_yaml import convert_md_to_structured
from src.extractors.extract_rtm import RTMExtractor
from src.visualizers.rtm_visualizer import RTMVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RTMRoundtrip:
    """
    Manages the full roundtrip process for RTM documents.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the RTM Roundtrip processor.

        Args:
            config_path: Path to configuration file
        """
        # Set up default paths
        self.project_root = PROJECT_ROOT
        self.input_dir = os.path.join(self.project_root, "input")
        self.output_dir = os.path.join(self.project_root, "output")
        self.temp_dir = os.path.join(self.project_root, "temp")
        self.history_dir = os.path.join(self.project_root, "history")

        # Load configuration if provided
        self.config = self._load_config(config_path)

        # Update paths from config
        if self.config:
            self.input_dir = self.config.get("input_dir", self.input_dir)
            self.output_dir = self.config.get("output_dir", self.output_dir)
            self.temp_dir = self.config.get("temp_dir", self.temp_dir)
            self.history_dir = self.config.get("history_dir", self.history_dir)

        # Initialize components
        self.word_converter = WordToMarkdownConverter(config_path)
        self.rtm_extractor = RTMExtractor()
        self.rtm_visualizer = RTMVisualizer()

        # Ensure directories exist
        for directory in [
            self.input_dir,
            self.output_dir,
            self.temp_dir,
            self.history_dir,
        ]:
            os.makedirs(directory, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not config_path:
            config_path = os.path.join(self.project_root, "config", "paths.yaml")

        if not os.path.exists(config_path):
            logger.warning(f"Configuration file not found: {config_path}")
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config or {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}

    def process_document(
        self, doc_path: str, version_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single document through the complete roundtrip.

        Args:
            doc_path: Path to the input document (DOCX/PDF)
            version_tag: Optional version tag for this document revision

        Returns:
            Dictionary with paths to generated artifacts
        """
        if not os.path.exists(doc_path):
            logger.error(f"Input document not found: {doc_path}")
            return {"error": f"Input document not found: {doc_path}"}

        # Generate timestamp and version info
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if not version_tag:
            version_tag = timestamp

        doc_filename = os.path.basename(doc_path)
        doc_name, doc_ext = os.path.splitext(doc_filename)

        # Step 1: Convert Word to Markdown
        logger.info(f"Step 1: Converting {doc_filename} to Markdown")
        md_path = os.path.join(self.output_dir, f"{doc_name}.md")
        self.word_converter.convert_file(doc_path, md_path)

        # Step 2: Extract JSON/YAML structured data
        logger.info("Step 2: Converting Markdown to structured data (JSON/YAML)")
        structured_data = convert_md_to_structured(md_path)

        # Step 3: Extract RTM data
        logger.info("Step 3: Extracting RTM data")
        rtm_path = os.path.join(self.output_dir, "rtm", f"{doc_name}_rtm.json")
        rtm_data = self.rtm_extractor.extract_from_file(md_path, rtm_path)

        # Step 4: Generate visualization
        logger.info("Step 4: Generating RTM visualization")
        viz_path = os.path.join(self.output_dir, "rtm_viz", f"{doc_name}_rtm.html")
        self.rtm_visualizer.visualize(rtm_path, viz_path, open_browser=False)

        # Step 5: Analyze and enhance the content
        logger.info("Step 5: Analyzing and enhancing content")
        enhanced_md_path = os.path.join(self.output_dir, f"{doc_name}_enhanced.md")
        enhanced_md = self.enhance_markdown(md_path, rtm_data)

        with open(enhanced_md_path, "w", encoding="utf-8") as f:
            f.write(enhanced_md)

        # Step 6: Generate improved Word document using Pandoc
        logger.info("Step 6: Converting enhanced Markdown back to Word")
        enhanced_docx_path = os.path.join(self.output_dir, f"{doc_name}_enhanced.docx")
        self.md_to_docx(enhanced_md_path, enhanced_docx_path)

        # Step 7: Save version history
        logger.info("Step 7: Saving version history")
        history_entry = self.save_history(
            doc_path, md_path, enhanced_md_path, rtm_path, version_tag, timestamp
        )

        # Step 8: Generate changelog
        logger.info("Step 8: Generating changelog")
        changelog_path = os.path.join(self.output_dir, f"{doc_name}_changelog.md")
        self.generate_changelog(doc_name, changelog_path)

        # Return paths to all generated files
        return {
            "input_docx": doc_path,
            "markdown": md_path,
            "json": structured_data.get("json") if structured_data else None,
            "yaml": structured_data.get("yaml") if structured_data else None,
            "rtm_data": rtm_path,
            "rtm_visualization": viz_path,
            "enhanced_markdown": enhanced_md_path,
            "enhanced_docx": enhanced_docx_path,
            "changelog": changelog_path,
            "history_entry": history_entry,
            "version": version_tag,
            "timestamp": timestamp,
        }

    def enhance_markdown(
        self, md_path: str, rtm_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze and enhance Markdown content with improvements.

        Args:
            md_path: Path to Markdown file
            rtm_data: RTM data for context (optional)

        Returns:
            Enhanced Markdown content
        """
        # Read original markdown
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        enhanced_content = content

        # Enhancement 1: Add header for tracking
        header = f"""---
title: Enhanced Document
date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
version: automated-enhancement
---

"""
        enhanced_content = header + enhanced_content

        # Enhancement 2: Standardize requirement formatting
        import re

        # Standardize requirement IDs (REQ-123) that aren't already in bold
        enhanced_content = re.sub(
            r"(?<!\*\*)(REQ-\d+(?:-\d+)*)(?!\*\*)", r"**\1**", enhanced_content
        )

        # Standardize test case IDs (TC-123) that aren't already in bold
        enhanced_content = re.sub(
            r"(?<!\*\*)(TC-\d+(?:-\d+)*)(?!\*\*)", r"**\1**", enhanced_content
        )

        # Enhancement 3: Improve traceability links
        enhanced_content = re.sub(
            r"(\*\*REQ-\d+(?:-\d+)*\*\*)\s*->\s*(\*\*TC-\d+(?:-\d+)*\*\*)",
            r"[\1] -> [\2]",
            enhanced_content,
        )

        # Enhancement 4: Add RTM summary if we have rtm_data
        if rtm_data:
            requirements = rtm_data.get("requirements", {})
            test_cases = rtm_data.get("test_cases", {})
            links = rtm_data.get("links", [])

            rtm_summary = f"""
## Requirements Traceability Summary

This document contains:
- {len(requirements)} requirements
- {len(test_cases)} test cases
- {len(links)} traceability links

"""
            enhanced_content = enhanced_content + "\n\n" + rtm_summary

        return enhanced_content

    def md_to_docx(self, md_path: str, docx_path: str) -> bool:
        """
        Convert Markdown to DOCX using Pandoc.

        Args:
            md_path: Path to Markdown file
            docx_path: Path to output DOCX file

        Returns:
            True if conversion succeeded, False otherwise
        """
        try:
            # Use Pandoc to convert Markdown to DOCX
            cmd = ["pandoc", md_path, "-o", docx_path, "--reference-doc=reference.docx"]

            # Check for custom reference document
            reference_doc = os.path.join(self.project_root, "config", "reference.docx")
            if os.path.exists(reference_doc):
                cmd = [
                    "pandoc",
                    md_path,
                    "-o",
                    docx_path,
                    f"--reference-doc={reference_doc}",
                ]

            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if os.path.exists(docx_path):
                logger.info(f"Successfully converted Markdown to DOCX: {docx_path}")
                return True
            else:
                logger.error("Pandoc completed but output file not found")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error(
                "Pandoc not found. Please install Pandoc to enable MD to DOCX conversion."
            )
            return False

    def save_history(
        self,
        docx_path: str,
        md_path: str,
        enhanced_md_path: str,
        rtm_path: str,
        version_tag: str,
        timestamp: str,
    ) -> Dict[str, Any]:
        """
        Save document artifacts to version history.

        Args:
            Various input and output paths
            version_tag: Version identifier
            timestamp: Processing timestamp

        Returns:
            Dictionary with history entry information
        """
        # Create history directory for this version
        doc_name = os.path.splitext(os.path.basename(docx_path))[0]
        version_dir = os.path.join(self.history_dir, f"{doc_name}_{timestamp}")
        os.makedirs(version_dir, exist_ok=True)

        # Copy artifacts to history
        history_files = {}

        for src_path, name in [
            (docx_path, "original.docx"),
            (md_path, "markdown.md"),
            (enhanced_md_path, "enhanced.md"),
            (rtm_path, "rtm.json"),
        ]:
            if os.path.exists(src_path):
                dest_path = os.path.join(version_dir, name)
                shutil.copy2(src_path, dest_path)
                history_files[name] = dest_path

        # Create metadata file
        metadata = {
            "document_name": doc_name,
            "version": version_tag,
            "timestamp": timestamp,
            "processed_date": datetime.datetime.now().isoformat(),
            "files": list(history_files.keys()),
        }

        metadata_path = os.path.join(version_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "version": version_tag,
            "timestamp": timestamp,
            "directory": version_dir,
            "files": history_files,
            "metadata": metadata_path,
        }

    def generate_changelog(self, doc_name: str, output_path: str) -> bool:
        """
        Generate changelog by comparing different document versions.

        Args:
            doc_name: Base name of the document
            output_path: Path to write the changelog

        Returns:
            True if changelog was generated, False otherwise
        """
        # Get all version directories for this document
        versions = []
        for item in os.listdir(self.history_dir):
            item_path = os.path.join(self.history_dir, item)
            if os.path.isdir(item_path) and item.startswith(doc_name + "_"):
                metadata_path = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                        versions.append((item, metadata))
                    except:
                        pass

        # Sort versions by timestamp
        versions.sort(key=lambda x: x[1].get("timestamp", ""))

        if len(versions) <= 1:
            logger.warning(f"Not enough versions to generate changelog for {doc_name}")
            return False

        # Generate changelog content
        changelog_content = f"# Changelog for {doc_name}\n\n"

        for i, (version_dir, metadata) in enumerate(versions):
            version = metadata.get("version", "unknown")
            timestamp = metadata.get("timestamp", "unknown")
            proc_date = metadata.get("processed_date", "unknown")

            changelog_content += f"## Version {version} ({timestamp})\n\n"
            changelog_content += f"Processed: {proc_date}\n\n"

            # If not the first version, compare with previous
            if i > 0:
                prev_version_dir, prev_metadata = versions[i - 1]
                prev_version = prev_metadata.get("version", "unknown")

                # Compare Markdown files
                prev_md_path = os.path.join(
                    self.history_dir, prev_version_dir, "markdown.md"
                )
                curr_md_path = os.path.join(
                    self.history_dir, version_dir, "markdown.md"
                )

                if os.path.exists(prev_md_path) and os.path.exists(curr_md_path):
                    changelog_content += f"### Changes from version {prev_version}\n\n"

                    try:
                        # Use a simple diff comparison
                        with open(prev_md_path, "r", encoding="utf-8") as f:
                            prev_content = f.readlines()

                        with open(curr_md_path, "r", encoding="utf-8") as f:
                            curr_content = f.readlines()

                        # Get differences
                        import difflib

                        diff = list(
                            difflib.unified_diff(prev_content, curr_content, n=1)
                        )

                        if diff:
                            changelog_content += (
                                "```diff\n" + "".join(diff) + "\n```\n\n"
                            )
                        else:
                            changelog_content += (
                                "No significant content changes detected.\n\n"
                            )

                    except Exception as e:
                        changelog_content += f"Error comparing files: {str(e)}\n\n"
                else:
                    changelog_content += (
                        "Cannot compare - previous version files not found.\n\n"
                    )

            changelog_content += "---\n\n"

        # Write changelog
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(changelog_content)
            logger.info(f"Changelog generated: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write changelog: {e}")
            return False

    def process_directory(
        self, input_dir: Optional[str] = None, version_tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all DOCX files in a directory.

        Args:
            input_dir: Directory with DOCX files
            version_tag: Optional version tag

        Returns:
            List of results for each document
        """
        if not input_dir:
            input_dir = self.input_dir

        if not os.path.isdir(input_dir):
            logger.error(f"Input directory not found: {input_dir}")
            return []

        # Find all DOCX files
        docx_files = []
        for file in os.listdir(input_dir):
            if file.lower().endswith(".docx") and not file.startswith("~$"):
                docx_files.append(os.path.join(input_dir, file))

        if not docx_files:
            logger.warning(f"No DOCX files found in {input_dir}")
            return []

        logger.info(f"Found {len(docx_files)} DOCX files to process")

        # Process each file
        results = []
        for docx_file in docx_files:
            result = self.process_document(docx_file, version_tag)
            results.append(result)

        return results
