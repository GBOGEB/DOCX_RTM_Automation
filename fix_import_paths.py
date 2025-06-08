#!/usr/bin/env python3
"""
Fix Import Paths - Update import statements after project organization
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def find_python_files():
    """Find all Python files in the organized structure."""
    python_files = []

    # Search in all directories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                file_path = Path(root) / file
                python_files.append(file_path)

    return python_files

def create_import_mapping():
    """Create a mapping of old imports to new paths."""

    # Map old module names to their new locations
    import_mapping = {
        # Parser modules
        'enhanced_word_to_md': 'src.parsers.enhanced_word_to_md',
        'word_to_md_converter': 'src.parsers.word_to_md_converter',
        'pandoc_converter': 'src.parsers.pandoc_converter',
        'exact_docx_to_md': 'src.parsers.exact_docx_to_md',
        'document_processing_success': 'src.parsers.document_processing_success',
        'extract_document_outline': 'src.parsers.extract_document_outline',
        'digital_twin_parser': 'src.parsers.digital_twin_parser',
        'try_word_to_md': 'src.parsers.try_word_to_md',
        'find_word_to_md': 'src.parsers.find_word_to_md',

        # RTM modules
        'rtm_workflow_manager': 'src.rtm.rtm_workflow_manager',
        'rtm_document_processor': 'src.rtm.rtm_document_processor',
        'enhanced_requirement_parser': 'src.rtm.enhanced_requirement_parser',

        # Analyzer modules
        'json_file_analyzer_safe': 'src.analyzers.json_file_analyzer_safe',
        'simple_quality_check': 'src.analyzers.simple_quality_check',
        'analyze_config_file': 'src.analyzers.analyze_config_file',
        'quality_check_heavy': 'src.analyzers.quality_check_heavy',
        'quality_check_light': 'src.analyzers.quality_check_light',
        'quick_quality_check': 'src.analyzers.quick_quality_check',
        'run_code_quality_checks': 'src.analyzers.run_code_quality_checks',

        # Dashboard modules
        'rtm_web_dashboard': 'src.dashboard.rtm_web_dashboard',
        'rtm_dashboard': 'src.dashboard.rtm_dashboard',
        'port_service_monitor_fixed': 'src.dashboard.port_service_monitor_fixed',
        'extension_dashboard': 'src.dashboard.extension_dashboard',

        # Utility modules
        'port_manager': 'src.utils.port_manager',
        'simple_git_commit': 'src.utils.simple_git_commit',
        'systematic_approach': 'src.utils.systematic_approach',
        'install_dependencies': 'src.utils.install_dependencies',
        'install_pandas': 'src.utils.install_pandas',
        'install_pyyaml': 'src.utils.install_pyyaml',
        'setup_debug_ports': 'src.utils.setup_debug_ports',

        # Integration modules
        'jenkins_rtm_integration': 'src.integrations.jenkins_rtm_integration',
        'lua_bridge': 'src.integrations.lua_bridge',
        'create_example_requests': 'src.integrations.create_example_requests'
    }

    return import_mapping

def fix_imports_in_file(file_path, import_mapping):
    """Fix imports in a single Python file."""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix different import patterns
        for old_module, new_module in import_mapping.items():

            # Pattern 1: from module import something
            pattern1 = rf'from\s+{re.escape(old_module)}\s+import'
            replacement1 = f'from {new_module} import'
            if re.search(pattern1, content):
                content = re.sub(pattern1, replacement1, content)
                changes_made.append(f"Updated: from {old_module} import -> from {new_module} import")

            # Pattern 2: import module
            pattern2 = rf'import\s+{re.escape(old_module)}(?=\s|$)'
            replacement2 = f'import {new_module}'
            if re.search(pattern2, content):
                content = re.sub(pattern2, replacement2, content)
                changes_made.append(f"Updated: import {old_module} -> import {new_module}")

            # Pattern 3: from module import *
            pattern3 = rf'from\s+{re.escape(old_module)}\s+import\s+\*'
            replacement3 = f'from {new_module} import *'
            if re.search(pattern3, content):
                content = re.sub(pattern3, replacement3, content)
                changes_made.append(f"Updated: from {old_module} import * -> from {new_module} import *")

        # If changes were made, save the file
        if content != original_content:
            # Create backup
            backup_path = str(file_path) + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)

            # Save updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, changes_made

        return False, []

    except Exception as e:
        return False, [f"Error: {e}"]

def add_init_files():
    """Add __init__.py files to make directories proper Python packages."""

    init_dirs = [
        "src",
        "src/rtm",
        "src/parsers",
        "src/analyzers",
        "src/dashboard",
        "src/integrations",
        "src/utils",
        "scripts",
        "scripts/setup",
        "scripts/debug",
        "scripts/quality",
        "scripts/automation"
    ]

    created_count = 0

    for dir_path in init_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            init_file = dir_obj / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f'"""Package initialization for {dir_path}"""\n')
                print(f"   ✅ Created: {init_file}")
                created_count += 1
            else:
                print(f"   📄 Exists: {init_file}")

    return created_count

def create_path_helper():
    """Create a helper script to add src to Python path."""

    helper_content = '''#!/usr/bin/env python3
"""
Path Helper - Add src directory to Python path for organized imports
"""

import sys
from pathlib import Path

def setup_paths():
    """Add src directory to Python path."""
    src_path = Path(__file__).parent / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        return True
    return False

# Auto-setup when imported
if __name__ != "__main__":
    setup_paths()

def main():
    """Manual path setup."""
    success = setup_paths()
    if success:
        print("✅ Python path configured for organized imports")
        print(f"📁 Added: {Path(__file__).parent / 'src'}")
    else:
        print("❌ Could not configure Python path")

if __name__ == "__main__":
    main()
'''

    helper_path = Path("path_helper.py")
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(helper_content)

    print(f"📋 Created path helper: {helper_path}")
    return helper_path

def main():
    """Main import fixing function."""

    print("🔧 RTM Import Path Fixer")
    print("=" * 30)
    print("Fixing import statements after project organization...")

    # Find all Python files
    python_files = find_python_files()
    print(f"📊 Found {len(python_files)} Python files")

    # Create import mapping
    import_mapping = create_import_mapping()
    print(f"📋 Created mapping for {len(import_mapping)} modules")

    # Add __init__.py files
    print(f"\n📦 Adding package initialization files:")
    init_count = add_init_files()
    print(f"✅ Created {init_count} __init__.py files")

    # Create path helper
    print(f"\n🛤️ Creating path helper:")
    create_path_helper()

    # Fix imports in each file
    print(f"\n🔧 Fixing import statements:")

    fixed_count = 0
    total_changes = 0

    for file_path in python_files:
        if 'backup' in str(file_path):  # Skip backup files
            continue

        success, changes = fix_imports_in_file(file_path, import_mapping)

        if success:
            print(f"   ✅ Fixed: {file_path} ({len(changes)} changes)")
            fixed_count += 1
            total_changes += len(changes)

            # Show first few changes
            for change in changes[:2]:
                print(f"      • {change}")
            if len(changes) > 2:
                print(f"      • ... and {len(changes) - 2} more")
        elif changes:  # Had errors
            print(f"   ❌ Error: {file_path}")
            for error in changes:
                print(f"      • {error}")

    # Summary
    print(f"\n📊 IMPORT FIX SUMMARY:")
    print("=" * 25)
    print(f"   📄 Files processed: {len(python_files)}")
    print(f"   ✅ Files fixed: {fixed_count}")
    print(f"   🔧 Total changes: {total_changes}")
    print(f"   📦 Package files: {init_count}")

    if fixed_count > 0:
        print(f"\n🎯 NEXT STEPS:")
        print("1. Test your organized modules:")
        print("   python -c \"import path_helper; from src.rtm import rtm_pipeline\"")
        print("2. Run your RTM pipeline:")
        print("   python -c \"import path_helper; from src.rtm.rtm_pipeline import main; main()\"")
        print("3. Or create a new main.py that imports from organized structure")

    return 0

if __name__ == "__main__":
    main()
