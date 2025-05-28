#!/usr/bin/env python3
"""
ASCII Diagram Generator
Generate text-based structure diagrams from documents
"""


from pathlib import Path
import re  # For regex-based header parsing
import sys  # For command-line arguments

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
            lines = f.readlines()

        structure_lines = []
        structure_lines.append(f"Document Structure: {md_file_path.name}")
        structure_lines.append(
            "=" * (len(structure_lines[0]))
        )  # Underline matches title length
        structure_lines.append("")

        # Extract headers
        header_pattern = r"^(#{1,6})\s+(.*?)$"  # Matches lines starting with 1 to 6 '#'

        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                level = len(match.group(1))  # Number of '#' indicates level
                title = match.group(2).strip()

                # Basic indentation for hierarchy
                indent = "  " * (level - 1)
                prefix = "└─ " if level > 1 else ""  # Simple prefix for sub-levels
                if level == 1:
                    prefix = "■─ "  # Different prefix for top-level

                structure_lines.append(f"{indent}{prefix}{title} (H{level})")

        if not any(re.match(header_pattern, line) for line in lines):
            structure_lines.append("No headers found in the document.")

        with open(output_file_path, "w", encoding="utf-8") as out_f:
            for s_line in structure_lines:
                out_f.write(s_line + "\n")

    except Exception as e:
        print(f"Error processing file {md_file_path}: {e}")
        return False

    print(f"Structure diagram for {md_file_path.name} saved to {output_file_path}")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file_arg = sys.argv[2] if len(sys.argv) > 2 else None

        # Make input_file relative to project root if not absolute
        input_path = Path(input_file)
        if not input_path.is_absolute():
            input_path = PROJECT_ROOT / input_file

        print(f"Generating diagram for: {input_path}")
        if output_file_arg:
            output_path_arg = Path(output_file_arg)
            if not output_path_arg.is_absolute():
                output_path_arg = PROJECT_ROOT / output_file_arg
            generate_structure_diagram(str(input_path), str(output_path_arg))
        else:
            generate_structure_diagram(str(input_path))
    else:
        print("Usage: python ascii_diagram.py <markdown_file_path> [output_file_path]")
        print(
            "\nExample: python code/ascii_diagram.py docs/sample.md output/diagrams/sample_structure.txt"
        )
        # Create a dummy markdown file for easy testing if it doesn't exist
        dummy_md_path = PROJECT_ROOT / "docs" / "sample_diagram_test.md"
        dummy_md_path.parent.mkdir(parents=True, exist_ok=True)
        if not dummy_md_path.exists():
            with open(dummy_md_path, "w", encoding="utf-8") as f_dummy:
                f_dummy.write(
                    "# Main Title\n\n## Section 1\n\n### Subsection 1.1\n\n## Section 2\n"
                )
            print(f"\nCreated a dummy file for testing: {dummy_md_path}")
            print(
                f"You can try running: python code/ascii_diagram.py {dummy_md_path.relative_to(PROJECT_ROOT)}"
            )
