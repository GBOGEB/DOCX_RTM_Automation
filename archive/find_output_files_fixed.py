#!/usr/bin/env python3
"""
Find Output Files - Fixed version with proper syntax
"""

import os
from pathlib import Path
from datetime import datetime

def find_output_files():
    """Find all output files in the output directory"""
    output_dir = Path("output")

    if not output_dir.exists():
        print("❌ Output directory not found")
        return []

    print(f"📁 Scanning output directory: {output_dir}")

    files = []
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            try:
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "extension": file_path.suffix.lower()
                }
                files.append(file_info)
            except (OSError, PermissionError) as e:
                print(f"⚠️  Could not access {file_path}: {e}")
                continue

    return files

def categorize_files(files):
    """Categorize files by type"""
    categories = {
        "documents": [".docx", ".pdf", ".rtf"],
        "data": [".json", ".yaml", ".yml"],
        "text": [".md", ".txt"],
        "images": [".png", ".jpg", ".jpeg", ".gif"],
        "logs": [".log"],
        "other": []
    }

    categorized = {category: [] for category in categories}

    for file_info in files:
        ext = file_info["extension"]
        categorized_file = False

        for category, extensions in categories.items():
            if category != "other" and ext in extensions:
                categorized[category].append(file_info)
                categorized_file = True
                break

        if not categorized_file:
            categorized["other"].append(file_info)

    return categorized

def display_results(categorized_files):
    """Display the results in a nice format"""
    print("\n" + "="*60)
    print("📊 OUTPUT FILES SUMMARY")
    print("="*60)

    total_files = sum(len(files) for files in categorized_files.values())
    total_size = sum(file["size"] for files in categorized_files.values() for file in files)

    print(f"📈 Total Files: {total_files}")
    print(f"💾 Total Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

    for category, files in categorized_files.items():
        if files:
            print(f"\n📂 {category.upper()} ({len(files)} files):")
            sorted_files = sorted(files, key=lambda x: x["modified"], reverse=True)

            for file_info in sorted_files[:10]:
                size_mb = file_info["size"] / 1024 / 1024
                if size_mb >= 1:
                    size_str = f"{size_mb:.1f} MB"
                else:
                    size_str = f"{file_info['size']:,} bytes"

                mod_time = file_info["modified"].strftime("%Y-%m-%d %H:%M")
                print(f"   • {file_info['name']} - {size_str} ({mod_time})")

            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more files")

def main():
    """Main function"""
    print("🔍 RTM Output File Finder - Fixed Version")
    print("=" * 60)
    print("Analyzing output directory for RTM pipeline results...")

    files = find_output_files()

    if not files:
        print("\n📭 No output files found")
        print("\n💡 Suggestions:")
        print("   • Run the RTM pipeline to generate output files")
        print("   • Check if the 'output' directory exists")
        print("   • Verify file permissions")
        return

    print(f"\n✅ Found {len(files)} files to analyze")

    categorized = categorize_files(files)
    display_results(categorized)

    print(f"\n💡 Analysis complete!")
    print("📁 Check the 'output' directory for all generated files")

if __name__ == "__main__":
    main()
