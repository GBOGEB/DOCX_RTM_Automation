#!/usr/bin/env python3
"""
Enhanced DOCX to Markdown Conversion with Structure Extraction

This script converts Word documents to Markdown and extracts
document structure information for visualization.
"""

import sys
import subprocess
import argparse
import json
import logging
from pathlib import Path

# Add parent directory to path for imports
# Use Path for robust path manipulation
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import structure generator
try:
    from src.modules.structure_generator import extract_structure_from_md
except ImportError:
    print("Warning: Could not import structure_generator module.")
    extract_structure_from_md = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def convert_docx_to_md(
    input_file: Path,
    output_file: Path,
    structure_output: Path = None,
    lua_filter: Path = None,
):
    """
    Convert DOCX to Markdown with structure extraction

    Args:
        input_file: Path to input DOCX file
        output_file: Path to output Markdown file
        structure_output: Path to save document structure
        lua_filter: Path to Lua filter for structure extraction

    Returns:
        True if conversion was successful
    """
    try:
        # Ensure input file exists
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            return False

        # Create output directories
        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build Pandoc command
        cmd = ["pandoc", str(input_file), "-o", str(output_file), "--wrap=none"]

        # Add structure extraction filter if provided
        if lua_filter and lua_filter.exists():
            cmd.extend(["--lua-filter", str(lua_filter)])
            logger.info(f"Using structure extraction filter: {lua_filter}")
        elif lua_filter:
            logger.warning(
                f"Lua filter not found: {lua_filter}, proceeding without it."
            )

        # Add common options
        media_dir = output_dir / "media"
        cmd.extend(["--extract-media", str(media_dir)])
        cmd.extend(["--standalone", "--toc", "--toc-depth=6", "--number-sections"])

        # Run Pandoc
        logger.info(f"Converting {input_file} to {output_file}")
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed: {result.stderr}")
            return False

        logger.info("Conversion completed successfully")

        # Generate structure visualization
        if structure_output:
            # If we have the structure_generator module, use it directly
            if extract_structure_from_md:
                logger.info(f"Generating document structure to {structure_output}")
                # Ensure structure_output directory exists
                structure_output.parent.mkdir(parents=True, exist_ok=True)
                if not extract_structure_from_md(
                    str(output_file), str(structure_output)
                ):
                    logger.warning("Failed to generate document structure directly")
            # Alternatively, if we have raw structure from Lua filter, process it
            else:
                # Assuming raw_structure_file is relative to project output or a defined path
                raw_structure_file = PROJECT_ROOT / "output/document_structure_raw.json"
                if raw_structure_file.exists():
                    logger.info(f"Processing raw structure from {raw_structure_file}")
                    with open(raw_structure_file, "r", encoding="utf-8") as f:
                        try:
                            structure_data = json.load(f)
                            # Ensure structure_output directory exists
                            structure_output.parent.mkdir(parents=True, exist_ok=True)
                            generate_structure_txt(structure_data, structure_output)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in {raw_structure_file}")
                else:
                    logger.warning(
                        f"Raw structure file not found: {raw_structure_file}"
                    )

        return True

    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return False


