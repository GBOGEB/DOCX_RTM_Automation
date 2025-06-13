#!/usr/bin/env python3
"""
Main RTM Automation Entry Point - Updated for new structure
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.rtm.document_converter import run_document_conversion
except ImportError:
    # Fallback to old location if new structure not ready
    try:
        from document_converter import run_document_conversion
    except ImportError:
        print("❌ Could not import document_converter module")
        print("Please ensure the RTM automation modules are available")
        sys.exit(1)

def find_input_documents():
    """Find DOCX files to process"""
    input_dirs = ["input", ".", "documents"]
    docx_files = []

    for input_dir in input_dirs:
        dir_path = Path(input_dir)
        if dir_path.exists():
            found_files = list(dir_path.glob("*.docx"))
            docx_files.extend(found_files)

    return docx_files

def main():
    """Main function for RTM automation"""
    print("🚀 RTM AUTOMATION SYSTEM")
    print("=" * 30)
    print("Starting document conversion process...\n")

    # Find input documents
    docx_files = find_input_documents()

    if not docx_files:
        print("⚠️  No DOCX files found for processing")
        print("\nSuggestions:")
        print("   • Place DOCX files in an 'input/' directory")
        print("   • Or place them in the current directory")
        print("   • Ensure files have .docx extension")
        return 1

    print(f"📄 Found {len(docx_files)} DOCX file(s) to process:")
    for docx_file in docx_files:
        print(f"   • {docx_file}")

    # Process each document
    total_processed = 0
    total_errors = 0

    for docx_file in docx_files:
        print(f"\n🔄 Processing: {docx_file.name}")
        try:
            # Call the document converter with the file path
            result = run_document_conversion(str(docx_file))

            if result:
                print(f"   ✅ Successfully processed: {docx_file.name}")
                total_processed += 1
            else:
                print(f"   ⚠️  Processing completed with warnings: {docx_file.name}")
                total_processed += 1

        except Exception as e:
            print(f"   ❌ Error processing {docx_file.name}: {e}")
            total_errors += 1

    # Show final results
    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 25)
    print(f"Files found: {len(docx_files)}")
    print(f"Successfully processed: {total_processed}")
    print(f"Errors: {total_errors}")

    if total_processed > 0:
        print(f"\n✅ RTM automation completed!")
        print(f"📁 Check 'output/' directory for results")

        # Show output directory info
        output_dir = Path("output")
        if output_dir.exists():
            output_files = list(output_dir.glob("*"))
            print(f"📊 Generated {len(output_files)} output files")

        return 0
    else:
        print(f"\n❌ No files were successfully processed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
