#!/usr/bin/env python3
"""
Verify and analyze the generated output files from document processing.
"""

import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def analyze_json_output(file_path):
    """Analyze a JSON output file and show key information."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n📄 Analysis of {file_path.name}:")
        print("=" * 40)

        # Check metadata
        metadata = data.get("metadata", {})
        print(f"📋 Document Title: {metadata.get('title', 'N/A')}")
        print(f"📁 Original File: {metadata.get('original_file', 'N/A')}")
        print(f"📊 Paragraphs: {metadata.get('paragraphs', 'N/A')}")
        print(f"📚 Sections: {metadata.get('sections', 'N/A')}")
        print(f"🔢 Tables: {metadata.get('tables', 'N/A')}")

        # Check for requirements if this is a markdown-derived file
        if "requirements_found" in metadata:
            requirements = metadata["requirements_found"]
            print(f"⚡ Requirements Found: {len(requirements)}")
            if requirements:
                print(f"   Requirements: {', '.join(requirements[:5])}")
                if len(requirements) > 5:
                    print(f"   ... and {len(requirements) - 5} more")

        # Check content structure
        content = data.get("content", [])
        if isinstance(content, list):
            print(f"📄 Content Sections: {len(content)}")
            for i, section in enumerate(content[:3]):  # Show first 3 sections
                if isinstance(section, dict):
                    heading = section.get("heading", f"Section {i + 1}")
                    content_items = len(section.get("content", []))
                    print(f"   - {heading} ({content_items} items)")
        elif isinstance(content, str):
            print(f"📄 Content Length: {len(content)} characters")

        # Check for HTML content (from markdown processing)
        if "html_content" in data:
            print(f"🌐 HTML Content: {len(data['html_content'])} characters")

        return True

    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return False


def verify_all_output_files():
    """Verify all generated output files."""
    output_dir = Path("output")

    if not output_dir.exists():
        print("❌ Output directory not found!")
        return

    print("🔍 Verifying Generated Output Files")
    print("=" * 45)

    # Find all output files
    json_files = list(output_dir.glob("*.json"))
    yaml_files = list(output_dir.glob("*.yaml"))
    md_files = list(output_dir.glob("*.md"))

    print("📊 Found Files:")
    print(f"   - JSON files: {len(json_files)}")
    print(f"   - YAML files: {len(yaml_files)}")
    print(f"   - Markdown files: {len(md_files)}")

    # Analyze JSON files
    for json_file in json_files:
        analyze_json_output(json_file)

    # Show file sizes and timestamps
    print("\n📈 File Details:")
    all_files = json_files + yaml_files + md_files
    for file_path in sorted(all_files):
        size = file_path.stat().st_size
        print(f"   {file_path.name}: {size:,} bytes")


def suggest_next_steps():
    """Suggest next steps based on the output files."""
    print("\n🚀 Suggested Next Steps:")
    print("=" * 30)

    output_dir = Path("output")

    # Check for specific files
    if (output_dir / "requirements.json").exists():
        print("✅ Requirements document processed successfully!")
        print("   Next: Generate visualization:")
        print(
            "   python src/visualizers/req_visualizer.py output/requirements.json -o output/requirements_chart.png"
        )

    if (output_dir / "sample_document_enhanced.json").exists():
        print("✅ Sample document available!")
        print("   Next: Create digital twin:")
        print(
            "   python digital_twin_parser.py input/sample/sample_document.md -o output/digital_twin"
        )

    # General suggestions
    print("\n📋 General Options:")
    print("   1. Process more DOCX files:")
    print(
        "      python enhance_document_parsing.py input/MASTER_1805_1144.docx -f json"
    )
    print("   2. Run interactive mode:")
    print("      python enhance_document_parsing.py --interactive")
    print("   3. Check code quality:")
    print("      python run_code_quality_checks.py")
    print("   4. Run full test suite:")
    print("      python test_all_features.bat")


if __name__ == "__main__":
    verify_all_output_files()
    suggest_next_steps()