def generate_structure_txt(structure_data, output_file: Path):
    """
    Generate document structure visualization from raw structure data

    Args:
        structure_data: Dictionary with structure information
        output_file: Path to save structure visualization
    """
    try:
        # Get document title
        doc_title = structure_data.get("title", "Document")

        # Start with title
        output = [doc_title]
        output.append("=" * len(doc_title))
        output.append("")

        # Process headings
        headings = structure_data.get("headings", [])

        # Build a tree structure for hierarchical display
        heading_tree = {}
        level_stack = [0] * 10  # Track current position at each level

        for i, heading in enumerate(headings):
            if i == 0 and heading.get("level", 0) == 1:
                continue  # Skip the first level 1 heading (title)

            level = heading.get("level", 1)
            section = heading.get("section", "")
            title = heading.get("title", "")
            lcp_phase = heading.get("lcp_phase", "")

            # Reset counts for deeper levels
            for j in range(level, len(level_stack)):
                level_stack[j] = 0

            # Increment counter for this level
            level_stack[level - 1] += 1

            # Create indentation and branch characters
            indent = "    " * (level - 1)
            prefix = ""

            if level > 1:
                # Determine if this is the last item at this level
                is_last = True
                for j in range(i + 1, len(headings)):
                    next_heading = headings[j]
                    if next_heading.get("level", 0) <= level:
                        is_last = next_heading.get("level", 0) < level
                        break

                # Build branch character based on position
                if is_last:
                    prefix = indent[:-4] + "└── "
                else:
                    prefix = indent[:-4] + "├── "

            # Format heading text with section number
            if section:
                heading_text = f"{section} {title}"
            else:
                heading_text = title

            # Add LCP phase if present
            if lcp_phase:
                heading_text += f" [LCP:{lcp_phase}]"

            # Build the line with proper indentation and branching
            if level == 1:
                line = heading_text
            else:
                line = prefix + heading_text

            output.append(line)

            # Process subheadings if any (for deeper nesting visualization)
            if i < len(headings) - 1 and headings[i + 1].get("level", 0) > level:
                # Check for subheadings with child elements
                if level < headings[i + 1].get("level", 0) - 1:
                    # Add vertical connector for multiple level jumps
                    connector_indent = indent + "│   "
                    output.append(connector_indent)

        # Add requirements dependency graph if available
        requirements = structure_data.get("requirements", [])
        dependencies = structure_data.get("dependencies", [])

        if dependencies:
            output.extend(
                [
                    "",
                    "REQUIREMENTS DEPENDENCY GRAPH",
                    "============================",
                    "",
                ]
            )

            # Group dependencies by source
            dep_by_source = {}
            for dep in dependencies:
                source = dep.get("source", "")
                target = dep.get("target", "")
                rel_type = dep.get("type", "references")

                if source not in dep_by_source:
                    dep_by_source[source] = []

                dep_by_source[source].append((target, rel_type))

            # Process each dependency group
            for source, targets in dep_by_source.items():
                # Get source description
                source_desc = next(
                    (
                        req["text"][:30] + "..."
                        for req in requirements
                        if req.get("id") == source
                    ),
                    "",
                )

                output.append(f"    {source}")
                if source_desc:
                    output.append(f"    ({source_desc})")

                # Add connections
                for i, (target, rel_type) in enumerate(targets):
                    if i == 0:
                        output.extend(
                            [
                                "          ▲",
                                "          │",
                                f"          │ {rel_type.replace('_', ' ')}",
                                "          │",
                            ]
                        )

                        # Get target description
                        target_desc = next(
                            (
                                req["text"][:30] + "..."
                                for req in requirements
                                if req.get("id") == target
                            ),
                            "",
                        )
                        output.append(f"    {target}")
                        if target_desc:
                            output.append(f"    ({target_desc})")
                    else:
                        output.append(f"    {source} ──────────── {target}")
                        output.append(
                            f"                           {rel_type.replace('_', ' ')}"
                        )

                output.append("")  # Blank line between groups

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output))

        logger.info(f"Document structure written to {output_file}")

    except Exception as e:
        logger.error(f"Error generating structure visualization: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert DOCX to Markdown with structure extraction"
    )
    parser.add_argument("input", type=Path, help="Input DOCX file")
    parser.add_argument("output", type=Path, help="Output Markdown file")
    parser.add_argument(
        "--structure",
        type=Path,
        help="Output file for document structure",
        default=PROJECT_ROOT / "output/document_structure.txt",
    )
    parser.add_argument(
        "--lua-filter",
        type=Path,
        help="Lua filter for structure extraction",
        default=PROJECT_ROOT / "config/structure_extraction.lua",
    )
    parser.add_argument(
        "--no-structure", action="store_true", help="Skip structure extraction"
    )

    args = parser.parse_args()

    # Determine structure output file
    structure_output = None if args.no_structure else args.structure

    # Check if lua filter exists
    lua_filter_path = args.lua_filter
    if not lua_filter_path.exists():
        logger.warning(
            f"Lua filter not found: {lua_filter_path}. Structure extraction might be limited."
        )
        lua_filter_to_pass = None
    else:
        lua_filter_to_pass = lua_filter_path

    # Perform conversion
    success = convert_docx_to_md(
        args.input, args.output, structure_output, lua_filter_to_pass
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
