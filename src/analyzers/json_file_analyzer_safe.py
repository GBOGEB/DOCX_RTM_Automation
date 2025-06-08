#!/usr/bin/env python3
"""
RTM JSON File Analyzer (Safe Version) - With robust error handling for malformed JSON
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def safe_json_load(file_path):
    """Safely load JSON with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON Error: {e}"
    except UnicodeDecodeError as e:
        return None, f"Encoding Error: {e}"
    except Exception as e:
        return None, f"File Error: {e}"


def analyze_json_ecosystem():
    """Analyze the entire JSON ecosystem in RTM system."""
    print("📊 RTM JSON File Ecosystem Analysis (Safe Version)")
    print("=" * 55)

    # Categories for JSON files
    categories = {
        "ariana_ai": [".ariana/", "ariana_", "ai_"],
        "output_data": ["output/", "_rtm.json", "_outline.json"],
        "configurations": ["config.json", "settings.json", "keybindings.json"],
        "extensions": ["extension_", ".vscode/", "launch.json"],
        "workflows": ["workflow", "pipeline", "rtm_workflow"],
        "documentation": ["docs/", "function_reference"],
        "test_data": ["test_", "sample_", "demo_"],
        "jenkins": ["jenkins", ".jenkinsrc"],
        "metadata": ["metadata.json", "status.json", "report.json"],
    }

    json_files = []
    categorized_files = defaultdict(list)
    malformed_files = []

    # Find all JSON files
    for json_file in Path(".").rglob("*.json"):
        if json_file.is_file():
            json_files.append(json_file)

            # Test if file is valid JSON
            data, error = safe_json_load(json_file)
            if error:
                malformed_files.append((json_file, error))

            # Categorize the file
            file_str = str(json_file).lower()
            categorized = False

            for category, patterns in categories.items():
                if any(pattern in file_str for pattern in patterns):
                    categorized_files[category].append(json_file)
                    categorized = True
                    break

            if not categorized:
                categorized_files["other"].append(json_file)

    print(f"🎯 Total JSON Files Found: {len(json_files)}")
    print(f"📁 Categories Identified: {len(categorized_files)}")
    print(f"⚠️ Malformed JSON Files: {len(malformed_files)}")

    if malformed_files:
        print("\n❌ Files with JSON errors:")
        for file_path, error in malformed_files[:5]:  # Show first 5
            print(f"   📄 {file_path}: {error}")
        if len(malformed_files) > 5:
            print(f"   ... and {len(malformed_files) - 5} more")

    return json_files, categorized_files, malformed_files


def analyze_by_category(categorized_files):
    """Analyze JSON files by category."""
    print("\n📈 JSON Files by Category:")
    print("=" * 35)

    for category, files in sorted(categorized_files.items()):
        print(f"\n🏷️ {category.replace('_', ' ').title()} ({len(files)} files):")

        total_size = 0
        valid_files = 0

        for file_path in files[:5]:  # Show first 5 files
            try:
                size = file_path.stat().st_size
                total_size += size

                # Check if valid JSON
                data, error = safe_json_load(file_path)
                status = "✅" if not error else "❌"
                if not error:
                    valid_files += 1

                # Show relative path
                rel_path = (
                    str(file_path)[:50] + "..."
                    if len(str(file_path)) > 50
                    else str(file_path)
                )
                print(f"   📄 {status} {rel_path} ({size:,} bytes)")

            except Exception:
                print(f"   📄 ❌ {file_path} (error reading)")

        if len(files) > 5:
            remaining_size = sum(f.stat().st_size for f in files[5:] if f.exists())
            total_size += remaining_size

            # Count valid files in remaining
            remaining_valid = 0
            for f in files[5:]:
                data, error = safe_json_load(f)
                if not error:
                    remaining_valid += 1

            valid_files += remaining_valid
            print(f"   ... and {len(files) - 5} more files")

        print(f"   📊 Category Total: {total_size:,} bytes")
        print(f"   ✅ Valid JSON files: {valid_files}/{len(files)}")


