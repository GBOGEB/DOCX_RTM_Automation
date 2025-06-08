#!/usr/bin/env python3
"""
Simple Quality Check - Encoding-safe version for RTM system verification
"""

import sys
from pathlib import Path


def check_rtm_system_health():
    """Check RTM system health without subprocess calls."""
    print("🔍 RTM System Health Check (Encoding-Safe)")
    print("=" * 50)

    health_score = 0
    max_score = 100
    issues = []

    # Check 1: Core Files Exist (30 points)
    print("\n📁 Checking Core Files...")
    core_files = [
        "enhance_document_parsing.py",
        "digital_twin_parser.py",
        "extension_manager.py",
        "Project Requirements.py",
    ]

    core_files_found = 0
    for file_path in core_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            core_files_found += 1
        else:
            print(f"   ❌ {file_path}")
            issues.append(f"Missing core file: {file_path}")

    core_score = (core_files_found / len(core_files)) * 30
    health_score += core_score
    print(f"   📊 Core Files Score: {core_score:.1f}/30")

    # Check 2: Input Files Available (20 points)
    print("\n📄 Checking Input Files...")
    input_dir = Path("input")

    if input_dir.exists():
        docx_files = list(input_dir.glob("*.docx"))
        md_files = list(input_dir.glob("*.md"))

        # Filter out temp files
        docx_files = [f for f in docx_files if not f.name.startswith("~$")]

        total_input_files = len(docx_files) + len(md_files)

        print(f"   📄 DOCX files: {len(docx_files)}")
        print(f"   📝 Markdown files: {len(md_files)}")

        if total_input_files >= 3:
            input_score = 20
        elif total_input_files >= 1:
            input_score = 15
        else:
            input_score = 5
            issues.append("Very few input files available")

        health_score += input_score
        print(f"   📊 Input Files Score: {input_score}/20")
    else:
        print("   ❌ Input directory not found")
        issues.append("Input directory missing")
        print("   📊 Input Files Score: 0/20")

    # Check 3: Output Files Generated (25 points)
    print("\n📁 Checking Output Files...")
    output_dir = Path("output")

    if output_dir.exists():
        output_files = list(output_dir.glob("*"))
        json_files = list(output_dir.glob("*.json"))
        yaml_files = list(output_dir.glob("*.yaml"))
        directories = [p for p in output_dir.iterdir() if p.is_dir()]

        total_outputs = len(output_files)
        print(f"   📊 Total output files: {total_outputs}")
        print(f"   📄 JSON files: {len(json_files)}")
        print(f"   📋 YAML files: {len(yaml_files)}")
        print(f"   📂 Directories: {len(directories)}")

        if total_outputs >= 50:
            output_score = 25
        elif total_outputs >= 20:
            output_score = 20
        elif total_outputs >= 5:
            output_score = 15
        elif total_outputs >= 1:
            output_score = 10
        else:
            output_score = 0
            issues.append("No output files generated")

        health_score += output_score
        print(f"   📊 Output Files Score: {output_score}/25")
    else:
        print("   ❌ Output directory not found")
        issues.append("Output directory missing")
        print("   📊 Output Files Score: 0/25")

    # Check 4: AI Integration (15 points)
    print("\n🤖 Checking AI Integration...")
    ariana_dir = Path(".ariana")

    if ariana_dir.exists():
        ariana_files = list(ariana_dir.iterdir())
        config_files = list(ariana_dir.glob("*.json"))

        print(f"   📁 Ariana files: {len(ariana_files)}")
        print(f"   📄 Config files: {len(config_files)}")

        if len(ariana_files) >= 100:
            ai_score = 15
        elif len(ariana_files) >= 10:
            ai_score = 10
        elif len(ariana_files) >= 1:
            ai_score = 5
        else:
            ai_score = 0

        health_score += ai_score
        print(f"   📊 AI Integration Score: {ai_score}/15")
    else:
        print("   ℹ️ Ariana directory not found (AI not integrated)")
        print("   📊 AI Integration Score: 0/15")

    # Check 5: System Dependencies (10 points)
    print("\n📦 Checking System Dependencies...")

    dependencies = ["pathlib", "json", "datetime", "subprocess"]
    deps_available = 0

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
            deps_available += 1
        except ImportError:
            print(f"   ❌ {dep}")
            issues.append(f"Missing dependency: {dep}")

    deps_score = (deps_available / len(dependencies)) * 10
    health_score += deps_score
    print(f"   📊 Dependencies Score: {deps_score:.1f}/10")

    # Final Health Assessment
    print("\n🎯 FINAL HEALTH ASSESSMENT:")
    print("=" * 40)
    print(f"   Total Score: {health_score:.1f}/{max_score}")
    print(f"   Percentage: {(health_score / max_score) * 100:.1f}%")

    if health_score >= 80:
        status = "🟢 EXCELLENT"
        message = "Your RTM system is in excellent condition!"
    elif health_score >= 60:
        status = "🟡 GOOD"
        message = "Your RTM system is in good condition with minor issues."
    elif health_score >= 40:
        status = "🟠 FAIR"
        message = "Your RTM system needs some attention."
    else:
        status = "🔴 POOR"
        message = "Your RTM system needs significant improvements."

    print(f"   Status: {status}")
    print(f"   Assessment: {message}")

    if issues:
        print(f"\n⚠️ Issues Found ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")

    # Determine if system is ready
    if health_score >= 60:
        print("\n✅ SYSTEM STATUS: READY FOR USE")
        print("   Your RTM automation system is operational!")
    else:
        print("\n⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        print("   Address the issues above before using for production.")

    return health_score >= 60


def main():
    """Main quality check function."""
    print("🔍 Simple RTM Quality Check")
    print("Encoding-safe system verification")
    print("=" * 45)

    is_ready = check_rtm_system_health()

    print("\n🎉 Quality check complete!")

    return 0 if is_ready else 1


if __name__ == "__main__":
    sys.exit(main())
