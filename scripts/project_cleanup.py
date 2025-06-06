#!/usr/bin/env python
"""
ASCII Diagram Generator for DOCX RTM Automation
"""

import sys
from typing import List, Dict, Any


class AsciiDiagramGenerator:
    def __init__(
        self,
        indent_size: int = 2,
        max_width: int = 80,
        indent_chars: str = "  ",
        branch_chars: Dict[str, str] = None,
    ):
        self.indent_size = indent_size
        self.max_width = max_width
        self.indent_chars = indent_chars
        self.branch_chars = branch_chars or {
            "vertical": "|",
            "horizontal": "-",
            "corner": "+",
            "tee": "+",
            "cross": "+",
            "bullet": "*",
        }

    def generate_from_outline(self, outline_data: Dict[str, Any]) -> str:
        """Generate ASCII diagram from outline data"""
        if not outline_data or not isinstance(outline_data, dict):
            return "Error: Invalid outline data"

        result = []
        result.append("Document Structure Diagram")
        result.append("========================")
        result.append("")

        # Process based on outline structure format
        if "sections" in outline_data:
            # Format: {title: "", sections: [{level: 1, title: "", number: ""}, ...]}
            sections = outline_data.get("sections", [])
            doc_title = outline_data.get("title", "Document Structure")

            result.append(f"{doc_title}")
            result.append("=" * len(doc_title))
            result.append("")

            # Create a tree representation of the sections
            last_level = [0] * 10  # Track the last seen section at each level

            for i, section in enumerate(sections):
                level = section.get("level", 1)
                title = section.get("title", "Untitled")
                number = section.get("number", "")

                # Ensure level is at least 1
                if level < 1:
                    level = 1

                # Create the indent and branch
                indent = ""
                for l in range(1, level):
                    # For each level, add vertical line if there are more sections at that level
                    if l < level - 1 and last_level[l] > 0:
                        indent += self.branch_chars["vertical"] + " " * (
                            self.indent_size - 1
                        )
                    else:
                        indent += " " * self.indent_size

                # Determine the connector character
                if i < len(sections) - 1 and sections[i + 1].get("level", 1) >= level:
                    connector = self.branch_chars["tee"]
                else:
                    connector = self.branch_chars["corner"]

                # Update last_level tracking
                last_level[level] = i + 1
                for l in range(level + 1, len(last_level)):
                    last_level[l] = 0

                # Format the section text
                section_text = f"{number} {title}" if number else title

                # Add the line to the result
                if level == 1:
                    result.append(
                        f"{connector}{self.branch_chars['horizontal']} {section_text}"
                    )
                else:
                    result.append(
                        f"{indent}{connector}{self.branch_chars['horizontal']} {section_text}"
                    )

        elif "headers" in outline_data:
            # Process the headers format
            headers = outline_data.get("headers", [])
            self._process_headers(headers, result)

        else:
            # Unknown format - search for any usable structure
            for key, value in outline_data.items():
                if (
                    isinstance(value, list)
                    and len(value) > 0
                    and isinstance(value[0], dict)
                ):
                    # Try to format this as a simple list
                    result.append(f"{key}:")
                    result.append("=" * (len(key) + 1))
                    result.append("")

                    for item in value:
                        if "title" in item:
                            result.append(
                                f"{self.branch_chars['bullet']} {item['title']}"
                            )
                        elif "name" in item:
                            result.append(
                                f"{self.branch_chars['bullet']} {item['name']}"
                            )

            if len(result) <= 3:  # Only has the header we added
                result.append("Could not find a compatible outline structure.")

        return "\n".join(result)

    def _process_headers(
        self, headers: List[Dict[str, Any]], result: List[str], depth: int = 0
    ) -> None:
        """Process headers recursively to build diagram"""
        for header in headers:
            title = header.get("title", "Untitled")
            level = header.get("level", 1)

            # Calculate indentation
            indent = self.indent_chars * depth

            # Add connection lines based on depth
            if depth > 0:
                connector = (
                    f"{self.branch_chars['tee']} "
                    if depth == 1
                    else f"{self.branch_chars['vertical']}   " * (depth - 1)
                    + f"{self.branch_chars['tee']} "
                )
            else:
                connector = ""

            # Add the header line
            result.append(f"{indent}{connector}{title}")

            # Process children if any
            children = header.get("children", [])
            if children:
                self._process_headers(children, result, depth + 1)

    def generate_from_rtm(self, rtm_data: Dict[str, Any]) -> str:
        """Generate ASCII diagram from RTM data"""
        if not rtm_data:
            return "Error: Invalid RTM data"

        result = []
        result.append("Requirements Traceability Matrix")
        result.append("==============================")
        result.append("")

        # Process requirements
        requirements = rtm_data.get("requirements", [])
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            description = req.get("text", req.get("description", "No description"))

            result.append(f"[{req_id}] {description}")

            # Add traceability links if any
            links = req.get("links", [])
            if links:
                for link in links:
                    target = link.get("target", "UNKNOWN")
                    relation = link.get("relation", "relates to")
                    result.append(
                        f"  {self.branch_chars['corner']}{self.branch_chars['horizontal']}{'─' if self.branch_chars['horizontal'] == '-' else self.branch_chars['horizontal']} {relation} → [{target}]"
                    )

            result.append("")

        return "\n".join(result)


def main():
    """Main function when script is executed directly"""
    import json
    import yaml
    import os
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate ASCII diagrams from document structure"
    )
    parser.add_argument(
        "input_file", help="Input YAML or JSON file containing outline or RTM data"
    )
    parser.add_argument(
        "--type",
        choices=["outline", "rtm"],
        default="outline",
        help="Type of diagram to generate (outline or rtm)",
    )
    parser.add_argument(
        "--output", help="Output file (if not specified, prints to stdout)"
    )
    parser.add_argument("--debug", action="store_true", help="Print debug information")

    args = parser.parse_args()

    if args.debug:
        print(f"Processing file: {args.input_file}")

    # Load the input file
    try:
        file_ext = os.path.splitext(args.input_file)[1].lower()
        with open(args.input_file, "r") as f:
            content = f.read()

            if args.debug:
                print(f"File content (first 200 chars): {content[:200]}...")

            if file_ext == ".json":
                data = json.loads(content)
            elif file_ext in [".yaml", ".yml"]:
                data = yaml.safe_load(content)
            else:
                print(f"Unsupported file format: {file_ext}")
                return 1

        if args.debug:
            print("File loaded successfully")
            print(f"Data structure: {type(data)}")
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                if "sections" in data:
                    print(f"Found {len(data['sections'])} sections")
    except Exception as e:
        print(f"Error loading input file: {e}")
        return 1

    # Generate diagram
    generator = AsciiDiagramGenerator(
        max_width=100,  # Increase maximum width
        indent_chars="    ",  # Wider indentation
        branch_chars={  # Custom branch characters
            "vertical": "│",  # Unicode box drawing characters
            "horizontal": "─",
            "corner": "└",
            "tee": "├",
            "cross": "┼",
            "bullet": "•",
        },
    )

    if args.type == "outline":
        diagram = generator.generate_from_outline(data)
    else:
        diagram = generator.generate_from_rtm(data)

    # Output the diagram
    if args.output:
        with open(args.output, "w") as f:
            f.write(diagram)
        print(f"Diagram written to {args.output}")
    else:
        print(diagram)

    return 0


if __name__ == "__main__":
    sys.exit(main())
