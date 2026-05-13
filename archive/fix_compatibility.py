from format_handler import FormatHandler
from pathlib import Path
import os

"""
Fix Compatibility Issues - Address unsupported file format warnings
"""


def fix_compatibility_issues():
    """Fix compatibility issues by converting unsupported files"""
    print("🔧 Fixing Compatibility Issues...")
    print("=" * 40)

    handler = FormatHandler()

    # Generate report first
    report = handler.generate_format_report("input")

    print(f"📊 Current Status:")
    print(f"   Supported files: {report['statistics']['supported_count']}")
    print(f"   Convertible files: {report['statistics']['convertible_count']}")
    print(f"   Unsupported files: {report['statistics']['unsupported_count']}")

    if report['statistics']['convertible_count'] > 0:
        print(f"\n🔄 Converting {report['statistics']['convertible_count']} files...")

        # Show what will be converted
        for file_info in report['convertible_files']:
            print(f"   📄 {file_info['filename']} ({file_info['extension']})")

        # Convert files
        converted_files = handler.batch_convert_unsupported("input")

        print(f"\n✅ Successfully converted {len(converted_files)} files:")
        for converted_file in converted_files:
            print(f"   ✅ {Path(converted_file).name}")

        print(f"\n💡 These converted files can now be processed by the RTM pipeline!")

    else:
        print("\n✅ No convertible files found - all good!")

    if report['statistics']['unsupported_count'] > 0:
        print(f"\n⚠️  {report['statistics']['unsupported_count']} files remain unsupported:")
        for file_info in report['unsupported_files']:
            print(f"   ❌ {file_info['filename']} ({file_info['extension']})")

        print(f"\n💡 Consider manually converting these files or adding support for these formats.")

if __name__ == "__main__":
    fix_compatibility_issues()