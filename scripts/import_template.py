import os
import sys
import json
import shutil
import argparse
from pathlib import Path

#!/usr/bin/env python3
"""
import_template.py - Template management utility for document conversion pipeline.

This script allows:
- Importing custom templates from external files
- Extracting template components from existing markdown files
- Creating default templates with styling
- Listing available templates
"""


# Define default templates directory - use a relative path that works with the script location
SCRIPT_DIR = Path(__file__).parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"

# Default template content for Markdown with styling
DEFAULT_TEMPLATE_MD = """---
title: Document Title
author: Author Name
date: Date
css: styles.css
---

# Document Title

## Introduction

This is a sample document that demonstrates the template styling.

::: {.requirement #REQ-001}
The system shall provide template functionality.

[priority:high] [status:draft]
:::

### Subsection

This demonstrates the hierarchical structure.

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| More     | More     | More     |

"""

# Default CSS content
DEFAULT_CSS = """
body {
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: auto;
    padding: 1em;
    line-height: 1.5;
}

h1, h2, h3, h4, h5, h6 {
    color: #333;
    font-weight: bold;
}

.requirement {
    border-left: 5px solid #3498db;
    background-color: #f8f9fa;
    padding: 10px;
    margin: 15px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
}
"""


def ensure_template_dir():
    """Ensure that the templates directory exists."""
    TEMPLATE_DIR.mkdir(exist_ok=True)


def create_default_template():
    """Create default template files."""
    ensure_template_dir()

    # Create the default markdown template
    template_path = TEMPLATE_DIR / "default.md"
    with open(template_path, "w") as f:
        f.write(DEFAULT_TEMPLATE_MD)

    # Create the default CSS
    css_path = TEMPLATE_DIR / "styles.css"
    with open(css_path, "w") as f:
        f.write(DEFAULT_CSS)

    print(f"Created default template at {template_path}")
    print(f"Created default CSS at {css_path}")


def list_templates():
    """List all available templates."""
    ensure_template_dir()

    templates = list(TEMPLATE_DIR.glob("*.md"))
    css_files = list(TEMPLATE_DIR.glob("*.css"))

    if not templates and not css_files:
        print("No templates available.")
        print("Use 'import_template.py create' to create a default template.")
        return

    if templates:
        print("Available markdown templates:")
        for template in templates:
            print(f"  - {template.name}")

    if css_files:
        print("Available CSS templates:")
        for css in css_files:
            print(f"  - {css.name}")


def import_template(source_path, name=None):
    """Import a template from an external file."""
    ensure_template_dir()

    source = Path(source_path)
    if not source.exists():
        print(f"Error: Source file {source_path} does not exist.")
        return False

    if name is None:
        name = source.name

    destination = TEMPLATE_DIR / name

    try:
        shutil.copy2(source, destination)
        print(f"Imported template: {source} -> {destination}")
        return True
    except Exception as e:
        print(f"Error importing template: {e}")
        return False


def extract_template(markdown_path, output_name=None):
    """
    Extract template components from an existing markdown file.
    """
    source = Path(markdown_path)
    if not source.exists():
        print(f"Error: Source file {markdown_path} does not exist.")
        return False

    ensure_template_dir()

    if output_name is None:
        output_name = f"extracted_{source.name}"

    destination = TEMPLATE_DIR / output_name

    try:
        shutil.copy2(source, destination)
        print(f"Extracted template from {source} to {destination}")
        return True
    except Exception as e:
        print(f"Error extracting template: {e}")
        return False


def main():
    """Main function to handle command-line arguments and execute operations."""
    parser = argparse.ArgumentParser(
        description="Template management utility for document conversion pipeline."
    )

    # Define subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create a default template")

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List available templates")

    # Import command
    import_parser = subparsers.add_parser(
        "import", help="Import a template from an external file"
    )
    import_parser.add_argument("source", help="Source template file path")
    import_parser.add_argument("--name", help="Name for the imported template")

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract", help="Extract template from a markdown file"
    )
    extract_parser.add_argument("source", help="Source markdown file path")
    extract_parser.add_argument(
        "--name", help="Name for the extracted template")

    # Parse arguments
    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "create":
        create_default_template()
    elif args.command == "list":
        list_templates()
    elif args.command == "import":
        import_template(args.source, args.name)
    elif args.command == "extract":
        extract_template(args.source, args.name)
    elif args.command == "--create-default":
        create_default_template()
    else:
        # If no command is specified, show help
        parser.print_help()


if __name__ == "__main__":
    create_default_template()
    os.system("python scripts/import_template.py --create-default")
    os.system(
        "scripts\\pandoc_convert.bat input\\your_document.docx output\\your_document.md"
    )
