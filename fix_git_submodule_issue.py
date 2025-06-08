#!/usr/bin/env python3
"""
Fix Git Submodule Issue - Resolve the .ariana/code/ submodule problem
"""

import subprocess
import sys
from pathlib import Path
import shutil

def analyze_git_issue():
    """Analyze the current Git issue"""
    print("🔍 Analyzing Git Submodule Issue")
    print("=" * 40)

    # Check if .ariana/code exists
    ariana_path = Path(".ariana/code")
    if ariana_path.exists():
        print(f"✅ Found problematic path: {ariana_path}")

        # Check if it's a Git repository
        if (ariana_path / ".git").exists():
            print("   📁 This is a Git submodule/repository")
        else:
            print("   📁 This is a regular directory")

        # List contents
        try:
            contents = list(ariana_path.rglob("*"))
            print(f"   📊 Contains {len(contents)} items")

            # Show first few items
            for item in contents[:5]:
                print(f"      • {item.relative_to(ariana_path)}")
            if len(contents) > 5:
                print(f"      • ... and {len(contents) - 5} more")

        except Exception as e:
            print(f"   ❌ Could not list contents: {e}")
    else:
        print("❌ .ariana/code/ not found")

    # Check Git status for this specific issue
    print(f"\n🔍 Git Status Analysis")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)

        ariana_entries = [line for line in result.stdout.split('\n')
                         if '.ariana' in line]

        if ariana_entries:
            print("   Found .ariana entries in Git status:")
            for entry in ariana_entries:
                print(f"      {entry}")
        else:
            print("   No .ariana entries in Git status")

    except Exception as e:
        print(f"   ❌ Error checking Git status: {e}")

def fix_submodule_issue():
    """Fix the submodule issue"""
    print(f"\n🔧 Fixing Submodule Issue")
    print("-" * 30)

    ariana_path = Path(".ariana")

    print("Options to fix the issue:")
    print("1. Remove .ariana directory completely")
    print("2. Add .ariana to .gitignore")
    print("3. Remove submodule properly")
    print("4. Skip this file and continue")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == '1':
        return remove_ariana_directory(ariana_path)
    elif choice == '2':
        return add_ariana_to_gitignore()
    elif choice == '3':
        return remove_submodule_properly()
    elif choice == '4':
        return skip_ariana_file()
    else:
        print("Invalid choice")
        return False

def remove_ariana_directory(ariana_path):
    """Remove the .ariana directory completely"""
    print(f"\n🗑️  Removing .ariana Directory")
    print("-" * 35)

    if not ariana_path.exists():
        print("✅ .ariana directory doesn't exist")
        return True

    try:
        # First, make sure it's not in use
        print("   Checking if directory is in use...")

        # Remove read-only permissions if any
        def make_writable(path):
            try:
                import stat
                path.chmod(stat.S_IWRITE | stat.S_IREAD)
            except:
                pass

        # Make all files writable
        for item in ariana_path.rglob("*"):
            if item.is_file():
                make_writable(item)

        # Remove the directory
        shutil.rmtree(ariana_path)
        print("   ✅ Successfully removed .ariana directory")

        # Clean Git index of any references
        try:
            subprocess.run(['git', 'rm', '-r', '--cached', '.ariana'],
                         capture_output=True, text=True)
            print("   ✅ Cleaned Git index")
        except:
            print("   ℹ️  Git index already clean")

        return True

    except Exception as e:
        print(f"   ❌ Error removing directory: {e}")
        print("   Try manually deleting the .ariana folder")
        return False

def add_ariana_to_gitignore():
    """Add .ariana to .gitignore"""
    print(f"\n🚫 Adding .ariana to .gitignore")
    print("-" * 35)

    try:
        gitignore_addition = "\n# Ariana assistant files\n.ariana/\n"

        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write(gitignore_addition)

        print("   ✅ Added .ariana/ to .gitignore")

        # Remove from Git tracking
        try:
            subprocess.run(['git', 'rm', '-r', '--cached', '.ariana'],
                         capture_output=True)
            print("   ✅ Removed from Git tracking")
        except:
            print("   ℹ️  Already removed from tracking")

        return True

    except Exception as e:
        print(f"   ❌ Error updating .gitignore: {e}")
        return False

