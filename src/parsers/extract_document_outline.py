#!/usr/bin/env python3
"""
Document outline extraction and processing utilities.
"""
import os
import sys
import json
import yaml
from pathlib import Path
import re


def extract_headings_from_markdown(markdown_file):
    """
    Extract headings and their hierarchy from a markdown file.

    Args:
        markdown_file: Path to the markdown file

    Returns:
        List of dictionaries with heading information
    """
    headings = []

    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match ATX-style headers (# Heading)
    pattern = re.compile(r"^(#+)\s+(.*?)(?:\s+\{#.*\})?\s*$", re.MULTILINE)

    for match in pattern.finditer(content):
        level = len(match.group(1))  # Number of # symbols
        text = match.group(2).strip()

        # Get line number
        line_num = content[: match.start()].count("\n") + 1

        heading = {
            "level": level,
            "text": text,
            "line": line_num,
            # Generate a simple ID from the text (for referencing)
            "id": text.lower().replace(" ", "-").replace(":", "").replace(".", "-"),
        }

        headings.append(heading)

    return headings


def build_outline_structure(headings):
    """
    Convert flat list of headings into a nested document structure.

    Args:
        headings: List of heading dictionaries

    Returns:
        Nested dictionary representing document outline
    """
    outline = {"sections": []}

    # Stack to keep track of current section nesting
    stack = [outline]

    for heading in headings:
        level = heading["level"]

        # Ensure the stack has enough levels
        while len(stack) > level:
            stack.pop()

        # Ensure the stack has the right size
        while len(stack) < level:
            # Create an intermediate empty section if we skipped levels
            empty_section = {
                "title": "(Untitled)",
                "level": len(stack),
                "subsections": [],
            }
            stack[-1]["sections" if "sections" in stack[-1] else "subsections"].append(
                empty_section
            )
            stack.append(empty_section)

        # Create new section
        new_section = {
            "title": heading["text"],
            "level": level,
            "id": heading["id"],
            "line": heading["line"],
            "subsections": [],
        }

        # Add to parent
        stack[-1]["sections" if "sections" in stack[-1] else "subsections"].append(
            new_section
        )

        # Push to stack
        stack.append(new_section)

    return outline


def extract_document_outline(markdown_file, output_dir=None):
    """
    Extract document outline from a markdown file and save as JSON and YAML.

    Args:
        markdown_file: Path to the markdown file
        output_dir: Directory to save output files (default: same as markdown file)

    Returns:
        Dictionary with paths to the created outline files
    """
    if not os.path.exists(markdown_file):
        print(f"Error: Markdown file not found - {markdown_file}")
        return None

    # Setup output directory
    markdown_path = Path(markdown_file)
    if output_dir is None:
        output_dir = markdown_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    base_name = markdown_path.stem

    # Extract headings
    headings = extract_headings_from_markdown(markdown_file)

    # Build outline
    outline_data = build_outline_structure(headings)

    # Add metadata
    outline_data["document_name"] = base_name
    outline_data["source_file"] = str(markdown_file)
    outline_data["heading_count"] = len(headings)

    # Save as JSON
    json_path = output_dir / f"{base_name}_outline.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(outline_data, f, indent=2)

    # Save as YAML
    yaml_path = output_dir / f"{base_name}_outline.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(outline_data, f, default_flow_style=False)

    print(f"Document outline extracted from {markdown_file}")
    print(f"JSON outline saved to: {json_path}")
    print(f"YAML outline saved to: {yaml_path}")

    return {"json": json_path, "yaml": yaml_path, "outline_data": outline_data}


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print(
            "Usage: python extract_document_outline.py <markdown_file> [output_directory]"
        )
        return 1

    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = extract_document_outline(markdown_file, output_dir)

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
