#!/usr/bin/env python3
"""
Extract document outline from Markdown files.

This script parses Markdown files and extracts heading structure to create
a document outline that can be used for the RTM.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import json
import argparse
import logging
from pathlib import Path

# --- Start of standard boilerplate for scripts in packages ---
_self_path_extract_outline = Path(__file__).resolve()
# project_root/src/extractors/extract_outline.py -> project_root is parents[2]
_project_root_extract_outline = _self_path_extract_outline.parents[2]

if str(_project_root_extract_outline) not in sys.path:
    sys.path.insert(0, str(_project_root_extract_outline))

if __name__ == "__main__" and not __package__:
    _package_path = _self_path_extract_outline.parent.relative_to(
        _project_root_extract_outline
    )
    __package__ = str(_package_path).replace(
        os.sep, "."
    )  # Changed Path().sep to os.sep
# --- End of standard boilerplate ---

# Original PROJECT_ROOT definition can be removed or aliased if needed elsewhere:
# PROJECT_ROOT = _project_root_extract_outline

from src.utils.config_loader import (
    load_config,
)  # pylint: disable=wrong-import-position # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("extract_outline")


def extract_headings(markdown_text):
    """Extract all headings from markdown text and create a hierarchical structure."""
    heading_pattern = re.compile(
        r"^(#{1,6})\s+(.+?)(?:\s+\{#([a-zA-Z0-9_-]+)\})?\s*$", re.MULTILINE
    )
    headings = []

    for match in heading_pattern.finditer(markdown_text):
        level = len(match.group(1))
        text = match.group(2).strip()
        anchor = match.group(3) if match.group(3) else None

        headings.append(
            {
                "level": level,
                "text": text,
                "anchor": anchor,
            }
        )

    return headings


def build_outline(headings):
    """Build a hierarchical outline from a flat list of headings."""
    if not headings:
        return []

    # Create hierarchical structure
    outline = []
    stack = []  # Stack to track the parent relationships

    for heading in headings:
        # Create node for current heading
        node = {
            "text": heading["text"],
            "level": heading["level"],
            "anchor": heading["anchor"],
            "children": [],
        }

        # Find correct parent for this heading
        while stack and stack[-1]["level"] >= heading["level"]:
            stack.pop()

        if not stack:
            # This is a top-level heading
            outline.append(node)
        else:
            # This is a child heading
            stack[-1]["children"].append(node)

        # Add current node to stack
        stack.append(node)

    return outline


def process_markdown_file(file_path):
    """Process a single Markdown file and extract its outline."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract headings from content
        headings = extract_headings(content)

        # Build hierarchical outline
        outline = build_outline(headings)

        # Extract filename without extension for outline structure
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)

        return {"filename": filename, "name": name, "outline": outline}
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error processing %s: %s", file_path, str(e))
        return None


def main():
    """Main function to extract outlines from Markdown files."""
    parser = argparse.ArgumentParser(
        description="Extract document outline from Markdown files"
    )
    parser.add_argument("--input-dir", help="Directory containing Markdown files")
    parser.add_argument("--output-dir", help="Output directory for extracted outlines")

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Determine input and output directories
    input_dir = args.input_dir
    if not input_dir:
        input_dir = os.path.join(
            _project_root_extract_outline,
            config.get("paths", {}).get("output_dir", "output"),
        )

    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.join(
            _project_root_extract_outline,
            config.get("paths", {}).get("outline_dir", "outlines"),
        )

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all Markdown files in the input directory
    md_files = [f for f in os.listdir(input_dir) if f.endswith(".md")]

    if not md_files:
        logger.warning("No Markdown files found in %s", input_dir)
        return

    logger.info("Found %d Markdown files to process", len(md_files))

    # Process each file and save its outline
    outlines = {}
    for md_file in md_files:
        input_path = os.path.join(input_dir, md_file)
        logger.info("Processing %s", input_path)

        result = process_markdown_file(input_path)
        if result:
            outlines[result["name"]] = result

    # Save all outlines to a JSON file
    output_path = os.path.join(output_dir, "document_outlines.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(outlines, f, indent=2)

    logger.info("Outlines extracted and saved to %s", output_path)


if __name__ == "__main__":
    main()
