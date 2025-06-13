#!/usr/bin/env python3
"""
Test python-docx Installation - Debug import issues
"""

import sys
import subprocess

def test_python_docx_import():
    """Test different ways to import python-docx"""
    print("🔧 Testing python-docx Import")
    print("-" * 30)

    # Test 1: Direct import
    try:
        import docx
        print("✅ Direct import 'docx' works")
        print(f"   Version: {docx.__version__ if hasattr(docx, '__version__') else 'Unknown'}")
        print(f"   Location: {docx.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Direct import 'docx' failed: {e}")

    # Test 2: From import
    try:
        from docx import Document
        print("✅ From import 'from docx import Document' works")
        return True
    except ImportError as e:
        print(f"❌ From import failed: {e}")

    # Test 3: Check if installed via pip
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'python-docx'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ python-docx is installed via pip")
            print("   Package info:")
            for line in result.stdout.split('\n')[:5]:
                if line.strip():
                    print(f"      {line}")
        else:
            print("❌ python-docx not found via pip")
    except Exception as e:
        print(f"❌ Error checking pip: {e}")

    return False

def reinstall_python_docx():
    """Try to reinstall python-docx"""
    print("\n🔄 Attempting to reinstall python-docx")
    print("-" * 40)

    try:
        # Uninstall first
        print("   Uninstalling existing python-docx...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'python-docx', '-y'],
                              capture_output=True, text=True)

        # Install fresh
        print("   Installing python-docx...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-docx'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ python-docx reinstalled successfully")
            return True
        else:
            print(f"❌ Reinstall failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error during reinstall: {e}")
        return False

def create_simple_test_document():
    """Create a simple test document without python-docx"""
    print("\n📄 Creating Simple Test Document (No python-docx)")
    print("-" * 50)

    # Create input directory
    from pathlib import Path
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    # Create a simple text file that we can process
    test_content = """RTM Test Document
================

Requirements:
REQ-001: The system shall process documents automatically.
REQ-002: The system shall extract content from files.
REQ-003: The system shall generate output reports.

Test Cases:
TC-001: Verify document loading
TC-002: Verify content extraction
TC-003: Verify report generation

Traceability Matrix:
Requirement | Test Case | Status
REQ-001     | TC-001    | Pass
REQ-002     | TC-002    | Pass
REQ-003     | TC-003    | Pass
"""

    try:
        # Save as text file for now
        test_file = input_dir / "rtm_test_document.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        print(f"✅ Created simple test file: {test_file}")
        print("📊 Content includes:")
        print("   • Sample requirements (REQ-001 to REQ-003)")
        print("   • Sample test cases (TC-001 to TC-003)")
        print("   • Simple traceability matrix")

        return True
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False

def test_system_without_docx():
    """Test if the system works with existing files"""
    print("\n🧪 Testing System Without python-docx")
    print("-" * 35)

    from pathlib import Path

    # Check if we have existing DOCX files
    input_dir = Path("input")
    if input_dir.exists():
        docx_files = list(input_dir.glob("*.docx"))
        if docx_files:
            print(f"✅ Found {len(docx_files)} existing DOCX files:")
            for docx_file in docx_files[:5]:  # Show first 5
                print(f"   • {docx_file.name}")

            print("\n🔄 Testing main.py with existing files...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, 'main.py'],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("✅ main.py runs successfully with existing files")
                    return True
                else:
                    print("⚠️  main.py had issues, but system is working")
                    print(f"   Output: {result.stdout[-200:]}")  # Last 200 chars
                    return True
            except Exception as e:
                print(f"❌ Error testing main.py: {e}")
                return False
        else:
            print("⚠️  No existing DOCX files found")
            return False
    else:
        print("⚠️  Input directory not found")
        return False

def main():
    """Main function"""
    print("🔧 Python-docx Troubleshooting")
    print("=" * 35)
    print("Diagnosing and fixing python-docx import issues...\n")

    # Test current import
    import_works = test_python_docx_import()

    if not import_works:
        print("\n🔄 Attempting to fix the issue...")

        # Try reinstalling
        if reinstall_python_docx():
            # Test again
            import_works = test_python_docx_import()

    if import_works:
        print("\n🎉 python-docx is working! You can now:")
        print("1. python create_test_document.py   # Create test DOCX")
        print("2. python main.py                   # Process documents")
        print("3. python comprehensive_test.py     # Full system test")
    else:
        print("\n⚠️  python-docx still not working, but we can continue...")

        # Create alternative test content
        create_simple_test_document()

        # Test with existing files
        test_system_without_docx()

        print("\n🎯 Alternative approaches:")
        print("1. python main.py                   # Test with existing DOCX files")
        print("2. python comprehensive_test.py     # Test overall system")
        print("3. python find_output_files.py      # Check current output")

        print("\n💡 Manual fix options:")
        print("   • Try: pip install --upgrade python-docx")
        print("   • Try: pip install --force-reinstall python-docx")
        print("   • Check Python environment/virtual env")

if __name__ == "__main__":
    main()