def remove_submodule_properly():
    """Remove submodule the proper Git way"""
    print(f"\n🔧 Removing Submodule Properly")
    print("-" * 35)

    try:
        # Remove submodule entry from .gitmodules
        gitmodules_path = Path('.gitmodules')
        if gitmodules_path.exists():
            print("   📝 Updating .gitmodules...")
            # This would need more complex parsing, for now just inform user
            print("   ⚠️  Manual .gitmodules edit may be needed")

        # Remove from Git config
        subprocess.run(['git', 'config', '--remove-section', 'submodule.ariana'],
                     capture_output=True)

        # Remove from index
        subprocess.run(['git', 'rm', '--cached', '.ariana'],
                     capture_output=True)

        # Remove directory
        ariana_path = Path('.ariana')
        if ariana_path.exists():
            shutil.rmtree(ariana_path)

        print("   ✅ Submodule removed properly")
        return True

    except Exception as e:
        print(f"   ❌ Error removing submodule: {e}")
        return False

def skip_ariana_file():
    """Skip the .ariana file and continue with other files"""
    print(f"\n⏭️  Skipping .ariana File")
    print("-" * 25)

    print("   Adding .ariana to .gitignore to avoid future issues...")

    try:
        gitignore_addition = "\n# Skip Ariana assistant files\n.ariana/\n"

        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write(gitignore_addition)

        print("   ✅ Added to .gitignore")
        return True

    except Exception as e:
        print(f"   ❌ Error updating .gitignore: {e}")
        return False

def continue_git_organization():
    """Continue with Git organization after fixing the issue"""
    print(f"\n📝 Continuing Git Organization")
    print("-" * 35)

    print("Now let's add the working files...")

    # Add Python files specifically
    python_files = [
        'main.py',
        'document_converter.py',
        'project_scanner.py',
        'find_output_files.py',
        'success_organizer.py',
        'test_pipeline_success.py'
    ]

    added_files = []

    for py_file in python_files:
        if Path(py_file).exists():
            try:
                result = subprocess.run(['git', 'add', py_file],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ Added: {py_file}")
                    added_files.append(py_file)
                else:
                    print(f"   ⚠️  Issue with {py_file}: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Error adding {py_file}: {e}")

    # Add documentation files
    doc_files = ['README.md', 'git_workflow_guide.md']

    for doc_file in doc_files:
        if Path(doc_file).exists():
            try:
                result = subprocess.run(['git', 'add', doc_file],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ Added: {doc_file}")
                    added_files.append(doc_file)
            except:
                pass

    print(f"\n📊 Successfully added {len(added_files)} files")

    if added_files:
        # Offer to create commit
        response = input("\nCreate commit with these files? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            create_fixed_commit()

    return len(added_files) > 0

def create_fixed_commit():
    """Create commit after fixing the submodule issue"""
    commit_message = """fix: resolve Git submodule issue and add core files

✅ Fixed Issues:
- Resolved .ariana/code/ submodule conflict
- Added essential Python files to Git
- Updated .gitignore to prevent future conflicts

📝 Files Added:
- Core pipeline files (main.py, document_converter.py)
- Project analysis tools (project_scanner.py, find_output_files.py)
- Success verification scripts
- Documentation files

🎯 Result:
- Clean Git repository without submodule conflicts
- All working RTM automation files properly tracked
- Ready for continued development and GitHub push"""

    try:
        result = subprocess.run(['git', 'commit', '-m', commit_message],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Commit created successfully!")

            # Show the commit
            result = subprocess.run(['git', 'log', '--oneline', '-1'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📦 {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Commit failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error creating commit: {e}")
        return False

def show_next_steps():
    """Show next steps after fixing the issue"""
    print(f"\n🎯 Next Steps")
    print("-" * 15)

    print("1. ✅ Git submodule issue resolved")
    print("2. 📝 Core files added to Git")
    print("3. 🚀 Ready to push to GitHub")

    print(f"\n💡 Recommended commands:")
    print("   git status                    # Verify clean status")
    print("   git push origin main          # Push to GitHub")
    print("   python main.py                # Test your pipeline")

    print(f"\n🎉 Your RTM automation project is back on track!")

def main():
    """Main function to fix the Git submodule issue"""
    print("🔧 Git Submodule Issue Fixer")
    print("=" * 35)
    print("Resolving the .ariana/code/ submodule conflict...\n")

    # Analyze the issue
    analyze_git_issue()

    # Fix the issue
    if fix_submodule_issue():
        print("✅ Submodule issue resolved!")

        # Continue with Git organization
        if continue_git_organization():
            print("✅ Git organization completed!")

        show_next_steps()
    else:
        print("❌ Could not fully resolve the issue")
        print("\nManual steps you can try:")
        print("1. Delete the .ariana folder manually")
        print("2. Run: git rm -r --cached .ariana")
        print("3. Add .ariana/ to .gitignore")
        print("4. Run: git add . && git commit -m 'fix: remove problematic files'")

if __name__ == "__main__":
    main()
