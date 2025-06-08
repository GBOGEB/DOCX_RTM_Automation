#!/usr/bin/env python3
"""
Verify the enhanced document parsing output and extract key information.
"""

import json
import yaml
from pathlib import Path


def verify_enhanced_output():
    """Verify the enhanced document parsing output."""
    print("Enhanced Document Parsing - Output Verification")
    print("=" * 50)

    # Check for output files
    output_dir = Path("output")
    files_to_check = [
        "sample_document_enhanced.md",
        "sample_document_enhanced.json",
        "sample_document_enhanced.yaml",
    ]

    for filename in files_to_check:
        file_path = output_dir / filename
        if file_path.exists():
            print(f"✅ Found: {filename}")

            # Show file details
            file_size = file_path.stat().st_size
            print(f"   Size: {file_size} bytes")

            # Parse and show metadata for JSON/YAML files
            if filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    metadata = data.get("metadata", {})
                    print(f"   Title: {metadata.get('title', 'N/A')}")
                    print(
                        f"   Requirements found: {len(metadata.get('requirements_found', []))}"
                    )
                    print(f"   Headings: {metadata.get('headings_count', 0)}")
                    print(f"   Lines: {metadata.get('lines_count', 0)}")
                    print(
                        f"   Markdown processed: {metadata.get('markdown_processed', False)}"
                    )

                    if (
                        "requirements_found" in metadata
                        and metadata["requirements_found"]
                    ):
                        print(
                            f"   Requirements: {', '.join(metadata['requirements_found'])}"
                        )

                except Exception as e:
                    print(f"   ⚠️ Error reading JSON: {e}")

            elif filename.endswith(".yaml"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    metadata = data.get("metadata", {})
                    print("   YAML metadata loaded successfully")
                    print(f"   Content length: {len(str(data.get('content', '')))}")

                except Exception as e:
                    print(f"   ⚠️ Error reading YAML: {e}")

            elif filename.endswith(".md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    print(f"   Total lines: {len(lines)}")

                    # Look for YAML front matter
                    if content.startswith("---"):
                        yaml_end = content.find("---", 3)
                        if yaml_end > 0:
                            print("   ✅ Contains YAML front matter")

                except Exception as e:
                    print(f"   ⚠️ Error reading Markdown: {e}")

        else:
            print(f"❌ Missing: {filename}")

    print("\n" + "=" * 50)
    print("Verification complete!")


if __name__ == "__main__":
    verify_enhanced_output()
