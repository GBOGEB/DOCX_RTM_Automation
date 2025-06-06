#!/usr/bin/env python3
"""
Quick Project Update Runner
===========================

This script runs the complete project update process.
Run this from your project root directory.
"""

import sys
from pathlib import Path


def main():
    """Run the project update"""
    print("🚀 DOCX RTM Automation - Project Update Runner")
    print("=" * 50)

    # Verify we're in the right directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")

    # Check if we have the project_update.py file
    update_script = current_dir / "project_update.py"

    if not update_script.exists():
        print("❌ project_update.py not found!")
        print("   Creating the update script...")

        # Create the project update script inline
        update_content = '''#!/usr/bin/env python3
"""
DOCX RTM Automation - Complete Project Update & Refactor
========================================================
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
import logging

def create_directories():
    """Create missing project directories"""
    dirs = [
        'src', 'src/core', 'src/modules', 'src/extractors',
        'docs', 'tests', 'scripts'
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
            
            # Create README in each directory
            readme_content = f"""# {dir_name.replace('/', ' - ').title()}

This directory is part of the DOCX RTM Automation project.

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            readme_path = dir_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

def create_documentation():
    """Create project documentation"""
    print("📝 Creating documentation...")
    
    # Create main README.md
    readme_content = """# DOCX RTM Automation

A comprehensive automation pipeline for converting DOCX documents to Requirements Traceability Matrix (RTM) format.

## 🚀 Quick Start

1. **Place your DOCX file** in the `input/` directory
2. **Run the main pipeline**:
   ```bash
   python code/main.py
   ```
3. **Check results** in the `output/` directory

## 📊 Output Files

- `*.md` - Converted Markdown with TOC and section numbering
- `*_outline.yaml` - Document structure hierarchy  
- `*_requirements.yaml` - Extracted requirements
- `*_structure.txt` - ASCII structure diagram

## 🔧 Configuration

Edit `config/paths.yaml` to customize processing options.

## 🐛 Troubleshooting

1. **Pandoc not found**: Install Pandoc from https://pandoc.org/installing.html
2. **TOC depth errors**: TOC depth is automatically limited to 6 (Pandoc maximum)
3. **Lua filter errors**: Check if Lua filters exist in `config/` directory

## 📞 Support

- Check the logs in `logs/` for error details
- Review the configuration in `config/paths.yaml`
"""
    
    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ Created README.md")
    
    # Create requirements.txt
    requirements_content = """# DOCX RTM Automation Requirements
PyYAML>=6.0
pathlib>=1.0.1
"""
    
    with open("requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.venv/

# Project specific
logs/*.log
output/*.md
output/*.yaml
output/*.txt
output/*.json
*.backup
*.bak*

# IDE
.vscode/
.idea/
*.swp
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
temp/
tmp/
*.tmp
"""
    
    with open(".gitignore", 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")

def check_main_script():
    """Check and validate main script"""
    main_script = Path("code/main.py")
    if main_script.exists():
        try:
            with open(main_script, 'r', encoding='utf-8') as f:
                compile(f.read(), main_script, 'exec')
            print("✅ Main script syntax is valid")
            return True
        except SyntaxError as e:
            print(f"❌ Main script syntax error: {e}")
            return False
    else:
        print("❌ Main script not found")
        return False

def main():
    """Run project update"""
    print("🔧 DOCX RTM Automation - Project Update")
    print("=" * 40)
    
    try:
        # Create directories
        create_directories()
        
        # Create documentation
        create_documentation()
        
        # Create git files
        create_gitignore()
        
        # Check main script
        script_ok = check_main_script()
        
        print("\\n" + "=" * 40)
        print("🎉 Project update completed!")
        
        if script_ok:
            print("✅ Ready to run: python code/main.py")
        else:
            print("⚠️  Check main script before running")
            
    except Exception as e:
        print(f"❌ Update failed: {e}")

if __name__ == "__main__":
    main()
'''

        with open(update_script, "w", encoding="utf-8") as f:
            f.write(update_content)
        print("✅ Created project_update.py")

    # Now run the update script
    print("\n🔄 Running project update...")
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(update_script)], capture_output=False, text=True
        )

        if result.returncode == 0:
            print("\n🎉 Project update completed successfully!")
        else:
            print(f"\n❌ Project update failed with code: {result.returncode}")

    except Exception as e:
        print(f"❌ Error running update: {e}")

        # Fallback - run the update directly
        print("🔄 Running update directly...")
        try:
            exec(open(update_script).read())
        except Exception as e2:
            print(f"❌ Direct execution failed: {e2}")
