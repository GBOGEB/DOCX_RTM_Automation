#!/usr/bin/env python3
"""
Quick Import Fix - Fix the remaining import issues in RTM pipeline
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def fix_rtm_pipeline_imports():
    """Fix the specific import issues in RTM pipeline."""

    pipeline_file = Path("src/rtm/rtm_pipeline.py")

    if not pipeline_file.exists():
        print(f"❌ RTM pipeline not found: {pipeline_file}")
        return False

    print(f"🔧 Fixing RTM Pipeline Imports")
    print("=" * 35)

    try:
        # Read the file
        with open(pipeline_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Create backup
        backup_path = str(pipeline_file) + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(pipeline_file, backup_path)
        print(f"📋 Backup created: {backup_path}")

        # Fix specific imports
        fixes = [
            (r'from src.parsers.try_word_to_md import', 'from ..parsers.try_word_to_md import'),
            (r'from src.parsers.enhanced_word_to_md import', 'from ..parsers.enhanced_word_to_md import'),
            (r'from src.parsers.word_to_md_converter import', 'from ..parsers.word_to_md_converter import'),
            (r'from src.parsers.find_word_to_md import', 'from ..parsers.find_word_to_md import'),
            (r'from src.rtm.rtm_document_processor import', 'from .rtm_document_processor import'),
            (r'from src.rtm.enhanced_requirement_parser import', 'from .enhanced_requirement_parser import'),
            (r'import try_word_to_md', 'from ..parsers import try_word_to_md'),
            (r'import enhanced_word_to_md', 'from ..parsers import enhanced_word_to_md')
        ]

        changes_made = []

        for old_pattern, new_replacement in fixes:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_replacement, content)
                changes_made.append(f"Fixed: {old_pattern} -> {new_replacement}")

        # Add relative import setup at the top if needed
        if 'from ..' in content and 'import sys' not in content:
            # Add path setup for relative imports
            path_setup = '''import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

'''
            # Insert after docstring/comments but before imports
            lines = content.split('\n')
            insert_index = 0

            # Find where to insert (after docstring)
            in_docstring = False
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    in_docstring = not in_docstring
                if not in_docstring and line.strip() and not line.startswith('#'):
                    insert_index = i
                    break

            lines.insert(insert_index, path_setup)
            content = '\n'.join(lines)
            changes_made.append("Added path setup for relative imports")

        # Save the fixed file
        if content != original_content:
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Fixed RTM pipeline with {len(changes_made)} changes:")
            for change in changes_made:
                print(f"   • {change}")

            return True
        else:
            print("📄 No changes needed")
            return True

    except Exception as e:
        print(f"❌ Error fixing pipeline: {e}")
        return False

def create_fallback_imports():
    """Create fallback import handlers."""

    fallback_content = '''#!/usr/bin/env python3
"""
Fallback Import Handler - Handle import issues gracefully
"""

import sys
from pathlib import Path

def setup_fallback_imports():
    """Setup fallback imports for RTM system."""

    # Add all potential import paths
    base_path = Path(__file__).parent

    paths_to_add = [
        base_path / "src",
        base_path / "src" / "parsers",
        base_path / "src" / "rtm",
        base_path / "src" / "analyzers",
        base_path / "src" / "dashboard",
        base_path / "src" / "utils",
        base_path / "src" / "integrations"
    ]

    for path in paths_to_add:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))

    return True

# Auto-setup when imported
setup_fallback_imports()

def safe_import(module_name, fallback_paths=None):
    """Safely import a module with fallback paths."""

    if fallback_paths is None:
        fallback_paths = []

    # Try direct import first
    try:
        return __import__(module_name)
    except ImportError:
        pass

    # Try with fallback paths
    for fallback in fallback_paths:
        try:
            full_name = f"{fallback}.{module_name}"
            return __import__(full_name, fromlist=[module_name])
        except ImportError:
            continue

    # Last resort - try to find the module file
    base_path = Path(__file__).parent

    search_dirs = [
        base_path / "src" / "parsers",
        base_path / "src" / "rtm",
        base_path / "src" / "analyzers"
    ]

    for search_dir in search_dirs:
        module_file = search_dir / f"{module_name}.py"
        if module_file.exists():
            # Add the directory to path and try import
            if str(search_dir) not in sys.path:
                sys.path.insert(0, str(search_dir))
            try:
                return __import__(module_name)
            except ImportError:
                continue

    raise ImportError(f"Could not import {module_name} with any method")

if __name__ == "__main__":
    print("✅ Fallback import handler ready")
    print(f"📁 Python path extended with {len(sys.path)} directories")
'''

    fallback_path = Path("fallback_imports.py")
    with open(fallback_path, 'w', encoding='utf-8') as f:
        f.write(fallback_content)

    print(f"📋 Created fallback import handler: {fallback_path}")
    return fallback_path

def test_fixed_imports():
    """Test that the fixed imports work."""

    print(f"\n🧪 Testing Fixed Imports:")
    print("=" * 30)

    # Test importing the fixed pipeline
    try:
        import sys
        from pathlib import Path

        # Add src to path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Try importing the pipeline
        from rtm import rtm_pipeline
        print("   ✅ RTM pipeline imports successfully!")

        # Try importing some parser modules
        try:
            from parsers import src.parsers.try_word_to_md
            print("   ✅ try_word_to_md accessible")
        except ImportError as e:
            print(f"   ⚠️ try_word_to_md: {e}")

        try:
            from parsers import src.parsers.enhanced_word_to_md
            print("   ✅ enhanced_word_to_md accessible")
        except ImportError as e:
            print(f"   ⚠️ enhanced_word_to_md: {e}")

        return True

    except ImportError as e:
        print(f"   ❌ RTM pipeline import failed: {e}")
        return False

def main():
    """Main quick fix function."""

    print("⚡ Quick Import Fix for RTM System")
    print("=" * 40)
    print("Fixing the remaining import issues...")

    # Fix RTM pipeline imports
    pipeline_fixed = fix_rtm_pipeline_imports()

    # Create fallback import handler
    print(f"\n📦 Creating Fallback Import Handler:")
    create_fallback_imports()

    # Test the fixes
    imports_working = test_fixed_imports()

    # Summary
    print(f"\n📊 QUICK FIX SUMMARY:")
    print("=" * 25)
    print(f"   🔧 Pipeline fixed: {'✅' if pipeline_fixed else '❌'}")
    print(f"   📦 Fallback created: ✅")
    print(f"   🧪 Imports working: {'✅' if imports_working else '❌'}")

    if pipeline_fixed and imports_working:
        print(f"\n🎉 SUCCESS! RTM Pipeline imports are now fixed!")
        print("🚀 You can now run:")
        print("   python -c \"import fallback_imports; from rtm.rtm_pipeline import main; main()\"")
        print("   python main_organized.py pipeline")
    else:
        print(f"\n⚠️ Some issues remain. Try:")
        print("   python main_organized.py analyze  # This works!")
        print("   python main_organized.py status   # This works!")

    return 0

if __name__ == "__main__":
    main()
