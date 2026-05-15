#!/usr/bin/env python3
"""
Setup and Run Pipeline - Automatic setup and execution of Word-Markdown pipeline
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
from word_markdown_pipeline_fixed import WordMarkdownPipeline, create_sample_word_document

def create_directories():
    """Create required directories."""
    print("[DIR] Setting up directories...")

    directories = ['input', 'output', 'temp_processing']
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"   [OK] Created/verified: {dir_path}")

def check_for_input_files():
    """Check for existing input files."""
    input_dir = Path("input")

    # Look for Word documents
    word_files = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.doc"))

    # Look for any text files that could be processed
    text_files = list(input_dir.glob("*.txt")) + list(input_dir.glob("*.md"))

    all_files = word_files + text_files

    print(f"[FILE] Checking for input files in {input_dir}...")

    if all_files:
        print(f"   Found {len(all_files)} files:")
        for file in all_files:
            file_size = file.stat().st_size
            print(f"   * {file.name} ({file_size:,} bytes)")
        return all_files
    else:
        print("   No input files found")
        return []

def create_sample_documents():
    """Create various sample documents for testing."""
    print("📝 Creating sample documents...")

    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    # Create Word document (if python-docx available)
    try:
        word_file = create_sample_word_document()
        if word_file:
            print(f"   [OK] Created Word document: {word_file}")
    except Exception as e:
        print(f"   [WARNING] Could not create Word document: {e}")
        word_file = None

    # Create Markdown sample
    try:
        md_content = f"""# Sample RTM Document (Markdown)

## 1. Introduction

This is a sample Markdown document for testing the RTM pipeline.

## 2. Requirements

### REQ-MD-001: Markdown Processing
**Description:** The system shall process Markdown documents through the RTM pipeline.
**Priority:** High
**Status:** Active

### REQ-MD-002: Content Preservation
**Description:** The system shall preserve Markdown formatting during processing.
**Priority:** Medium
**Status:** Active

### REQ-MD-003: RTM Enhancement
**Description:** The system shall enhance Markdown documents with RTM metadata.
**Priority:** High
**Status:** Active

## 3. Test Cases

### TC-MD-001: Markdown to Word Conversion
**Description:** Verify that Markdown documents can be converted to Word format.
**Test Steps:**
1. Load Markdown document
2. Process through RTM pipeline
3. Verify Word output generation
4. Check content preservation

**Expected Result:** Word document generated with RTM enhancements

### TC-MD-002: RTM Metadata Addition
**Description:** Verify that RTM metadata is properly added to documents.
**Test Steps:**
1. Process document through RTM system
2. Verify requirements extraction
3. Verify test case generation
4. Check traceability matrix

**Expected Result:** Document enhanced with complete RTM metadata

## 4. Traceability Matrix

| Requirement | Test Case | Status |
|-------------|-----------|--------|
| REQ-MD-001 | TC-MD-001 | Linked |
| REQ-MD-002 | TC-MD-001 | Linked |
| REQ-MD-003 | TC-MD-002 | Linked |

## 5. Document Metadata

- **Document Type:** Sample RTM Document
- **Format:** Markdown
- **Purpose:** Pipeline testing
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        md_file = input_dir / "sample_rtm_document.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"   [OK] Created Markdown document: {md_file}")

    except Exception as e:
        print(f"   [WARNING] Could not create Markdown document: {e}")
        md_file = None

    # Create simple text document
    try:
        txt_content = f"""Sample RTM Document (Text Format)
=====================================

1. INTRODUCTION
This is a sample text document for testing the RTM pipeline.

2. REQUIREMENTS
REQ-TXT-001: The system shall process text documents efficiently.
REQ-TXT-002: The system shall extract requirements from text format.
REQ-TXT-003: The system shall generate RTM reports from text input.

3. TEST CASES
TC-TXT-001: Verify text document processing
- Load text document
- Process through RTM pipeline
- Verify output generation

TC-TXT-002: Verify requirement extraction
- Parse text content
- Identify requirement patterns
- Extract requirement metadata

4. TRACEABILITY
REQ-TXT-001 is verified by TC-TXT-001
REQ-TXT-002 is verified by TC-TXT-002
REQ-TXT-003 is verified by TC-TXT-001 and TC-TXT-002

5. METADATA
Document: Sample RTM Text Document
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Purpose: RTM Pipeline Testing
"""

        txt_file = input_dir / "sample_rtm_document.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)

        print(f"   [OK] Created text document: {txt_file}")

    except Exception as e:
        print(f"   [WARNING] Could not create text document: {e}")
        txt_file = None

    # Return list of created files
    created_files = []
    for file in [word_file, md_file, txt_file]:
        if file and Path(file).exists():
            created_files.append(Path(file))

    return created_files

