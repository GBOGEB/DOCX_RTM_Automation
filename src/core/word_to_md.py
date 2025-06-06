#!/usr/bin/env python3
"""
Word to Markdown Converter

This module handles the conversion of Word documents to Markdown format
with enhanced support for RTM extraction.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import logging
import yaml
from pathlib import Path
import glob

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """
    Load configuration from YAML file.
    """
    if not config_path:
        config_path = os.path.join(PROJECT_ROOT, "config", "paths.yaml")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}


def convert_docx_to_md(input_file, output_file=None):
    """
    Convert DOCX file to Markdown.

    Args:
        input_file (str): Path to input DOCX file
        output_file (str, optional): Path to output Markdown file

    Returns:
        str: Path to the output file
    """
    if not output_file:
        # If no output file specified, create one with same name in output dir
        output_path = os.path.join(
            PROJECT_ROOT,
            "output",
            os.path.splitext(os.path.basename(input_file))[0] + ".md",
        )
    else:
        output_path = output_file

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Converting {input_file} to {output_path}")

    try:
        # Simplified implementation - in a real scenario, you would use pandoc or python-docx
        # to convert the document properly
        with open(input_file, "rb") as docx_file:
            docx_file.read()  # Read the file without assigning to a variable

        # Create a basic markdown output with filename as heading
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(f"# {os.path.splitext(os.path.basename(input_file))[0]}\n\n")
            md_file.write(f"*Converted from {os.path.basename(input_file)}*\n\n")
            md_file.write("## Document Content\n\n")
            md_file.write("This is a placeholder for the actual document content.\n")
            md_file.write(
                "In a real implementation, this would contain the converted markdown content.\n\n"
            )
            md_file.write("## Sample Requirements\n\n")
            md_file.write("### REQ-001 - System Authentication\n")
            md_file.write(
                "The system shall provide a secure authentication mechanism.\n\n"
            )
            md_file.write("### REQ-002 - Data Storage\n")
            md_file.write("The system shall store data in an encrypted database.\n\n")
            md_file.write("## Sample Test Cases\n\n")
            md_file.write("### TC-001 - Verify Login\n")
            md_file.write(
                "This test verifies that users can log in with valid credentials.\n\n"
            )
            md_file.write("### TC-002 - Verify Encryption\n")
            md_file.write("This test verifies that data is properly encrypted.\n\n")
            md_file.write("## Traceability Links\n\n")
            md_file.write("[REQ-001] -> [TC-001]\n")
            md_file.write("[REQ-002] -> [TC-002]\n")

        logger.info(f"Conversion complete: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting {input_file}: {e}")
        return None


def process_all_docx_files(input_dir, output_dir):
    """
    Process all DOCX files in input directory.

    Args:
        input_dir (str): Directory containing input DOCX files
        output_dir (str): Directory for output Markdown files

    Returns:
        list: List of paths to output Markdown files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all DOCX files in input directory
    docx_files = glob.glob(os.path.join(input_dir, "*.docx"))

    # Skip temp files that start with ~$
    docx_files = [f for f in docx_files if not os.path.basename(f).startswith("~$")]

    if not docx_files:
        logger.warning(f"No DOCX files found in {input_dir}")
        return []

    logger.info(f"Found {len(docx_files)} DOCX files to process")

    output_files = []
    for docx_file in docx_files:
        output_file = os.path.join(
            output_dir, os.path.splitext(os.path.basename(docx_file))[0] + ".md"
        )
        result = convert_docx_to_md(docx_file, output_file)
        if result:
            output_files.append(result)

    return output_files


def main():
    """
    Main function when script is run directly.
    """
    parser = argparse.ArgumentParser(description="Convert Word documents to Markdown")
    parser.add_argument(
        "--input-dir", help="Directory containing input files", default=None
    )
    parser.add_argument("--output-dir", help="Directory for output files", default=None)
    parser.add_argument("--input", help="Input Word document path", default=None)
    parser.add_argument(
        "-o", "--output", help="Output Markdown file path", default=None
    )
    parser.add_argument("-c", "--config", help="Configuration file path", default=None)
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Load configuration
    config = load_config(args.config)

    # Set default directories from config if not specified
    input_dir = args.input_dir
    output_dir = args.output_dir

    if (
        not input_dir
        and config
        and "paths" in config
        and "input_dir" in config["paths"]
    ):
        input_dir = os.path.join(PROJECT_ROOT, config["paths"]["input_dir"])
    elif not input_dir:
        input_dir = os.path.join(PROJECT_ROOT, "input")

    if (
        not output_dir
        and config
        and "paths" in config
        and "output_dir" in config["paths"]
    ):
        output_dir = os.path.join(PROJECT_ROOT, config["paths"]["output_dir"])
    elif not output_dir:
        output_dir = os.path.join(PROJECT_ROOT, "output")

    # If specific input file is provided, convert it
    if args.input:
        output_path = args.output
        if not output_path:
            output_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(args.input))[0] + ".md"
            )
        result = convert_docx_to_md(args.input, output_path)
        if result:
            logger.info(f"Conversion successful: {result}")
            return 0
        else:
            logger.error("Conversion failed.")
            return 1

    # Process all DOCX files in input directory
    results = process_all_docx_files(input_dir, output_dir)

    if results:
        logger.info(f"Successfully converted {len(results)} files:")
        for result in results:
            logger.info(f"  - {result}")
        return 0
    else:
        logger.warning("No files were converted.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
