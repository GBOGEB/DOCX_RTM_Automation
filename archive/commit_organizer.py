#!/usr/bin/env python3
"""
Commit Organizer - Create organized commits from complex changes
"""

import subprocess
import sys
from pathlib import Path

def create_project_reorganization_commit():
    """Create a commit for the major project reorganization"""

    commit_message = """feat: major project reorganization and structure improvement

🏗️ Project Structure:
- Moved all scripts to organized directory structure (scripts/)
- Relocated source files to proper src/ hierarchy
- Created dedicated directories: parsers/, analyzers/, dashboard/
- Established proper Python module structure with __init__.py files

📁 Directory Organization:
- scripts/automation/ - Automation and batch scripts
- scripts/debug/ - Debug and troubleshooting tools
- scripts/quality/ - Code quality and linting tools
- scripts/setup/ - Installation and setup scripts
- src/rtm/ - Core RTM processing modules
- src/parsers/ - Document parsing functionality
- src/analyzers/ - Code and quality analysis tools
- src/dashboard/ - Web dashboard components
- src/integrations/ - External service integrations
- docs/ - Comprehensive documentation

🔧 Technical Improvements:
- Fixed import paths and module references
- Updated configuration files (pyproject.toml, .yamllint)
- Improved dependency management
- Enhanced error handling and logging
- Added comprehensive backup system

📚 Documentation:
- Reorganized all documentation into docs/
- Created comprehensive guides and references
- Added detailed code citations and commit summaries
- Improved quick start and usage instructions

This reorganization follows Python best practices and establishes
a maintainable, scalable project structure for future development."""

    return commit_message

def check_and_commit():
    """Check staged changes and create commit"""
    print("📋 Checking staged changes...")

    # Check if we have staged changes
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'],
                          capture_output=True)

    if result.returncode == 0:
        print("ℹ️  No staged changes found")
        print("\nTo stage your changes:")
        print("git add -A  # Add all changes")
        print("git add .   # Add current directory")
        return False

    # Show summary of staged changes
    result = subprocess.run(['git', 'diff', '--cached', '--name-status'],
                          capture_output=True, text=True)

    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        added = sum(1 for line in lines if line.startswith('A'))
        modified = sum(1 for line in lines if line.startswith('M'))
        deleted = sum(1 for line in lines if line.startswith('D'))
        renamed = sum(1 for line in lines if line.startswith('R'))

        print(f"📊 Staged changes summary:")
        print(f"   ✅ Added: {added}")
        print(f"   ✏️  Modified: {modified}")
        print(f"   🗑️  Deleted: {deleted}")
        print(f"   📝 Renamed: {renamed}")
        print(f"   📦 Total: {len(lines)}")

    # Get the commit message
    commit_message = create_project_reorganization_commit()

    print(f"\n📝 Commit Message Preview:")
    print("-" * 50)
    print(commit_message[:200] + "..." if len(commit_message) > 200 else commit_message)
    print("-" * 50)

    response = input(f"\nCreate commit with this message? (y/n): ").lower().strip()

    if response == 'y':
        try:
            # Create the commit
            result = subprocess.run(['git', 'commit', '-m', commit_message],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Commit created successfully!")

                # Show commit info
                result = subprocess.run(['git', 'log', '--oneline', '-1'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"📦 Commit: {result.stdout.strip()}")

                return True
            else:
                print(f"❌ Commit failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error creating commit: {e}")
            return False
    else:
        print("Commit cancelled")
        return False

def handle_unstaged_changes():
    """Help handle unstaged changes"""
    print(f"\n🔍 Checking unstaged changes...")

    # Check for unstaged changes
    result = subprocess.run(['git', 'diff', '--name-only'],
                          capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        unstaged_files = result.stdout.strip().split('\n')
        print(f"⚠️  Found {len(unstaged_files)} unstaged files")

        print(f"\nFirst few unstaged files:")
        for filename in unstaged_files[:10]:
            print(f"   • {filename}")
        if len(unstaged_files) > 10:
            print(f"   • ... and {len(unstaged_files) - 10} more")

        print(f"\nOptions for unstaged changes:")
        print("1. Stage all unstaged changes: git add -A")
        print("2. Stage specific files: git add <filename>")
        print("3. View changes: git diff")
        print("4. Stash changes: git stash")
        print("5. Discard changes: git checkout -- <filename>")

    else:
        print("✅ No unstaged changes")

def handle_untracked_files():
    """Help handle untracked files"""
    print(f"\n🔍 Checking untracked files...")

    # Get untracked files
    result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                          capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        untracked_files = result.stdout.strip().split('\n')
        print(f"📄 Found {len(untracked_files)} untracked files")

        # Categorize files
        important_files = []
        temp_files = []

        for filename in untracked_files:
            if any(pattern in filename.lower() for pattern in
                   ['.backup', '_backup', '.tmp', 'temp_', '__pycache__', '.pyc']):
                temp_files.append(filename)
            else:
                important_files.append(filename)

        if important_files:
            print(f"\n📋 Important untracked files:")
            for filename in important_files[:10]:
                print(f"   • {filename}")
            if len(important_files) > 10:
                print(f"   • ... and {len(important_files) - 10} more")

        if temp_files:
            print(f"\n🗑️  Temporary files (consider cleaning):")
            for filename in temp_files[:5]:
                print(f"   • {filename}")
            if len(temp_files) > 5:
                print(f"   • ... and {len(temp_files) - 5} more")

        print(f"\nTo handle untracked files:")
        print("1. Add important files: git add <filename>")
        print("2. Add to .gitignore: echo '<pattern>' >> .gitignore")
        print("3. Clean temp files: git clean -fd (careful!)")

    else:
        print("✅ No untracked files")

def main():
    """Main function"""
    print("📦 Commit Organizer")
    print("=" * 25)
    print("Create organized commits from your project reorganization\n")

    # Check Git status
    try:
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error checking Git status")
            return 1

    except Exception as e:
        print(f"❌ Error running Git commands: {e}")
        return 1

    # Create main reorganization commit
    print("🏗️  Step 1: Project Reorganization Commit")
    print("-" * 45)

    commit_success = check_and_commit()

    # Handle remaining changes
    if commit_success:
        print(f"\n🎉 Main reorganization commit created!")
        print("Now let's handle any remaining changes...\n")

    # Check for remaining work
    handle_unstaged_changes()
    handle_untracked_files()

    print(f"\n📚 Next Steps:")
    print("1. Review any remaining unstaged changes")
    print("2. Add important untracked files")
    print("3. Update .gitignore for temp files")
    print("4. Test your reorganized project")
    print("5. Push to GitHub: git push origin main")

    print(f"\n✅ Commit organization complete!")

if __name__ == "__main__":
    sys.exit(main())
