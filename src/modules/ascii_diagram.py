#!/usr/bin/env python3
"""
ASCII Diagram Generator

This module generates ASCII art diagrams from document outlines.
"""

import sys
import os
import argparse
import yaml
import json
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_outline(file_path: str) -> Dict[str, Any]:
    """
    Load document outline from YAML or JSON file

    Args:
        file_path: Path to the outline file

    Returns:
        Document outline as dictionary
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Outline file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                return yaml.safe_load(f)
            elif file_path.endswith(".json"):
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        logger.error(f"Error loading outline file: {e}")
        raise


def generate_ascii_diagram(outline: Dict[str, Any], max_depth: int = 7) -> str:
    """
    Generate ASCII art diagram from outline

    Args:
        outline: Document outline dictionary
        max_depth: Maximum depth to display (default: 7)

    Returns:
        ASCII diagram as string
    """
    if "sections" not in outline or not outline["sections"]:
        return "No sections found in outline"

    sections = outline["sections"]
    title = outline.get("title", "Document Outline")

    # Start with the title
    diagram = f"{title}\n{'=' * len(title)}\n\n"

    # Track the current level for proper indentation
    current_levels = [0] * (max_depth + 1)

    for section in sections:
        level = section.get("level", 1)
        if level > max_depth:
            continue

        title = section.get("title", "")
        number = section.get("number", "")

        # Reset levels deeper than current
        for i in range(level, max_depth + 1):
            current_levels[i] = 0

        # Increment current level
        current_levels[level] += 1

        # Generate prefix for the current level
        if level == 1:
            prefix = ""
        else:
            prefix = "│  " * (level - 2) + "├──"

        # Generate the line
        line = f"{prefix}{' ' if prefix else ''}{number} {title}"
        diagram += line + "\n"

    return diagram


def generate_tree_diagram(outline: Dict[str, Any], max_depth: int = 7) -> str:
    """
    Generate tree-style ASCII diagram

    Args:
        outline: Document outline dictionary
        max_depth: Maximum depth to display

    Returns:
        Tree diagram as string
    """
    if "sections" not in outline or not outline["sections"]:
        return "No sections found in outline"

    sections = outline["sections"]
    title = outline.get("title", "Document Outline")

    # Start with the title
    diagram = f"{title}\n{'=' * len(title)}\n\n"

    # Group sections by parent to build a tree
    tree = {}
    root_sections = []

    for section in sections:
        level = section.get("level", 1)
        if level > max_depth:
            continue

        if level == 1:
            root_sections.append(section)
        else:
            # Find the parent section
            parent_number = ".".join(section.get("number", "").split(".")[:-1])
            if parent_number not in tree:
                tree[parent_number] = []
            tree[parent_number].append(section)

    # Recursively build the tree
    def build_tree(section, indent=""):
        section_number = section.get("number", "")
        section_title = section.get("title", "")

        result = f"{indent}{'└──' if indent else ''} {section_number} {section_title}\n"

        # Add children
        if section_number in tree:
            children = tree[section_number]
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                child_indent = indent + ("    " if indent else "")
                if not is_last:
                    child_result = build_tree(child, child_indent)
                    child_result = child_result.replace("└──", "├──")
                    result += child_result
                else:
                    result += build_tree(child, child_indent)

        return result

    # Build the tree starting with root sections
    for root_section in root_sections:
        diagram += build_tree(root_section)

    return diagram


def generate_mindmap_diagram(outline: Dict[str, Any], max_depth: int = 7) -> str:
    """
    Generate mind-map style ASCII diagram

    Args:
        outline: Document outline dictionary
        max_depth: Maximum depth to display

    Returns:
        Mind-map diagram as string
    """
    if "sections" not in outline or not outline["sections"]:
        return "No sections found in outline"

    title = outline.get("title", "Document Outline")
    diagram = f"  {title}\n"

    # Track current section at each level
    sections_by_level = {}
    current_branch = [0] * (max_depth + 1)

    # Group sections by level
    for section in outline["sections"]:
        level = section.get("level", 1)
        if level > max_depth:
            continue

        if level not in sections_by_level:
            sections_by_level[level] = []
        sections_by_level[level].append(section)

    # Generate the mindmap
    def generate_branch(level, parent_index, indent=""):
        result = ""

        if level not in sections_by_level:
            return result

        # Filter sections that belong to the parent
        parent_number = (
            ""
            if level == 1
            else sections_by_level[level - 1][parent_index].get("number", "")
        )
        filtered_sections = [
            s
            for s in sections_by_level[level]
            if s.get("number", "").startswith(parent_number)
        ]

        for i, section in enumerate(filtered_sections):
            is_last = i == len(filtered_sections) - 1
            connector = "└── " if is_last else "├── "
            title = section.get("title", "")
            number = section.get("number", "")

            result += f"{indent}{connector}{number} {title}\n"

            # Process next level
            if level < max_depth:
                next_indent = indent + ("    " if is_last else "│   ")
                result += generate_branch(level + 1, i, next_indent)

        return result

    # Start with level 1
    diagram += generate_branch(1, 0)
    return diagram


def main() -> int:
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate ASCII diagram from document outline"
    )
    parser.add_argument(
        "input", help="Input YAML or JSON file containing document outline"
    )
    parser.add_argument(
        "-o", "--output", help="Output file for the ASCII diagram (default: stdout)"
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=7,
        help="Maximum depth to display (default: 7)",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["basic", "tree", "mindmap"],
        default="tree",
        help="Type of diagram to generate (default: tree)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    # Set up logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        # Load outline
        outline = load_outline(args.input)

        # Generate diagram
        if args.type == "basic":
            diagram = generate_ascii_diagram(outline, args.depth)
        elif args.type == "mindmap":
            diagram = generate_mindmap_diagram(outline, args.depth)
        else:  # tree
            diagram = generate_tree_diagram(outline, args.depth)

        # Output
        if args.output:
            try:
                # Explicitly open the output file with UTF-8 encoding
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(diagram)
                print(f"ASCII diagram written to {args.output}")
            except Exception as e:
                print(f"Error writing diagram to {args.output}: {e}")
                return 1
        else:
            print(diagram)

        return 0

    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
