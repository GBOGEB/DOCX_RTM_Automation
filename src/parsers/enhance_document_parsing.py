#!/usr/bin/env python3
"""
Enhanced Document Parsing Tool

This script provides improved document parsing capabilities for RTM automation,
with support for multiple formats and enhanced metadata extraction.
"""

import os
import sys
import json
import yaml
import argparse
import logging
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check for markdown library (now that it's working)
try:
    import markdown

    MARKDOWN_AVAILABLE = True
    logger.info(
        "Markdown library available (version %s)",
        getattr(markdown, "__version__", "unknown"),
    )
except ImportError:
    MARKDOWN_AVAILABLE = False
    logger.warning("Markdown library not available")

# Check for python-docx
try:
    from docx import Document

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def enhance_document_parsing(input_file, output_file=None, format_type="markdown"):
    """
    Enhance document parsing with improved metadata extraction.

    Args:
        input_file: Path to the input document
        output_file: Path for the output file (default: auto-generated)
        format_type: Output format (markdown, json, yaml)

    Returns:
        Path to the output file
    """
    logger.info(f"Enhancing document parsing for: {input_file}")

    # Determine input file type
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_file}")
        return None

    # Handle different input types
    if input_path.suffix.lower() in [".docx", ".doc"]:
        return parse_word_document(input_path, output_file, format_type)
    elif input_path.suffix.lower() in [".md", ".markdown"]:
        return enhance_markdown_document(input_path, output_file, format_type)
    elif input_path.suffix.lower() in [".json"]:
        return enhance_json_document(input_path, output_file, format_type)
    elif input_path.suffix.lower() in [".yaml", ".yml"]:
        return enhance_yaml_document(input_path, output_file, format_type)
    else:
        logger.error(f"Unsupported input format: {input_path.suffix}")
        return None


def parse_word_document(input_path, output_file=None, format_type="markdown"):
    """Parse a Word document with enhanced metadata extraction."""
    logger.info(f"Parsing Word document: {input_path}")

    if not DOCX_AVAILABLE:
        logger.error("python-docx not installed. Run: pip install python-docx")
        return None

    try:
        # Load the document
        doc = Document(input_path)

        # Determine output path if not specified
        if output_file is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True, parents=True)
            output_file = (
                output_dir
                / f"{input_path.stem}.{format_type_to_extension(format_type)}"
            )
        else:
            output_file = Path(output_file)

        # Extract document content and metadata
        document_data = {
            "metadata": {
                "title": input_path.stem,
                "original_file": str(input_path),
                "paragraphs": len(doc.paragraphs),
                "sections": len(doc.sections),
                "tables": len(doc.tables),
            },
            "content": [],
        }

        # Process document properties if available
        if hasattr(doc, "core_properties"):
            props = doc.core_properties
            document_data["metadata"].update(
                {
                    "author": props.author,
                    "subject": props.subject,
                    "created": str(props.created) if props.created else None,
                    "modified": str(props.modified) if props.modified else None,
                    "title": props.title or input_path.stem,
                    "keywords": props.keywords,
                }
            )

        # Process paragraphs
        current_section = {"heading": document_data["metadata"]["title"], "content": []}

        for para in doc.paragraphs:
            if not para.text.strip():
                continue

            # Check if it's a heading
            if para.style.name.startswith("Heading"):
                # Add the previous section if it has content
                if current_section["content"]:
                    document_data["content"].append(current_section)
                # Start a new section
                heading_level = (
                    int(para.style.name[-1]) if para.style.name[-1].isdigit() else 1
                )
                current_section = {
                    "heading": para.text,
                    "level": heading_level,
                    "content": [],
                }
            else:
                # Add paragraph to current section
                current_section["content"].append(
                    {"type": "paragraph", "text": para.text, "style": para.style.name}
                )

        # Add the last section if it has content
        if current_section["content"]:
            document_data["content"].append(current_section)

        # Save in appropriate format
        save_document_data(document_data, output_file, format_type)

        return output_file

    except Exception as e:
        logger.error(f"Error parsing Word document: {e}")
        import traceback

        traceback.print_exc()
        return None


