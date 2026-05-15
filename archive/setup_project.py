#!/usr/bin/env python3
"""
Setup Project - Initialize RTM Automation project with Git and GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_installation():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git is not properly configured")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        print("Please install Git from: https://git-scm.com/")
        return False

def configure_git():
    """Configure Git user settings"""
    print("\n📝 Git Configuration")
    print("-" * 30)

    try:
        name_result = subprocess.run(['git', 'config', '--global', 'user.name'],
                                   capture_output=True, text=True)
        email_result = subprocess.run(['git', 'config', '--global', 'user.email'],
                                    capture_output=True, text=True)

        current_name = name_result.stdout.strip() if name_result.returncode == 0 else ""
        current_email = email_result.stdout.strip() if email_result.returncode == 0 else ""

        if current_name and current_email:
            print(f"Current Git user: {current_name} <{current_email}>")
            response = input("Use current Git configuration? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True

        print("\nEnter your Git configuration:")
        name = input("Your name: ").strip()
        email = input("Your email: ").strip()

        if name and email:
            subprocess.run(['git', 'config', '--global', 'user.name', name])
            subprocess.run(['git', 'config', '--global', 'user.email', email])
            print(f"✅ Git configured for: {name} <{email}>")
            return True
        else:
            print("❌ Name and email are required")
            return False

    except Exception as e:
        print(f"❌ Error configuring Git: {e}")
        return False

def create_project_structure():
    """Create recommended project structure"""
    print("\n📁 Creating Project Structure")
    print("-" * 35)

    directories = [
        'output',
        'docs',
        'tests',
        'config',
        'pipeline',
        'utils'
    ]

    created = 0
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"   ✅ Created: {directory}/")
                created += 1
            except Exception as e:
                print(f"   ❌ Failed to create {directory}/: {e}")
        else:
            print(f"   ℹ️  Exists: {directory}/")

    if created > 0:
        print(f"✅ Created {created} new directories")
    else:
        print("ℹ️  All directories already exist")

    return True

def create_readme():
    """Create a basic README.md file"""
    readme_content = """# RTM Automation Project

Automated processing for RTM (Requirements Traceability Matrix) files.

## Features

- DOCX file processing
- RTM data extraction
- Automated report generation
- File analysis and categorization

## Quick Start

1. Install dependencies:
   ```bash
   pip install python-docx
   ```

2. Run the main pipeline:
   ```bash
   python main.py
   ```

3. Check output files:
   ```bash
   python find_output_files.py
   ```

## Project Structure

```
DOCX_RTM_Automation_v1.0/
├── pipeline/          # Processing pipeline modules
├── utils/            # Utility functions
├── config/           # Configuration files
├── output/           # Generated output files
├── docs/             # Documentation
└── tests/            # Test files
```

## Development

See `git_workflow_guide.md` for Git and GitHub workflow instructions.

## License

[Add your license information here]
"""

    try:
        if not Path('README.md').exists():
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print("✅ Created README.md")
            return True
        else:
            print("ℹ️  README.md already exists")
            return True
    except Exception as e:
        print(f"❌ Failed to create README.md: {e}")
        return False

def initialize_git_repo():
    """Initialize Git repository"""
    print("\n🔧 Initializing Git Repository")
    print("-" * 35)

    if Path('.git').exists():
        print("✅ Git repository already initialized")
        return True

    try:
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize Git repository: {e}")
        return False

def create_initial_commit():
    """Create initial commit"""
    print("\n📦 Creating Initial Commit")
    print("-" * 30)

    try:
        # Add all Python files
        subprocess.run(['git', 'add', '*.py'], check=True)

        # Add documentation files
        for pattern in ['*.md', '*.txt', '*.rst']:
            subprocess.run(['git', 'add', pattern], check=False)

        # Check if there are staged changes
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if result.returncode != 0:
            subprocess.run(['git', 'commit', '-m', 'Initial commit: RTM Automation project setup'], check=True)
            print("✅ Initial commit created")
            return True
        else:
            print("ℹ️  No files to commit")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create initial commit: {e}")
        return False

def setup_github_remote():
    """Setup GitHub remote repository"""
    print("\n🌐 GitHub Remote Setup")
    print("-" * 25)

    print("To connect to GitHub:")
    print("1. Create a new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Repository name: DOCX_RTM_Automation")
    print("   - Description: Automated RTM processing for DOCX files")
    print("   - Choose Public or Private")
    print("   - DON'T initialize with README (we have local files)")

    response = input("\nHave you created the GitHub repository? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Please create the GitHub repository first, then run this setup again.")
        return False

    github_url = input("Enter your GitHub repository URL: ").strip()
    if not github_url:
        print("❌ GitHub URL is required")
        return False

    try:
        subprocess.run(['git', 'remote', 'add', 'origin', github_url], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)

        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully connected to GitHub and pushed code")
            return True
        else:
            print(f"⚠️  Push to GitHub failed: {result.stderr}")
            print("You may need to authenticate with GitHub")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup GitHub remote: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 RTM Automation Project Setup")
    print("=" * 40)
    print("This script will help you set up Git and GitHub for your project.\n")

    steps = [
        ("Checking Git installation", check_git_installation),
        ("Configuring Git", configure_git),
        ("Creating project structure", create_project_structure),
        ("Creating README", create_readme),
        ("Initializing Git repository", initialize_git_repo),
        ("Creating initial commit", create_initial_commit),
    ]

    completed_steps = 0
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if step_function():
            completed_steps += 1
        else:
            print(f"⚠️  Step failed: {step_name}")
            response = input("Continue anyway? (y/n): ").lower().strip()
            if response not in ['y', 'yes']:
                break

    print(f"\n📊 Setup Summary: {completed_steps}/{len(steps)} steps completed")

    if completed_steps >= 4:
        print("\n🎉 Basic setup complete!")

        response = input("\nSetup GitHub remote now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            setup_github_remote()

        print("\n📚 Next Steps:")
        print("1. Review your project structure")
        print("2. Run: python project_scanner.py")
        print("3. Read: git_workflow_guide.md")
        print("4. Start coding and committing!")

    else:
        print("\n⚠️  Setup incomplete. Please resolve the issues and run again.")

if __name__ == "__main__":
    main()
