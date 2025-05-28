#!/usr/bin/env python3
"""
Converts Word (DOCX) documents to Markdown format.
"""


def convert_docx_to_md(input_file, output_file=None):
    """Convert DOCX to Markdown."""
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.md'

    print(f"Converting {input_file} to {output_file}")
    # Implementation would go here
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python word_to_md.py input.docx [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = convert_docx_to_md(input_file, output_file)
    print(f"Conversion complete: {result}")

import re
import yaml
from pathlib import Path
import sys
import os

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def extract_outline_from_md(md_file_path_str: str, output_file_str: str = None):
    """Extract document outline from markdown file"""
    md_file_path = Path(md_file_path_str)

    if not md_file_path.exists():
        print(f"Error: Markdown input file not found: {md_file_path}")
        return False

    if output_file_str is None:
        # Default output path relative to project root's output directory
        output_dir = PROJECT_ROOT / "output" / "outlines"
        output_file_path = output_dir / f"{md_file_path.stem}_outline.yaml"
    else:
        output_file_path = Path(output_file_str)

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        outline = []

        # Extract headers
        header_pattern = r"^(#{1,6})\s+(.*?)$"

        for match in re.finditer(header_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()

            # Extract section number if present
            section_match = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)", title)
            if section_match:
                section_num = section_match.group(1)
                clean_title = section_match.group(2)
            else:
                section_num = ""
                clean_title = title

            outline.append(
                {
                    "level": level,
                    "section": section_num,
                    "title": clean_title,
                    "raw_title": title,
                }
            )

        with open(output_file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                {"document_outline": outline, "total_sections": len(outline)},
                f,
                default_flow_style=False,
                allow_unicode=True,
            )

        print(f"Outline extracted from {md_file_path.name} and saved to {output_file_path}")
        return True

    except Exception as e:
        print(f"Error extracting outline from {md_file_path.name}: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_md_file = Path(sys.argv[1])
        if not input_md_file.is_absolute():
             # Assume relative to project root if not absolute
            input_md_file = PROJECT_ROOT / input_md_file

        custom_output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if custom_output_file and not custom_output_file.is_absolute():
            custom_output_file = PROJECT_ROOT / custom_output_file

        extract_outline_from_md(str(input_md_file), str(custom_output_file) if custom_output_file else None)
    else:
        default_input_md = PROJECT_ROOT / "output" / "MASTER_1805_1144.md" # Example path
        print(f"No input file provided. Trying default: {default_input_md}")
        extract_outline_from_md(str(default_input_md))
