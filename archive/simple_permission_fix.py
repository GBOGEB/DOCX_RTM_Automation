#!/usr/bin/env python3
"""
Simple Permission Fix - Basic file permission handling without external dependencies
"""

import os
import time
from pathlib import Path
from datetime import datetime

def test_file_access(file_path):
    """Test if we can write to a file."""
    try:
        # Try to open the file for writing
        with open(file_path, 'ab') as f:
            pass
        return True
    except PermissionError:
        return False
    except FileNotFoundError:
        # File doesn't exist, which is fine - we can create it
        return True
    except Exception as e:
        print(f"⚠️ Unexpected error testing {file_path}: {e}")
        return False

def simple_file_cleanup():
    """Simple cleanup of problematic output files."""
    print("🔧 SIMPLE FILE PERMISSION FIX")
    print("=" * 35)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    problematic_files = [
        Path("output/sample_rtm_document_rtm_processed.docx"),
        Path("output/sample_rtm_document_rtm_processed.md"),
        Path("temp_processing/sample_rtm_document_processed.md"),
    ]

    print("🎯 This will:")
    print("   • Delete problematic output files")
    print("   • Test directory write access")
    print("   • Clear file locks (simple method)")
    print()

    # Test and fix output directories
    output_dirs = [Path("output"), Path("temp_processing")]

    for output_dir in output_dirs:
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {output_dir}")
            except Exception as e:
                print(f"❌ Could not create directory {output_dir}: {e}")
                continue

        # Test write access
        test_file = output_dir / "test_write_access.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # Delete test file
            print(f"✅ Write access OK: {output_dir}")
        except Exception as e:
            print(f"❌ No write access to {output_dir}: {e}")

    print()

    # Handle problematic files
    for file_path in problematic_files:
        if file_path.exists():
            print(f"📄 Checking: {file_path}")

            if not test_file_access(file_path):
                print(f"❌ Permission denied: {file_path}")
                print("💡 Trying to remove the file...")

                try:
                    # First try a simple delete
                    file_path.unlink()
                    print(f"✅ Successfully removed: {file_path}")
                except PermissionError:
                    print(f"⚠️ Permission denied - file may be open in Word")
                    print("📝 Please close Microsoft Word and try again")

                    # Try to rename instead of delete
                    backup_path = file_path.with_suffix(f'.backup_{int(time.time())}{file_path.suffix}')
                    try:
                        file_path.rename(backup_path)
                        print(f"🔄 Moved to backup: {backup_path}")
                    except Exception as e:
                        print(f"❌ Could not move file: {e}")
                        print("💡 Manual action needed:")
                        print(f"   1. Close Microsoft Word")
                        print(f"   2. Delete: {file_path}")
                        print(f"   3. Run the pipeline again")
                except Exception as e:
                    print(f"❌ Error removing file: {e}")
            else:
                print(f"✅ File access OK: {file_path}")
        else:
            print(f"✅ File doesn't exist: {file_path} (no issue)")

    print("\n🎉 SIMPLE PERMISSION FIX COMPLETE!")
    print()
    print("💡 NEXT STEPS:")
    print("   1. Make sure Microsoft Word is completely closed")
    print("   2. Run: python simple_test_pipeline.py")
    print("   3. If still failing, restart your computer")
    print()
    print("🔄 TROUBLESHOOTING TIPS:")
    print("   • Close all Word documents before running pipelines")
    print("   • Check Task Manager for WINWORD.EXE processes")
    print("   • Run terminal as Administrator if needed")

def check_word_processes():
    """Check for Word processes using simple methods."""
    print("\n🔍 CHECKING FOR MICROSOFT WORD")
    print("=" * 35)

    print("💡 Manual Word Process Check:")
    print("   1. Press Ctrl+Shift+Esc to open Task Manager")
    print("   2. Look for 'Microsoft Word' or 'WINWORD.EXE'")
    print("   3. End any Word processes you find")
    print("   4. Close Task Manager and try the pipeline again")
    print()

    # Try a simple command to check for Word processes
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/fi', 'imagename eq WINWORD.EXE'],
                              capture_output=True, text=True, shell=True)

        if 'WINWORD.EXE' in result.stdout:
            print("⚠️ Microsoft Word processes detected!")
            print("📝 Please close Word and try again")
        else:
            print("✅ No Word processes found")

    except Exception as e:
        print(f"⚠️ Could not check processes automatically: {e}")
        print("💡 Please manually check Task Manager for Word processes")

def main():
    """Main function."""
    simple_file_cleanup()
    check_word_processes()

if __name__ == "__main__":
    main()
