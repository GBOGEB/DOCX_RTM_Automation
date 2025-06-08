#!/usr/bin/env python3
"""
Integration test script to verify all components are working together.
"""

import os
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_markdown_integration():
    """Test markdown library integration."""
    try:
        import markdown

        test_md = "# Test Heading\n\nThis is a **test** paragraph."
        markdown.markdown(test_md)
        logger.info("✅ Markdown library working correctly")
        return True
    except Exception as e:
        logger.error("❌ Markdown library test failed: %s", e)
        return False


def test_enhance_document_parsing():
    """Test the enhance_document_parsing script."""
    try:
        # Import the module
        import enhance_document_parsing

        # Test dependency check
        deps_ok = enhance_document_parsing.check_integration_dependencies()
        if deps_ok:
            logger.info("✅ Enhancement script dependencies OK")
        else:
            logger.warning("⚠️ Some enhancement script dependencies missing")

        # Test Project Requirements integration
        project_req = enhance_document_parsing.integrate_with_project_requirements()
        if project_req:
            logger.info("✅ Project Requirements integration available")
        else:
            logger.info("ℹ️ Project Requirements integration not available (optional)")

        return True
    except Exception as e:
        logger.error("❌ Enhancement script test failed: %s", e)
        return False


def test_sample_file_creation():
    """Test creating and processing a sample file."""
    try:
        # Create a test markdown file
        test_file = Path("input/test/integration_test.md")
        test_file.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                """# Integration Test Document

## FR-1: Functional Requirement
This is a test functional requirement.

## NFR-1: Non-Functional Requirement
This is a test non-functional requirement.

### Requirements List
- REQ-001: First test requirement
- REQ-002: Second test requirement

## Test Table

| Requirement | Status | Priority |
|-------------|--------|----------|
| FR-1        | Active | High     |
| NFR-1       | Active | Medium   |
"""
            )

        logger.info("✅ Created test markdown file: %s", test_file)

        # Test processing it
        import enhance_document_parsing

        result = enhance_document_parsing.enhance_document_parsing(
            str(test_file), None, "json"
        )

        if result and os.path.exists(result):
            logger.info("✅ Successfully processed test file, output: %s", result)
            return True
        else:
            logger.error("❌ Failed to process test file")
            return False

    except Exception as e:
        logger.error("❌ Sample file test failed: %s", e)
        return False


def main():
    """Run integration tests."""
    print("🔧 Running Integration Tests")
    print("=" * 40)

    tests = [
        ("Markdown Library", test_markdown_integration),
        ("Document Parsing", test_enhance_document_parsing),
        ("Sample File Processing", test_sample_file_creation),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error("❌ Test '%s' crashed: %s", test_name, e)
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 Integration Test Results:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