def enhance_markdown_document(input_path, output_file=None, format_type="markdown"):
    """Enhance a Markdown document with additional metadata and structure."""
    logger.info("Enhancing Markdown document: %s", input_path)

    try:
        # Read the markdown content
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Determine output path if not specified
        if output_file is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True, parents=True)
            ext = format_type_to_extension(format_type)
            output_file = output_dir / f"{input_path.stem}_enhanced.{ext}"
        else:
            output_file = Path(output_file)

        # Extract structure and metadata using regex
        import re

        # Extract headings
        heading_pattern = re.compile(r"^(#+)\s+(.*?)$", re.MULTILINE)
        headings = [(len(h[0]), h[1]) for h in heading_pattern.findall(content)]

        # Extract potential requirement IDs
        req_pattern = re.compile(r"([A-Z]+-\d+(?:\.\d+)*)")
        requirements = req_pattern.findall(content)

        # If markdown library is available, also parse with it for validation
        html_content = None
        if MARKDOWN_AVAILABLE:
            try:
                html_content = markdown.markdown(content)
                logger.info("Successfully parsed markdown to HTML for validation")
            except Exception as e:
                logger.warning("Error parsing with markdown library: %s", e)

        # Build document data structure
        document_data = {
            "metadata": {
                "title": headings[0][1] if headings else input_path.stem,
                "original_file": str(input_path),
                "requirements_found": list(set(requirements)),
                "headings_count": len(headings),
                "content_length": len(content),
                "lines_count": len(content.splitlines()),
                "markdown_processed": (MARKDOWN_AVAILABLE and html_content is not None),
            },
            "content": content,
        }

        # Add HTML content if available
        if html_content:
            document_data["html_content"] = html_content

        # Save in appropriate format
        save_document_data(document_data, output_file, format_type)

        return output_file

    except Exception as e:
        logger.error("Error enhancing Markdown document: %s", e)
        import traceback

        traceback.print_exc()
        return None


def enhance_json_document(input_path, output_file=None, format_type="json"):
    """Enhance a JSON document with additional structure and validation."""
    logger.info(f"Enhancing JSON document: {input_path}")

    try:
        # Read the JSON content
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Determine output path if not specified
        if output_file is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True, parents=True)
            ext = format_type_to_extension(format_type)
            output_file = output_dir / f"{input_path.stem}_enhanced.{ext}"
        else:
            output_file = Path(output_file)

        # Enhance the data structure
        import datetime

        enhanced_data = {
            "metadata": {
                "title": data.get("title", input_path.stem),
                "original_file": str(input_path),
                "processed_date": str(datetime.datetime.now()),
            },
            "content": data,
        }

        # Save in appropriate format
        save_document_data(enhanced_data, output_file, format_type)

        return output_file

    except Exception as e:
        logger.error(f"Error enhancing JSON document: {e}")
        import traceback

        traceback.print_exc()
        return None


def enhance_yaml_document(input_path, output_file=None, format_type="yaml"):
    """Enhance a YAML document with additional structure and validation."""
    logger.info(f"Enhancing YAML document: {input_path}")

    try:
        # Read the YAML content
        with open(input_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Determine output path if not specified
        if output_file is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True, parents=True)
            ext = format_type_to_extension(format_type)
            output_file = output_dir / f"{input_path.stem}_enhanced.{ext}"
        else:
            output_file = Path(output_file)

        # Enhance the data structure
        import datetime

        enhanced_data = {
            "metadata": {
                "title": data.get("title", input_path.stem),
                "original_file": str(input_path),
                "processed_date": str(datetime.datetime.now()),
            },
            "content": data,
        }

        # Save in appropriate format
        save_document_data(enhanced_data, output_file, format_type)

        return output_file

    except Exception as e:
        logger.error(f"Error enhancing YAML document: {e}")
        import traceback

        traceback.print_exc()
        return None


def integrate_with_project_requirements():
    """Integrate with Project Requirements.py if available."""
    try:
        # Try to import Project Requirements module
        project_req_path = project_root / "Project Requirements.py"
        if project_req_path.exists():
            # Import dynamically to avoid issues
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "project_requirements", project_req_path
            )
            if spec and spec.loader:
                project_req_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(project_req_module)

                # Check if the module has expected functions
                if hasattr(project_req_module, "analyze_requirements"):
                    logger.info("Successfully integrated with Project Requirements.py")
                    return project_req_module
                else:
                    logger.warning(
                        "Project Requirements.py found but missing expected functions"
                    )
        else:
            logger.info(
                "Project Requirements.py not found - continuing without integration"
            )

    except Exception as e:
        logger.warning("Could not integrate with Project Requirements.py: %s", e)

    return None


