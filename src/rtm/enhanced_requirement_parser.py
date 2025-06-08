#!/usr/bin/env python3
"""
Enhanced requirement parser that can detect various requirement formats.
This script improves requirement detection in markdown documents.
"""
import re
import json
from pathlib import Path
import os
import sys

# Define the regex patterns for different requirement ID formats
REQUIREMENT_PATTERNS = [
    # Standard format in headings: CF-1, FR-1.2, NFR-2, IR-1, IM-2
    r"^#+\s+((?:[A-Z]+-\d+(?:\.\d+)*):.*?)$",
    # Alternative format in headings: REQ-001, REQ-A001, etc.
    r"^#+\s+((?:REQ-[A-Za-z0-9]+):.*?)$",
    # Basic Req # format in headings: Req #123, Req # 456
    r"^#+\s+(?:Req\s+#\s*)(\d+).*?$",
    # New QQQ format in headings: QQQ.123, QQQ.456.789
    r"^#+\s+((?:QQQ\.\d+(?:\.\d+)*):.*?)$",
    # Table format: | REQ-001 | Description... |
    r"^\|\s*([A-Z]+-\d+(?:\.\d+)*)\s*\|.*?\|$",
    # Bullet list format: - REQ-001: Description
    r"^[\s-]*[-*]\s+((?:[A-Z]+-\d+(?:\.\d+)*):.*?)$",
    # Numbered list format: 1. REQ-001: Description
    r"^[\s-]*\d+\.\s+((?:[A-Z]+-\d+(?:\.\d+)*):.*?)$",
    # Bullet list for QQQ format: - QQQ.123: Description
    r"^[\s-]*[-*]\s+((?:QQQ\.\d+(?:\.\d+)*):.*?)$",
    # Numbered list for QQQ format: 1. QQQ.123: Description
    r"^[\s-]*\d+\.\s+((?:QQQ\.\d+(?:\.\d+)*):.*?)$",
    # Requirement in paragraph text: Requirement REQ-001:
    r"(?:^|\s)(?:Requirement\s+)((?:[A-Z]+-\d+(?:\.\d+)*)):",
    # Inline requirement mention: (see REQ-001)
    r"(?:^|\s)(?:\(see\s+)((?:[A-Z]+-\d+(?:\.\d+)*))\)",
]


def extract_requirements_from_markdown(markdown_file):
    """
    Extract requirements from a markdown file using multiple patterns.

    Args:
        markdown_file: Path to the markdown file

    Returns:
        Dictionary of requirements with their details
    """
    try:
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {markdown_file}: {e}")
        return {}

    requirements = {}

    # Process each pattern
    for pattern in REQUIREMENT_PATTERNS:
        regex = re.compile(pattern, re.MULTILINE)

        for match in regex.finditer(content):
            # Extract the requirement ID from the match
            if len(match.groups()) > 0:
                req_id = match.group(1).strip()

                # Clean up the requirement ID if it ends with a colon
                if req_id.endswith(":"):
                    req_id = req_id[:-1].strip()

                # For Req # format, prepend "REQ-" for consistency
                if pattern == REQUIREMENT_PATTERNS[2]:  # This is the "Req #" pattern
                    req_id = f"REQ-{req_id}"

                # Skip if this doesn't look like a valid requirement ID
                if not re.match(
                    r"^[A-Za-z]+-\d+(?:\.\d+)*$|^QQQ\.\d+(?:\.\d+)*$", req_id
                ):
                    continue

                # If we already processed this requirement, skip
                if req_id in requirements:
                    continue

                # Get the line number
                line_num = content[: match.start()].count("\n") + 1

                # Extract requirement category (CF, FR, NFR, etc. or REQ)
                category_match = re.match(r"^([A-Za-z]+)", req_id)
                category = category_match.group(1) if category_match else "UNKNOWN"

                # Extract the full text of the requirement
                # Look for the full line containing the requirement
                line_start = content.rfind("\n", 0, match.start()) + 1
                line_end = content.find("\n", match.start())
                if line_end == -1:  # No newline found, we're at the end of the file
                    line_end = len(content)

                full_text = content[line_start:line_end].strip()

                # Extract description from the full text
                description = ""
                if ":" in full_text:
                    parts = full_text.split(":", 1)
                    if len(parts) > 1:
                        description = parts[1].strip()

                requirements[req_id] = {
                    "line": line_num,
                    "text": full_text,
                    "description": description,
                    "implementation_files": [],
                    "category": category,
                    "status": "Not Implemented",
                }

    return requirements


