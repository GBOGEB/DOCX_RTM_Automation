#!/usr/bin/env python3
"""
Digital Twin Parser for RTM Automation
Creates a digital twin representation of document structure and requirements
that can be used for advanced traceability analysis.
"""

import os
import sys
import json
import argparse
import logging
import datetime  # For timestamp in metadata
from pathlib import Path
import re  # Moved import re to top

import yaml  # Third party imports after standard library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentNode:
    """Class representing a node in the document's digital twin."""

    def __init__(self, node_id, node_type, content=None, parent=None):
        self.id = node_id
        self.type = node_type  # section, requirement, table, etc.
        self.content = content or {}
        self.children = []
        self.parent = parent
        self.references = []
        self.attributes = {}

    def add_child(self, node):
        """Add a child node to this node."""
        self.children.append(node)
        node.parent = self
        return node

    def to_dict(self):
        """Convert node to dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'attributes': self.attributes,
            'references': self.references,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data, parent=None):
        """Create node from dictionary."""
        node = cls(data['id'], data['type'], data.get('content', {}), parent)
        node.attributes = data.get('attributes', {})
        node.references = data.get('references', [])

        for child_data in data.get('children', []):
            node.add_child(cls.from_dict(child_data, node))

        return node


def build_digital_twin_from_markdown(markdown_file):
    """
    Build a digital twin model from a markdown document.

    Args:
        markdown_file: Path to the markdown file

    Returns:
        DocumentNode: Root node of the digital twin
    """
    if not os.path.exists(markdown_file):
        logger.error("File not found: %s", markdown_file)
        return None

    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error("Error reading markdown file: %s", e)
        return None

    # Create root node
    root = DocumentNode("document", "document")
    root.attributes['source_file'] = str(markdown_file)
    root.content['title'] = os.path.basename(markdown_file)

    # Track current section and stack
    section_stack = [root]
    current_node = root

    # Process line by line
    lines = content.splitlines()
    line_index = 0

    while line_index < len(lines):
        line = lines[line_index]

        # Process headings (sections)
        heading_match = re.match(r'^(#+)\s+(.*?)(?:\s+\{#(.*?)\})?$', line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2)
            heading_id = heading_match.group(3) if heading_match.group(3) else f"heading-{line_index}"

            # Adjust section stack according to heading level
            while len(section_stack) > level:
                section_stack.pop()

            # Create new section node
            section = DocumentNode(heading_id, "section")
            section.content['title'] = title
            section.content['level'] = level
            section.content['line'] = line_index + 1

            # Add to parent and update stack
            section_stack[-1].add_child(section)
            section_stack.append(section)
            current_node = section

        # Process code blocks
        elif line.strip().startswith("```"):
            # Find the end of the code block
            code_start = line_index
            code_end = code_start + 1
            while code_end < len(lines) and not lines[code_end].strip().startswith("```"):
                code_end += 1

            if code_end < len(lines):
                # Extract code content
                code_content = "\n".join(lines[code_start+1:code_end])

                # Create code node
                code_node = DocumentNode(f"code-{line_index}", "code")
                code_node.content['code'] = code_content
                code_node.content['language'] = line.strip()[3:] or "text"
                current_node.add_child(code_node)

                # Skip to after code block
                line_index = code_end

        # Process tables
        elif line.strip().startswith("|") and line.strip().endswith("|"):
            # Look for separator row
            if line_index + 1 < len(lines) and "|" in lines[line_index + 1] and "-" in lines[line_index + 1]:
                table_rows = [line]
                table_rows.append(lines[line_index + 1])

                # Find remaining table rows
                row_index = line_index + 2
                while row_index < len(lines) and lines[row_index].strip().startswith("|") and lines[row_index].strip().endswith("|"):
                    table_rows.append(lines[row_index])
                    row_index += 1

                # Create table node
                table_node = DocumentNode(f"table-{line_index}", "table")
                table_node.content['rows'] = table_rows

                # Extract header cells
                header_cells = [cell.strip() for cell in table_rows[0].split('|')[1:-1]]
                table_node.content['headers'] = header_cells
                table_node.content['row_count'] = len(table_rows) - 1  # Account for header separator

                current_node.add_child(table_node)

                # Skip processed lines
                line_index = row_index - 1

        # Process requirements (look for patterns like REQ-123, FR-1.2, etc.)
        req_match = re.search(r'(?:^|\s)([A-Z]+-\d+(?:\.\d+)*)', line)
        if req_match:
            req_id = req_match.group(1)
            req_node = DocumentNode(f"req-{req_id}", "requirement")
            req_node.content['id'] = req_id
            req_node.content['text'] = line.strip()
            req_node.content['line'] = line_index + 1

            # Extract req type from ID
            req_type = req_id.split('-')[0] if '-' in req_id else "REQ"
            req_node.content['type'] = req_type

            current_node.add_child(req_node)

        line_index += 1

    # Do a second pass to extract relationships
    build_relationships(root)

    return root


def build_relationships(root):
    """
    Build relationships between nodes in the digital twin.

    Args:
        root: Root DocumentNode
    """
    # Build a map of requirement IDs to their nodes
    requirement_map = {}

    def collect_requirements(node):
        if node.type == "requirement" and 'id' in node.content:
            requirement_map[node.content['id']] = node
        for child in node.children:
            collect_requirements(child)

    collect_requirements(root)

    # Look for references between requirements
    def find_references(node):
        if node.type in ["section", "table", "paragraph"]:
            # Look for requirement references in the content
            content_text = str(node.content)
            for req_id, _ in requirement_map.items():  # Mark req_node as unused
                # Skip self-references
                if node.type == "requirement" and node.content.get('id') == req_id:
                    continue

                # Look for the requirement ID in this node's content
                if req_id in content_text:
                    node.references.append(req_id)

        # Recursively process children
        for child in node.children:
            find_references(child)

    find_references(root)


def integrate_with_requirements_data(digital_twin, requirements_file):
    """
    Integrate requirements data with the digital twin.

    Args:
        digital_twin: Root DocumentNode of the digital twin
        requirements_file: Path to the requirements JSON file

    Returns:
        Updated digital twin with integrated requirements data
    """
    if not os.path.exists(requirements_file):
        logger.error("Requirements file not found: %s", requirements_file)
        return digital_twin

    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements_data = json.load(f)
    except Exception as e:
        logger.error("Error reading requirements file: %s", e)
        return digital_twin

    # Find requirement nodes and update them with data from the requirements file
    def update_requirements(node):
        if node.type == "requirement" and 'id' in node.content:
            req_id = node.content['id']
            if req_id in requirements_data:
                # Update node with detailed requirement info
                req_data = requirements_data[req_id]
                node.attributes.update({
                    'description': req_data.get('description', ''),
                    'status': req_data.get('status', 'Unknown'),
                    'implementation_files': req_data.get('implementation_files', []),
                    'category': req_data.get('category', 'Unknown'),
                })

                # Add relationships if any
                for ref in req_data.get('references', []):
                    if ref not in node.references:
                        node.references.append(ref)

        # Recursively process children
        for child in node.children:
            update_requirements(child)

    update_requirements(digital_twin)
    return digital_twin


def parse_digital_twin(data):
    """
    Parse raw digital twin data into a structured model.

    Args:
        data (dict): The input digital twin data.

    Returns:
        dict: Parsed and structured data.
    """
    try:
        # If we're parsing JSON from a file
        if isinstance(data, str) and os.path.exists(data):
            with open(data, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # Main parsing logic
        parsed_data = {
            "id": data.get("id"),
            "name": data.get("name"),
            "properties": data.get("properties", {}),
            "relationships": data.get("relationships", []),
            "structure": data.get("structure", {})
        }

        # Add structure analysis if needed
        if "children" in data:
            parsed_data["structure"] = {
                "total_nodes": count_nodes(data),
                "max_depth": calculate_depth(data),
                "node_types": count_node_types(data)
            }

        logger.info("Successfully parsed digital twin with ID: %s", parsed_data['id'])
        return parsed_data

    except Exception as e:
        logger.error("Error parsing digital twin data: %s", e)
        return None


def count_nodes(data):
    """Count total nodes in the digital twin."""
    if not isinstance(data, dict):
        return 0

    count = 1  # Count this node
    for child in data.get('children', []):
        count += count_nodes(child)
    return count


def calculate_depth(data, current_depth=0):
    """Calculate maximum depth of the digital twin tree."""
    if not isinstance(data, dict):
        return current_depth

    max_depth = current_depth + 1
    for child in data.get('children', []):
        child_depth = calculate_depth(child, max_depth)
        max_depth = max(max_depth, child_depth)

    return max_depth


def count_node_types(data):
    """Count nodes of each type in the digital twin."""
    if not isinstance(data, dict):
        return {}

    node_types = {}
    node_type = data.get('type', 'unknown')

    # Count this node's type
    node_types[node_type] = node_types.get(node_type, 0) + 1

    # Count children's types
    for child in data.get('children', []):
        child_types = count_node_types(child)
        for t, count in child_types.items():
            node_types[t] = node_types.get(t, 0) + count

    return node_types


def save_digital_twin(root, output_dir=None, formats=None):
    """
    Save digital twin to disk in multiple formats.

    Args:
        root: Root DocumentNode or dict representing the digital twin
        output_dir: Directory to save output files (default: output/)
        formats: List of formats to save (default: ['json', 'yaml'])

    Returns:
        Dictionary with paths to the saved files
    """
    if output_dir is None:
        output_dir = Path('output')
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True, parents=True)

    if formats is None:
        formats = ['json', 'yaml']

    # Convert to dict if necessary
    if hasattr(root, 'to_dict'):
        data = root.to_dict()
    else:
        data = root

    # Add metadata
    if 'metadata' not in data:
        data['metadata'] = {
            'creation_time': str(datetime.datetime.now()),
            'node_count': count_nodes(data),
            'max_depth': calculate_depth(data)
        }

    output_files = {}
    base_name = 'digital_twin'

    # Save in requested formats
    if 'json' in formats:
        json_path = output_dir / f"{base_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        output_files['json'] = json_path
        logger.info("Saved digital twin as JSON: %s", json_path)

    if 'yaml' in formats:
        yaml_path = output_dir / f"{base_name}.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        output_files['yaml'] = yaml_path
        logger.info("Saved digital twin as YAML: %s", yaml_path)

    return output_files


def main():
    """Main entry point for the digital twin parser."""
    parser = argparse.ArgumentParser(
        description="Create a digital twin representation of document structure and requirements"
    )
    parser.add_argument(
        "input_file", nargs="?",
        help="Input file to parse (markdown or JSON)"
    )
    parser.add_argument(
        "-r", "--requirements",
        help="Path to requirements JSON file to integrate"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory to save output files"
    )
    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        choices=["json", "yaml"],
        default=["json", "yaml"],
        help="Output formats to generate"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # When run directly, use the example data if no input file provided
    if not args.input_file:
        # Use example data
        sample_data = {
            "id": "12345",
            "name": "Sample Twin",
            "properties": {"temperature": 22.5, "status": "active"},
            "relationships": [{"type": "connectedTo", "target": "67890"}],
        }

        result = parse_digital_twin(sample_data)
        print("Parsed Digital Twin Data:", result)
        return 0

    # Process input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error("Input file not found: %s", args.input_file)
        return 1

    # Branch based on input file type
    if input_path.suffix.lower() in ['.md', '.markdown']:
        # Build digital twin from markdown
        logger.info("Building digital twin from markdown: %s", input_path)
        digital_twin = build_digital_twin_from_markdown(input_path)

        # Integrate requirements data if provided
        if args.requirements and os.path.exists(args.requirements):
            digital_twin = integrate_with_requirements_data(digital_twin, args.requirements)

        # Save to disk
        save_digital_twin(digital_twin, args.output_dir, args.formats)

    elif input_path.suffix.lower() == '.json':
        # Parse existing digital twin data
        logger.info("Parsing digital twin from JSON: %s", input_path)
        digital_twin_data = parse_digital_twin(args.input_file)

        if digital_twin_data:
            # Save parsed data
            with open(Path(args.output_dir) / "parsed_digital_twin.json", 'w', encoding='utf-8') as f:
                json.dump(digital_twin_data, f, indent=2)
            logger.info("Successfully parsed and saved digital twin data")
        else:
            logger.error("Failed to parse digital twin data")
            return 1

    else:
        logger.error("Unsupported file type: %s", input_path.suffix)
        return 1

    logger.info("Digital twin processing complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
