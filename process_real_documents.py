#!/usr/bin/env python3
"""
Process Your Real Documents - Use actual filenames instead of placeholders
"""

import subprocess
import sys
from pathlib import Path

def list_available_documents():
    """List all available documents in the input directory."""
    print("📁 Available Documents in input/ directory:")
    print("=" * 50)

    input_dir = Path("input")
    if not input_dir.exists():
        print("❌ Input directory not found!")
        return [], []

    # Find DOCX files
    docx_files = list(input_dir.glob("*.docx"))
    md_files = list(input_dir.glob("*.md"))

    print(f"\n📄 DOCX Files ({len(docx_files)}):")
    for i, file in enumerate(docx_files, 1):
        print(f"   {i}. {file.name}")

    print(f"\n📝 Markdown Files ({len(md_files)}):")
    for i, file in enumerate(md_files, 1):
        print(f"   {i}. {file.name}")

    if not docx_files and not md_files:
        print("❌ No documents found in input/ directory")

    return docx_files, md_files

def process_document(file_path, output_format="json"):
    """Process a single document."""
    print(f"\n📊 Processing {file_path.name} → {output_format.upper()}...")

    try:
        result = subprocess.run([
            sys.executable, "enhance_document_parsing.py",
            str(file_path), "-f", output_format
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"   ✅ SUCCESS: {file_path.name} processed")
            return True
        else:
            print(f"   ⚠️ Issues with {file_path.name}: {result.stderr[:100]}...")
            return False
    except Exception as e:
        print(f"   ❌ Error processing {file_path.name}: {e}")
        return False

def create_digital_twin(file_path, output_dir=None):
    """Create digital twin from markdown file."""
    if output_dir is None:
        output_dir = f"output/{file_path.stem}_twin"

    print(f"\n🔗 Creating digital twin from {file_path.name}...")

    try:
        result = subprocess.run([
            sys.executable, "digital_twin_parser.py",
            str(file_path), "-o", output_dir
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"   ✅ SUCCESS: Digital twin created in {output_dir}")
            return True
        else:
            print(f"   ⚠️ Issues creating digital twin: {result.stderr[:100]}...")
            return False
    except Exception as e:
        print(f"   ❌ Error creating digital twin: {e}")
        return False

def main():
    """Main function to process real documents."""
    print("🚀 Process Your Real RTM Documents")
    print("=" * 45)
    print("Using actual filenames from your input directory...")

    # List available documents
    docx_files, md_files = list_available_documents()

    if not docx_files and not md_files:
        print("\n❌ No documents found. Please add documents to the input/ directory.")
        return 1

    # Process DOCX files
    docx_success = 0
    for docx_file in docx_files:
        if process_document(docx_file, "json"):
            docx_success += 1

    # Process Markdown files for digital twins
    md_success = 0
    for md_file in md_files:
        if create_digital_twin(md_file):
            md_success += 1

    # Summary
    total_processed = docx_success + md_success
    total_files = len(docx_files) + len(md_files)

    print(f"\n📊 Processing Summary:")
    print(f"   DOCX files processed: {docx_success}/{len(docx_files)}")
    print(f"   Digital twins created: {md_success}/{len(md_files)}")
    print(f"   Total success: {total_processed}/{total_files}")

    success_rate = (total_processed / total_files * 100) if total_files > 0 else 0

    if success_rate >= 75:
        print(f"   🎉 EXCELLENT! {success_rate:.1f}% success rate")
    elif success_rate >= 50:
        print(f"   ✅ GOOD! {success_rate:.1f}% success rate")
    else:
        print(f"   ⚠️ {success_rate:.1f}% success rate - check individual results")

    # Show output files
    output_dir = Path("output")
    if output_dir.exists():
        output_files = list(output_dir.glob("*"))
        print(f"\n📁 Generated {len(output_files)} output files in output/ directory")

    print(f"\n🚀 Your RTM automation is processing real documents!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
