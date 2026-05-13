#!/usr/bin/env python3
"""
Quick Setup - Get your Git repository organized right now
"""

import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check current Git repository status"""
    print("🔍 Current Git Status")
    print("-" * 30)

    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ You're in a Git repository")

            # Show current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'],
                                         capture_output=True, text=True)
            if branch_result.returncode == 0:
                print(f"📍 Current branch: {branch_result.stdout.strip()}")

            # Show git status
            status_result = subprocess.run(['git', 'status', '--porcelain'],
                                         capture_output=True, text=True)
            if status_result.stdout.strip():
                print("📋 Files with changes:")
                for line in status_result.stdout.strip().split('\n'):
                    print(f"   {line}")
            else:
                print("✅ Working directory is clean")

            return True
        else:
            print("❌ Not in a Git repository")
            return False

    except Exception as e:
        print(f"❌ Error checking Git status: {e}")
        return False

def check_git_config():
    """Check Git configuration"""
    print("\n🔧 Git Configuration")
    print("-" * 25)

    try:
        name_result = subprocess.run(['git', 'config', '--global', 'user.name'],
                                   capture_output=True, text=True)
        email_result = subprocess.run(['git', 'config', '--global', 'user.email'],
                                    capture_output=True, text=True)

        if name_result.returncode == 0 and email_result.returncode == 0:
            name = name_result.stdout.strip()
            email = email_result.stdout.strip()

            if name == "Your Name" or email == "your.email@example.com":
                print("⚠️  You're using placeholder Git config!")
                print(f"   Name: {name}")
                print(f"   Email: {email}")
                print("\n🔧 Please update your Git config:")
                print('   git config --global user.name "Your Real Name"')
                print('   git config --global user.email "your.real.email@example.com"')
                return False
            else:
                print(f"✅ Git user: {name} <{email}>")
                return True
        else:
            print("❌ Git user not configured")
            return False

    except Exception as e:
        print(f"❌ Error checking Git config: {e}")
        return False

def list_current_files():
    """List current files in the project"""
    print("\n📁 Current Project Files")
    print("-" * 30)

    current_dir = Path(".")

    # Group files by type
    python_files = []
    doc_files = []
    other_files = []

    for file_path in current_dir.glob("*"):
        if file_path.is_file():
            if file_path.suffix == ".py":
                python_files.append(file_path.name)
            elif file_path.suffix in [".md", ".txt", ".rst"]:
                doc_files.append(file_path.name)
            else:
                other_files.append(file_path.name)

    if python_files:
        print("🐍 Python files:")
        for file in sorted(python_files):
            print(f"   • {file}")

    if doc_files:
        print("📄 Documentation files:")
        for file in sorted(doc_files):
            print(f"   • {file}")

    if other_files:
        print("📋 Other files:")
        for file in sorted(other_files):
            print(f"   • {file}")

def suggest_next_steps():
    """Suggest what to do next"""
    print("\n🎯 Suggested Next Steps")
    print("-" * 25)

    print("1. Fix Git configuration (if needed):")
    print('   git config --global user.name "Your Real Name"')
    print('   git config --global user.email "your.real.email@example.com"')

    print("\n2. Add files to Git:")
    print("   git add *.py          # Add all Python files")
    print("   git add *.md          # Add documentation")
    print("   git add .             # Add everything (be careful!)")

    print("\n3. Create a commit:")
    print('   git commit -m "Initial commit: RTM automation project"')

    print("\n4. Check what's in your commit:")
    print("   git log --oneline     # See commit history")
    print("   git show              # See last commit details")

    print("\n5. Set up GitHub remote:")
    print("   # First create repo on GitHub, then:")
    print("   git remote add origin https://github.com/yourusername/DOCX_RTM_Automation.git")
    print("   git push -u origin main")

def create_gitignore():
    """Create .gitignore if it doesn't exist"""
    gitignore_path = Path(".gitignore")

    if gitignore_path.exists():
        print("✅ .gitignore already exists")
        return True

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
output/
*.log
*.tmp
temp/
cache/

# Sensitive files
config.ini
secrets.json
.env
"""

    try:
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
        return True
    except Exception as e:
        print(f"❌ Could not create .gitignore: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RTM Automation - Quick Git Setup")
    print("=" * 45)
    print("Let's get your Git repository organized!\n")

    # Check current status
    git_ok = check_git_status()
    config_ok = check_git_config()

    # Show current files
    list_current_files()

    # Create .gitignore if needed
    print(f"\n📝 .gitignore Setup")
    print("-" * 20)
    create_gitignore()

    # Show next steps
    suggest_next_steps()

    print(f"\n📊 Setup Status:")
    print(f"   Git Repository: {'✅' if git_ok else '❌'}")
    print(f"   Git Config: {'✅' if config_ok else '⚠️'}")
    print(f"   .gitignore: ✅")

    if not config_ok:
        print(f"\n⚠️  Please fix your Git configuration before proceeding!")
    else:
        print(f"\n🎉 You're ready to start committing!")

if __name__ == "__main__":
    main()
