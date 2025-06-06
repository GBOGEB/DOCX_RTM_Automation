#!/usr/bin/env python3
"""
Document parsing utilities for extracting requirements and structure.
"""

import os
import sys
import re
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Add the project root to path if needed
project_root_path = Path(__file__).resolve().parent.parent
if str(project_root_path) not in sys.path:
    sys.path.append(str(project_root_path))

from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from utils.docx_converter import DocxConverter


class DocumentParser:
    """
    Parser for extracting structured information from documents,
    particularly requirements and traceability information.
    """

    def __init__(self, output_handler: Optional[OutputHandler] = None):
        """Initialize the document parser"""
        self.paths = PathsManager()
        self.output_handler = output_handler or OutputHandler(
            self.paths.get_output_dir()
        )
        self.docx_converter = DocxConverter(self.output_handler)

    def parse_document(
        self, document_path: str, output_format: str = "json"
    ) -> Optional[str]:
        """
        Parse a document to extract structured information

        Args:
            document_path: Path to the document (DOCX or MD)
            output_format: Format of the output file (json, yaml, md)

        Returns:
            Path to the output file if successful, None otherwise
        """
        if not os.path.isfile(document_path):
            self.output_handler.log_error(f"Document not found: {document_path}")
            return None

        # Convert to markdown if it's a DOCX file
        file_ext = os.path.splitext(document_path)[1].lower()
        md_content = ""

        if file_ext == ".docx":
            # Convert to markdown
            md_path = self.docx_converter.convert_to_markdown(document_path)
            if not md_path:
                self.output_handler.log_error(
                    f"Failed to convert {document_path} to Markdown"
                )
                return None

            # Read the markdown content
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        elif file_ext == ".md":
            # Read markdown content directly
            with open(document_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        else:
            self.output_handler.log_error(f"Unsupported document format: {file_ext}")
            return None

        # Parse the markdown content
        parsed_data = self._parse_markdown(md_content)

        # Generate output file path
        output_path = os.path.join(
            self.paths.get_output_dir(),
            f"{os.path.splitext(os.path.basename(document_path))[0]}.{output_format}",
        )

        # Save in the requested format
        if output_format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=2)
        elif output_format.lower() == "yaml":
            import yaml

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(parsed_data, f, default_flow_style=False)
        elif output_format.lower() == "md":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(self._data_to_markdown(parsed_data))
        else:
            self.output_handler.log_error(f"Unsupported output format: {output_format}")
            return None

        self.output_handler.log_info(f"Document parsed and saved to {output_path}")
        return output_path

    def extract_requirements(
        self, document_path: str, output_format: str = "json"
    ) -> Optional[str]:
        """
        Extract requirements from a document

        Args:
            document_path: Path to the document (DOCX or MD)
            output_format: Format of the output file (json, yaml, md)

        Returns:
            Path to the output file if successful, None otherwise
        """
        if not os.path.isfile(document_path):
            self.output_handler.log_error(f"Document not found: {document_path}")
            return None

        # Convert to markdown if it's a DOCX file
        file_ext = os.path.splitext(document_path)[1].lower()
        md_content = ""

        if file_ext == ".docx":
            # Convert to markdown
            md_path = self.docx_converter.convert_to_markdown(document_path)
            if not md_path:
                self.output_handler.log_error(
                    f"Failed to convert {document_path} to Markdown"
                )
                return None

            # Read the markdown content
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        elif file_ext == ".md":
            # Read markdown content directly
            with open(document_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        else:
            self.output_handler.log_error(f"Unsupported document format: {file_ext}")
            return None

        # Extract requirements from the markdown content
        requirements = self._extract_requirements_from_markdown(md_content)

        # Generate output file path
        output_path = os.path.join(
            self.paths.get_output_dir(),
            f"requirements_{os.path.splitext(os.path.basename(document_path))[0]}.{output_format}",
        )

        # Save in the requested format
        if output_format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"requirements": requirements}, f, indent=2)
        elif output_format.lower() == "yaml":
            import yaml

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump({"requirements": requirements}, f, default_flow_style=False)
        elif output_format.lower() == "md":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(self._requirements_to_markdown(requirements))
        else:
            self.output_handler.log_error(f"Unsupported output format: {output_format}")
            return None

        self.output_handler.log_info(
            f"Requirements extracted and saved to {output_path}"
        )
        return output_path

    def _parse_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """
        Parse markdown content into structured data

        Args:
            markdown_content: Markdown content to parse

        Returns:
            Structured data extracted from the markdown
        """
        # Extract document structure
        structure = {
            "title": "",
            "sections": [],
            "metadata": {},
        }

        # Extract title (first h1)
        title_match = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
        if title_match:
            structure["title"] = title_match.group(1).strip()

        # Extract metadata (yaml front matter)
        yaml_match = re.search(r"^---\n(.*?)\n---", markdown_content, re.DOTALL)
        if yaml_match:
            try:
                import yaml

                metadata_text = yaml_match.group(1)
                structure["metadata"] = yaml.safe_load(metadata_text)
            except:
                pass

        # Extract sections
        sections = re.findall(r"^(#{2,6})\s+(.+)$", markdown_content, re.MULTILINE)
        current_section = None

        for level, heading in sections:
            level = len(level)  # Number of # characters
            section = {"level": level, "title": heading.strip(), "content": ""}

            structure["sections"].append(section)
            current_section = section

        return structure

    def _extract_requirements_from_markdown(
        self, markdown_content: str
    ) -> List[Dict[str, Any]]:
        """
        Extract requirements from markdown content

        Args:
            markdown_content: Markdown content to parse

        Returns:
            List of extracted requirements
        """
        requirements = []

        # Look for requirement patterns
        # Pattern 1: Headers with REQ prefix
        req_headers = re.finditer(
            r"^(#{1,6})\s+(REQ-\d+)(?:[:\.]\s+)?(.+)?$", markdown_content, re.MULTILINE
        )
        for match in req_headers:
            level, req_id, title = match.groups()
            requirements.append(
                {
                    "id": req_id,
                    "title": title.strip() if title else "",
                    "type": "Requirement",
                    "level": len(level),
                }
            )

        # Pattern 2: List items with REQ prefix
        req_items = re.finditer(
            r"^(?:\*|\-|\d+\.)\s+(REQ-\d+)(?:[:\.]\s+)?(.+)?$",
            markdown_content,
            re.MULTILINE,
        )
        for match in req_items:
            req_id, description = match.groups()
            requirements.append(
                {
                    "id": req_id,
                    "description": description.strip() if description else "",
                    "type": "Requirement",
                }
            )

        # Pattern 3: Table rows with REQ prefix
        table_rows = re.finditer(
            r"^\|\s*(REQ-\d+)\s*\|\s*([^|]+)\s*\|", markdown_content, re.MULTILINE
        )
        for match in table_rows:
            req_id, content = match.groups()
            requirements.append(
                {"id": req_id, "content": content.strip(), "type": "Requirement"}
            )

        return requirements

    def _data_to_markdown(self, data: Dict[str, Any]) -> str:
        """
        Convert structured data back to markdown

        Args:
            data: Structured data to convert

        Returns:
            Markdown representation of the data
        """
        md_lines = []

        # Add title
        if data.get("title"):
            md_lines.append(f"# {data['title']}\n")

        # Add metadata as YAML front matter if present
        if data.get("metadata"):
            import yaml

            md_lines.append("---")
            md_lines.append(
                yaml.dump(data["metadata"], default_flow_style=False).strip()
            )
            md_lines.append("---\n")

        # Add sections
        for section in data.get("sections", []):
            level = section.get("level", 2)
            title = section.get("title", "")
            content = section.get("content", "")

            # Add heading
            md_lines.append(f"{'#' * level} {title}\n")

            # Add content
            if content:
                md_lines.append(content)
                # Add extra newline if content doesn't end with one
                if not content.endswith("\n"):
                    md_lines.append("")

        return "\n".join(md_lines)

    def _requirements_to_markdown(self, requirements: List[Dict[str, Any]]) -> str:
        """
        Convert requirements to markdown format

        Args:
            requirements: List of requirement dictionaries

        Returns:
            Markdown representation of the requirements
        """
        md_lines = ["# Requirements\n"]

        # Add requirements as a list
        for req in requirements:
            req_id = req.get("id", "")

            if "title" in req:
                md_lines.append(f"## {req_id}: {req['title']}\n")

                # Add other properties as list items
                for key, value in req.items():
                    if key not in ["id", "title"]:
                        md_lines.append(f"- **{key}**: {value}")
            elif "description" in req:
                md_lines.append(f"- **{req_id}**: {req['description']}")
            else:
                props = ", ".join([f"{k}: {v}" for k, v in req.items() if k != "id"])
                md_lines.append(f"- **{req_id}** ({props})")

            md_lines.append("")  # Empty line between requirements

        return "\n".join(md_lines)


