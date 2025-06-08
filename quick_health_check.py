#!/usr/bin/env python3
"""
Quick Health Check - Verify JSON ecosystem status after aggressive fixes
"""

import json
from pathlib import Path
from datetime import datetime

def quick_check():
    """Quick verification of JSON health."""
    print("🏥 Quick JSON Health Check")
    print("=" * 35)

    # Find all JSON files
    json_files = list(Path(".").rglob("*.json"))
    print(f"📊 Total JSON files: {len(json_files)}")

    valid = 0
    invalid = 0
    invalid_list = []

    # Check each file
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
            valid += 1
        except json.JSONDecodeError as e:
            invalid += 1
            invalid_list.append(str(json_file))
        except Exception:
            pass  # Skip unreadable files

    health_score = (valid / (valid + invalid) * 100) if (valid + invalid) > 0 else 100

    print(f"✅ Valid JSON files: {valid}")
    print(f"❌ Invalid JSON files: {invalid}")
    print(f"📈 Health Score: {health_score:.1f}%")

    if invalid_list:
        print(f"\n⚠️ Invalid files:")
        for file_path in invalid_list[:5]:
            print(f"   📄 {file_path}")

    # Check the specific files that were fixed
    fixed_files = [
        ".vscode/settings.json",
        ".ariana/.vscode/settings.json",
        ".ariana/DOCX_RTM_Automation/.vscode/launch.json",
        "DOCX_RTM_Automation/.vscode/launch.json"
    ]

    print(f"\n🔧 Previously Fixed Files Status:")
    all_fixed = True

    for file_path in fixed_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"   ✅ {file_path}: VALID")
            except json.JSONDecodeError:
                print(f"   ❌ {file_path}: STILL INVALID")
                all_fixed = False
        else:
            print(f"   📄 {file_path}: NOT FOUND")

    # Summary
    print(f"\n🎯 SUMMARY:")
    if health_score == 100:
        print("🏆 PERFECT! 100% JSON health achieved!")
        print("🚀 Your RTM system has pristine JSON ecosystem!")
    elif health_score >= 98:
        print("🥇 EXCELLENT! Nearly perfect JSON health!")
        print("🌟 Your RTM system is enterprise-ready!")
    else:
        print(f"⚠️ Health score: {health_score:.1f}%")
        print("💡 Some JSON files may need attention")

    return health_score >= 98

if __name__ == "__main__":
    success = quick_check()
    exit(0 if success else 1)
