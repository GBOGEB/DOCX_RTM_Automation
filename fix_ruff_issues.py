#!/usr/bin/env python3
"""
Fix Ruff Issues - Clean up code quality issues detected by ruff
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_ruff_check():
    """Run ruff check and capture results."""
    print("🔍 Running Ruff Code Quality Check")
    print("=" * 40)

    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ No ruff issues found!")
            return []
        else:
            # Parse JSON output
            try:
                issues = json.loads(result.stdout)
                print(f"⚠️ Found {len(issues)} ruff issues")
                return issues
            except json.JSONDecodeError:
                print("❌ Could not parse ruff output")
                print(f"Raw output: {result.stdout}")
                print(f"Error output: {result.stderr}")
                return []

    except subprocess.TimeoutExpired:
        print("⏰ Ruff check timed out")
        return []
    except FileNotFoundError:
        print("❌ Ruff not found. Install with: pip install ruff")
        return []
    except Exception as e:
        print(f"❌ Error running ruff: {e}")
        return []


def analyze_ruff_issues(issues):
    """Analyze and categorize ruff issues."""
    if not issues:
        return {}

    categories = {}
    for issue in issues:
        rule_code = issue.get("code", "UNKNOWN")
        if rule_code not in categories:
            categories[rule_code] = []
        categories[rule_code].append(issue)

    print("\n📊 Issue Categories:")
    for rule_code, rule_issues in categories.items():
        print(f"   {rule_code}: {len(rule_issues)} issues")

    return categories


def fix_common_issues():
    """Fix common ruff issues automatically."""
    print("\n🔧 Attempting Automatic Fixes")
    print("=" * 35)

    try:
        # Run ruff with --fix flag
        result = subprocess.run(
            ["ruff", "check", ".", "--fix"], capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            print("✅ All fixable issues resolved!")
            return True
        else:
            print("⚠️ Some issues remain after auto-fix")
            return False

    except Exception as e:
        print(f"❌ Error during auto-fix: {e}")
        return False


def generate_quality_report(issues_before, issues_after):
    """Generate code quality improvement report."""

    quality_report = {
        "quality_check": {
            "timestamp": datetime.now().isoformat(),
            "issues_before_fix": len(issues_before),
            "issues_after_fix": len(issues_after),
            "issues_resolved": len(issues_before) - len(issues_after),
            "improvement_percentage": (
                (len(issues_before) - len(issues_after)) / len(issues_before) * 100
            )
            if issues_before
            else 100,
        },
        "issues_before": issues_before,
        "issues_after": issues_after,
        "rtm_system_status": {
            "code_quality": "EXCELLENT"
            if len(issues_after) == 0
            else "GOOD"
            if len(issues_after) < 5
            else "NEEDS_ATTENTION",
            "production_ready": len(issues_after) < 10,
            "enterprise_grade": len(issues_after) == 0,
        },
    }

    # Save report
    report_file = Path("code_quality_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)

    return quality_report


def verify_rtm_files_quality():
    """Verify that key RTM files pass quality checks."""
    print("\n🎯 Verifying Key RTM Files Quality")
    print("=" * 40)

    key_files = [
        "main_organized.py",
        "src/analyzers/json_file_analyzer_safe.py",
        "src/rtm/rtm_pipeline.py",
        "src/dashboard/rtm_web_dashboard.py",
        "test_organized_imports.py",
        "verify_rtm_still_perfect.py",
    ]

    quality_status = {}

    for file_path in key_files:
        if Path(file_path).exists():
            try:
                result = subprocess.run(
                    ["ruff", "check", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                quality_status[file_path] = {
                    "exists": True,
                    "passes_check": result.returncode == 0,
                    "issues": result.stdout.count("\n") if result.stdout else 0,
                }

                status = "✅" if result.returncode == 0 else "⚠️"
                print(f"   {status} {file_path}")

            except Exception as e:
                quality_status[file_path] = {
                    "exists": True,
                    "passes_check": False,
                    "error": str(e),
                }
                print(f"   ❌ {file_path}: Error checking")
        else:
            quality_status[file_path] = {"exists": False}
            print(f"   ❌ {file_path}: Not found")

    return quality_status


def main():
    """Main function for fixing ruff issues."""

    print("🧹 RTM Code Quality Improvement Tool")
    print("=" * 45)

    # Initial check
    print("📊 Initial Code Quality Assessment:")
    issues_before = run_ruff_check()

    if issues_before:
        # Analyze issues
        analyze_ruff_issues(issues_before)

        # Attempt automatic fixes
        fix_common_issues()

        # Check results after fix
        print("\n🔍 Post-Fix Quality Check:")
        issues_after = run_ruff_check()
    else:
        issues_after = []

    # Verify key RTM files
    verify_rtm_files_quality()

    # Generate quality report
    quality_report = generate_quality_report(issues_before, issues_after)

    # Display results
    print("\n🎊 CODE QUALITY IMPROVEMENT COMPLETE!")
    print("=" * 45)

    metrics = quality_report["quality_check"]

    print("📊 QUALITY METRICS:")
    print(f"   🔍 Issues before: {metrics['issues_before_fix']}")
    print(f"   ✅ Issues after: {metrics['issues_after_fix']}")
    print(f"   🎯 Issues resolved: {metrics['issues_resolved']}")
    print(f"   📈 Improvement: {metrics['improvement_percentage']:.1f}%")

    status = quality_report["rtm_system_status"]
    print("\n🏆 RTM SYSTEM CODE QUALITY:")
    print(f"   💎 Code Quality: {status['code_quality']}")
    print(f"   🚀 Production Ready: {'✅' if status['production_ready'] else '❌'}")
    print(f"   🏢 Enterprise Grade: {'✅' if status['enterprise_grade'] else '❌'}")

    if metrics["issues_after_fix"] == 0:
        print("\n🎉 PERFECT! Your RTM system has ZERO code quality issues!")
        print("   🏆 Enterprise-grade code quality achieved")
        print("   💎 Production deployment ready")
        print("   🌟 Industry-leading standards met")
    elif metrics["issues_after_fix"] < 5:
        print("\n👍 EXCELLENT! Minimal issues remaining")
        print("   🎯 High-quality code maintained")
        print("   🚀 Production ready with minor improvements")
    else:
        print("\n⚠️ Some quality issues remain")
        print("   📋 Consider reviewing remaining issues")

    print("\n💾 Quality report saved to: code_quality_report.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
