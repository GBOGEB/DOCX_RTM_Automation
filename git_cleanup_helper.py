#!/usr/bin/env python3
"""
Git Cleanup Helper - Manage complex Git status with many changes
"""

import subprocess
import sys
from pathlib import Path

def analyze_git_status():
    """Analyze the current Git status"""
    print("🔍 Git Status Analysis")
    print("=" * 50)

    try:
        # Get detailed status
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error getting Git status")
            return False

        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        # Categorize changes
        staged_changes = []
        unstaged_changes = []
        untracked_files = []

        for line in lines:
            if not line.strip():
                continue

            status = line[:2]
            filename = line[3:]

            if status[0] != ' ' and status[0] != '?':
                staged_changes.append((status, filename))
            if status[1] != ' ':
                unstaged_changes.append((status, filename))
            if status == '??':
                untracked_files.append(filename)

        # Display summary
        print(f"📊 Summary:")
        print(f"   Staged changes: {len(staged_changes)}")
        print(f"   Unstaged changes: {len(unstaged_changes)}")
        print(f"   Untracked files: {len(untracked_files)}")

        return {
            'staged': staged_changes,
            'unstaged': unstaged_changes,
            'untracked': untracked_files
        }

    except Exception as e:
        print(f"❌ Error analyzing Git status: {e}")
        return False

def show_staged_changes(staged_changes):
    """Show what's currently staged"""
    if not staged_changes:
        print("\n✅ No staged changes")
        return

    print(f"\n📦 Staged Changes ({len(staged_changes)}):")
    print("-" * 40)

    # Group by change type
    change_types = {}
    for status, filename in staged_changes:
        change_type = get_change_type(status)
        if change_type not in change_types:
            change_types[change_type] = []
        change_types[change_type].append(filename)

    for change_type, files in change_types.items():
        print(f"\n{change_type} ({len(files)} files):")
        for filename in files[:5]:  # Show first 5
            print(f"   • {filename}")
        if len(files) > 5:
            print(f"   • ... and {len(files) - 5} more")

def get_change_type(status):
    """Convert Git status code to readable description"""
    status_map = {
        'A': '✅ Added',
        'M': '✏️  Modified',
        'D': '🗑️  Deleted',
        'R': '📝 Renamed',
        'C': '📄 Copied',
        'U': '⚠️  Unmerged'
    }

    return status_map.get(status[0], f"❓ Unknown ({status})")

def suggest_commit_strategy(git_status):
    """Suggest how to handle the current situation"""
    print("\n🎯 Recommended Strategy")
    print("=" * 30)

    staged_count = len(git_status['staged'])
    unstaged_count = len(git_status['unstaged'])
    untracked_count = len(git_status['untracked'])

    if staged_count > 50:
        print("⚠️  You have many staged changes. Consider:")
        print("1. Create a major reorganization commit")
        print("2. Split into smaller commits by category")
        print("3. Review what's staged before committing")

    if unstaged_count > 20:
        print("⚠️  Many unstaged changes detected:")
        print("1. Review each file carefully")
        print("2. Stage important changes only")
        print("3. Consider stashing work-in-progress")

    if untracked_count > 10:
        print("⚠️  Many untracked files:")
        print("1. Add important files to Git")
        print("2. Add temp files to .gitignore")
        print("3. Clean up unnecessary files")

def create_organized_commit():
    """Help create an organized commit"""
    print("\n📦 Creating Organized Commit")
    print("-" * 35)

    # Check if we have staged changes
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'],
                          capture_output=True)

    if result.returncode == 0:
        print("ℹ️  No staged changes to commit")
        return False

    # Suggest commit message
    commit_message = """chore: major project reorganization

- Moved scripts to organized directory structure
- Relocated source files to src/ directory
- Updated documentation structure
- Created proper module hierarchy
- Fixed import paths and dependencies
- Improved project organization

This commit reorganizes the entire project structure for better
maintainability and follows Python best practices."""

    print("📝 Suggested commit message:")
    print("-" * 25)
    print(commit_message)
    print("-" * 25)

    response = input("\nUse this commit message? (y/n/edit): ").lower().strip()

    if response == 'y':
        try:
            # Create commit with the message
            result = subprocess.run(['git', 'commit', '-m', commit_message],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Commit created successfully!")
                return True
            else:
                print(f"❌ Commit failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error creating commit: {e}")
            return False

    elif response == 'edit':
        print("\nTo create commit with custom message:")
        print('git commit -m "Your custom message here"')
        return False

    else:
        print("Commit cancelled")
        return False

def clean_untracked_files(untracked_files):
    """Help clean up untracked files"""
    print("\n🧹 Untracked Files Cleanup")
    print("-" * 30)

    if not untracked_files:
        print("✅ No untracked files")
        return

    # Categorize untracked files
    important_files = []
    temp_files = []
    backup_files = []

    for filename in untracked_files:
        if any(ext in filename.lower() for ext in ['.backup', '.bak', '_backup', '.old']):
            backup_files.append(filename)
        elif any(ext in filename.lower() for ext in ['.tmp', 'temp_', '__pycache__', '.log']):
            temp_files.append(filename)
        else:
            important_files.append(filename)

    print(f"📋 File categories:")
    print(f"   Important files: {len(important_files)}")
    print(f"   Backup files: {len(backup_files)}")
    print(f"   Temp files: {len(temp_files)}")

    if important_files:
        print(f"\n📄 Important files to consider adding:")
        for filename in important_files[:10]:
            print(f"   • {filename}")
        if len(important_files) > 10:
            print(f"   • ... and {len(important_files) - 10} more")

    if backup_files or temp_files:
        print(f"\n🗑️  Files you might want to clean up:")
        for filename in (backup_files + temp_files)[:10]:
            print(f"   • {filename}")

def quick_actions_menu():
    """Show quick action options"""
    print("\n⚡ Quick Actions")
    print("-" * 20)
    print("1. Commit staged changes")
    print("2. View staged files")
    print("3. Unstage all files")
    print("4. Add important untracked files")
    print("5. Check Git log")
    print("6. Exit")

    choice = input("\nSelect action (1-6): ").strip()

    if choice == '1':
        return create_organized_commit()
    elif choice == '2':
        subprocess.run(['git', 'diff', '--cached', '--name-status'])
        return True
    elif choice == '3':
        response = input("Unstage all files? (y/n): ").lower().strip()
        if response == 'y':
            subprocess.run(['git', 'reset', 'HEAD'])
            print("✅ All files unstaged")
        return True
    elif choice == '4':
        print("Add files manually with: git add <filename>")
        return True
    elif choice == '5':
        subprocess.run(['git', 'log', '--oneline', '-10'])
        return True
    elif choice == '6':
        return False
    else:
        print("Invalid choice")
        return True

def main():
    """Main function"""
    print("🔧 Git Cleanup Helper")
    print("=" * 25)
    print("Help manage complex Git status with many changes\n")

    # Analyze current status
    git_status = analyze_git_status()

    if not git_status:
        print("❌ Could not analyze Git status")
        return 1

    # Show staged changes
    show_staged_changes(git_status['staged'])

    # Suggest strategy
    suggest_commit_strategy(git_status)

    # Clean untracked files
    clean_untracked_files(git_status['untracked'])

    # Interactive menu
    print("\n" + "=" * 50)
    while True:
        if not quick_actions_menu():
            break

    print("\n🎉 Git cleanup session complete!")
    print("\nRemember:")
    print("- Review changes before committing")
    print("- Use meaningful commit messages")
    print("- Keep commits focused and atomic")

if __name__ == "__main__":
    sys.exit(main())
