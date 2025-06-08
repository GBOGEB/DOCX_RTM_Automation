#!/usr/bin/env python3
"""
Generate Sample Output - Create sample output files to demonstrate the RTM system
"""

import sys
from pathlib import Path
from datetime import datetime
from setup_and_run_pipeline import create_directories, create_sample_documents
from word_markdown_pipeline_fixed import WordMarkdownPipeline

def main():
    """Generate sample output files."""
    print("🎯 RTM Sample Output Generator")
    print("=" * 35)

    try:
        # Create directories
        print("1️⃣ Setting up directories...")
        create_directories()

        # Create sample documents
        print("2️⃣ Creating sample documents...")
        sample_files = create_sample_documents()

        if not sample_files:
            print("❌ Could not create sample documents")
            return 1

        print(f"✅ Created {len(sample_files)} sample documents")

        # Process first sample through pipeline
        print("3️⃣ Running pipeline on sample document...")
        test_file = sample_files[0]

        pipeline = WordMarkdownPipeline()
        result = pipeline.run_full_pipeline(str(test_file))

        print("4️⃣ Pipeline Results:")
        print(f"   Status: {result.get('status')}")
        print(f"   Processing time: {result.get('processing_time', 'unknown')}")

        if result.get('status') == 'completed':
            print(f"   ✅ Output: {result.get('output_file')}")
        else:
            print(f"   ❌ Error: {result.get('error')}")

        # Show what was created
        print("5️⃣ Generated Files:")

        # Check output directory
        output_dir = Path("output")
        if output_dir.exists():
            output_files = list(output_dir.glob("*"))
            if output_files:
                print(f"   📁 output/ ({len(output_files)} files):")
                for file in output_files:
                    file_size = file.stat().st_size
                    print(f"      📄 {file.name} ({file_size:,} bytes)")

        # Check temp directory
        temp_dir = Path("temp_processing")
        if temp_dir.exists():
            temp_files = list(temp_dir.glob("*"))
            if temp_files:
                print(f"   📁 temp_processing/ ({len(temp_files)} files):")
                for file in temp_files:
                    file_size = file.stat().st_size
                    print(f"      📄 {file.name} ({file_size:,} bytes)")

        # Check input directory
        input_dir = Path("input")
        if input_dir.exists():
            input_files = list(input_dir.glob("*"))
            if input_files:
                print(f"   📁 input/ ({len(input_files)} files):")
                for file in input_files:
                    file_size = file.stat().st_size
                    print(f"      📄 {file.name} ({file_size:,} bytes)")

        print("\n🎉 Sample output generation complete!")
        print("📍 Check the following directories:")
        print("   • output/ - Processed documents")
        print("   • temp_processing/ - Intermediate files")
        print("   • input/ - Source documents")

        return 0

    except Exception as e:
        print(f"❌ Error generating sample output: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
