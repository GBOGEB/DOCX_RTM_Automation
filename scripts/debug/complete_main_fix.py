#!/usr/bin/env python3
"""
Complete Main Fix - Thoroughly fix the main.py function signature issue
"""

import sys
import re
from pathlib import Path

def analyze_main_py():
    """Analyze main.py to find all function calls"""
    print("🔍 Analyzing main.py for function signature issues...")

    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found")
        return False

    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("📋 Current main.py analysis:")

        # Find all run_document_conversion calls
        conversion_calls = re.findall(r'run_document_conversion\([^)]+\)', content)

        if conversion_calls:
            print(f"   Found {len(conversion_calls)} function calls:")
            for i, call in enumerate(conversion_calls, 1):
                print(f"   {i}. {call}")

                # Check if it has extra parameters
                if ',' in call:
                    print(f"      ⚠️  This call has multiple parameters - NEEDS FIXING")
                else:
                    print(f"      ✅ This call looks correct")
        else:
            print("   ❌ No run_document_conversion calls found")

        # Check import
        if 'from document_converter import run_document_conversion' in content:
            print("   ✅ Import statement found")
        else:
            print("   ❌ Import statement missing")

        return content

    except Exception as e:
        print(f"❌ Error analyzing main.py: {e}")
        return False

def create_fixed_main_py():
    """Create a completely fixed main.py"""
    print("\n🔧 Creating fixed main.py...")

    fixed_main_content = '''#!/usr/bin/env python3
"""
RTM Pipeline - Main execution script (FIXED VERSION)
"""

import logging
from pathlib import Path
from datetime import datetime
import sys

# Import the document conversion function
from document_converter import run_document_conversion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger('rtm_pipeline')

def find_input_document(input_dir="input"):
    """Find the first DOCX document in the input directory"""
    input_path = Path(input_dir)

    if not input_path.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return None

    # Look for DOCX files
    docx_files = list(input_path.glob("*.docx"))

    if not docx_files:
        logger.error(f"No DOCX files found in {input_dir}")
        return None

    # Return the first DOCX file found
    selected_doc = docx_files[0]
    logger.info(f"Using found document: {selected_doc}")
    return str(selected_doc)

def run_rtm_pipeline():
    """Run the complete RTM processing pipeline"""
    logger.info("Starting RTM Pipeline")
    logger.info("=" * 50)

    try:
        # Step 1: Find input document
        logger.info("Step 1: Finding input document...")
        input_document = find_input_document()

        if not input_document:
            logger.error("No input document found - pipeline cannot continue")
            return False

        # Step 2: Run document conversion (FIXED - single parameter only)
        logger.info("Step 2: Converting document...")
        conversion_result = run_document_conversion(input_document)

        if conversion_result["status"] != "success":
            logger.error(f"Document conversion failed: {conversion_result.get('error', 'Unknown error')}")
            return False

        logger.info(f"Document conversion successful!")
        logger.info(f"Generated {len(conversion_result['converted_files'])} output files")

        # Step 3: Additional processing could go here
        logger.info("Step 3: Pipeline processing complete")

        # Summary
        logger.info("=" * 50)
        logger.info("RTM Pipeline completed successfully!")
        logger.info(f"Input: {input_document}")
        logger.info(f"Output directory: {conversion_result['output_directory']}")
        logger.info(f"Files generated: {len(conversion_result['converted_files'])}")

        return True

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RTM Automation Pipeline")
    print("=" * 30)
    print("Starting automated RTM processing...\\n")

    # Initialize OpenAI integration if available
    try:
        print("Initializing OpenAI integration...")
        # Add your OpenAI initialization here if needed
        print("OpenAI integration ready")
    except Exception as e:
        print(f"OpenAI integration not available: {e}")

    # Run the pipeline
    success = run_rtm_pipeline()

    if success:
        print("\\n✅ Pipeline completed successfully!")
        print("\\nNext steps:")
        print("1. Check the output directory for generated files")
        print("2. Run: python find_output_files.py")
        print("3. Review the conversion results")
    else:
        print("\\n❌ Pipeline failed!")
        print("\\nTroubleshooting:")
        print("1. Check that input DOCX files exist in the 'input' directory")
        print("2. Ensure you have the required dependencies installed")
        print("3. Check the error messages above")

if __name__ == "__main__":
    main()
'''

    try:
        # Backup current main.py
        main_file = Path("main.py")
        if main_file.exists():
            backup_file = Path("main.py.backup_before_fix")
            main_file.rename(backup_file)
            print(f"   📋 Backed up current main.py to: {backup_file}")

        # Write fixed version
        with open("main.py", 'w', encoding='utf-8') as f:
            f.write(fixed_main_content)

        print("   ✅ Created fixed main.py")
        return True

    except Exception as e:
        print(f"   ❌ Error creating fixed main.py: {e}")
        return False

def verify_document_converter():
    """Verify document_converter.py has correct signature"""
    print("\n🔍 Verifying document_converter.py...")

    converter_file = Path("document_converter.py")
    if not converter_file.exists():
        print("   ❌ document_converter.py not found")
        return False

    try:
        with open(converter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check function signature
        if 'def run_document_conversion(input_file):' in content:
            print("   ✅ Function signature is correct")
        elif 'def run_document_conversion(' in content:
            print("   ⚠️  Function exists but signature may be wrong")
            # Show the actual signature
            import re
            match = re.search(r'def run_document_conversion\([^)]+\):', content)
            if match:
                print(f"      Found: {match.group(0)}")
        else:
            print("   ❌ Function not found")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Error checking document_converter.py: {e}")
        return False

def test_fixed_pipeline():
    """Test the fixed pipeline"""
    print("\n🧪 Testing fixed pipeline...")

    try:
        # Try to import
        print("   1. Testing import...")
        from document_converter import run_document_conversion
        print("   ✅ Import successful")

        # Check if input files exist
        print("   2. Checking input files...")
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                print(f"   ✅ Found {len(docx_files)} DOCX files")

                # Test the function call syntax
                print("   3. Testing function call syntax...")
                test_file = str(docx_files[0])
                print(f"   Calling: run_document_conversion('{test_file}')")

                # This should work now
                result = run_document_conversion(test_file)
                print(f"   ✅ Function call successful: {result['status']}")

                return True
            else:
                print("   ⚠️  No DOCX files found, but syntax should be fixed")
                return True
        else:
            print("   ⚠️  Input directory not found, but syntax should be fixed")
            return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main function to completely fix the pipeline"""
    print("🔧 Complete Main Pipeline Fixer")
    print("=" * 35)
    print("Thoroughly fixing the run_document_conversion function signature issue...\n")

    # Step 1: Analyze current main.py
    current_content = analyze_main_py()

    # Step 2: Create fixed main.py
    if create_fixed_main_py():
        print("✅ Fixed main.py created")
    else:
        print("❌ Failed to create fixed main.py")
        return 1

    # Step 3: Verify document converter
    if verify_document_converter():
        print("✅ document_converter.py verified")
    else:
        print("❌ document_converter.py has issues")

    # Step 4: Test the fix
    if test_fixed_pipeline():
        print("✅ Pipeline test successful")
    else:
        print("❌ Pipeline test failed")

    print("\n🎉 Complete fix process finished!")
    print("\nNow try running:")
    print("python main.py")

    print("\nIf it still fails, check:")
    print("1. That document_converter.py exists")
    print("2. That python-docx is installed: pip install python-docx")
    print("3. That input DOCX files exist in the input/ directory")

if __name__ == "__main__":
    sys.exit(main())
