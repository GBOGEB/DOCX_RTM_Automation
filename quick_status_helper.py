#!/usr/bin/env python3
"""
Quick Status Helper - Handle the remaining 257 unstaged and 108 untracked files
"""

import subprocess
import sys
from pathlib import Path

def quick_analysis():
    """Quick analysis of current Git status"""
    print("⚡ Quick Status Analysis")
    print("=" * 30)

    # Count unstaged files
    result = subprocess.run(['git', 'diff', '--name-only'],
                          capture_output=True, text=True)
    unstaged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

    # Count untracked files
    result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                          capture_output=True, text=True)
    untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

    print(f"📊 Status Summary:")
    print(f"   Unstaged files: {len(unstaged_files)}")
    print(f"   Untracked files: {len(untracked_files)}")
    print(f"   Total remaining: {len(unstaged_files) + len(untracked_files)}")

    return unstaged_files, untracked_files

def categorize_untracked_files(untracked_files):
    """Categorize untracked files by importance"""
    categories = {
        'essential': [],
        'scripts': [],
        'docs': [],
        'temp': [],
        'backups': []
    }

    for file in untracked_files:
        lower_file = file.lower()

        # Essential files
        if file in ['README.md', 'main.py', 'requirements.txt', 'setup.py']:
            categories['essential'].append(file)
        # Python scripts
        elif file.endswith('.py') and not any(x in lower_file for x in ['backup', 'temp', 'test']):
            categories['scripts'].append(file)
        # Documentation
        elif file.endswith(('.md', '.txt')) and not any(x in lower_file for x in ['backup', 'temp']):
            categories['docs'].append(file)
        # Backup files
        elif any(x in lower_file for x in ['backup', '.bak', '_backup', '.old']):
            categories['backups'].append(file)
        # Temporary files
        elif any(x in lower_file for x in ['temp', '.tmp', 'test', '__pycache__']):
            categories['temp'].append(file)
        else:
            # Other important files
            categories['essential'].append(file)

    return categories

def quick_action_menu():
    """Quick action menu for immediate decisions"""
    print("\n⚡ Quick Actions Menu")
    print("=" * 25)

    actions = [
        "1. Add all Python files (git add *.py)",
        "2. Add essential documentation (git add *.md)",
        "3. Add everything important (selective add)",
        "4. Clean up temp/backup files",
        "5. Update .gitignore",
        "6. View detailed status",
        "7. Push current state to GitHub",
        "8. Exit"
    ]

    for action in actions:
        print(action)

    return input("\nSelect action (1-8): ").strip()

def execute_action(choice, categories):
    """Execute the selected action"""
    try:
        if choice == '1':
            # Add all Python files
            result = subprocess.run(['git', 'add', '*.py'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Added all Python files")
            else:
                print(f"⚠️  Warning: {result.stderr}")
            return True

        elif choice == '2':
            # Add documentation files
            result = subprocess.run(['git', 'add', '*.md'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Added all Markdown files")
            else:
                print(f"⚠️  Warning: {result.stderr}")
            return True

        elif choice == '3':
            # Selective add of important files
            important_files = categories['essential'] + categories['scripts'] + categories['docs']
            if important_files:
                print(f"Adding {len(important_files)} important files...")
                for file in important_files:
                    subprocess.run(['git', 'add', file], capture_output=True)
                print("✅ Added important files")
            else:
                print("ℹ️  No important files to add")
            return True

        elif choice == '4':
            # Clean up temp/backup files
            temp_files = categories['temp'] + categories['backups']
            if temp_files:
                print(f"Found {len(temp_files)} temp/backup files:")
                for file in temp_files[:10]:
                    print(f"   • {file}")
                if len(temp_files) > 10:
                    print(f"   • ... and {len(temp_files) - 10} more")

                response = input("\nDelete these files? (y/n): ").lower().strip()
                if response == 'y':
                    for file in temp_files:
                        try:
                            Path(file).unlink()
                            print(f"Deleted: {file}")
                        except Exception as e:
                            print(f"Could not delete {file}: {e}")
                    print("✅ Cleanup complete")
            else:
                print("ℹ️  No temp/backup files found")
            return True

        elif choice == '5':
            # Update .gitignore
            update_gitignore()
            return True

        elif choice == '6':
            # View detailed status
            subprocess.run(['git', 'status'])
            return True

        elif choice == '7':
            # Push to GitHub
            print("Pushing to GitHub...")
            result = subprocess.run(['git', 'push', 'origin', 'main'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Successfully pushed to GitHub")
            else:
                print(f"❌ Push failed: {result.stderr}")
            return True

        elif choice == '8':
            return False

        else:
            print("Invalid choice")
            return True

    except Exception as e:
        print(f"❌ Error executing action: {e}")
        return True

def update_gitignore():
    """Update .gitignore with common patterns"""
    gitignore_additions = """
# RTM Project - Additional ignore patterns
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
*.unicode_backup
parsing_samples/
removed_files_backup/
temp_processing/
"""

    try:
        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
        print("✅ Updated .gitignore with additional patterns")
    except Exception as e:
        print(f"❌ Could not update .gitignore: {e}")

def create_summary_commit():
    """Create a commit for any staged changes"""
    # Check if there are staged changes
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'],
                          capture_output=True)

    if result.returncode != 0:  # There are staged changes
        print("\n📦 Creating commit for staged changes...")
        commit_msg = "chore: add remaining project files after reorganization"

        result = subprocess.run(['git', 'commit', '-m', commit_msg],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Commit created successfully")
            # Show the commit
            subprocess.run(['git', 'log', '--oneline', '-1'])
            return True
        else:
            print(f"❌ Commit failed: {result.stderr}")
            return False
    else:
        print("ℹ️  No staged changes to commit")
        return False

def main():
    """Main function for quick status helper"""
    print("⚡ Quick Status Helper")
    print("=" * 25)
    print("Let's quickly organize your remaining files!\n")

    # Quick analysis
    unstaged_files, untracked_files = quick_analysis()

    if not unstaged_files and not untracked_files:
        print("\n🎉 Repository is clean!")
        print("Consider pushing to GitHub: git push origin main")
        return 0

    # Categorize untracked files
    categories = categorize_untracked_files(untracked_files)

    print(f"\n📋 File Categories:")
    for category, files in categories.items():
        if files:
            print(f"   {category.title()}: {len(files)} files")

    # Interactive menu
    while True:
        choice = quick_action_menu()

        if not execute_action(choice, categories):
            break

        # Check if user wants to commit
        if choice in ['1', '2', '3']:
            response = input("\nCreate commit for staged changes? (y/n): ").lower().strip()
            if response == 'y':
                create_summary_commit()

    print("\n🎉 Quick cleanup complete!")
    print("\nNext steps:")
    print("1. Review any remaining files: git status")
    print("2. Test your project: python main.py")
    print("3. Push to GitHub: git push origin main")

if __name__ == "__main__":
    sys.exit(main())
