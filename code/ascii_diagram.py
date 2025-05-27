#!/usr/bin/env python3
"""
ASCII Diagram Generator
Generate text-based structure diagrams from documents
"""

import re
from pathlib import Path
import sys

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def generate_structure_diagram(md_file_path_str: str, output_file_str: str = None):
    """Generate ASCII structure diagram from markdown file"""
    md_file_path = Path(md_file_path_str)

    if not md_file_path.exists():
        print(f"Error: Markdown input file not found: {md_file_path}")
        return False

    if output_file_str is None:
        # Default output path relative to project root's output directory
        output_dir = PROJECT_ROOT / "output" / "diagrams"
        output_file_path = output_dir / f"{md_file_path.stem}_structure.txt"
    else:
        output_file_path = Path(output_file_str)

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        structure_lines = []
        structure_lines.append("Document Structure")
        structure_lines.append("==================")
        structure_lines.append("")

        # Extract headers
        header_pattern = r"^(#{1,6})\s+(.*?)$"
        prev_level = 0

        for match in re.finditer(header_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()

            # Create indentation
            indent = "  " * (level - 1)

            # Create tree structure
            if level > prev_level:
                prefix = "├── " if level > 1 else ""
            else:
                prefix = "├── " if level > 1 else ""

            # Clean title
            clean_title = re.sub(r"^\d+(?:\.\d+)*\s*", "", title)

            structure_lines.append(f"{indent}{prefix}{clean_title}")
            prev_level = level

        structure_lines.append("")
        structure_lines.append("Requirements Summary")
        structure_lines.append("==================")

        # Count requirements
        req_count = len(re.findall(r"shall|must|will", content, re.IGNORECASE))
        structure_lines.append(f"Estimated requirements: {req_count}")

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(structure_lines))

    except Exception as e:
        print(f"Error generating structure diagram for {md_file_path.name}: {e}")
        return False

    print(f"Structure diagram for {md_file_path.name} saved to {output_file_path}")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_md_file = Path(sys.argv[1])
        if not input_md_file.is_absolute():
            input_md_file = PROJECT_ROOT / input_md_file

        custom_output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if custom_output_file and not custom_output_file.is_absolute():
            custom_output_file = PROJECT_ROOT / custom_output_file

        generate_structure_diagram(str(input_md_file), str(custom_output_file) if custom_output_file else None)
    else:
        default_input_md = PROJECT_ROOT / "output" / "MASTER_1805_1144.md" # Example path
        print(f"No input file provided. Trying default: {default_input_md}")
        generate_structure_diagram(str(default_input_md))