def extract_requirements(markdown_file, outline_json=None):
    """Extract requirements from markdown."""
    try:
        # Import from local module
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from enhanced_requirement_parser import extract_requirements_from_markdown, find_requirements_in_code

        # Extract requirements from markdown
        requirements = extract_requirements_from_markdown(markdown_file)

        # Add outline information if available
        if outline_json and os.path.exists(outline_json):
            try:
                with open(outline_json, 'r', encoding='utf-8') as f:
                    outline_data = json.load(f)

                # Enhance requirements with section information from outline
                enhance_with_outline(requirements, outline_data)
            except Exception as e:
                logger.warning(f"Could not process outline data: {e}")

        # Find requirement references in code
        project_root = Path(__file__).resolve().parent.parent

        code_files = []
        excluded_dirs = ['.git', '.venv', '__pycache__', 'node_modules', 'output']

        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    code_files.append(file_path)

        requirements_with_files = find_requirements_in_code(code_files, requirements)

        # Add requirement numbering for better organization
        requirements_with_numbering = add_requirement_numbering(requirements_with_files)

        # Save to file
        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "enhanced_requirements_analysis.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(requirements_with_numbering, f, indent=2)

        logger.info(f"Requirements extracted and saved to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Requirements extraction failed: {e}")
        raise

