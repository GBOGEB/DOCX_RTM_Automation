#!/usr/bin/env python3
"""
Find and test Word to Markdown conversion functionality.
"""

import os
from pathlib import Path
import subprocess
import sys


def search_files_for_docx_processing():
    """Find files that might handle DOCX to Markdown conversion."""
    keywords = [
        "docx",
        "markdown",
        "convert",
        "word",
        "md",
        "python-docx",
        "docx2python",
        "pandoc",
        "document",
    ]

    results = []
    for root, _, files in os.walk("."):
        if any(
            excluded in root
            for excluded in [".git", ".venv", "__pycache__", "node_modules"]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()

                    matches = []
                    for keyword in keywords:
                        if keyword.lower() in content:
                            matches.append(keyword)

                    if matches:
                        score = len(matches)

                        # Boost score for files with clear conversion hints
                        if "docx_to_markdown" in content or "word_to_md" in content:
                            score += 5
                        if "docx2md" in content or "to_markdown" in content:
                            score += 3
                        if "Document(" in content and (
                            "write(" in content or "save(" in content
                        ):
                            score += 2

                        results.append((file_path, score, matches))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Sort by match score (higher is better)
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def test_conversion(docx_file):
    """Test the conversion of a DOCX file to Markdown."""
    # Ensure the output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print(f"\nTesting conversion of: {docx_file}")

    # 1. Try with try_word_to_md.py first (our enhanced converter)
    try_word_to_md = Path("try_word_to_md.py")
    if try_word_to_md.exists():
        output_md = output_dir / Path(docx_file).with_suffix(".md").name
        cmd = [sys.executable, str(try_word_to_md), str(docx_file), str(output_md)]

        print(f"\nRunning: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Conversion successful!")
                print(f"Output file: {output_md}")
                return output_md
            else:
                print("❌ Conversion failed with try_word_to_md.py")
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Error running try_word_to_md.py: {e}")

    # 2. If not successful, try to find and use other conversion scripts
    results = search_files_for_docx_processing()

    for script_path, score, _ in results[:3]:  # Try top 3 candidates
        if script_path == str(try_word_to_md):
            continue  # Already tried this one

        output_md = output_dir / Path(docx_file).with_suffix(".md").name
        cmd = [sys.executable, script_path, str(docx_file), str(output_md)]

        print(f"\nTrying with {script_path}: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Conversion successful!")
                print(f"Output file: {output_md}")
                return output_md
            else:
                print(f"❌ Conversion failed with {script_path}")
        except Exception as e:
            print(f"Error running {script_path}: {e}")

    print("\n❌ No conversion method succeeded.")
    return None


def main():
    """Main function."""
    print("\nWord to Markdown Conversion Tool Finder\n")

    # Check if try_word_to_md.py exists, if not, create it
    try_word_to_md = Path("try_word_to_md.py")
    if not try_word_to_md.exists():
        print("Creating try_word_to_md.py as it doesn't exist...")
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import requests; r = requests.get('https://raw.githubusercontent.com/user/repo/main/try_word_to_md.py'); open('try_word_to_md.py', 'wb').write(r.content)",
            ]
        )

    # Search for potential conversion scripts
    results = search_files_for_docx_processing()

    if results:
        print("Files possibly related to Word-to-Markdown conversion:\n")
        print("{:5} | {:60} | {:20}".format("Score", "File Path", "Keywords"))
        print("-" * 90)
        for file_path, score, matches in results[:10]:  # Show top 10
            print(
                "{:5d} | {:60} | {:20}".format(score, file_path, ", ".join(matches[:3]))
            )

        print("\nRecommended conversion scripts:")
        for file_path, score, _ in results[:3]:
            print(f"- {file_path}")
    else:
        print("No potential conversion scripts found.")

    # Ask user for input file
    default_docx_file = Path("input") / "test_document.docx"

    if not default_docx_file.exists():
        # Try to find another DOCX file in the input directory
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                default_docx_file = docx_files[0]
            else:
                # Create a test document if none exists
                print("\nNo DOCX files found. Creating a test document...")
                try:
                    from create_test_docx import create_test_document

                    default_docx_file = create_test_document()
                except Exception as e:
                    print(f"Error creating test document: {e}")
                    default_docx_file = "input/test_document.docx"

    # Get input file from user, with default
    docx_file = input(
        f"\nEnter the path to the .docx file [{default_docx_file}]: "
    ).strip()
    if not docx_file:
        docx_file = default_docx_file

    docx_path = Path(docx_file)
    if not docx_path.exists():
        print(f"Error: File {docx_path} does not exist.")
        return 1

    # Test the conversion
    output_md = test_conversion(docx_path)

    if output_md and Path(output_md).exists():
        print(f"\nSuccessfully converted {docx_path} to {output_md}")
        print("\nNow you can use this Markdown file with Project Requirements.py")
        return 0
    else:
        print("\nConversion failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
