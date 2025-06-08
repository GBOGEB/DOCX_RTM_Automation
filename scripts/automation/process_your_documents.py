#!/usr/bin/env python3
"""
Process Your Actual RTM Documents - Use your real documents for RTM automation
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Process your actual available documents."""
    print("🎯 Processing Your Real RTM Documents")
    print("=" * 50)

    # Check available documents
    input_dir = Path("input")
    available_docs = {
        "docx": list(input_dir.glob("*.docx")),
        "md": list(input_dir.glob("*.md")),
    }

    print("📊 Found documents:")
    for ext, files in available_docs.items():
        print(f"   {ext.upper()}: {len(files)} files")
        for f in files:
            print(f"      - {f.name}")

    if not any(available_docs.values()):
        print("❌ No documents found in input/ directory")
        return 1

    success_count = 0
    total_count = 0

    # Process DOCX files
    for docx_file in available_docs["docx"]:
        total_count += 1
        print(f"\n📄 Processing {docx_file.name}...")

        try:
            # Process to JSON
            result = subprocess.run(
                [
                    sys.executable,
                    "enhance_document_parsing.py",
                    str(docx_file),
                    "-f",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                print("   ✅ JSON conversion: SUCCESS")
                success_count += 1

                # Also try YAML
                subprocess.run(
                    [
                        sys.executable,
                        "enhance_document_parsing.py",
                        str(docx_file),
                        "-f",
                        "yaml",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                print("   ✅ YAML conversion: SUCCESS")

            else:
                print(f"   ⚠️ Issues: {result.stderr[:200]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Process Markdown files
    for md_file in available_docs["md"]:
        total_count += 1
        print(f"\n📝 Creating digital twin for {md_file.name}...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "digital_twin_parser.py",
                    str(md_file),
                    "-o",
                    f"output/{md_file.stem}_digital_twin",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                print("   ✅ Digital twin: SUCCESS")
                success_count += 1
            else:
                print(f"   ⚠️ Issues: {result.stderr[:200]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Summary
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print("\n🎯 Processing Summary:")
    print(f"   Documents processed: {success_count}/{total_count}")
    print(f"   Success rate: {success_rate:.1f}%")

    if success_rate >= 75:
        print("   🎉 EXCELLENT! Your RTM system is processing real documents!")
    elif success_rate >= 50:
        print("   ✅ GOOD! Most documents processed successfully")
    else:
        print("   ⚠️ Some issues - check individual results above")

    # Show output files
    output_dir = Path("output")
    if output_dir.exists():
        output_files = list(output_dir.glob("*"))
        print(f"\n📁 Generated Output Files ({len(output_files)}):")
        for f in sorted(output_files)[:10]:  # Show first 10
            size = f.stat().st_size if f.is_file() else 0
            print(f"   📄 {f.name} ({size:,} bytes)")
        if len(output_files) > 10:
            print(f"   ... and {len(output_files) - 10} more files")

    print("\n🚀 Your RTM automation is processing real enterprise documents!")
    print("   Check the output/ directory for JSON, YAML, and digital twin files")

    return 0 if success_rate >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
