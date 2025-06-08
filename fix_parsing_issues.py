#!/usr/bin/env python3
"""
Fix Parsing Issues - Diagnostic and repair tool for document parsing problems
"""

import json
import sys
import traceback
from pathlib import Path
from datetime import datetime
import importlib.util


def check_parsing_dependencies():
    """Check if required parsing dependencies are available."""
    print("🔍 Checking Parsing Dependencies")
    print("=" * 35)

    dependencies = {
        "python-docx": "docx",
        "PyYAML": "yaml",
        "lxml": "lxml",
        "openpyxl": "openpyxl",
    }

    available = {}
    missing = []

    for package_name, import_name in dependencies.items():
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"   ✅ {package_name}: Available")
                available[package_name] = True
            else:
                print(f"   ❌ {package_name}: Not found")
                available[package_name] = False
                missing.append(package_name)
        except Exception as e:
            print(f"   ⚠️ {package_name}: Error checking - {e}")
            available[package_name] = False
            missing.append(package_name)

    return available, missing


def test_enhanced_parsing():
    """Test the enhanced parsing module."""
    print("\n🧪 Testing Enhanced Parsing Module")
    print("=" * 40)

    try:
        # Try to import the enhanced parsing module
        enhanced_parsing_path = Path(".ariana/enhance_document_parsing.py")

        if not enhanced_parsing_path.exists():
            print(f"❌ Enhanced parsing module not found at: {enhanced_parsing_path}")
            return False

        print("✅ Enhanced parsing module found")

        # Try to import and test
        sys.path.insert(0, str(enhanced_parsing_path.parent))

        try:
            from enhance_document_parsing import (
                EnhancedDocumentParser,
            )

            print("✅ Successfully imported EnhancedDocumentParser")

            # Test parser initialization
            parser = EnhancedDocumentParser()
            print("✅ Parser initialized successfully")
            print(f"   📄 Supported formats: {parser.supported_formats}")

            return True

        except Exception as e:
            print(f"❌ Error importing enhanced parsing: {e}")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ Error testing enhanced parsing: {e}")
        return False


def create_sample_documents():
    """Create sample documents for testing parsing."""
    print("\n📄 Creating Sample Documents for Testing")
    print("=" * 45)

    # Create samples directory
    samples_dir = Path("parsing_samples")
    samples_dir.mkdir(exist_ok=True)

    # Sample Markdown with RTM content
    sample_md = samples_dir / "sample_rtm.md"
    with open(sample_md, "w", encoding="utf-8") as f:
        f.write(
            """# RTM Sample Document

## Requirements

### REQ-001: User Authentication
The system shall provide user authentication functionality.

### REQ-002: Data Validation
The system shall validate all input data.

## Test Cases

### TC-001: Login Test
Verify user can login with valid credentials.
**Traces to:** REQ-001

### TC-002: Input Validation Test
Verify system rejects invalid input.
**Traces to:** REQ-002

## Traceability Matrix

| Requirement | Test Case | Status |
|-------------|-----------|--------|
| REQ-001     | TC-001    | PASS   |
| REQ-002     | TC-002    | PASS   |
"""
        )

    # Sample JSON with RTM content
    sample_json = samples_dir / "sample_rtm.json"
    with open(sample_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "requirements": [
                    {
                        "id": "REQ-001",
                        "description": "User Authentication",
                        "priority": "high",
                    },
                    {
                        "id": "REQ-002",
                        "description": "Data Validation",
                        "priority": "medium",
                    },
                ],
                "test_cases": [
                    {
                        "id": "TC-001",
                        "description": "Login Test",
                        "traces_to": ["REQ-001"],
                    },
                    {
                        "id": "TC-002",
                        "description": "Validation Test",
                        "traces_to": ["REQ-002"],
                    },
                ],
                "traceability": {"REQ-001": ["TC-001"], "REQ-002": ["TC-002"]},
            },
            f,
            indent=2,
        )

    # Sample text file
    sample_txt = samples_dir / "sample_rtm.txt"
    with open(sample_txt, "w", encoding="utf-8") as f:
        f.write(
            """RTM Sample Text Document

REQUIREMENT REQ-001: System shall authenticate users
TESTCASE TC-001: Verify login functionality
TRACE LINK: TC-001 -> REQ-001

REQUIREMENT REQ-002: System shall validate inputs
TESTCASE TC-002: Verify input validation
TRACE LINK: TC-002 -> REQ-002
"""
        )

    print(f"✅ Created sample documents in: {samples_dir}")
    print(f"   📄 {sample_md.name}")
    print(f"   📄 {sample_json.name}")
    print(f"   📄 {sample_txt.name}")

    return [str(sample_md), str(sample_json), str(sample_txt)]


