#!/usr/bin/env python3
"""
Fix File Permissions - Handle file access issues that prevent pipeline execution
"""

import os
import time
import psutil
from pathlib import Path
from datetime import datetime

def find_processes_using_file(file_path):
    """Find processes that are using a specific file."""
    processes = []

    try:
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                if proc.info['open_files']:
                    for file_info in proc.info['open_files']:
                        if str(file_path).lower() in file_info.path.lower():
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'file': file_info.path
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        print(f"⚠️ Could not scan processes: {e}")

    return processes

def close_file_handles(file_path):
    """Attempt to close file handles for a specific file."""
    print(f"🔍 Checking processes using: {file_path}")

    processes = find_processes_using_file(file_path)

    if not processes:
        print("✅ No processes found using this file")
        return True

    print(f"📋 Found {len(processes)} processes using the file:")
    for proc in processes:
        print(f"   • PID {proc['pid']}: {proc['name']}")

    # Ask user if they want to close Word processes
    word_processes = [p for p in processes if 'word' in p['name'].lower() or 'winword' in p['name'].lower()]

    if word_processes:
        print("\n💡 Microsoft Word appears to be using this file.")
        print("📋 Options:")
        print("   1. Close Word manually and press Enter")
        print("   2. Let the script attempt to close Word")
        print("   3. Skip this file")

        choice = input("\nChoice (1/2/3): ").strip()

        if choice == "1":
            input("📝 Please close Microsoft Word and press Enter to continue...")
            return True
        elif choice == "2":
            return close_word_processes(word_processes)
        else:
            print("⏭️ Skipping file")
            return False

    return True

def close_word_processes(word_processes):
    """Safely close Word processes."""
    print("🔄 Attempting to close Word processes...")

    for proc_info in word_processes:
        try:
            proc = psutil.Process(proc_info['pid'])
            print(f"🔧 Closing {proc_info['name']} (PID: {proc_info['pid']})")

            # Try graceful termination first
            proc.terminate()

            # Wait up to 5 seconds for graceful exit
            try:
                proc.wait(timeout=5)
                print(f"✅ Process closed gracefully")
            except psutil.TimeoutExpired:
                print(f"⚠️ Process didn't close gracefully, forcing...")
                proc.kill()
                proc.wait(timeout=3)
                print(f"✅ Process forced to close")

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"⚠️ Could not close process {proc_info['pid']}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error closing process: {e}")
            return False

    # Wait a moment for file handles to be released
    time.sleep(2)
    return True

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

def fix_output_directory_permissions():
    """Fix permissions for output directories."""
    print("🔧 FIXING OUTPUT DIRECTORY PERMISSIONS")
    print("=" * 40)

    output_dirs = [
        Path("output"),
        Path("temp_processing"),
        Path("reports"),
        Path("logs")
    ]

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

def fix_problematic_output_files():
    """Fix issues with existing output files."""
    print("\n🔧 FIXING PROBLEMATIC OUTPUT FILES")
    print("=" * 35)

    problematic_files = [
        Path("output/sample_rtm_document_rtm_processed.docx"),
        Path("output/sample_rtm_document_rtm_processed.md"),
        Path("temp_processing/sample_rtm_document_processed.md"),
    ]

    for file_path in problematic_files:
        if file_path.exists():
            print(f"\n📄 Checking: {file_path}")

            if not test_file_access(file_path):
                print(f"❌ Permission denied: {file_path}")

                if close_file_handles(file_path):
                    if test_file_access(file_path):
                        print(f"✅ File access restored: {file_path}")
                    else:
                        print(f"❌ Still cannot access: {file_path}")
                        # Try to rename/move the problematic file
                        backup_path = file_path.with_suffix('.backup' + file_path.suffix)
                        try:
                            file_path.rename(backup_path)
                            print(f"🔄 Moved to backup: {backup_path}")
                        except Exception as e:
                            print(f"⚠️ Could not backup file: {e}")
            else:
                print(f"✅ File access OK: {file_path}")

def main():
    """Main permission fixing function."""
    print("🔧 RTM FILE PERMISSION FIXER")
    print("=" * 40)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("🎯 This script will:")
    print("   • Check for processes using output files")
    print("   • Close Microsoft Word if necessary")
    print("   • Fix directory permissions")
    print("   • Clear file access issues")
    print()

    # Fix directory permissions
    fix_output_directory_permissions()

    # Fix problematic files
    fix_problematic_output_files()

    print("\n🎉 PERMISSION FIX COMPLETE!")
    print()
    print("💡 NEXT STEPS:")
    print("   1. Run: python simple_test_pipeline.py")
    print("   2. If still fails, try: python setup_and_run_pipeline.py")
    print("   3. Make sure Word is closed before running pipelines")
    print()
    print("🔄 TIPS TO PREVENT ISSUES:")
    print("   • Close Word before running pipelines")
    print("   • Don't open output files during processing")
    print("   • Run terminal as Administrator if needed")

if __name__ == "__main__":
    main()
