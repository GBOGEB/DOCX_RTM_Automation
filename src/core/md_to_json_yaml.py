#!/usr/bin/env python3
"""
Convert Markdown documents to JSON and YAML formats.
"""
import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
import glob  # Added import

import yaml  # Moved yaml import after standard library

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


def convert_md_to_structured(md_file, output_format=None, output_file=None):
    """
    Convert Markdown file to JSON and/or YAML format.

    Args:
        md_file: Path to input Markdown file
        output_format: Output format ('json', 'yaml', or None for both)
        output_file: Path to output file (without extension)

    Returns:
        Dictionary with paths to generated files
    """
    md_path = Path(md_file)
    if not md_path.exists():
        logger.error("Input file not found: %s", md_file)
        return None

    # Parse Markdown to structured data
    try:
        md_structure = parse_markdown(md_path)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to parse Markdown file: %s", e)
        return None

    # Determine output file(s)
    if output_file is None:
        output_stem = md_path.stem
    else:
        output_stem = Path(output_file).stem

    output_dir = md_path.parent if output_file is None else Path(output_file).parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save in specified format(s)
    output_files = {}

    if output_format is None or output_format.lower() == 'json':
        json_path = output_dir / f"{output_stem}.json"
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(md_structure, f, indent=2, ensure_ascii=False)
            logger.info("Saved JSON structure to %s", json_path)
            output_files['json'] = str(json_path)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to save JSON file: %s", e)

    if output_format is None or output_format.lower() in ('yaml', 'yml'):
        yaml_path = output_dir / f"{output_stem}.yaml"
        try:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(md_structure, f, default_flow_style=False, allow_unicode=True)
            logger.info("Saved YAML structure to %s", yaml_path)
            output_files['yaml'] = str(yaml_path)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to save YAML file: %s", e)

    return output_files


def parse_markdown(md_path):
    """Parse Markdown file to structured data."""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info("Successfully read Markdown file: %s", md_path)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error reading Markdown file %s: %s", md_path, e)
        return None

    # Extract document title (first H1)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled Document"

    # Extract headers and their content
    sections = []
    current_section = None
    lines = content.split('\n')

    for line in lines:
        header_match = re.match(r'^(#{1,6}) (.+)$', line)

        if header_match:
            # Start a new section
            level = len(header_match.group(1))
            heading = header_match.group(2)

            # Extract section number if present
            section_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.*)', heading)
            if section_match:
                section_num = section_match.group(1)
                heading_text = section_match.group(2)
            else:
                section_num = ""
                heading_text = heading

            new_section = {
                "level": level,
                "heading": heading_text,
                "section_num": section_num,
                "content": ""
            }

            sections.append(new_section)
            current_section = new_section
        elif current_section is not None:
            # Append to current section content
            if current_section["content"]:
                current_section["content"] += "\n" + line
            else:
                current_section["content"] = line

    # Process content to extract metadata and code blocks
    for section in sections:
        content = section["content"]

        # Extract code blocks
        code_blocks = []
        code_pattern = r'```([a-zA-Z0-9]*)\n(.*?)\n```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            language = match.group(1) or "text"
            code = match.group(2)
            code_blocks.append({
                "language": language,
                "code": code
            })

        section["code_blocks"] = code_blocks

        # Remove code blocks from content for plain text analysis
        content_without_code = re.sub(code_pattern, '', content, flags=re.DOTALL)
        section["plain_text"] = content_without_code.strip()

    # Build the final structure
    document = {
        "title": title,
        "sections": sections,
        "metadata": {
            "source_file": str(md_path),
            "section_count": len(sections)
        }
    }

    return document


def save_to_yaml(data, output_path):
    """Save data to a YAML file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
        logger.info("Successfully wrote YAML to %s", output_path)
        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error writing YAML to %s: %s", output_path, e)
        return False


def process_all_md_files(input_dir, output_dir=None, output_format=None):
    """
    Process all Markdown files in a directory.

    Args:
        input_dir: Directory containing Markdown files
        output_dir: Directory for output files
        output_format: Output format ('json', 'yaml', or None for both)

    Returns:
        List of paths to output files
    """
    if not input_dir:
        input_dir = os.path.join(
            PROJECT_ROOT, "output"
        )
        logger.info("Input directory not specified, using default: %s", input_dir)

    if not output_dir:
        output_dir = os.path.join(
            PROJECT_ROOT, "output", "structured"
        )
        logger.info("Output directory not specified, using default: %s", output_dir)

    os.makedirs(output_dir, exist_ok=True)

    # Find all Markdown files
    md_files = glob.glob(os.path.join(input_dir, "*.md"))
    md_files.extend(glob.glob(os.path.join(os.path.join(input_dir, "**"), "*.md")))

    if not md_files:
        logger.warning("No Markdown files found in %s", input_dir)
        return []

    logger.info("Found %d Markdown files to process.", len(md_files))

    output_files = []
    for md_file in md_files:
        output_file = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(md_file))[0]
        )
        results = convert_md_to_structured(md_file, output_format, output_file)
        if results:
            output_files.extend(results.values())

    logger.info(
        "Processing complete. JSON/YAML files saved in %s", output_dir
    )

    return output_files


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Convert Markdown to JSON and/or YAML")
    parser.add_argument("--input", help="Input Markdown file")
    parser.add_argument("-f", "--format", choices=['json', 'yaml', 'yml'], help="Output format (default: both)")
    parser.add_argument("-o", "--output", help="Output file path (without extension)")
    parser.add_argument("--input-dir", help="Directory containing input files")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Standardize format name
    format_arg = args.format
    if format_arg == 'yml':
        format_arg = 'yaml'

    # Process a single file
    if args.input:
        output_files = convert_md_to_structured(args.input, format_arg, args.output)

        if output_files:
            logger.info("Conversion successful:")
            for fmt, path in output_files.items():
                logger.info("  - %s: %s", fmt.upper(), path)
            return 0
        else:
            logger.error("Conversion failed.")
            return 1

    # Process directory if specified
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = os.path.join(PROJECT_ROOT, "output")

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(PROJECT_ROOT, "output", "structured")

    results = process_all_md_files(input_dir, output_dir, format_arg)

    if results:
        logger.info("Successfully processed %d files:", len(results))
        for result in results:
            logger.info("  - %s", result)
        return 0
    else:
        logger.warning("No files were processed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
