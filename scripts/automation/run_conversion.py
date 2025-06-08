#!/usr/bin/env python3
"""
Conversion Runner Script

This script provides better error handling and automation for the document conversion process.
It helps detect common issues like missing files and incorrect paths.
"""

import os
import sys
import glob
import argparse
from pathlib import Path

def find_document(document_path):
    """Find the document, handling common issues like typos in extension."""
    if os.path.exists(document_path):
        return document_path

    # Check if it's an extension issue
    base_path = os.path.splitext(document_path)[0]
    for ext in ['.docx', '.doc', '.rtf', '.odt']:
        test_path = f"{base_path}{ext}"
        if os.path.exists(test_path):
            print(f"Found document with corrected extension: {test_path}")
            return test_path

    # Check in common directories
    filename = os.path.basename(document_path)
    base_filename = os.path.splitext(filename)[0]

    # Look in input directory
    input_dir = Path("input")
    if input_dir.exists():
        for ext in ['.docx', '.doc', '.rtf', '.odt']:
            matches = list(input_dir.glob(f"{base_filename}{ext}"))
            if matches:
                print(f"Found document in input directory: {matches[0]}")
                return str(matches[0])

            # Try partial name match
            matches = list(input_dir.glob(f"*{base_filename}*{ext}"))
            if matches:
                print(f"Found similar document in input directory: {matches[0]}")
                return str(matches[0])

    # List available documents
    print(f"Error: Could not find document '{document_path}'")
    print("\nAvailable documents:")

    for directory in [".", "input"]:
        dir_path = Path(directory)
        if dir_path.exists():
            doc_files = list(dir_path.glob("*.docx")) + list(dir_path.glob("*.doc"))
            if doc_files:
                print(f"\nIn {directory}/ directory:")
                for i, doc in enumerate(doc_files, 1):
                    print(f"  {i}. {doc}")

    return None

def fix_output_path(output_path):
    """Fix output path with incorrect separators."""
    # Replace backslashes with forward slashes for consistency
    fixed_path = output_path.replace('\\', '/')

    # Check if the directory exists, create if needed
    output_dir = os.path.dirname(fixed_path)
    os.makedirs(output_dir, exist_ok=True)

    return fixed_path

def main():
    parser = argparse.ArgumentParser(description="Run document conversion with improved error handling")
    parser.add_argument("input_file", nargs="?", help="Input document file")
    parser.add_argument("output_file", nargs="?", help="Output markdown file")
    parser.add_argument("--list", action="store_true", help="List available documents")
    parser.add_argument("--converter", choices=["try_word_to_md", "pandoc_converter", "enhanced_word_to_md", "exact_docx_to_md"],
                        default="try_word_to_md", help="Converter to use")

    args = parser.parse_args()

    # If --list is specified, just list documents and exit
    if args.list:
        print("Available documents:")
        for directory in [".", "input"]:
            dir_path = Path(directory)
            if dir_path.exists():
                doc_files = list(dir_path.glob("*.docx")) + list(dir_path.glob("*.doc"))
                if doc_files:
                    print(f"\nIn {directory}/ directory:")
                    for i, doc in enumerate(doc_files, 1):
                        print(f"  {i}. {doc}")
        return 0

    # No input file specified, try to find one
    if not args.input_file:
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                args.input_file = str(docx_files[0])
                print(f"Using found document: {args.input_file}")
            else:
                print("No DOCX files found. Use --list to see available documents.")
                return 1
        else:
            print("No input file specified and no 'input' directory found.")
            return 1

    # Find the document
    input_file = find_document(args.input_file)
    if not input_file:
        return 1

    # Fix output path if provided
    output_file = args.output_file
    if output_file:
        output_file = fix_output_path(output_file)

    # Run the converter
    converter_script = args.converter + ".py"
    if not os.path.exists(converter_script):
        print(f"Converter script not found: {converter_script}")
        return 1

    try:
        print(f"Running conversion with {converter_script}...")
        cmd = [sys.executable, converter_script, input_file]
        if output_file:
            cmd.append(output_file)

        import subprocess
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"Conversion failed with exit code {result.returncode}")
            return result.returncode

        print("Conversion completed successfully!")

        # If we got here, optionally continue the workflow
        print("\nDo you want to:")
        print("1. Enhance the markdown (improve formatting)")
        print("2. Extract requirements")
        print("3. Generate RTM")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            # Find the output file if not specified
            if not output_file:
                output_dir = Path("output")
                if output_dir.exists():
                    md_files = list(output_dir.glob("*.md"))
                    if md_files:
                        output_file = str(md_files[0])
                        print(f"Using generated markdown file: {output_file}")

            if output_file:
                subprocess.run([sys.executable, "enhance_document_parsing.py", output_file])
            else:
                print("No markdown file found to enhance.")

        elif choice == "2":
            # Find the markdown file
            md_file = output_file
            if not md_file:
                output_dir = Path("output")
                if output_dir.exists():
                    md_files = list(output_dir.glob("*.md"))
                    if md_files:
                        md_file = str(md_files[0])

            if md_file:
                subprocess.run([sys.executable, "enhanced_requirement_parser.py", md_file])
            else:
                print("No markdown file found to extract requirements from.")

        elif choice == "3":
            # Look for requirements JSON file
            req_file = None
            output_dir = Path("output")
            if output_dir.exists():
                json_files = list(output_dir.glob("*requirements*.json"))
                if json_files:
                    req_file = str(json_files[0])

            if req_file:
                subprocess.run([sys.executable, "generate_rtm_table.py", req_file])
            else:
                print("No requirements file found. Extract requirements first.")

        return 0

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())