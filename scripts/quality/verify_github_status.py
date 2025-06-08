#!/usr/bin/env python3
"""
Verify GitHub Status - Check if everything is pushed and retrievable from GitHub
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

def check_git_repository_status():
    """Check the current Git repository status"""
    print("🔍 Git Repository Status Check")
    print("=" * 40)

    # Check if we're in a Git repository
    if not Path('.git').exists():
        print("❌ Not in a Git repository")
        return False

    try:
        # Check current branch
        result = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            print(f"📍 Current branch: {current_branch}")
        else:
            print("⚠️  Could not determine current branch")
            current_branch = "unknown"

        # Check remote repository
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("🌐 Remote repositories:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        else:
            print("❌ No remote repositories configured")
            return False

        # Check if we have commits
        result = subprocess.run(['git', 'log', '--oneline', '-5'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n📦 Recent commits:")
            for line in result.stdout.strip().split('\n')[:3]:
                print(f"   {line}")
        else:
            print("⚠️  No commits found")

        return True

    except Exception as e:
        print(f"❌ Error checking Git status: {e}")
        return False

def check_working_directory_status():
    """Check for uncommitted changes"""
    print(f"\n🔍 Working Directory Status")
    print("-" * 35)

    try:
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                untracked = [line for line in lines if line.startswith('??')]
                modified = [line for line in lines if line.startswith(' M')]
                staged = [line for line in lines if line.startswith('A ') or line.startswith('M ')]

                print(f"📊 Changes found:")
                print(f"   Untracked files: {len(untracked)}")
                print(f"   Modified files: {len(modified)}")
                print(f"   Staged files: {len(staged)}")

                if len(untracked) > 0:
                    print(f"\n📋 Sample untracked files:")
                    for file in untracked[:5]:
                        print(f"   • {file[3:]}")
                    if len(untracked) > 5:
                        print(f"   • ... and {len(untracked) - 5} more")

                return False  # There are uncommitted changes
            else:
                print("✅ Working directory is clean")
                return True
        else:
            print("❌ Could not check working directory status")
            return False

    except Exception as e:
        print(f"❌ Error checking working directory: {e}")
        return False

def check_sync_with_remote():
    """Check if local repository is in sync with remote"""
    print(f"\n🔄 Remote Sync Status")
    print("-" * 25)

    try:
        # Fetch latest from remote
        print("Fetching latest from remote...")
        result = subprocess.run(['git', 'fetch'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(f"⚠️  Fetch warning: {result.stderr}")

        # Check if we're ahead/behind remote
        result = subprocess.run(['git', 'status', '--porcelain=v1', '--branch'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            status_line = result.stdout.split('\n')[0] if result.stdout else ""

            if "ahead" in status_line:
                print("⬆️  Local repository is AHEAD of remote")
                print("   You have unpushed commits")
                return "ahead"
            elif "behind" in status_line:
                print("⬇️  Local repository is BEHIND remote")
                print("   You need to pull changes")
                return "behind"
            else:
                print("✅ Local repository is in sync with remote")
                return "synced"
        else:
            print("❌ Could not check sync status")
            return "unknown"

    except Exception as e:
        print(f"❌ Error checking remote sync: {e}")
        return "error"

def get_commit_info():
    """Get detailed commit information"""
    print(f"\n📦 Commit Information")
    print("-" * 25)

    try:
        # Get last commit hash and message
        result = subprocess.run(['git', 'log', '-1', '--format=%H|%s|%ad', '--date=short'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            commit_info = result.stdout.strip().split('|')
            if len(commit_info) >= 3:
                commit_hash = commit_info[0][:8]
                commit_message = commit_info[1]
                commit_date = commit_info[2]

                print(f"🆔 Latest commit: {commit_hash}")
                print(f"📝 Message: {commit_message}")
                print(f"📅 Date: {commit_date}")

                return {
                    'hash': commit_hash,
                    'message': commit_message,
                    'date': commit_date
                }

        print("⚠️  Could not get commit information")
        return None

    except Exception as e:
        print(f"❌ Error getting commit info: {e}")
        return None

def check_essential_files():
    """Check if essential project files are present and tracked"""
    print(f"\n📁 Essential Files Check")
    print("-" * 30)

    essential_files = [
        'main.py',
        'document_converter.py',
        'README.md',
        '.gitignore',
        'requirements.txt',
        'pyproject.toml'
    ]

    tracked_files = []
    missing_files = []

    for file in essential_files:
        file_path = Path(file)
        if file_path.exists():
            # Check if file is tracked by Git
            result = subprocess.run(['git', 'ls-files', file],
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                tracked_files.append(file)
                print(f"✅ {file} - present and tracked")
            else:
                print(f"⚠️  {file} - present but not tracked")
                missing_files.append(file)
        else:
            print(f"❌ {file} - missing")
            missing_files.append(file)

    print(f"\n📊 Summary: {len(tracked_files)}/{len(essential_files)} essential files tracked")

    return len(missing_files) == 0

def test_github_connectivity():
    """Test if we can connect to GitHub"""
    print(f"\n🌐 GitHub Connectivity Test")
    print("-" * 35)

    try:
        # Try to get remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"📎 Remote URL: {remote_url}")

            if 'github.com' in remote_url:
                print("✅ GitHub repository detected")

                # Test connectivity with a simple fetch
                print("Testing GitHub connectivity...")
                result = subprocess.run(['git', 'ls-remote', 'origin'],
                                      capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    print("✅ GitHub connection successful")
                    return True
                else:
                    print(f"❌ GitHub connection failed: {result.stderr}")
                    return False
            else:
                print("⚠️  Remote is not GitHub")
                return False
        else:
            print("❌ No remote origin configured")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ GitHub connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing GitHub connectivity: {e}")
        return False

def push_remaining_changes():
    """Push any remaining changes to GitHub"""
    print(f"\n🚀 Push Remaining Changes")
    print("-" * 30)

    try:
        # Push to remote
        result = subprocess.run(['git', 'push', 'origin', 'main'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub")
            if result.stdout.strip():
                print(f"📤 Push result: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Push failed: {result.stderr}")

            # Check if it's because we're up to date
            if "up-to-date" in result.stderr.lower():
                print("ℹ️  Repository is already up to date")
                return True

            return False

    except Exception as e:
        print(f"❌ Error pushing to GitHub: {e}")
        return False

def generate_clone_instructions():
    """Generate instructions for cloning the repository"""
    print(f"\n📋 Clone Instructions")
    print("-" * 25)

    try:
        # Get remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            remote_url = result.stdout.strip()

            print("🎯 To retrieve a clean copy from GitHub:")
            print(f"   1. Navigate to a new directory")
            print(f"   2. Run: git clone {remote_url}")
            print(f"   3. Navigate into the cloned directory")
            print(f"   4. Test: python main.py")

            # Generate a test script
            test_script = f"""#!/bin/bash
