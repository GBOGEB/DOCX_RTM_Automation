#!/usr/bin/env python3
"""
RTM Pipeline Script - Orchestrates the entire RTM workflow
This script streamlines the process by connecting the different steps:
1. Converts DOCX to MD (using either pandoc or python-docx)
2. Analyzes requirements in the markdown
3. Generates the requirements traceability matrix
"""

import os
import sys
import argparse
import subprocess  # Added import
from pathlib import Path

# Local imports - ensure these modules are in PYTHONPATH or same directory
from src.parsers.enhanced_word_to_md import convert_docx_to_markdown_with_metadata
from src.parsers.pandoc_converter import convert_with_pandoc
from src.parsers.try_word_to_md import convert_docx_to_markdown


def convert_doc(input_file, output_file=None, use_pandoc=True, extract_metadata=True):
    """Convert a DOCX file to Markdown with optional metadata extraction."""
    if extract_metadata:
        try:
            md_file, outline_json, outline_yaml = (
                convert_docx_to_markdown_with_metadata(
                    input_file, output_file, extract_outline=True
                )
            )
            return {
                "markdown": md_file,
                "outline_json": outline_json,
                "outline_yaml": outline_yaml,
            }
        except ImportError:
            print("Enhanced converter not available, using standard methods...")

    if use_pandoc:
        try:
            result = convert_with_pandoc(input_file, output_file)
            if result:
                return {"markdown": result}
            else:
                print("Pandoc conversion failed, falling back to python-docx...")
        except (ImportError, FileNotFoundError):
            print("Pandoc not available, using python-docx instead...")

    return {"markdown": convert_docx_to_markdown(input_file, output_file)}


def analyze_requirements(markdown_file, outline_json=None):
    """Analyze the requirements in the markdown file."""
    try:
        print(f"Analyzing requirements in {markdown_file}...")
        cmd = [sys.executable, "enhanced_requirement_parser.py", str(markdown_file)]

        if outline_json and os.path.exists(outline_json):
            cmd.extend(["--outline", str(outline_json)])

        subprocess.run(cmd, check=True)
        print("Requirement analysis complete.")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            print(
                "Enhanced parser not found, falling back to Project Requirements.py..."
            )
            subprocess.run([sys.executable, "Project Requirements.py"], check=True)
            print("Requirement analysis complete.")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"Error analyzing requirements: {e}")
            return False


def list_available_docx_files():
    """List all available DOCX files in the input directory and current directory."""
    input_dir = Path("input")
    docx_files = []

    if input_dir.exists():
        docx_files.extend(list(input_dir.glob("*.docx")))

    docx_files.extend(list(Path(".").glob("*.docx")))

    return docx_files


def main():
    """Main function to run the RTM pipeline."""
    parser = argparse.ArgumentParser(
        description="RTM Pipeline for DOCX to Markdown conversion and analysis."
    )
    parser.add_argument("input_file", nargs="?", help="Input DOCX file")
    parser.add_argument("-o", "--output", help="Output markdown file")
    parser.add_argument(
        "--no-pandoc",
        action="store_true",
        help="Skip pandoc attempt, use python-docx directly",
    )
    parser.add_argument(
        "--no-metadata", action="store_true", help="Skip metadata extraction"
    )
    parser.add_argument(
        "--convert-only",
        action="store_true",
        help="Only convert, don't analyze requirements",
    )
    parser.add_argument(
        "--list-files", action="store_true", help="List available DOCX files"
    )

    args = parser.parse_args()

    if args.list_files:
        print("\nAvailable DOCX files:")
        docx_files = list_available_docx_files()

        if not docx_files:
            print("No DOCX files found in the input directory or current directory.")
            return 1

        for i, file_path in enumerate(docx_files, 1):
            print(f"  {i}. {file_path}")

        print("\nTo convert a file, run:")
        print("  python rtm_pipeline.py path/to/file.docx")
        return 0

    if args.input_file is None:
        docx_files = list_available_docx_files()

        if docx_files:
            args.input_file = str(docx_files[0])
            print(f"Using found document: {args.input_file}")
        else:
            print("No DOCX files found in input directory or current directory.")
            print(
                "Please specify an input file path or run with --list-files to see available files."
            )
            return 1

    if not os.path.exists(args.input_file):
        print(f"Error: File not found - '{args.input_file}'")
        print("Available DOCX files:")

        docx_files = list_available_docx_files()
        if docx_files:
            for i, file_path in enumerate(docx_files, 1):
                print(f"  {i}. {file_path}")
            print("\nPlease choose one of these files or provide a valid path.")
        else:
            print("No DOCX files found in the input directory or current directory.")
            print(
                "Please place a DOCX file in the input directory or current directory."
            )

        return 1

    conversion_result = convert_doc(
        args.input_file, args.output, not args.no_pandoc, not args.no_metadata
    )

    if not conversion_result or "markdown" not in conversion_result:
        print("Conversion failed.")
        return 1

    output_file = conversion_result["markdown"]
    outline_json = conversion_result.get("outline_json")

    if not args.convert_only:
        if not analyze_requirements(output_file, outline_json):
            print("Requirements analysis failed.")
            return 1

    print("\nRTM Pipeline completed successfully!")
    print(f"- DOCX converted to: {output_file}")

    if outline_json and os.path.exists(outline_json):
        print(f"- Document outline saved as JSON: {outline_json}")

    if not args.convert_only:
        print("- Requirements analyzed")
        print("- Check the output directory for results")

    return 0


if __name__ == "__main__":
    sys.exit(main())
