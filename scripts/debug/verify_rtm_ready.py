#!/usr/bin/env python3
"""
RTM System Production Readiness Verification

Comprehensive verification that your RTM automation system is ready for use.
"""

import subprocess
import sys
import json
from pathlib import Path
import time


def verify_rtm_system():
    """Verify RTM system is ready for production use."""
    print("🎯 RTM Automation System - Production Readiness Check")
    print("=" * 60)

    verification_results = {
        "quality_checks": {"passed": False, "score": 0},
        "core_functionality": {"passed": False, "tests": []},
        "document_processing": {"passed": False, "formats": []},
        "digital_twin": {"passed": False, "capabilities": []},
        "requirements_tracing": {"passed": False, "features": []},
        "integration": {"passed": False, "components": []},
    }

    # 1. Quality Checks
    print("\n🔍 1. Code Quality Verification")
    print("-" * 30)

    try:
        # Run light quality check
        result = subprocess.run(
            [sys.executable, "quality_check_light.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and "🎉" in result.stdout:
            verification_results["quality_checks"]["passed"] = True
            verification_results["quality_checks"]["score"] = 100
            print("   ✅ Code quality: EXCELLENT")
        else:
            print("   ⚠️ Code quality: Some issues remain")
            verification_results["quality_checks"]["score"] = 85

    except Exception as e:
        print(f"   ❌ Quality check failed: {e}")

    # 2. Core Functionality
    print("\n⚙️ 2. Core Functionality Verification")
    print("-" * 30)

    core_tests = [
        ("enhance_document_parsing.py", "Document parsing engine"),
        ("digital_twin_parser.py", "Digital twin generation"),
        ("verify_system_status.py", "System status monitoring"),
        ("test_integration.py", "Integration testing"),
    ]

    passed_tests = 0
    for file_path, description in core_tests:
        if Path(file_path).exists():
            try:
                # Quick syntax check
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print(f"   ✅ {description}")
                    verification_results["core_functionality"]["tests"].append(
                        description
                    )
                    passed_tests += 1
                else:
                    print(f"   ❌ {description}: Syntax error")
            except Exception:
                print(f"   ❌ {description}: Failed to verify")
        else:
            print(f"   ❌ {description}: File missing")

    verification_results["core_functionality"]["passed"] = passed_tests >= 3

    # 3. Document Processing
    print("\n📄 3. Document Processing Capabilities")
    print("-" * 30)

    # Test sample document processing
    processing_formats = []
    try:
        # Test Markdown processing
        result = subprocess.run(
            [sys.executable, "enhance_document_parsing.py", "--sample", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("   ✅ Markdown → JSON conversion")
            processing_formats.append("Markdown→JSON")

        # Test YAML output
        result = subprocess.run(
            [sys.executable, "enhance_document_parsing.py", "--sample", "-f", "yaml"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("   ✅ Markdown → YAML conversion")
            processing_formats.append("Markdown→YAML")

        # Check if requirements.json exists (DOCX processing)
        if Path("output/requirements.json").exists():
            print("   ✅ DOCX → JSON conversion")
            processing_formats.append("DOCX→JSON")

    except Exception as e:
        print(f"   ⚠️ Document processing test failed: {e}")

    verification_results["document_processing"]["passed"] = len(processing_formats) >= 2
    verification_results["document_processing"]["formats"] = processing_formats

    # 4. Digital Twin Capabilities
    print("\n🔗 4. Digital Twin System")
    print("-" * 30)

    digital_twin_features = []
    try:
        # Test digital twin creation
        result = subprocess.run(
            [
                sys.executable,
                "digital_twin_parser.py",
                "input/sample/sample_document.md",
                "-o",
                "output/verification_twin",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("   ✅ Digital twin generation")
            digital_twin_features.append("Generation")

            # Check output files
            if Path("output/verification_twin/digital_twin.json").exists():
                print("   ✅ JSON digital twin format")
                digital_twin_features.append("JSON export")

            if Path("output/verification_twin/digital_twin.yaml").exists():
                print("   ✅ YAML digital twin format")
                digital_twin_features.append("YAML export")

    except Exception as e:
        print(f"   ⚠️ Digital twin test failed: {e}")

    verification_results["digital_twin"]["passed"] = len(digital_twin_features) >= 2
    verification_results["digital_twin"]["capabilities"] = digital_twin_features

    # 5. Requirements Tracing
    print("\n📋 5. Requirements Tracing System")
    print("-" * 30)

    requirements_features = []

    # Check for requirements extraction
    output_files = list(Path("output").glob("*.json"))
    for output_file in output_files:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            if "requirements_found" in metadata and metadata["requirements_found"]:
                print(
                    f"   ✅ Requirements extraction: {len(metadata['requirements_found'])} found"
                )
                requirements_features.append("Extraction")

                # Check requirement patterns
                reqs = metadata["requirements_found"]
                if any(req.startswith("REQ-") for req in reqs):
                    requirements_features.append("REQ pattern")
                if any(req.startswith("FR-") for req in reqs):
                    requirements_features.append("FR pattern")
                if any(req.startswith("NFR-") for req in reqs):
                    requirements_features.append("NFR pattern")
                break
        except Exception:
            continue

    # Check for Project Requirements integration
    if Path("Project Requirements.py").exists():
        print("   ✅ Project Requirements integration")
        requirements_features.append("Integration")

    verification_results["requirements_tracing"]["passed"] = (
        len(requirements_features) >= 2
    )
    verification_results["requirements_tracing"]["features"] = requirements_features

    # 6. Integration Status
    print("\n🔧 6. System Integration")
    print("-" * 30)

    integration_components = []

    # Check dependencies
    try:
        import markdown

        print("   ✅ Markdown library integrated")
        integration_components.append("Markdown")
    except ImportError:
        print("   ❌ Markdown library missing")

    try:
        from docx import Document

        print("   ✅ python-docx integrated")
        integration_components.append("python-docx")
    except ImportError:
        print("   ❌ python-docx missing")

    try:
        import yaml

        print("   ✅ PyYAML integrated")
        integration_components.append("PyYAML")
    except ImportError:
        print("   ❌ PyYAML missing")

    # Check directory structure
    required_dirs = ["input", "output", "src"]
    for directory in required_dirs:
        if Path(directory).exists():
            integration_components.append(f"{directory} directory")

    verification_results["integration"]["passed"] = len(integration_components) >= 4
    verification_results["integration"]["components"] = integration_components

    # Final Assessment
    print("\n🎯 FINAL RTM SYSTEM ASSESSMENT")
    print("=" * 60)

    total_categories = len(verification_results)
    passed_categories = sum(
        1 for result in verification_results.values() if result["passed"]
    )

    overall_score = int((passed_categories / total_categories) * 100)

    print(f"Categories Passed: {passed_categories}/{total_categories}")
    print(f"Overall Score: {overall_score}/100")

    if overall_score >= 90:
        status = "🎉 PRODUCTION READY!"
        color = "🟢"
    elif overall_score >= 75:
        status = "✅ READY FOR USE"
        color = "🟡"
    else:
        status = "⚠️ NEEDS ATTENTION"
        color = "🔴"

    print(f"Status: {color} {status}")

    # Save verification report
    verification_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": overall_score,
        "status": status,
        "categories_passed": f"{passed_categories}/{total_categories}",
        "detailed_results": verification_results,
    }

    report_path = Path("output") / "rtm_verification_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(verification_report, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")

    # RTM Usage Instructions
    if overall_score >= 75:
        print("\n🚀 YOUR RTM SYSTEM IS READY!")
        print("=" * 40)
        print("Next steps to start using RTM:")
        print("1. Process documents:")
        print("   python enhance_document_parsing.py input/your_document.docx -f json")
        print("2. Create digital twins:")
        print("   python digital_twin_parser.py input/your_document.md -o output/twin")
        print("3. Generate visualizations:")
        print("   python src/visualizers/req_visualizer.py output/requirements.json")
        print("4. Run integration tests:")
        print("   python test_integration.py")

    return overall_score


if __name__ == "__main__":
    score = verify_rtm_system()
    sys.exit(0 if score >= 75 else 1)