# Test script to verify clean clone
cd /tmp
rm -rf RTM_test_clone
git clone {remote_url} RTM_test_clone
cd RTM_test_clone
echo "Testing pipeline..."
python main.py
echo "Clone test complete!"
"""

            try:
                with open('test_clone.sh', 'w') as f:
                    f.write(test_script)
                print(f"\n📄 Created test_clone.sh script for testing")
            except:
                pass

            return remote_url
        else:
            print("❌ Could not get remote URL")
            return None

    except Exception as e:
        print(f"❌ Error generating clone instructions: {e}")
        return None

def create_status_report():
    """Create a comprehensive status report"""
    print(f"\n📊 Creating Status Report")
    print("-" * 30)

    report = {
        "timestamp": datetime.now().isoformat(),
        "git_status": "unknown",
        "github_connectivity": False,
        "sync_status": "unknown",
        "essential_files": False,
        "ready_for_clone": False
    }

    try:
        # Collect all the status information
        git_ok = check_git_repository_status()
        working_clean = check_working_directory_status()
        sync_status = check_sync_with_remote()
        essential_ok = check_essential_files()
        github_ok = test_github_connectivity()

        # Update report
        report["git_status"] = "ok" if git_ok else "issues"
        report["working_directory_clean"] = working_clean
        report["sync_status"] = sync_status
        report["essential_files"] = essential_ok
        report["github_connectivity"] = github_ok
        report["ready_for_clone"] = all([git_ok, working_clean, sync_status == "synced", essential_ok, github_ok])

        # Save report
        with open('github_status_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print("✅ Status report saved to: github_status_report.json")
        return report

    except Exception as e:
        print(f"❌ Error creating status report: {e}")
        return report

def show_final_summary(report):
    """Show final summary and recommendations"""
    print(f"\n🏆 FINAL GITHUB STATUS SUMMARY")
    print("=" * 45)

    if report["ready_for_clone"]:
        print("🎉 SUCCESS! Your repository is ready for clean clone!")
        print("\n✅ All checks passed:")
        print("   • Git repository is properly configured")
        print("   • Working directory is clean")
        print("   • In sync with GitHub")
        print("   • Essential files are tracked")
        print("   • GitHub connectivity confirmed")

        print(f"\n🎯 You can now retrieve a clean copy with:")
        clone_url = generate_clone_instructions()

        print(f"\n🧪 Test Commands:")
        print("   python verify_github_status.py  # Re-run this check")
        print("   bash test_clone.sh              # Test clean clone")

    else:
        print("⚠️  Repository needs attention before clean clone")
        print("\n❌ Issues found:")

        if not report.get("git_status") == "ok":
            print("   • Git repository configuration issues")
        if not report.get("working_directory_clean"):
            print("   • Uncommitted changes in working directory")
        if not report.get("sync_status") == "synced":
            print("   • Not synchronized with remote")
        if not report.get("essential_files"):
            print("   • Missing or untracked essential files")
        if not report.get("github_connectivity"):
            print("   • GitHub connectivity problems")

        print(f"\n🔧 Recommended actions:")
        if not report.get("working_directory_clean"):
            print("   git add . && git commit -m 'final cleanup'")
        if report.get("sync_status") == "ahead":
            print("   git push origin main")
        if report.get("sync_status") == "behind":
            print("   git pull origin main")
        if not report.get("github_connectivity"):
            print("   Check GitHub authentication and network")

def main():
    """Main verification function"""
    print("🔍 GitHub Status Verification")
    print("=" * 35)
    print("Checking if your RTM automation project is fully pushed and retrievable...\n")

    # Run all checks
    git_ok = check_git_repository_status()

    if not git_ok:
        print("\n❌ Git repository issues detected. Please fix and try again.")
        return 1

    working_clean = check_working_directory_status()
    sync_status = check_sync_with_remote()
    essential_ok = check_essential_files()
    github_ok = test_github_connectivity()

    # If we have unpushed commits, offer to push
    if sync_status == "ahead":
        response = input("\n🚀 Push unpushed commits to GitHub? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if push_remaining_changes():
                sync_status = "synced"

    # Create comprehensive report
    report = create_status_report()

    # Show final summary
    show_final_summary(report)

    return 0 if report["ready_for_clone"] else 1

if __name__ == "__main__":
    sys.exit(main())
