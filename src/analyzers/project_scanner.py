"""
Project Scanner - RTM Automation Module
"""

#!/usr/bin/env python3
"""
Project Scanner - Analyze the RTM Automation project structure
"""

import os
from pathlib import Path
import json
from datetime import datetime

def scan_project_structure():
    """Scan the entire project directory structure"""
    project_root = Path(".")

    structure = {
        "scan_time": datetime.now().isoformat(),
        "root_path": str(project_root.resolve()),
        "directories": [],
        "python_files": [],
        "other_files": [],
        "extensions": {},
        "total_files": 0,
        "total_size": 0
    }

    print("Scanning project structure...")
    print(f"Root: {project_root.resolve()}")
    print("-" * 60)

    for item in project_root.rglob("*"):
        if item.is_dir():
            # Skip common directories we don't need
            if any(skip in item.name for skip in ['.git', '__pycache__', '.vscode', 'node_modules']):
                continue

            dir_info = {
                "name": item.name,
                "path": str(item.relative_to(project_root)),
                "full_path": str(item)
            }
            structure["directories"].append(dir_info)

        elif item.is_file():
            try:
                file_size = item.stat().st_size
                file_modified = datetime.fromtimestamp(item.stat().st_mtime)

                file_info = {
                    "name": item.name,
                    "path": str(item.relative_to(project_root)),
                    "full_path": str(item),
                    "size": file_size,
                    "modified": file_modified.isoformat(),
                    "extension": item.suffix.lower()
                }

                structure["total_files"] += 1
                structure["total_size"] += file_size

                # Count extensions
                ext = item.suffix.lower()
                if ext:
                    structure["extensions"][ext] = structure["extensions"].get(ext, 0) + 1
                else:
                    structure["extensions"]["no_extension"] = structure["extensions"].get("no_extension", 0) + 1

                # Categorize files
                if ext == ".py":
                    structure["python_files"].append(file_info)
                else:
                    structure["other_files"].append(file_info)

            except (OSError, PermissionError) as e:
                print(f"Could not access {item}: {e}")
                continue

    return structure

def analyze_python_files(structure):
    """Analyze Python files for imports and functions"""
    print("\nPython Files Analysis:")
    print("=" * 60)

    if not structure["python_files"]:
        print("No Python files found!")
        return

    for py_file in structure["python_files"]:
        print(f"\n📄 {py_file['name']}")
        print(f"   Path: {py_file['path']}")
        print(f"   Size: {py_file['size']:,} bytes")
        print(f"   Modified: {py_file['modified'][:19]}")

        # Try to analyze the file content
        try:
            file_path = Path(py_file["full_path"])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count lines
            lines = content.split('\n')
            print(f"   Lines: {len(lines)}")

            # Find imports
            imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
            if imports:
                print(f"   Imports: {len(imports)}")
                for imp in imports[:3]:  # Show first 3
                    print(f"      • {imp}")
                if len(imports) > 3:
                    print(f"      • ... and {len(imports) - 3} more")

            # Find function definitions
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            if functions:
                print(f"   Functions: {len(functions)}")
                for func in functions[:3]:  # Show first 3
                    func_name = func.split('(')[0].replace('def ', '')
                    print(f"      • {func_name}()")
                if len(functions) > 3:
                    print(f"      • ... and {len(functions) - 3} more")

            # Find classes
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            if classes:
                print(f"   Classes: {len(classes)}")
                for cls in classes:
                    cls_name = cls.split('(')[0].replace('class ', '').replace(':', '')
                    print(f"      • {cls_name}")

        except Exception as e:
            print(f"   ⚠️  Could not analyze content: {e}")

def display_project_summary(structure):
    """Display a summary of the project structure"""
    print("\n" + "=" * 60)
    print("PROJECT STRUCTURE SUMMARY")
    print("=" * 60)

    print(f"📁 Total Directories: {len(structure['directories'])}")
    print(f"📄 Total Files: {structure['total_files']}")
    print(f"📊 Total Size: {structure['total_size']:,} bytes ({structure['total_size']/1024/1024:.1f} MB)")

    print(f"\n🐍 Python Files: {len(structure['python_files'])}")
    print(f"📋 Other Files: {len(structure['other_files'])}")

    print("\nFile Extensions:")
    sorted_extensions = sorted(structure["extensions"].items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_extensions:
        if ext == "no_extension":
            print(f"   • (no extension): {count}")
        else:
            print(f"   • {ext}: {count}")

    print("\nDirectories:")
    if structure["directories"]:
        for directory in sorted(structure["directories"], key=lambda x: x["path"]):
            print(f"   📁 {directory['path']}/")
    else:
        print("   (No subdirectories found)")

def save_scan_results(structure):
    """Save scan results to JSON file"""
    output_file = "project_scan_results.json"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, default=str)
        print(f"\n💾 Scan results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save scan results: {e}")

def generate_git_commands():
    """Generate useful Git commands for this project"""
    print("\n" + "=" * 60)
    print("SUGGESTED GIT COMMANDS")
    print("=" * 60)

    print("\n1. Initialize Git repository:")
    print("   git init")

    print("\n2. Add all Python files:")
    print("   git add *.py")

    print("\n3. Add all files (be careful!):")
    print("   git add .")

    print("\n4. Create initial commit:")
    print('   git commit -m "Initial commit: RTM Automation project setup"')

    print("\n5. Create .gitignore file:")
    print("   # Run the create_gitignore() function or manually create")

    print("\n6. Connect to GitHub:")
    print("   git remote add origin https://github.com/yourusername/DOCX_RTM_Automation.git")
    print("   git branch -M main")
    print("   git push -u origin main")

def create_gitignore():
    """Create a .gitignore file for the project"""
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
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

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
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
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
.env.local
.env.production

# Large files
*.zip
*.tar.gz
*.rar
"""

    try:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ .gitignore file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Could not create .gitignore file: {e}")
        return False

def main():
    """Main function to run the project scanner"""
    print("RTM Automation Project Scanner")
    print("=" * 60)
    print("Analyzing project structure and preparing Git workflow...")

    # Scan project structure
    structure = scan_project_structure()

    # Display results
    display_project_summary(structure)
    analyze_python_files(structure)

    # Save results
    save_scan_results(structure)

    # Generate Git commands
    generate_git_commands()

    # Offer to create .gitignore
    print("\n" + "=" * 60)
    response = input("Create .gitignore file? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        create_gitignore()

    print("\n🎉 Project scan complete!")
    print("\nNext steps:")
    print("1. Review the scan results")
    print("2. Follow the Git workflow guide")
    print("3. Set up your GitHub repository")
    print("4. Start committing your code!")

if __name__ == "__main__":
    main()