def check_integration_dependencies():
    """Check for integration dependencies and suggest fixes."""
    logger.info("Checking integration dependencies...")

    dependencies = {
        "markdown": MARKDOWN_AVAILABLE,
        "python-docx": DOCX_AVAILABLE,
        "yaml": True,  # yaml is part of standard library or should be installed
        "json": True,  # json is part of standard library
    }

    missing_deps = [name for name, available in dependencies.items() if not available]

    if missing_deps:
        logger.warning("Missing dependencies: %s", ", ".join(missing_deps))
        logger.info("Install missing dependencies with:")
        for dep in missing_deps:
            if dep == "python-docx":
                logger.info("  pip install python-docx")
            elif dep == "markdown":
                logger.info("  pip install markdown")
    else:
        logger.info("All integration dependencies are available")

    return len(missing_deps) == 0


def format_type_to_extension(format_type):
    """Convert format type to file extension."""
    format_map = {"markdown": "md", "json": "json", "yaml": "yaml", "yml": "yml"}
    return format_map.get(format_type.lower(), "txt")


def save_document_data(data, output_file, format_type):
    """Save document data in the specified format."""
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)

    if format_type.lower() == "markdown":
        # Create markdown content
        with open(output_file, "w", encoding="utf-8") as f:
            # Write metadata as YAML front matter
            f.write("---\n")
            yaml.dump(data["metadata"], f, default_flow_style=False)
            f.write("---\n\n")
            # Write content
            if isinstance(data["content"], str):
                f.write(data["content"])
            else:
                # Convert structured content to markdown
                for section in data.get("content", []):
                    heading = section.get("heading", "")
                    level = section.get("level", 1)
                    if heading:
                        f.write("#" * level + " " + heading + "\n\n")

                    for item in section.get("content", []):
                        if item.get("type") == "paragraph":
                            f.write(item.get("text", "") + "\n\n")

    elif format_type.lower() in ["json"]:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    elif format_type.lower() in ["yaml", "yml"]:
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)

    logger.info(f"Saved enhanced document to {output_file}")


def list_available_input_files():
    """List available input files that can be processed."""
    input_dirs = ["input", "input/docx", "input/markdown"]
    available_files = []
    for dir_name in input_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.glob("*.*"):
                if file_path.suffix.lower() in [
                    ".docx",
                    ".doc",
                    ".md",
                    ".markdown",
                    ".json",
                    ".yaml",
                    ".yml",
                ]:
                    available_files.append(str(file_path))
    return available_files


# ...existing code...


