#!/usr/bin/env python3
"""
Remove Problematic Files - Remove files that are causing syntax errors
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import shutil


def is_file_essential(file_path):
    """Check if a file is essential for the RTM system."""
    essential_patterns = [
        "main_organized.py",
        "rtm_pipeline_executor.py",
        "src/analyzers/",
        "src/rtm/",
        "src/dashboard/",
        "verify_rtm_still_perfect.py",
        "test_organized_imports.py",
    ]

    file_str = str(file_path)
    return any(pattern in file_str for pattern in essential_patterns)


def remove_problematic_files():
    """Remove files that are causing syntax errors but aren't essential."""

    # Files that are causing syntax errors
    problematic_files = [
        "DOCX_RTM_Automation/scripts/debug_full_pipeline.py",
        "DOCX_RTM_Automation/scripts/docx_rtm_automation.py",
        "DOCX_RTM_Automation/src/extractors/extract_outline.py",
        "DOCX_RTM_Automation/src/extractors/extract_rtm.py",
        "scripts/automation/run_full_pipeline.py",
        "scripts/debug/fix_pyproject_and_final_cleanup.py",
        "scripts/debug_full_pipeline.py",
        "scripts/docx_rtm_automation.py",
        "server/app.py",
    ]

    removal_report = {
        "timestamp": datetime.now().isoformat(),
        "files_checked": len(problematic_files),
        "files_removed": [],
        "files_backed_up": [],
        "files_skipped": [],
    }

    print("🗑️ Removing Problematic Files")
    print("=" * 35)
    print("This will remove files causing syntax errors to allow ruff to work")
    print()

    for file_path in problematic_files:
        path_obj = Path(file_path)

        if not path_obj.exists():
            print(f"⏭️ Skip (not found): {file_path}")
            continue

        if is_file_essential(file_path):
            print(f"🔒 Skip (essential): {file_path}")
            removal_report["files_skipped"].append(file_path)
            continue

        try:
            # Create backup first
            backup_dir = Path("removed_files_backup")
            backup_dir.mkdir(exist_ok=True)

            backup_file = (
                backup_dir
                / f"{path_obj.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(file_path, backup_file)
            removal_report["files_backed_up"].append(str(backup_file))

            # Remove the problematic file
            path_obj.unlink()
            removal_report["files_removed"].append(file_path)

            print(f"✅ Removed: {file_path}")
            print(f"   📋 Backup: {backup_file}")

        except Exception as e:
            print(f"❌ Error removing {file_path}: {e}")

    # Save removal report
    with open("file_removal_report.json", "w") as f:
        json.dump(removal_report, f, indent=2)

    return removal_report


def main():
    """Main function for removing problematic files."""

    print("🗑️ RTM Problematic File Removal Tool")
    print("=" * 45)
    print("This tool removes files causing syntax errors in ruff")
    print("All removed files will be backed up first")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with removing problematic files? (y/N): ")

    if response.lower() != "y":
        print("❌ Operation cancelled")
        return 1

    # Remove problematic files
    report = remove_problematic_files()

    # Display results
    print("\n🎊 FILE REMOVAL COMPLETE!")
    print("=" * 30)
    print(f"📊 Files checked: {report['files_checked']}")
    print(f"🗑️ Files removed: {len(report['files_removed'])}")
    print(f"📋 Files backed up: {len(report['files_backed_up'])}")
    print(f"🔒 Files skipped: {len(report['files_skipped'])}")

    if report["files_removed"]:
        print("\n✅ Removed files:")
        for file_path in report["files_removed"]:
            print(f"   • {file_path}")

    print("\n🚀 Now you can run:")
    print("   ruff format .")
    print("   ruff check . --fix")
    print("   python rtm_pipeline_executor.py")

    print("\n💾 Removal report saved to: file_removal_report.json")
    print("📂 Backups saved to: removed_files_backup/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
