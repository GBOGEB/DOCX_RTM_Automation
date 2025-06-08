#!/usr/bin/env python3
"""
Simple Test Pipeline - Quick test of the Word-Markdown pipeline
"""

import sys
from pathlib import Path
from setup_and_run_pipeline import create_directories, create_sample_documents
from word_markdown_pipeline_fixed import WordMarkdownPipeline

def main():
    """Simple test of the pipeline."""
    print("🧪 RTM Pipeline Simple Test")
    print("=" * 30)

    try:
        # Setup
        print("1️⃣ Setting up directories...")
        create_directories()

        # Create sample
        print("2️⃣ Creating sample document...")
        sample_files = create_sample_documents()

        if not sample_files:
            print("[ERROR] Could not create sample documents")
            return 1

        # Use first sample file
        test_file = sample_files[0]
        print(f"3️⃣ Testing with: {test_file}")

        # Run pipeline
        print("4️⃣ Running pipeline...")
        pipeline = WordMarkdownPipeline()
        result = pipeline.run_full_pipeline(str(test_file))

        # Show results
        print("5️⃣ Results:")
        print(f"   Status: {result.get('status')}")
        print(f"   Time: {result.get('processing_time', 'unknown')}")

        if result.get('status') == 'completed':
            print(f"   [OK] Output: {result.get('output_file')}")
            print("[SUCCESS] Test PASSED!")
        else:
            print(f"   [ERROR] Error: {result.get('error')}")
            print("[ERROR] Test FAILED!")

        return 0 if result.get('status') == 'completed' else 1

    except Exception as e:
        print(f"[ERROR] Test error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
