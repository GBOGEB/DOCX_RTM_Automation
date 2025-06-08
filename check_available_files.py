#!/usr/bin/env python3
"""
Check what files are actually available for processing
"""

from pathlib import Path


def main():
    """Check available files and show correct commands."""
    print("🔍 RTM File Availability Check")
    print("=" * 40)

    input_dir = Path("input")

    if not input_dir.exists():
        print("❌ Input directory not found!")
        print("   Create it with: mkdir input")
        return

    # Check for files
    docx_files = list(input_dir.glob("*.docx"))
    md_files = list(input_dir.glob("*.md"))

    print(f"📁 Input Directory: {input_dir.absolute()}")
    print(f"📊 Found {len(docx_files)} DOCX files and {len(md_files)} Markdown files")

    if docx_files:
        print("\n📄 Available DOCX Files:")
        for i, file in enumerate(docx_files, 1):
            print(f"   {i}. {file.name}")

        print("\n✅ Correct commands for your DOCX files:")
        for file in docx_files[:3]:  # Show first 3
            print(f"   python enhance_document_parsing.py input/{file.name} -f json")

    if md_files:
        print("\n📝 Available Markdown Files:")
        for i, file in enumerate(md_files, 1):
            print(f"   {i}. {file.name}")

        print("\n✅ Correct commands for your Markdown files:")
        for file in md_files[:3]:  # Show first 3
            print(
                f"   python digital_twin_parser.py input/{file.name} -o output/{file.stem}_twin"
            )

    if not docx_files and not md_files:
        print("\n❌ No documents found in input/ directory")
        print("\n💡 Based on your previous tests, you should have:")
        print("   📄 MASTER_1805_1144.docx")
        print("   📄 requirements.docx")
        print("   📄 sample_requirements.docx")
        print("   📝 requirements.md")
        print("\n🔧 Try running:")
        print("   python enhance_document_parsing.py --list")
    else:
        print("\n🚀 Process all available documents with:")
        print("   python process_real_documents.py")


if __name__ == "__main__":
    main()
