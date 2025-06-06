#!/usr/bin/env python3
"""
Document Structure Generator

This module extracts document structure from markdown files and generates
an ASCII tree visualization of the document hierarchy, along with a
requirements dependency graph.
"""

import os
import re
import logging
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentStructure:
    """Extract and visualize document structure from markdown"""

    def __init__(self):
        """Initialize the document structure extractor"""
        self.headings = []  # List of (level, number, title, lcp_phase) tuples
        self.requirements = []  # List of requirement objects
        # List of (source_id, target_id, rel_type) tuples
        self.dependencies = []

    def parse_markdown(self, markdown_file: str) -> bool:
        """
        Parse a markdown file to extract structure and requirements

        Args:
            markdown_file: Path to the markdown file to parse

        Returns:
            True if parsing was successful
        """
        try:
            with open(markdown_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract headings with potential LCP phase
            heading_pattern = (
                r"^(#{1,6})\s+((\d+(?:\.\d+)*)\s+)?([^\n\[]+)(?:\s+\[LCP:(\d+)\])?"
            )
            for match in re.finditer(heading_pattern, content, re.MULTILINE):
                level = len(match.group(1))
                section_num = match.group(3) or ""
                title = match.group(4).strip()
                lcp_phase = match.group(5) or ""

                self.headings.append((level, section_num, title, lcp_phase))
                logger.debug(
                    f"Found heading: L{level} {section_num} {title} [LCP:{lcp_phase}]"
                )

            # Extract requirements from div class="requirement"
            req_div_pattern = r'<div\s+class="requirement">\s*([^<]*)</div>'
            for match in re.finditer(req_div_pattern, content, re.DOTALL):
                req_text = match.group(1).strip()

                # Extract requirement ID
                req_id_match = re.search(r"([Rr][Ee][Qq]-\d+)", req_text)
                req_id = (
                    req_id_match.group(1)
                    if req_id_match
                    else f"REQ-AUTO-{len(self.requirements) + 1}"
                )

                # Get current section from the nearest heading above
                section = self._find_section_for_position(match.start(), content)

                # Extract metadata
                meta = {}
                meta_pattern = r"\[([a-zA-Z_-]+):([^\]]+)\]"
                for meta_match in re.finditer(meta_pattern, req_text):
                    key = meta_match.group(1).lower()
                    value = meta_match.group(2).strip()
                    meta[key] = value

                # Clean the text (remove metadata)
                for meta_match in re.finditer(meta_pattern, req_text):
                    req_text = req_text.replace(meta_match.group(0), "").strip()

                # Remove the requirement ID from the text
                if req_id_match:
                    req_text = req_text.replace(req_id_match.group(1), "", 1).strip()

                # Add the requirement
                self.requirements.append(
                    {
                        "id": req_id,
                        "text": req_text,
                        "section": section,
                        "metadata": meta,
                    }
                )
                logger.debug(f"Found requirement: {req_id} in section {section}")

            # Also look for requirements in paragraphs (without div)
            para_req_patterns = [
                r"([Rr][Ee][Qq]-\d+)[\s:]+(.*?)(?=\n\n|\Z)",  # REQ-XXX format
                r"shall\s+(.*?)(?=\n\n|\Z)",  # "shall" statements
                r"must\s+(.*?)(?=\n\n|\Z)",  # "must" statements
            ]

            for pattern in para_req_patterns:
                for match in re.finditer(pattern, content, re.DOTALL):
                    # For REQ-XXX format
                    if match.group(1) if len(match.groups()) > 1 else None:
                        req_id = match.group(1)
                        req_text = match.group(2).strip()
                    # For "shall/must" statements
                    else:
                        req_id = f"REQ-IMP-{len(self.requirements) + 1}"
                        req_text = match.group(1).strip()

                    # Skip if this looks like it was already captured via div
                    if any(
                        req["id"].upper() == req_id.upper() for req in self.requirements
                    ):
                        continue

                    # Get current section from the nearest heading above
                    section = self._find_section_for_position(match.start(), content)

                    # Extract metadata
                    meta = {}
                    meta_pattern = r"\[([a-zA-Z_-]+):([^\]]+)\]"
                    for meta_match in re.finditer(meta_pattern, req_text):
                        key = meta_match.group(1).lower()
                        value = meta_match.group(2).strip()
                        meta[key] = value

                    # Clean the text (remove metadata)
                    for meta_match in re.finditer(meta_pattern, req_text):
                        req_text = req_text.replace(meta_match.group(0), "").strip()

                    # Add the requirement
                    self.requirements.append(
                        {
                            "id": req_id,
                            "text": req_text,
                            "section": section,
                            "metadata": meta,
                        }
                    )
                    logger.debug(
                        f"Found paragraph requirement: {req_id} in section {section}"
                    )

            # Extract dependencies
            dep_patterns = [
                r"([Rr][Ee][Qq]-\d+)\s+(depends\s+on)\s+([Rr][Ee][Qq]-\d+)",
                r"([Rr][Ee][Qq]-\d+)\s+(refines)\s+([Rr][Ee][Qq]-\d+)",
                r"([Rr][Ee][Qq]-\d+)\s+(related\s+to)\s+([Rr][Ee][Qq]-\d+)",
            ]

            for pattern in dep_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    source_id = match.group(1)
                    rel_type = match.group(2).lower().replace(" ", "_")
                    target_id = match.group(3)

                    self.dependencies.append((source_id, target_id, rel_type))
                    logger.debug(
                        f"Found dependency: {source_id} {rel_type} {target_id}"
                    )

            # Also check tables with dependency information
            table_pattern = r"\|\s*([Rr][Ee][Qq]-\d+)\s*\|[^|]*\|[^|]*\|\s*([Rr][Ee][Qq]-\d+(?:,\s*[Rr][Ee][Qq]-\d+)*)\s*\|"
            for match in re.finditer(table_pattern, content):
                source_id = match.group(1)
                targets = re.findall(r"[Rr][Ee][Qq]-\d+", match.group(2))

                for target_id in targets:
                    self.dependencies.append((source_id, target_id, "depends_on"))
                    logger.debug(
                        f"Found table dependency: {source_id} depends_on {target_id}"
                    )

            return True

        except Exception as e:
            logger.error(f"Error parsing markdown file {markdown_file}: {e}")
            return False

    def _find_section_for_position(self, position: int, content: str) -> str:
        """Find the section number for a given position in the content"""
        # Get all heading matches before this position
        heading_pattern = r"^(#{1,6})\s+((\d+(?:\.\d+)*)\s+)?(.+?)(?:\s+\[LCP:\d+\])?$"
        heading_matches = list(
            re.finditer(heading_pattern, content[:position], re.MULTILINE)
        )

        if not heading_matches:
            return ""

        # Get the last heading before this position
        last_match = heading_matches[-1]
        if last_match.group(3):  # If there's a section number
            return last_match.group(3)

        return ""

    def process_raw_structure_json(self, json_file: str) -> bool:
        """Process raw structure data from JSON file"""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Process headings
            for heading in data.get("headings", []):
                level = heading.get("level", 1)
                section = heading.get("section", "")
                title = heading.get("title", "")
                lcp_phase = heading.get("lcp_phase", "")

                self.headings.append((level, section, title, lcp_phase))

            # Process requirements
            for req in data.get("requirements", []):
                self.requirements.append(
                    {
                        "id": req.get("id", f"REQ-AUTO-{len(self.requirements) + 1}"),
                        "text": req.get("text", ""),
                        "section": req.get("section", ""),
                        "metadata": req.get("metadata", {}),
                    }
                )

            # Process dependencies
            for dep in data.get("dependencies", []):
                source_id = dep.get("source", "")
                target_id = dep.get("target", "")
                rel_type = dep.get("type", "depends_on")

                if source_id and target_id:
                    self.dependencies.append((source_id, target_id, rel_type))

            return True

        except Exception as e:
            logger.error(f"Error processing structure JSON {json_file}: {e}")
            return False

    def generate_structure_tree(self) -> str:
        """
        Generate an ASCII tree representation of the document structure

        Returns:
            ASCII tree as a string
        """
        if not self.headings:
            return "No document structure found"

        # Extract the document title from the first heading
        doc_title = self.headings[0][2] if self.headings else "Document"

        output = [doc_title]
        output.append("=" * len(doc_title))
        output.append("")

        # Keep track of the current branch characters at each level
        branch_chars = [""] * 20

        # Process each heading (skip the first, which is the title)
        for i, (level, number, title, lcp_phase) in enumerate(self.headings[1:], 1):
            # Calculate indentation
            indent = "    " * (level - 1)

            # Format the heading text
            if number:
                heading_text = f"{number} {title}"
            else:
                heading_text = title

            if lcp_phase:
                heading_text += f" [LCP:{lcp_phase}]"

            # Determine if this is the last item at its level
            is_last = True
            for next_heading in self.headings[i + 1 :]:
                if (
                    next_heading[0] <= level
                ):  # If we find another heading at same or higher level
                    is_last = (
                        next_heading[0] < level
                    )  # It's last only if the next is at a higher level
                    break

            # Generate the branch character
            if level == 1:
                branch = ""  # No branch for top-level headings
            elif is_last:
                branch = "└── "  # Last item at this level
                branch_chars[level] = "    "  # No continuing vertical line
            else:
                branch = "├── "  # Non-last item
                # Continue vertical line for this level
                branch_chars[level] = "│   "

            # Build the full line with the correct indentation and branching
            if level == 1:
                line = heading_text
            else:
                # Replace the last indent space with the appropriate branch characters from higher levels
                indented_line = ""
                for j in range(1, level):
                    indented_line += branch_chars[j]

                line = indented_line + branch + heading_text

            output.append(line)

        return "\n".join(output)

    def generate_dependency_graph(self) -> str:
        """
        Generate an ASCII representation of the requirement dependencies

        Returns:
            Dependency graph as a string
        """
        if not self.dependencies:
            return "No dependencies found"

        output = [
            "",
            "REQUIREMENTS DEPENDENCY GRAPH",
            "============================",
            "",
        ]

        # Group dependencies by source
        dep_groups = defaultdict(list)
        for source, target, rel_type in self.dependencies:
            dep_groups[source].append((target, rel_type))

        # Process each group
        for source_id, targets in dep_groups.items():
            # Get source requirement description
            source_desc = ""
            for req in self.requirements:
                if req["id"].upper() == source_id.upper():
                    source_desc = req["text"][:30] + (
                        "..." if len(req["text"]) > 30 else ""
                    )
                    break

            # Add the source node
            output.append(f"    {source_id}")
            if source_desc:
                output.append(f"    ({source_desc})")

            # Add connections to targets
            for i, (target_id, rel_type) in enumerate(targets):
                if i == 0:  # First connection uses vertical arrows
                    output.append("          ▲")
                    output.append("          │")
                    output.append(f"          │ {rel_type.replace('_', ' ')}")
                    output.append("          │")
                else:  # Additional connections use horizontal lines
                    output.append(f"    {source_id} ──────────── {target_id}")
                    output.append(
                        f"                           {rel_type.replace('_', ' ')}"
                    )

                # Only get target description for the first connection
                if i == 0:
                    # Get target description
                    target_desc = ""
                    for req in self.requirements:
                        if req["id"].upper() == target_id.upper():
                            target_desc = req["text"][:30] + (
                                "..." if len(req["text"]) > 30 else ""
                            )
                            break

            # Add the target info for first connection
            if targets:
                target_id, _ = targets[0]
                output.append(f"    {target_id}")

                # Get target description
                target_desc = ""
                for req in self.requirements:
                    if req["id"].upper() == target_id.upper():
                        target_desc = req["text"][:30] + (
                            "..." if len(req["text"]) > 30 else ""
                        )
                        break

                if target_desc:
                    output.append(f"    ({target_desc})")

            output.append("")  # Add a blank line between dependency groups

        return "\n".join(output)

    def generate_output(self, output_file: str) -> bool:
        """
        Generate the complete document structure output file

        Args:
            output_file: Path to save the output

        Returns:
            True if successful
        """
        try:
            structure_tree = self.generate_structure_tree()
            dep_graph = self.generate_dependency_graph()

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(structure_tree)
                f.write("\n\n")
                f.write(dep_graph)

            logger.info(f"Document structure written to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error generating document structure: {e}")
            return False


def extract_structure_from_md(input_file: str, output_file: str) -> bool:
    """
    Extract document structure from markdown and generate ASCII visualization

    Args:
        input_file: Path to input markdown file
        output_file: Path to save structure visualization

    Returns:
        True if successful
    """
    doc_structure = DocumentStructure()

    # Check if raw structure JSON exists (from Lua filter)
    raw_json = "output/document_structure_raw.json"
    if os.path.exists(raw_json):
        logger.info(f"Using raw structure data from {raw_json}")
        if not doc_structure.process_raw_structure_json(raw_json):
            logger.warning(
                "Failed to process raw structure data, falling back to markdown parsing"
            )
            if not doc_structure.parse_markdown(input_file):
                logger.error(f"Failed to parse markdown: {input_file}")
                return False
    else:
        # Parse the markdown file directly
        logger.info(f"Parsing markdown file: {input_file}")
        if not doc_structure.parse_markdown(input_file):
            logger.error(f"Failed to parse markdown: {input_file}")
            return False

    # Generate the output
    return doc_structure.generate_output(output_file)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate document structure visualization from markdown"
    )
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument(
        "--output", "-o", help="Output file", default="output/document_structure.txt"
    )
    parser.add_argument("--raw-json", "-j", help="Raw structure JSON file")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Process raw JSON if provided
    if args.raw_json:
        doc_structure = DocumentStructure()
        success = doc_structure.process_raw_structure_json(args.raw_json)
        if success:
            success = doc_structure.generate_output(args.output)
    else:
        # Standard markdown parsing
        success = extract_structure_from_md(args.input, args.output)

    sys.exit(0 if success else 1)
