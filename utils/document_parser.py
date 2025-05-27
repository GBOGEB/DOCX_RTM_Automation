import os
import sys
import re
from typing import Dict, Any, List, Optional, Tuple, Union
import json
from pathlib import Path

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
        self.output_handler = output_handler or OutputHandler(self.paths.get_output_dir())
        self.docx_converter = DocxConverter(self.output_handler)

    def parse_document(self,
                      document_path: str,
                      output_format: str = "json") -> Optional[str]:
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

        if file_ext == '.docx':
            # Convert to markdown
            md_path = self.docx_converter.convert_to_markdown(document_path)
            if not md_path:
                self.output_handler.log_error(f"Failed to convert {document_path} to Markdown")
                return None

            # Read the markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        elif file_ext == '.md':
            # Read markdown content directly
            with open(document_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        else:
            self.output_handler.log_error(f"Unsupported document format: {file_ext}")
            return None

        # Parse the markdown content
        parsed_data = self._parse_markdown(md_content)

        # Generate output file path
        output_path = os.path.join(
            self.paths.get_output_dir(),
            f"{os.path.splitext(os.path.basename(document_path))[0]}.{output_format}"
        )

        # Save in the requested format
        if output_format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2)
        elif output_format.lower() == 'yaml':
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(parsed_data, f, default_flow_style=False)
        elif output_format.lower() == 'md':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._data_to_markdown(parsed_data))
        else:
            self.output_handler.log_error(f"Unsupported output format: {output_format}")
            return None

        self.output_handler.log_info(f"Document parsed and saved to {output_path}")
        return output_path

    def extract_requirements(self,
                           document_path: str,
                           output_format: str = "json") -> Optional[str]:
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

        if file_ext == '.docx':
            # Convert to markdown
            md_path = self.docx_converter.convert_to_markdown(document_path)
            if not md_path:
                self.output_handler.log_error(f"Failed to convert {document_path} to Markdown")
                return None

            # Read the markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        elif file_ext == '.md':
            # Read markdown content directly
            with open(document_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        else:
            self.output_handler.log_error(f"Unsupported document format: {file_ext}")
            return None

        # Extract requirements from the markdown content
        requirements = self._extract_requirements_from_markdown(md_content)

        # Generate output file path
        output_path = os.path.join(
            self.paths.get_output_dir(),
            f"requirements_{os.path.splitext(os.path.basename(document_path))[0]}.{output_format}"
        )

        # Save in the requested format
        if output_format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"requirements": requirements}, f, indent=2)
        elif output_format.lower() == 'yaml':
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump({"requirements": requirements}, f, default_flow_style=False)
        elif output_format.lower() == 'md':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._requirements_to_markdown(requirements))
        else:
            self.output_handler.log_error(f"Unsupported output format: {output_format}")
            return None

        self.output_handler.log_info(f"Requirements extracted and saved to {output_path}")
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
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if title_match:
            structure["title"] = title_match.group(1).strip()

        # Extract metadata (yaml front matter)
        yaml_match = re.search(r'^---\n(.*?)\n---', markdown_content, re.DOTALL)
        if yaml_match:
            try:
                import yaml
                metadata_text = yaml_match.group(1)
                structure["metadata"] = yaml.safe_load(metadata_text)
            except:
                pass

        # Extract sections
        sections = re.findall(r'^(#{2,6})\s+(.+)$', markdown_content, re.MULTILINE)
        current_section = None

        for level, heading in sections:
            level = len(level)  # Number of # characters
            section = {
                "level": level,
                "title": heading.strip(),
                "content": ""
            }

            structure["sections"].append(section)
            current_section = section

        return structure

    def _extract_requirements_from_markdown(self, markdown_content: str) -> List[Dict[str, Any]]:
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
        req_headers = re.finditer(r'^(#{1,6})\s+(REQ-\d+)(?:[:\.]\s+)?(.+)?$', markdown_content, re.MULTILINE)
        for match in req_headers:
            level, req_id, title = match.groups()
            requirements.append({
                "id": req_id,
                "title": title.strip() if title else "",
                "type": "Requirement",
                "level": len(level)
            })

        # Pattern 2: List items with REQ prefix
        req_items = re.finditer(r'^(?:\*|\-|\d+\.)\s+(REQ-\d+)(?:[:\.]\s+)?(.+)?$', markdown_content, re.MULTILINE)
        for match in req_items:
            req_id, description = match.groups()
            requirements.append({
                "id": req_id,
                "description": description.strip() if description else "",
                "type": "Requirement"
            })

        # Pattern 3: Table rows with REQ prefix
        table_rows = re.finditer(r'^\|\s*(REQ-\d+)\s*\|\s*([^|]+)\s*\|', markdown_content, re.MULTILINE)
        for match in table_rows:
            req_id, content = match.groups()
            requirements.append({
                "id": req_id,
                "content": content.strip(),
                "type": "Requirement"
            })

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
            md_lines.append(yaml.dump(data["metadata"], default_flow_style=False).strip())
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

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse documents and extract requirements")
    parser.add_argument("input", help="Input document file (DOCX or MD)")
    parser.add_argument("-o", "--output", help="Output format (json, yaml, md)", default="json")
    parser.add_argument("-r", "--requirements", action="store_true", help="Extract requirements only")

    args = parser.parse_args()

    parser = DocumentParser()

    if args.requirements:
        result = parser.extract_requirements(args.input, args.output)
    else:
        result = parser.parse_document(args.input, args.output)

    if result:
        print(f"Processing successful: {result}")
    else:
        print("Processing failed")
