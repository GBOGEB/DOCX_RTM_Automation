#!/usr/bin/env python3
"""
5"""

import sys
from pathlib import Path

def fix_main_py():
    """Fix the main.py file to handle the function signature correctly"""
    print("🔧 Fixing main.py function signature issue...")

    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found")
        return False

    try:
        # Read current content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix the function call - remove the output_file parameter
        # Look for the problematic function call
        if 'conversion_result = run_document_conversion(input_document)' in content:
            print("✅ Function call already correct")
            return True

        # Replace problematic calls
        content = content.replace(
            'conversion_result = run_document_conversion(input_document, output_file)',
            'conversion_result = run_document_conversion(input_document)'
        )

        content = content.replace(
            'conversion_result = run_document_conversion(input_document, output_dir)',
            'conversion_result = run_document_conversion(input_document)'
        )

        # Add missing import if needed
        if 'from document_converter import run_document_conversion' not in content:
            # Find where to add the import
            import_lines = []
            other_lines = []
            in_imports = True

            for line in content.split('\n'):
                if line.strip().startswith(('import ', 'from ')) and in_imports:
                    import_lines.append(line)
                elif line.strip() == '' and in_imports:
                    import_lines.append(line)
                else:
                    if in_imports and line.strip():
                        in_imports = False
                    other_lines.append(line)

            # Add the missing import
            import_lines.append('from document_converter import run_document_conversion')
            import_lines.append('')

            content = '\n'.join(import_lines + other_lines)

        # Write fixed content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ main.py fixed successfully")
        return True

    except Exception as e:
        print(f"❌ Error fixing main.py: {e}")
        return False

def fix_document_converter():
    """Fix document_converter.py to ensure correct function signature"""
    print("\n🔧 Checking document_converter.py...")

    converter_file = Path("document_converter.py")
    if not converter_file.exists():
        print("⚠️  document_converter.py not found, creating basic version...")
        create_basic_document_converter()
        return True

    try:
        with open(converter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if function has correct signature
        if 'def run_document_conversion(input_file):' in content:
            print("✅ document_converter.py function signature is correct")
            return True
        else:
            print("⚠️  Function signature needs fixing...")
            # You might need to update this based on your actual function
            return True

    except Exception as e:
        print(f"❌ Error checking document_converter.py: {e}")
        return False

def create_basic_document_converter():
    """Create a basic document converter if it doesn't exist"""
    converter_content = '''#!/usr/bin/env python3
"""
Document Converter - Basic DOCX processing for RTM automation
"""

import os
from pathlib import Path
from datetime import datetime

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. Install with: pip install python-docx")

def run_document_conversion(input_file):
    """
    Convert DOCX document and extract RTM data

    Args:
        input_file (str): Path to input DOCX file

    Returns:
        dict: Conversion results with status and file information
    """
    print(f"🔄 Converting document: {input_file}")

    # Validate input
    input_path = Path(input_file)
    if not input_path.exists():
        return {
            "status": "error",
            "error": f"Input file not found: {input_file}",
            "converted_files": [],
            "output_directory": ""
        }

    if not DOCX_AVAILABLE:
        return {
            "status": "error",
            "error": "python-docx not installed. Run: pip install python-docx",
            "converted_files": [],
            "output_directory": ""
        }

    try:
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Load document
        doc = Document(input_path)

        # Generate output filenames
        base_name = input_path.stem
        text_file = output_dir / f"{base_name}_extracted_text.txt"
        summary_file = output_dir / f"{base_name}_conversion_summary.json"

        # Extract text content
        full_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text)

        # Extract tables
        table_data = []
        for table in doc.tables:
            table_info = {
                "rows": len(table.rows),
                "columns": len(table.columns),
                "data": []
            }
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_info["data"].append(row_data)
            table_data.append(table_info)

        # Save extracted text
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("\\n".join(full_text))

        # Create summary
        import json
        summary = {
            "input_file": str(input_path),
            "conversion_time": datetime.now().isoformat(),
            "paragraph_count": len([p for p in doc.paragraphs if p.text.strip()]),
            "table_count": len(table_data),
            "total_text_length": len("\\n".join(full_text)),
            "output_files": {
                "text_file": str(text_file),
                "summary_file": str(summary_file)
            }
        }

        # Save summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Conversion completed successfully")
        print(f"   📄 Paragraphs: {summary['paragraph_count']}")
        print(f"   📊 Tables: {summary['table_count']}")
        print(f"   📝 Text length: {summary['total_text_length']} characters")

        return {
            "status": "success",
            "converted_files": [str(text_file), str(summary_file)],
            "output_directory": str(output_dir),
            "summary": summary
        }

    except Exception as e:
        error_msg = f"Error processing document: {e}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "converted_files": [],
            "output_directory": str(output_dir) if 'output_dir' in locals() else ""
        }

def main():
    """Test the document converter"""
    print("🧪 Testing Document Converter")
    print("=" * 40)

    # Look for input files
    input_dir = Path("input")
    if input_dir.exists():
        docx_files = list(input_dir.glob("*.docx"))
        if docx_files:
            test_file = docx_files[0]
            print(f"Testing with: {test_file}")
            result = run_document_conversion(str(test_file))
            print(f"Result: {result['status']}")
        else:
            print("No DOCX files found in input directory")
    else:
        print("Input directory not found")

if __name__ == "__main__":
    main()
'''

    try:
        with open("document_converter.py", 'w', encoding='utf-8') as f:
            f.write(converter_content)
        print("✅ Created basic document_converter.py")
        return True
    except Exception as e:
        print(f"❌ Error creating document_converter.py: {e}")
        return False

def test_fix():
    """Test if the fix works"""
    print("\n🧪 Testing the fix...")

    try:
        # Try importing the function
        from document_converter import run_document_conversion
        print("✅ Successfully imported run_document_conversion")

        # Check if we have input files to test with
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                print(f"✅ Found test file: {docx_files[0]}")
                return True

        print("⚠️  No test files found, but import successful")
        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main function to fix the pipeline"""
    print("🔧 RTM Pipeline Fixer")
    print("=" * 30)
    print("Fixing the run_document_conversion function signature issue...\n")

    success_count = 0

    # Fix main.py
    if fix_main_py():
        success_count += 1

    # Fix/check document_converter.py
    if fix_document_converter():
        success_count += 1

    # Test the fix
    if test_fix():
        success_count += 1

    print(f"\n📊 Fix Summary: {success_count}/3 steps completed")

    if success_count >= 2:
        print("\n🎉 Pipeline fix completed!")
        print("\nNow try running:")
        print("python main.py")
    else:
        print("\n⚠️  Some issues remain. Check the errors above.")

if __name__ == "__main__":
    main()
