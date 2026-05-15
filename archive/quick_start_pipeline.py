#!/usr/bin/env python3
"""
Quick Start Pipeline - Easy way to test the Word-Markdown pipeline
"""

import sys
from pathlib import Path
from word_markdown_pipeline_fixed import WordMarkdownPipeline, create_sample_word_document

def main():
    """Quick start for testing the pipeline."""
    print("🚀 RTM Pipeline Quick Start")
    print("=" * 30)

    # Create sample document
    print("📄 Creating sample document...")
    sample_file = create_sample_word_document()

    if not sample_file:
        print("❌ Failed to create sample document")
        return 1

    print(f"✅ Sample document created: {sample_file}")

    # Run pipeline
    print("\n🔄 Running RTM pipeline...")
    pipeline = WordMarkdownPipeline()
    result = pipeline.run_full_pipeline(str(sample_file))

    # Display results
    print(f"\n📊 Results:")
    print(f"   Status: {result.get('status')}")
    print(f"   Processing time: {result.get('processing_time', 'unknown')}")

    if result.get('steps'):
        print(f"\n🔧 Steps completed:")
        for step in result['steps']:
            status_icon = "✅" if step.get('status') == 'completed' else "❌"
            print(f"   {status_icon} {step.get('description')}")

    if result.get('status') == 'completed':
        print(f"\n🎉 SUCCESS! Processed document: {result.get('output_file')}")

        # Show what was created
        output_dir = Path("output")
        temp_dir = Path("temp_processing")

        print(f"\n📁 Files created:")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                print(f"   📄 {file}")

        if temp_dir.exists():
            print(f"\n📁 Temporary files:")
            for file in temp_dir.glob("*"):
                print(f"   📄 {file}")
    else:
        print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