def find_requirements_in_code(code_files, requirements):
    """Find requirements referenced in code files."""
    for file_path in code_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Check for each requirement ID in the file
                for req_id in requirements:
                    # Special handling for different formats
                    patterns = [
                        req_id,  # Exact match
                        req_id.replace("-", " "),  # Spaces instead of hyphens
                        req_id.replace("-", ""),  # No separator
                        req_id.replace("-", "_"),  # Underscores instead of hyphens
                    ]

                    for pattern in patterns:
                        if pattern in content:
                            if (
                                file_path
                                not in requirements[req_id]["implementation_files"]
                            ):
                                requirements[req_id]["implementation_files"].append(
                                    file_path
                                )
                                requirements[req_id]["status"] = "Implemented"
                            break

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    return requirements


def main():
    """Main function."""
    if len(sys.argv) < 2:
        markdown_file = input(
            "Enter the path to the markdown file containing requirements: "
        )
    else:
        markdown_file = sys.argv[1]

    if not os.path.exists(markdown_file):
        print(f"Error: File not found - {markdown_file}")
        return 1

    # Extract requirements from markdown
    print(f"Extracting requirements from {markdown_file}...")
    requirements = extract_requirements_from_markdown(markdown_file)
    print(f"Found {len(requirements)} requirements")

    # Define the project root directory for searching code files
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Get all Python files in the project (excluding certain directories)
    code_files = []
    excluded_dirs = [".git", ".venv", "__pycache__", "node_modules", "output"]

    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                code_files.append(file_path)

    print(f"Found {len(code_files)} code files to search for requirement references")

    # Find requirements in code files
    requirements_with_files = find_requirements_in_code(code_files, requirements)

    # Save to a JSON file
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "enhanced_requirements_analysis.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(requirements_with_files, f, indent=2)

    print(f"Requirements analysis saved to {output_file}")

    # Generate a more comprehensive report
    output_report = os.path.join(output_dir, "enhanced_requirements_report.md")
    with open(output_report, "w", encoding="utf-8") as f:
        f.write("# Enhanced Requirements Analysis Report\n\n")

        # Summary
        total_requirements = len(requirements_with_files)
        implemented_requirements = sum(
            1 for r in requirements_with_files.values() if r["status"] == "Implemented"
        )

        f.write(f"## Summary\n\n")
        f.write(f"- **Total Requirements**: {total_requirements}\n")
        f.write(
            f"- **Implemented Requirements**: {implemented_requirements} ({((implemented_requirements*100/(total_requirements if total_requirements > 0 else 1) if total_requirements > 0 else 0) if total_requirements > 0 else 0):.1f}%)\n"
        )
        f.write(
            f"- **Not Implemented Requirements**: {total_requirements - implemented_requirements}\n\n"
        )

        # Categories
        categories = {}
        for req_id, details in requirements_with_files.items():
            category = details["category"]
            if category not in categories:
                categories[category] = {"total": 0, "implemented": 0}
            categories[category]["total"] += 1
            if details["status"] == "Implemented":
                categories[category]["implemented"] += 1

        f.write("## Requirement Categories\n\n")
        f.write("| Category | Total | Implemented | Progress |\n")
        f.write("|----------|-------|-------------|----------|\n")
        for category, counts in sorted(categories.items()):
            progress = (
                f"{counts['implemented']*100/counts['total']:.1f}%"
                if counts["total"] > 0
                else "N/A"
            )
            f.write(
                f"| {category} | {counts['total']} | {counts['implemented']} | {progress} |\n"
            )
        f.write("\n")

        # Requirements List
        f.write("## Requirements List\n\n")

        for req_id, details in sorted(requirements_with_files.items()):
            f.write(f"### {req_id}\n\n")
            f.write(f"- **Text**: {details['text']}\n")
            if "description" in details and details["description"]:
                f.write(f"- **Description**: {details['description']}\n")
            f.write(f"- **Status**: {details['status']}\n")

            if details["implementation_files"]:
                f.write("- **Implementation Files**:\n")
                for impl_file in details["implementation_files"]:
                    rel_path = os.path.relpath(impl_file, project_root)
                    f.write(f"  - `{rel_path}`\n")
            else:
                f.write("- **Implementation Files**: None\n")

            f.write("\n")

    print(f"Requirements report generated at {output_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
