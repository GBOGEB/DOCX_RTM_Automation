#!/usr/bin/env python3
"""
Post-Commit Cleanup - Organize remaining changes after successful reorganization commit
"""

import subprocess
import sys
from pathlib import Path

def check_current_status():
    """Check the current Git status after the reorganization commit"""
    print("🔍 Current Repository Status")
    print("=" * 40)

    try:
        # Show the latest commit
        result = subprocess.run(['git', 'log', '--oneline', '-1'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Latest commit: {result.stdout.strip()}")

        # Get detailed status
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error getting Git status")
            return False

        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        # Categorize remaining changes
        unstaged_changes = []
        untracked_files = []

        for line in lines:
            if not line.strip():
                continue

            status = line[:2]
            filename = line[3:]

            if status == '??':
                untracked_files.append(filename)
            elif status[1] != ' ':
                unstaged_changes.append((status, filename))

        print(f"📊 Remaining work:")
        print(f"   Unstaged changes: {len(unstaged_changes)}")
        print(f"   Untracked files: {len(untracked_files)}")

        return {
            'unstaged': unstaged_changes,
            'untracked': untracked_files
        }

    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def categorize_remaining_files(status_info):
    """Categorize remaining files by importance and type"""
    if not status_info:
        return None

    print(f"\n📋 File Analysis")
    print("-" * 20)

    # Categorize untracked files
    important_files = []
    backup_files = []
    temp_files = []
    script_files = []

    for filename in status_info['untracked']:
        lower_name = filename.lower()

        if any(pattern in lower_name for pattern in ['.backup', '_backup', '.bak', '.old']):
            backup_files.append(filename)
        elif any(pattern in lower_name for pattern in ['.tmp', 'temp_', '__pycache__', '.pyc', '.log']):
            temp_files.append(filename)
        elif filename.endswith('.py'):
            script_files.append(filename)
        elif filename.endswith(('.md', '.txt', '.bat', '.sh')):
            important_files.append(filename)
        else:
            important_files.append(filename)

    categories = {
        'scripts': script_files,
        'documentation': [f for f in important_files if f.endswith(('.md', '.txt'))],
        'automation': [f for f in important_files if f.endswith(('.bat', '.sh'))],
        'other_important': [f for f in important_files if not f.endswith(('.md', '.txt', '.bat', '.sh'))],
        'backups': backup_files,
        'temporary': temp_files
    }

    return categories

def display_file_categories(categories):
    """Display categorized files with recommendations"""
    print(f"\n📁 File Categories & Recommendations")
    print("=" * 45)

    if categories['scripts']:
        print(f"\n🐍 Python Scripts ({len(categories['scripts'])} files):")
        for file in categories['scripts'][:10]:
            print(f"   • {file}")
        if len(categories['scripts']) > 10:
            print(f"   • ... and {len(categories['scripts']) - 10} more")
        print("   📝 Action: Review and add important scripts")

    if categories['documentation']:
        print(f"\n📄 Documentation ({len(categories['documentation'])} files):")
        for file in categories['documentation'][:10]:
            print(f"   • {file}")
        if len(categories['documentation']) > 10:
            print(f"   • ... and {len(categories['documentation']) - 10} more")
        print("   📝 Action: Add important documentation files")

    if categories['automation']:
        print(f"\n⚙️  Automation Scripts ({len(categories['automation'])} files):")
        for file in categories['automation'][:5]:
            print(f"   • {file}")
        if len(categories['automation']) > 5:
            print(f"   • ... and {len(categories['automation']) - 5} more")
        print("   📝 Action: Add useful automation scripts")

    if categories['other_important']:
        print(f"\n📋 Other Important Files ({len(categories['other_important'])} files):")
        for file in categories['other_important'][:5]:
            print(f"   • {file}")
        if len(categories['other_important']) > 5:
            print(f"   • ... and {len(categories['other_important']) - 5} more")
        print("   📝 Action: Review and selectively add")

    if categories['backups']:
        print(f"\n🗃️  Backup Files ({len(categories['backups'])} files):")
        for file in categories['backups'][:5]:
            print(f"   • {file}")
        if len(categories['backups']) > 5:
            print(f"   • ... and {len(categories['backups']) - 5} more")
        print("   📝 Action: Consider cleaning up")

    if categories['temporary']:
        print(f"\n🗑️  Temporary Files ({len(categories['temporary'])} files):")
        for file in categories['temporary'][:5]:
            print(f"   • {file}")
        if len(categories['temporary']) > 5:
            print(f"   • ... and {len(categories['temporary']) - 5} more")
        print("   📝 Action: Clean up or add to .gitignore")

def suggest_cleanup_actions(categories):
    """Suggest specific cleanup actions"""
    print(f"\n🎯 Recommended Cleanup Actions")
    print("=" * 35)

    print("1. 📝 Add important new files:")
    important_count = len(categories['scripts']) + len(categories['documentation']) + len(categories['automation'])
    if important_count > 0:
        print(f"   git add *.py *.md *.bat  # Add scripts and docs")
        print(f"   git commit -m 'chore: add remaining project files'")
    else:
        print("   ✅ No critical files to add")

    print(f"\n2. 🧹 Clean up temporary files:")
    if categories['temporary'] or categories['backups']:
        print("   # Review files first, then:")
        print("   git clean -fd  # Remove untracked files (CAREFUL!)")
        print("   # Or manually delete specific files")
    else:
        print("   ✅ No temporary files to clean")

    print(f"\n3. ⚙️  Update .gitignore:")
    print("   # Add patterns for files you don't want to track:")
    print("   echo '*.backup' >> .gitignore")
    print("   echo 'temp_*' >> .gitignore")
    print("   echo '*.log' >> .gitignore")

    print(f"\n4. 🚀 Push to GitHub:")
    print("   git push origin main")

    print(f"\n5. 🧪 Test your reorganized project:")
    print("   python main.py")
    print("   python project_scanner.py")

def interactive_cleanup():
    """Interactive cleanup process"""
    print(f"\n⚡ Interactive Cleanup")
    print("-" * 25)

    actions = [
        ("Add important Python files", "git add *.py"),
        ("Add documentation files", "git add *.md README.md"),
        ("Add automation scripts", "git add *.bat *.sh"),
        ("Update .gitignore", "update_gitignore"),
        ("View current status", "git status"),
        ("Push to GitHub", "git push origin main"),
        ("Exit cleanup", "exit")
    ]

    while True:
        print(f"\nSelect an action:")
        for i, (desc, _) in enumerate(actions, 1):
            print(f"{i}. {desc}")

        choice = input(f"\nEnter choice (1-{len(actions)}): ").strip()

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(actions):
                desc, action = actions[choice_idx]

                if action == "exit":
                    break
                elif action == "update_gitignore":
                    update_gitignore()
                else:
                    print(f"\nExecuting: {action}")
                    try:
                        result = subprocess.run(action.split(),
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✅ {desc} completed")
                            if result.stdout.strip():
                                print(result.stdout.strip())
                        else:
                            print(f"❌ {desc} failed: {result.stderr}")
                    except Exception as e:
                        print(f"❌ Error executing {action}: {e}")
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a number")

def update_gitignore():
    """Update .gitignore with common patterns"""
    gitignore_additions = """
# Additional patterns for RTM project
*.backup
*.bak
*_backup*
temp_*/
*.tmp
*.log
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
.DS_Store
Thumbs.db
"""

    try:
        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
        print("✅ Updated .gitignore with additional patterns")
        return True
    except Exception as e:
        print(f"❌ Could not update .gitignore: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🧹 Post-Commit Cleanup Assistant")
    print("=" * 40)
    print("Let's organize your remaining files after the successful reorganization!\n")

    # Check current status
    status_info = check_current_status()

    if not status_info:
        print("❌ Could not analyze repository status")
        return 1

    if not status_info['unstaged'] and not status_info['untracked']:
        print("\n🎉 Repository is clean!")
        print("Your reorganization is complete. Consider pushing to GitHub:")
        print("git push origin main")
        return 0

    # Categorize remaining files
    categories = categorize_remaining_files(status_info)

    if categories:
        # Display categorized files
        display_file_categories(categories)

        # Show cleanup suggestions
        suggest_cleanup_actions(categories)

        # Offer interactive cleanup
        print(f"\n" + "=" * 50)
        response = input("Start interactive cleanup? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            interactive_cleanup()

    print(f"\n🎉 Cleanup session complete!")
    print("\nFinal recommendations:")
    print("1. Review any remaining files manually")
    print("2. Test your reorganized project")
    print("3. Push to GitHub when ready")
    print("4. Continue with your RTM automation development!")

if __name__ == "__main__":
    sys.exit(main())
