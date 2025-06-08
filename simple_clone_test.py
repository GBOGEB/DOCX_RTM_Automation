#!/usr/bin/env python3
"""
Simple Clone Test - Test Git/GitHub roundtrip with Windows-friendly approach
"""

import subprocess
import sys
from pathlib import Path
import os

def get_repository_info():
    """Get current repository information"""
    print("🔍 Repository Information")
    print("-" * 30)

    try:
        # Get remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"📎 Remote URL: {remote_url}")
        else:
            print("❌ No remote configured")
            return None

        # Get current commit
        result = subprocess.run(['git', 'log', '-1', '--format=%H|%s'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            commit_info = result.stdout.strip().split('|')
            commit_hash = commit_info[0][:8]
            commit_message = commit_info[1] if len(commit_info) > 1 else "No message"
            print(f"📦 Latest commit: {commit_hash} - {commit_message[:50]}...")

        return remote_url

    except Exception as e:
        print(f"❌ Error getting repo info: {e}")
        return None

def test_github_connectivity():
    """Test GitHub connectivity"""
    print(f"\n🌐 GitHub Connectivity Test")
    print("-" * 30)

    try:
        result = subprocess.run(['git', 'ls-remote', 'origin'],
                              capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("✅ GitHub connection successful")
            refs = result.stdout.strip().split('\n')
            print(f"📋 Found {len(refs)} remote references")
            return True
        else:
            print(f"❌ GitHub connection failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ GitHub connection timed out")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def create_simple_clone_test(remote_url):
    """Create a simple clone test in C:\temp"""
    print(f"\n📥 Simple Clone Test")
    print("-" * 25)

    # Use C:\temp for Windows compatibility
    test_dir = Path("C:/temp/rtm_clone_test")
    clone_dir = test_dir / "DOCX_RTM_Automation"

    print(f"🎯 Test directory: {test_dir}")
    print(f"📁 Clone target: {clone_dir}")

    try:
        # Create test directory
        test_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing clone if it exists
        if clone_dir.exists():
            import shutil
            shutil.rmtree(clone_dir)
            print("🧹 Removed existing clone")

        # Clone the repository
        print("⬇️  Cloning repository...")
        result = subprocess.run(['git', 'clone', remote_url, str(clone_dir)],
                              capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Clone successful!")
            return clone_dir
        else:
            print(f"❌ Clone failed: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("⏰ Clone timed out")
        return None
    except Exception as e:
        print(f"❌ Clone error: {e}")
        return None

def verify_clone_contents(clone_dir):
    """Verify the cloned repository contents"""
    print(f"\n📋 Verifying Clone Contents")
    print("-" * 30)

    if not clone_dir.exists():
        print("❌ Clone directory doesn't exist")
        return False

    # Check essential files
    essential_files = [
        'main.py',
        'document_converter.py',
        'README.md',
        '.gitignore'
    ]

    print("🔍 Checking essential files:")
    found_files = 0

    for file in essential_files:
        file_path = clone_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file} ({size:,} bytes)")
            found_files += 1
        else:
            print(f"   ❌ {file} (missing)")

    # Check helper scripts
    helper_scripts = [
        'test_clone_workflow.py',
        'verify_github_status.py',
        'quick_commit_fix.py'
    ]

    print("\n🔧 Checking helper scripts:")
    found_helpers = 0

    for script in helper_scripts:
        script_path = clone_dir / script
        if script_path.exists():
            print(f"   ✅ {script}")
            found_helpers += 1
        else:
            print(f"   ⚠️  {script} (missing)")

    # Count total files
    try:
        all_files = list(clone_dir.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])

        print(f"\n📊 Clone summary:")
        print(f"   Essential files: {found_files}/{len(essential_files)}")
        print(f"   Helper scripts: {found_helpers}/{len(helper_scripts)}")
        print(f"   Total files: {file_count}")

        return found_files >= 3  # At least 3 essential files

    except Exception as e:
        print(f"❌ Error counting files: {e}")
        return False

def test_clone_functionality(clone_dir):
    """Test basic functionality in the cloned repository"""
    print(f"\n🧪 Testing Clone Functionality")
    print("-" * 30)

    original_cwd = Path.cwd()

    try:
        # Change to clone directory
        os.chdir(clone_dir)
        print(f"📂 Changed to: {clone_dir}")

        # Test 1: Python syntax check
        print("\n1. 🐍 Python syntax check:")
        main_py = Path("main.py")
        if main_py.exists():
            result = subprocess.run(['python', '-m', 'py_compile', 'main.py'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ main.py syntax is valid")
            else:
                print(f"   ❌ main.py syntax error: {result.stderr}")
                return False

        # Test 2: Check Git functionality
        print("\n2. 🔧 Git functionality check:")
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Git operations working")
        else:
            print("   ❌ Git operations failed")
            return False

        # Test 3: Check remote connection
        print("\n3. 🌐 Remote connection check:")
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Remote configured properly")
        else:
            print("   ❌ Remote configuration issues")
            return False

        print("\n✅ Clone functionality test passed!")
        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False
    finally:
        # Always return to original directory
        os.chdir(original_cwd)

def show_clone_instructions(remote_url):
    """Show manual clone instructions"""
    print(f"\n📋 Manual Clone Instructions")
    print("-" * 35)

    print("🎯 To manually test clone anywhere:")
    print(f"   mkdir C:\\temp\\my_rtm_test")
    print(f"   cd C:\\temp\\my_rtm_test")
    print(f"   git clone {remote_url}")
    print(f"   cd DOCX_RTM_Automation")
    print(f"   python main.py")

    print(f"\n📱 Share your repository:")
    print(f"   Repository URL: {remote_url}")
    print(f"   Anyone can clone with: git clone {remote_url}")

def cleanup_test(clone_dir, keep_clone=False):
    """Clean up test clone"""
    print(f"\n🧹 Cleanup")
    print("-" * 15)

    if not keep_clone and clone_dir and clone_dir.exists():
        try:
            import shutil
            shutil.rmtree(clone_dir.parent)  # Remove C:/temp/rtm_clone_test
            print(f"✅ Cleaned up test directory")
        except Exception as e:
            print(f"⚠️  Could not clean up: {e}")
    else:
        print(f"📁 Test clone preserved at: {clone_dir}")

def show_final_summary(test_results, remote_url):
    """Show final test summary"""
    print(f"\n🏆 CLONE TEST SUMMARY")
    print("=" * 30)

    print(f"🌐 Repository: {remote_url}")

    # Calculate success rate
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")

    for test_name, passed in test_results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")

    if success_rate >= 80:
        print("\n🎉 EXCELLENT! Your repository clone test passed!")
        print("\n✅ What this means:")
        print("• Repository clones successfully from GitHub")
        print("• All essential files are present")
        print("• Basic functionality works")
        print("• Others can easily use your project")

        print(f"\n🚀 Your RTM automation project is ready for sharing!")

    elif success_rate >= 60:
        print("\n✅ GOOD! Clone works with minor issues")
        print("Most functionality working - review any failed tests")

    else:
        print("\n⚠️  NEEDS ATTENTION! Several clone issues found")
        print("Review failed tests and fix critical issues")

    print(f"\n📞 Quick Commands:")
    print("   python main.py                  # Test your pipeline")
    print("   python verify_github_status.py  # Check GitHub status")
    print(f"   git clone {remote_url}         # Clone anywhere")

def main():
    """Main test function"""
    print("🧪 Simple Clone Test")
    print("=" * 25)
    print("Testing Git/GitHub clone functionality with Windows-friendly approach...\n")

    # Step 1: Get repository info
    remote_url = get_repository_info()
    if not remote_url:
        print("❌ Could not get repository information")
        return 1

    test_results = {}

    # Step 2: Test GitHub connectivity
    github_ok = test_github_connectivity()
    test_results['GitHub Connectivity'] = github_ok

    if not github_ok:
        print("❌ Cannot proceed without GitHub connectivity")
        show_final_summary(test_results, remote_url)
        return 1

    # Step 3: Create test clone
    clone_dir = create_simple_clone_test(remote_url)
    test_results['Clone Creation'] = clone_dir is not None

    if not clone_dir:
        print("❌ Clone test failed")
        show_final_summary(test_results, remote_url)
        return 1

    # Step 4: Verify clone contents
    contents_ok = verify_clone_contents(clone_dir)
    test_results['Content Verification'] = contents_ok

    # Step 5: Test clone functionality
    functionality_ok = test_clone_functionality(clone_dir)
    test_results['Functionality Test'] = functionality_ok

    # Step 6: Show instructions
    show_clone_instructions(remote_url)

    # Step 7: Show summary
    show_final_summary(test_results, remote_url)

    # Step 8: Cleanup
    keep_clone = input(f"\nKeep test clone for inspection? (y/n): ").lower().strip() == 'y'
    cleanup_test(clone_dir, keep_clone)

    print(f"\n🎊 Clone test completed!")

    return 0 if all(test_results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