def main():
    """Main function for the enhance_document_parsing script."""
    parser = argparse.ArgumentParser(
        description="Enhanced document parsing tool for RTM automation"
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to input document file (DOCX, MD, JSON, or YAML)",
    )
    parser.add_argument("-o", "--output", help="Path for the enhanced output file")
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json", "yaml"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available input files and exit"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use sample document if no input file is specified",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode if no input file is specified",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check integration dependencies and exit",
    )
    parser.add_argument(
        "--integrate",
        action="store_true",
        help="Enable integration with Project Requirements.py",
    )

    # Parse arguments with better error handling
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:  # Not a --help request
            print(
                "\nFor usage information, run: python enhance_document_parsing.py --help"
            )
            print("Quick start options:")
            print("  --list        Show available input files")
            print("  --sample      Use sample document")
            print("  --check-deps  Check dependencies")
        return e.code

    # Handle --check-deps option
    if args.check_deps:
        all_deps_ok = check_integration_dependencies()

        # Also check for Project Requirements.py
        project_req_module = integrate_with_project_requirements()
        if project_req_module:
            print("✅ Project Requirements.py integration available")
        else:
            print("❌ Project Requirements.py integration not available")

        return 0 if all_deps_ok else 1

    # Handle --list option
    if args.list:
        available_files = list_available_input_files()
        if available_files:
            print("\nAvailable input files:")
            for file_path in available_files:
                print(f"  {file_path}")
            print(f"\nExample: python {Path(sys.argv[0]).name} {available_files[0]}")
        else:
            print("\nNo input files found in standard directories.")
            print("Place files in input/, input/docx/, or input/markdown/ directories.")
        return 0

    # Check dependencies before processing
    if not check_integration_dependencies():
        logger.warning("Some dependencies are missing. Functionality may be limited.")

    # Try to integrate with Project Requirements.py if requested
    project_req_module = None
    if args.integrate:
        project_req_module = integrate_with_project_requirements()

    # Determine input file
    input_file = args.input_file

    # Handle the case when no input file is provided
    if not input_file:
        if args.sample:
            # Use sample document
            sample_path = Path("input/sample/sample_document.md")
            if not sample_path.exists():
                # Create a sample document
                sample_path.parent.mkdir(exist_ok=True, parents=True)
                with open(sample_path, "w", encoding="utf-8") as f:
                    f.write("# Sample Document\n\n")
                    f.write("This is a sample document for demonstration purposes.\n\n")
                    f.write("## Requirements\n\n")
                    f.write("The following requirements are included:\n\n")
                    f.write("* REQ-001: First example requirement\n")
                    f.write("* REQ-002: Second example requirement\n\n")
                    f.write("## FR-1: Functional Requirement\n\n")
                    f.write("This section includes a functional requirement.\n\n")
                    f.write("## NFR-1: Non-Functional Requirement\n\n")
                    f.write("This section includes a performance requirement.\n")

            input_file = str(sample_path)
            print(f"Using sample document: {input_file}")
        elif args.interactive:
            # Interactive mode - let user select a file
            available_files = list_available_input_files()
            if not available_files:
                print("\nNo input files found in standard directories.")
                print(
                    "Place files in input/, input/docx/, or input/markdown/ directories."
                )
                return 1

            print("\nPlease select an input file:")
            for idx, file_path in enumerate(available_files, 1):
                print(f"  {idx}. {file_path}")

            try:
                choice = int(input("\nEnter number (or 0 to exit): "))
                if choice == 0:
                    print("Exiting.")
                    return 0
                if 1 <= choice <= len(available_files):
                    input_file = available_files[choice - 1]
                    print(f"Selected: {input_file}")
                else:
                    print("Invalid selection. Exiting.")
                    return 1
            except (ValueError, KeyboardInterrupt):
                print("\nExiting.")
                return 0
        else:
            # No input file provided, show help
            print("\nNo input file specified. Please use one of these options:")
            print(
                "  1. Specify an input file: "
                "python enhance_document_parsing.py input/myfile.docx"
            )
            print("  2. Use --sample flag: python enhance_document_parsing.py --sample")
            print(
                "  3. Use --interactive mode: "
                "python enhance_document_parsing.py --interactive"
            )
            print(
                "  4. List available files: python enhance_document_parsing.py --list"
            )
            print(
                "  5. Check dependencies: "
                "python enhance_document_parsing.py --check-deps"
            )
            return 1

    # Ensure input file exists
    if not os.path.exists(input_file):
        print(f"\nError: File not found - {input_file}")
        print("Run with --list to see available files")
        return 1

    # Process the document
    try:
        result = enhance_document_parsing(input_file, args.output, args.format)

        if result:
            print(f"\nSuccess! Enhanced document saved to: {result}")

            # If Project Requirements integration is available and enabled
            if project_req_module and args.integrate:
                try:
                    # Try to analyze the enhanced document
                    if hasattr(project_req_module, "analyze_requirements"):
                        print("Running integrated requirements analysis...")
                        analysis_result = project_req_module.analyze_requirements(
                            str(result)
                        )
                        if analysis_result:
                            print("✅ Requirements analysis completed successfully")
                        else:
                            print("⚠️ Requirements analysis completed with warnings")
                except Exception as e:
                    logger.warning("Error in integrated requirements analysis: %s", e)

            return 0
        else:
            print("\nError: Document processing failed. Check the logs for details.")
            return 1

    except Exception as e:
        logger.error("Unexpected error during processing: %s", e)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