def run_pipeline_interactive():
    """Run pipeline with interactive file selection."""
    print("\n[LAUNCH] RTM Pipeline Interactive Mode")
    print("=" * 40)

    # Check for existing files
    existing_files = check_for_input_files()

    if not existing_files:
        print("\n📝 No input files found. Creating sample documents...")
        created_files = create_sample_documents()

        if not created_files:
            print("[ERROR] Could not create sample documents")
            return 1

        print(f"\n[OK] Created {len(created_files)} sample documents")
        files_to_choose = created_files
    else:
        print(f"\n[FILE] Found {len(existing_files)} existing files")

        # Ask if user wants to use existing or create new samples
        choice = input("\nUse existing files (e) or create new samples (n)? [e/N]: ").lower()

        if choice == 'e':
            files_to_choose = existing_files
        else:
            print("\n📝 Creating additional sample documents...")
            created_files = create_sample_documents()
            files_to_choose = existing_files + created_files

    # Let user choose which file to process
    print("\n📋 Available files for processing:")
    for i, file in enumerate(files_to_choose, 1):
        file_size = file.stat().st_size
        print(f"   {i}. {file.name} ({file_size:,} bytes)")

    print("   0. Process all files")

    while True:
        try:
            choice = input(f"\nSelect file to process (0-{len(files_to_choose)}): ").strip()

            if choice == '0':
                # Process all files
                selected_files = files_to_choose
                break
            else:
                choice_num = int(choice)
                if 1 <= choice_num <= len(files_to_choose):
                    selected_files = [files_to_choose[choice_num - 1]]
                    break
                else:
                    print(f"[ERROR] Invalid choice. Please enter 0-{len(files_to_choose)}")
        except ValueError:
            print("[ERROR] Please enter a number")

    # Process selected files
    pipeline = WordMarkdownPipeline()
    results = []

    for file_path in selected_files:
        print(f"\n🔄 Processing: {file_path}")
        print("-" * 50)

        result = pipeline.run_full_pipeline(str(file_path))
        results.append(result)

        # Show result
        print(f"[REPORT] Result for {file_path.name}:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Processing time: {result.get('processing_time', 'unknown')}")

        if result.get('status') == 'completed':
            print(f"   [OK] Output: {result.get('output_file')}")
        else:
            print(f"   [ERROR] Error: {result.get('error', 'Unknown error')}")

    # Summary
    print("\n[SUCCESS] PROCESSING COMPLETE!")
    print("=" * 30)
    print(f"[DIR] Files processed: {len(results)}")

    successful = sum(1 for r in results if r.get('status') == 'completed')
    failed = len(results) - successful

    print(f"[OK] Successful: {successful}")
    print(f"[ERROR] Failed: {failed}")

    if successful > 0:
        print("\n📂 Check the 'output' folder for processed documents!")

        # Show output files
        output_dir = Path("output")
        if output_dir.exists():
            output_files = list(output_dir.glob("*"))
            if output_files:
                print("\n[FILE] Generated files:")
                for file in output_files:
                    file_size = file.stat().st_size
                    print(f"   * {file.name} ({file_size:,} bytes)")

    return 0

def main():
    """Main function."""
    print("[LAUNCH] RTM Pipeline Setup & Execution")
    print("=" * 40)

    # Initialize debug console if available
    debug_console = None
    try:
        from debug_console import RTMDebugConsole
        debug_console = RTMDebugConsole()
        debug_console.logger.info("RTM Pipeline starting with debug support")
    except ImportError:
        print("Debug console not available - running in standard mode")

    try:
        # Setup directories
        if debug_console:
            debug_console.trace_operation("setup_directories", create_directories)
        else:
            create_directories()

        # Run interactive pipeline
        if debug_console:
            return debug_console.trace_operation("run_pipeline_interactive", run_pipeline_interactive)
        else:
            return run_pipeline_interactive()

    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user")
        if debug_console:
            debug_console.logger.warning("Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        if debug_console:
            debug_console.logger.error("Pipeline failed: %s", str(e))
            debug_console.logger.error("Full traceback: %s", traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