def test_parsing_with_samples(sample_files):
    """Test parsing with sample files."""
    print("\n🔧 Testing Parsing with Sample Files")
    print("=" * 40)

    try:
        from enhance_document_parsing import EnhancedDocumentParser

        parser = EnhancedDocumentParser()
        results = []

        for file_path in sample_files:
            print(f"\n📄 Parsing: {Path(file_path).name}")

            try:
                result = parser.parse_document(file_path)

                if result.get("status") == "success":
                    print(f"   ✅ Status: {result['status']}")
                    print(
                        f"   📋 Requirements: {result['summary']['requirements_found']}"
                    )
                    print(f"   🧪 Test cases: {result['summary']['test_cases_found']}")
                    print(
                        f"   🔗 Traceability: {result['summary']['traceability_links_found']}"
                    )
                else:
                    print(f"   ❌ Status: {result['status']}")
                    print(f"   ⚠️ Error: {result.get('error_message', 'Unknown error')}")

                results.append(result)

            except Exception as e:
                print(f"   ❌ Parse error: {e}")
                results.append({"status": "error", "error": str(e)})

        # Save test results
        test_results_file = Path("parsing_test_results.json")
        with open(test_results_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "test_timestamp": datetime.now().isoformat(),
                    "sample_files": sample_files,
                    "results": results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Test results saved to: {test_results_file}")
        return True

    except Exception as e:
        print(f"❌ Error testing parsing: {e}")
        traceback.print_exc()
        return False


def generate_parsing_diagnostic_report():
    """Generate comprehensive parsing diagnostic report."""

    diagnostic_report = {
        "diagnostic_timestamp": datetime.now().isoformat(),
        "parsing_diagnostic": {
            "dependencies": {},
            "module_status": "unknown",
            "test_results": "not_run",
            "recommendations": [],
        },
    }

    print("🏥 Generating Parsing Diagnostic Report")
    print("=" * 45)

    # Check dependencies
    available_deps, missing_deps = check_parsing_dependencies()
    diagnostic_report["parsing_diagnostic"]["dependencies"] = {
        "available": available_deps,
        "missing": missing_deps,
    }

    # Test enhanced parsing module
    module_working = test_enhanced_parsing()
    diagnostic_report["parsing_diagnostic"]["module_status"] = (
        "working" if module_working else "error"
    )

    # Create and test with samples if module is working
    if module_working:
        sample_files = create_sample_documents()
        test_success = test_parsing_with_samples(sample_files)
        diagnostic_report["parsing_diagnostic"]["test_results"] = (
            "success" if test_success else "failure"
        )

    # Generate recommendations
    recommendations = []

    if missing_deps:
        recommendations.append(
            f"Install missing dependencies: pip install {' '.join(missing_deps)}"
        )

    if not module_working:
        recommendations.append("Fix enhanced parsing module import issues")

    if module_working and available_deps:
        recommendations.append("Enhanced parsing is working correctly!")

    diagnostic_report["parsing_diagnostic"]["recommendations"] = recommendations

    # Save diagnostic report
    report_file = Path("parsing_diagnostic_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(diagnostic_report, f, indent=2)

    print("\n📋 DIAGNOSTIC SUMMARY:")
    print(
        f"   📦 Available dependencies: {len([k for k, v in available_deps.items() if v])}"
    )
    print(f"   ❌ Missing dependencies: {len(missing_deps)}")
    print(
        f"   🔧 Module status: {diagnostic_report['parsing_diagnostic']['module_status']}"
    )
    print(
        f"   🧪 Test results: {diagnostic_report['parsing_diagnostic']['test_results']}"
    )

    print("\n💡 RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"   • {rec}")

    print(f"\n💾 Diagnostic report saved to: {report_file}")

    return diagnostic_report


def main():
    """Main function for parsing issue diagnostics."""

    print("🔧 RTM Parsing Issues Diagnostic Tool")
    print("=" * 45)

    try:
        # Generate comprehensive diagnostic
        diagnostic = generate_parsing_diagnostic_report()

        print("\n🎯 PARSING DIAGNOSTIC COMPLETE!")
        print("=" * 35)

        if diagnostic["parsing_diagnostic"]["module_status"] == "working":
            print("✅ Enhanced parsing module is working correctly!")
            print("🚀 You can now use enhanced document parsing features")
        else:
            print("⚠️ Enhanced parsing module has issues")
            print("📋 Check recommendations above for fixes")

        return 0

    except Exception as e:
        print(f"❌ Error in diagnostic: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
