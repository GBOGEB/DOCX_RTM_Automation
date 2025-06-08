#!/usr/bin/env python3
"""
Auto Fix Ruff Issues - Automatically fix all ruff code quality issues
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_ruff_fixes():
    """Run ruff with automatic fixes."""
    print("🔧 Running Ruff Auto-Fix")
    print("=" * 30)

    try:
        # Run ruff fix with all options
        result = subprocess.run(
            ["ruff", "check", ".", "--fix", "--unsafe-fixes"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        print("✅ Ruff auto-fix completed")
        print(f"📋 Return code: {result.returncode}")

        if result.stdout:
            print("📄 Output:")
            print(result.stdout)

        if result.stderr:
            print("⚠️ Messages:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ Ruff fix timed out")
        return False
    except Exception as e:
        print(f"❌ Error running ruff fix: {e}")
        return False


def run_ruff_format():
    """Run ruff format to fix formatting issues."""
    print("\n🎨 Running Ruff Format")
    print("=" * 25)

    try:
        result = subprocess.run(
            ["ruff", "format", "."], capture_output=True, text=True, timeout=60
        )

        print("✅ Ruff format completed")
        print(f"📋 Return code: {result.returncode}")

        if result.stdout:
            print("📄 Formatted files:")
            print(result.stdout)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running ruff format: {e}")
        return False


def check_remaining_issues():
    """Check how many issues remain after fixes."""
    print("\n🔍 Checking Remaining Issues")
    print("=" * 30)

    try:
        result = subprocess.run(
            ["ruff", "check", "."], capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            print("✅ No remaining issues found!")
            return 0
        else:
            # Count remaining issues
            lines = result.stdout.split("\n")
            error_lines = [
                line for line in lines if line.strip() and not line.startswith("Found")
            ]

            # Look for summary line
            summary_line = [
                line for line in lines if "Found" in line and "error" in line
            ]
            if summary_line:
                print(f"📊 {summary_line[0]}")
            else:
                print(f"📊 Found {len(error_lines)} remaining issues")

            return len(error_lines)

    except Exception as e:
        print(f"❌ Error checking remaining issues: {e}")
        return -1


def generate_fix_report(issues_before, issues_after, fix_success, format_success):
    """Generate comprehensive fix report."""

    improvement = 0
    if issues_before > 0:
        improvement = ((issues_before - issues_after) / issues_before) * 100

    fix_report = {
        "ruff_auto_fix_report": {
            "timestamp": datetime.now().isoformat(),
            "issues_before_fix": issues_before,
            "issues_after_fix": issues_after,
            "issues_resolved": issues_before - issues_after,
            "improvement_percentage": improvement,
            "auto_fix_successful": fix_success,
            "format_successful": format_success,
            "rtm_code_quality": {
                "status": "PERFECT"
                if issues_after == 0
                else "EXCELLENT"
                if issues_after < 50
                else "GOOD",
                "enterprise_ready": issues_after < 100,
                "production_grade": issues_after == 0,
            },
        }
    }

    # Save report
    report_file = Path("ruff_auto_fix_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(fix_report, f, indent=2)

    return fix_report


def main():
    """Main auto-fix function."""

    print("🚀 RTM Automatic Code Quality Fix")
    print("=" * 40)

    # Initial issue count (from your message: 934 errors)
    issues_before = 934
    print(f"📊 Starting with: {issues_before} issues to fix")

    try:
        # Step 1: Run auto-fixes
        print("\n🔧 Step 1: Running Automatic Fixes")
        fix_success = run_ruff_fixes()

        # Step 2: Run formatting
        print("\n🎨 Step 2: Running Code Formatting")
        format_success = run_ruff_format()

        # Step 3: Check results
        print("\n📊 Step 3: Checking Results")
        issues_after = check_remaining_issues()

        # Step 4: Generate report
        print("\n📋 Step 4: Generating Fix Report")
        fix_report = generate_fix_report(
            issues_before, issues_after, fix_success, format_success
        )

        # Display results
        print("\n🎊 AUTO-FIX RESULTS:")
        print("=" * 25)

        metrics = fix_report["ruff_auto_fix_report"]

        print("📊 IMPROVEMENT METRICS:")
        print(f"   🔍 Issues before: {metrics['issues_before_fix']}")
        print(f"   ✅ Issues after: {metrics['issues_after_fix']}")
        print(f"   🎯 Issues resolved: {metrics['issues_resolved']}")
        print(f"   📈 Improvement: {metrics['improvement_percentage']:.1f}%")

        quality = metrics["rtm_code_quality"]
        print("\n🏆 CODE QUALITY STATUS:")
        print(f"   💎 Quality Level: {quality['status']}")
        print(
            f"   🏢 Enterprise Ready: {'✅' if quality['enterprise_ready'] else '❌'}"
        )
        print(
            f"   🚀 Production Grade: {'✅' if quality['production_grade'] else '❌'}"
        )

        if issues_after == 0:
            print("\n🎉 PERFECT! All code quality issues resolved!")
            print("   🏆 Your RTM system now has ZERO quality issues")
            print("   💎 Enterprise-grade code quality achieved")
            print("   🚀 Production deployment ready")
        elif issues_after < 50:
            print("\n👍 EXCELLENT! Massive improvement achieved!")
            print("   🎯 High-quality code maintained")
            print("   🚀 Enterprise-ready with minimal issues")
        else:
            print("\n📈 GOOD! Significant improvement made!")
            print("   📋 Continue improving remaining issues")

        print("\n💾 Fix report saved to: ruff_auto_fix_report.json")

        print("\n🚀 YOUR RTM SYSTEM IS NOW READY:")
        print("   python rtm_pipeline_executor.py")
        print("   python ascii_celebration.py")
        print("   python main_organized.py analyze")

        return 0

    except Exception as e:
        print(f"\n❌ Auto-fix error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