def enhance_with_outline(requirements, outline_data):
    """Add section information to requirements from outline data."""
    # Build a mapping of section titles to their position in the document
    section_map = {}

    def process_sections(sections, path=""):
        for section in sections:
            title = section.get('title', '')
            current_path = f"{path}/{title}" if path else title
            section_map[current_path] = section

            if 'subsections' in section:
                process_sections(section['subsections'], current_path)

    # Process all sections in the outline
    process_sections(outline_data.get('sections', []))

    # Add section context to requirements
    for req_id, req_info in requirements.items():
        # Try to determine the containing section based on line number
        line_num = req_info.get('line', 0)
        closest_section = None
        closest_distance = float('inf')

        for section_path, section in section_map.items():
            section_line = section.get('paragraph_index', 0)
            if section_line <= line_num and (line_num - section_line) < closest_distance:
                closest_distance = line_num - section_line
                closest_section = section_path

        if closest_section:
            req_info['section_path'] = closest_section

def add_requirement_numbering(requirements):
    """Add sequential numbers to requirements based on category."""
    # Group requirements by category
    categories = {}
    for req_id, req_info in requirements.items():
        category = req_info.get('category', 'UNKNOWN')
        if category not in categories:
            categories[category] = []
        categories[category].append(req_id)

    # Add numbering to each requirement
    for category, req_ids in categories.items():
        for i, req_id in enumerate(sorted(req_ids), 1):
            requirements[req_id]['sequence_number'] = i
            requirements[req_id]['full_id'] = f"{category}-{i:03d}"

    return requirements


def main():
    """Command-line interface for the document parser."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract requirements from documents")
    parser.add_argument("input", nargs='?', help="Input markdown file")
    parser.add_argument("-o", "--output-dir", help="Output directory for requirements data")
    parser.add_argument("--outline", help="Path to outline JSON file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Only parse args when run directly
    if __name__ == "__main__":
        args = parser.parse_args()
    else:
        return 0  # Return early when imported

    # Run extraction only when executed directly
    # ...existing code...

if __name__ == "__main__":
    sys.exit(main())
