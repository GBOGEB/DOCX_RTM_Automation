#!/usr/bin/env python3
"""
Clean and format the outline file from potentially corrupted outline.yaml.
Supports nested headings up to level 6.
The script outputs to 'output/MASTER_outline.yaml' and 'output/MASTER_outline.json'.
If these files already exist, they will be overwritten.
"""

import yaml
import json
import sys
from pathlib import Path
import re


# ANSI Colors (optional, consider moving to a shared utility if used in multiple scripts)
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    ENDC = "\033[0m"


def print_error(message):
    print(f"{Colors.RED}ERROR: {message}{Colors.ENDC}", file=sys.stderr)


def print_success(message):
    print(f"{Colors.GREEN}SUCCESS: {message}{Colors.ENDC}")


def save_outline(outline_data: dict, base_output_name: str, output_dir: Path):
    """Saves the outline data to YAML and JSON formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_output_path = output_dir / f"{base_output_name}.yaml"
    json_output_path = output_dir / f"{base_output_name}.json"

    try:
        with open(yaml_output_path, "w", encoding="utf-8") as f:
            yaml.dump(
                outline_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        print_success(f"Cleaned outline saved to: {yaml_output_path}")
    except Exception as e:
        print_error(f"Failed to save YAML outline to {yaml_output_path}: {e}")
        return False

    try:
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(outline_data, f, indent=2, ensure_ascii=False)
        print_success(f"JSON version saved to: {json_output_path}")
    except Exception as e:
        print_error(f"Failed to save JSON outline to {json_output_path}: {e}")
        return False
    return True


def _parse_line_based_outline(content: str) -> list[dict]:
    """Helper to parse line-based outline format."""
    sections = []
    # Regex to find lines like "- title: Actual Title Here"
    # It captures indentation, the title itself.
    # It's simplified to not rely on 'children:' for structure initially.
    title_line_re = re.compile(r"^(\s*)-\s*title:\s*(.+)$", re.MULTILINE)

    for match in title_line_re.finditer(content):
        indentation = len(match.group(1))
        title = match.group(2).strip()

        # Skip lines that look like Python code remnants if any slip through
        if title.lower().startswith(("import ", "with ", "print(", "for ")):
            continue

        # Basic heuristic for level: 2 spaces per indent level, starting at level 1
        # This might need adjustment based on actual file format.
        level = (indentation // 2) + 1
        level = min(level, 6)  # Cap at level 6

        sections.append({"title": title, "level": level, "raw_indent": indentation})

    # Attempt to fix levels if simple indentation logic is insufficient
    # This is a heuristic: if a line is less indented than previous but not 0,
    # it might be a sibling or a new top-level item.
    # A more robust approach would be a proper stack-based parser.
    if sections:
        # Post-process levels based on indentation changes
        # This is a simplified approach. A full stack-based parser would be more robust.
        corrected_sections = []
        level_stack = [0]  # Stack to keep track of current level based on indentation
        indent_stack = [-1]  # Stack to keep track of indentation of current level

        for sec in sections:
            while sec["raw_indent"] <= indent_stack[-1]:
                indent_stack.pop()
                level_stack.pop()

            current_level = level_stack[-1] + 1
            current_level = min(current_level, 6)  # Cap level

            indent_stack.append(sec["raw_indent"])
            level_stack.append(current_level)

            corrected_sections.append({"title": sec["title"], "level": current_level})
        sections = corrected_sections

    return sections


def _process_yaml_data_to_sections(data, current_level=1) -> list[dict]:
    """Recursively processes parsed YAML data to a flat list of sections with levels."""
    flat_sections = []
    if isinstance(data, list):
        for item in data:
            flat_sections.extend(_process_yaml_data_to_sections(item, current_level))
    elif isinstance(data, dict):
        title = data.get("title")
        if title:  # Ensure there's a title
            level = data.get("level", current_level)  # Use provided level or current
            level = min(int(level), 6)  # Cap level
            flat_sections.append({"title": str(title), "level": level})

        children = data.get("children")
        if children:
            flat_sections.extend(
                _process_yaml_data_to_sections(children, current_level + 1)
            )
    return flat_sections


def build_numbered_outline(sections: list[dict]) -> dict:
    """Builds a structured outline with section numbers."""
    outline_data = {"title": "MASTER Document Outline", "sections": []}
    current_numbering = [0] * 10  # Support up to 10 levels

    for section in sections:
        level = section["level"]
        title = section["title"]

        if not (1 <= level <= 9):  # Validate level
            print_error(f"Invalid level '{level}' for title '{title}'. Skipping.")
            continue

        current_numbering[level - 1] += 1
        for i in range(level, len(current_numbering)):
            current_numbering[i] = 0

        section_number_parts = [str(n) for n in current_numbering[:level] if n > 0]
        section_number = ".".join(section_number_parts)

        outline_data["sections"].append(
            {"level": level, "title": title, "number": section_number}
        )
    return outline_data


def extract_hierarchical_structure(input_path: Path) -> dict | None:
    """
    Extracts hierarchical structure from a YAML file.
    Tries direct YAML parsing first, then falls back to line-based parsing.
    """
    print(f"Processing outline file: {input_path}")
    if not input_path.is_file():
        print_error(f"Input file not found: {input_path}")
        return None

    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception as e:
        print_error(f"Error reading file {input_path}: {e}")
        return None

    sections = []
    try:
        # Attempt to parse as YAML directly
        # This expects a well-formed YAML list of dicts, possibly nested with 'children'
        data = yaml.safe_load(content)
        if data:  # If YAML parsing yields something
            sections = _process_yaml_data_to_sections(data)
    except yaml.YAMLError as ye:
        print(
            f"Could not parse as standard YAML ({ye}), attempting line-based extraction."
        )
        # Fallback to line-based parsing if direct YAML load fails or is not structured as expected
        sections = _parse_line_based_outline(content)

    if not sections:  # If still no sections after YAML parse attempt, try line-based
        sections = _parse_line_based_outline(content)

    if not sections:
        print_error(f"No sections could be extracted from {input_path}.")
        return None

    return build_numbered_outline(sections)


def main():
    """Main function"""
    if len(sys.argv) > 1:
        input_file_path_str = sys.argv[1]
    else:
        input_file_path_str = "input/MASTER_outline.yaml"  # Default input

    input_path = Path(input_file_path_str)
    output_dir = Path("output")
    # Using input filename stem for output, e.g. MASTER_outline
    output_base_name = input_path.stem

    print(f"Input outline: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Output base name: {output_base_name}")

    outline_data = extract_hierarchical_structure(input_path)

    if outline_data and outline_data.get("sections"):
        if save_outline(outline_data, output_base_name, output_dir):
            return 0
        return 1  # Saving failed
    # else: # Redundant else
    print_error("Outline extraction failed or resulted in no sections.")
    # Fallback to the old clean_outline logic if extract_hierarchical_structure fails badly
    # This part is removed as extract_hierarchical_structure now incorporates the fallback.
    # If a distinct 'clean_outline' is needed, it should be a separate, simpler function.
    return 1


if __name__ == "__main__":
    sys.exit(main())