def analyze_key_json_files_safe():
    """Analyze key JSON files with safe error handling."""
    print("\n🔍 Key JSON File Analysis (Safe):")
    print("=" * 40)

    key_files = [
        ".jenkinsrc.json",
        "extension_config.json",
        "extension_report.json",
        ".ariana/config.json",
        "output/MASTER_1805_1144.json",
        "output/workflow_summary.json",
        ".vscode/settings.json",
    ]

    for file_path in key_files:
        path_obj = Path(file_path)
        if path_obj.exists():
            try:
                size = path_obj.stat().st_size
                data, error = safe_json_load(path_obj)

                print(f"\n📄 {file_path}:")
                print(f"   Size: {size:,} bytes")

                if error:
                    print("   ❌ Status: MALFORMED JSON")
                    print(f"   🔧 Error: {error}")
                    print("   💡 Run json_file_fixer.py to fix this file")
                else:
                    print("   ✅ Status: VALID JSON")
                    print(
                        f"   🔑 Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
                    )

                    # Show specific insights for valid files
                    if "jenkins" in file_path.lower():
                        print("   🔧 Jenkins Configuration")
                        if isinstance(data, dict) and "Local" in data:
                            local_config = data["Local"]
                            print(
                                f"      Applications: {local_config.get('applications', [])}"
                            )
                            print(
                                f"      Description: {local_config.get('description', 'N/A')}"
                            )

                    elif "extension" in file_path.lower():
                        print("   📦 Extension Management")
                        if isinstance(data, dict):
                            if "extensions" in data:
                                ext_count = len(data["extensions"])
                                print(f"      Extensions: {ext_count}")
                            if "summary" in data:
                                summary = data["summary"]
                                print(
                                    f"      Total Extensions: {summary.get('total_extensions', 0)}"
                                )

                    elif "ariana" in file_path.lower():
                        print("   🤖 Ariana AI Configuration")

                    elif "MASTER" in file_path:
                        print("   📊 Master Document Processing Result")

            except Exception as e:
                print(f"\n📄 {file_path}: ❌ Error accessing file ({e})")
        else:
            print(f"\n📄 {file_path}: ❌ Not found")


def show_health_recommendations(malformed_files):
    """Show recommendations for maintaining JSON health."""
    print("\n💊 JSON Health Recommendations:")
    print("=" * 40)

    if not malformed_files:
        print("✅ Your JSON ecosystem is HEALTHY!")
        print("   All JSON files are properly formatted")
        print("   No action needed")
    else:
        print(f"⚠️ Found {len(malformed_files)} problematic JSON files")
        print("\n🔧 Recommended Actions:")
        print("   1. Run: python json_file_fixer.py")
        print("   2. Review VS Code settings.json for comments/trailing commas")
        print("   3. Validate JSON before committing changes")
        print("   4. Use proper JSON formatting tools")

        print("\n📋 Files needing attention:")
        for file_path, error in malformed_files[:3]:
            print(f"   📄 {file_path}")
            print(f"      Error: {error}")


def generate_json_health_report():
    """Generate comprehensive JSON health report."""
    print("\n📋 Generating JSON Health Report...")

    json_files, categorized_files, malformed_files = analyze_json_ecosystem()

    # Calculate health metrics
    total_files = len(json_files)
    valid_files = total_files - len(malformed_files)
    health_percentage = (valid_files / total_files * 100) if total_files > 0 else 100

    # Create health report
    report = {
        "timestamp": datetime.now().isoformat(),
        "rtm_system": "DOCX RTM Automation v1.0",
        "json_health_summary": {
            "total_json_files": total_files,
            "valid_files": valid_files,
            "malformed_files": len(malformed_files),
            "health_percentage": round(health_percentage, 1),
            "categories": {cat: len(files) for cat, files in categorized_files.items()},
            "total_size_bytes": sum(f.stat().st_size for f in json_files if f.exists()),
        },
        "health_status": (
            "EXCELLENT"
            if health_percentage >= 95
            else "GOOD"
            if health_percentage >= 80
            else "NEEDS_ATTENTION"
        ),
        "malformed_file_list": [str(f[0]) for f in malformed_files],
        "recommendations": [
            (
                "Run json_file_fixer.py to fix malformed files"
                if malformed_files
                else "Maintain current JSON standards"
            ),
            "Validate JSON before commits",
            "Use JSON formatting tools in IDE",
        ],
    }

    # Save report
    try:
        report_path = Path("json_health_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"✅ JSON health report saved to: {report_path}")
        return report

    except Exception as e:
        print(f"⚠️ Could not save health report: {e}")
        return report


def main():
    """Main analysis function with safe JSON handling."""
    print("🔍 RTM JSON File Ecosystem Analyzer (Safe Version)")
    print("=" * 60)
    print("Analyzing JSON ecosystem with robust error handling...")

    # Full ecosystem analysis
    json_files, categorized_files, malformed_files = analyze_json_ecosystem()

    # Category breakdown
    analyze_by_category(categorized_files)

    # Key files analysis (safe)
    analyze_key_json_files_safe()

    # Health recommendations
    show_health_recommendations(malformed_files)

    # Generate health report
    report = generate_json_health_report()

    # Final summary
    health_percentage = report["json_health_summary"]["health_percentage"]

    print("\n🎉 ANALYSIS COMPLETE!")
    print("=" * 30)
    print("📊 Your RTM JSON ecosystem:")
    print(f"   • {len(json_files)} total JSON files")
    print(f"   • {len(json_files) - len(malformed_files)} valid files")
    print(f"   • {len(malformed_files)} files need fixing")
    print(f"   • {health_percentage}% health score")

    if health_percentage >= 95:
        print("\n🏆 EXCELLENT! Your JSON ecosystem is in top condition!")
    elif health_percentage >= 80:
        print("\n✅ GOOD! Minor issues to address for perfect health!")
    else:
        print("\n⚠️ Run json_file_fixer.py to improve JSON ecosystem health!")

    return 0


if __name__ == "__main__":
    main()
