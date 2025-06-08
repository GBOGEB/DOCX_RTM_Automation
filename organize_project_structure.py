#!/usr/bin/env python3
"""
Project Structure Organizer - Refactor RTM system into proper directory structure
"""

import shutil
from pathlib import Path
import json
from datetime import datetime


def create_organized_structure():
    """Create the organized directory structure."""

    # Define the target structure
    structure = {
        "src/": {
            "rtm/": ["Core RTM processing modules"],
            "parsers/": ["Document parsing and conversion"],
            "analyzers/": ["JSON and quality analysis"],
            "dashboard/": ["Web dashboard and UI"],
            "integrations/": ["Jenkins, Git, external systems"],
            "utils/": ["Utility functions and helpers"],
        },
        "scripts/": {
            "setup/": ["Installation and setup scripts"],
            "debug/": ["Debugging and testing scripts"],
            "quality/": ["Quality checks and linting"],
            "automation/": ["Batch files and automation"],
        },
        "config/": ["Configuration files"],
        "data/": {
            "input/": ["Input documents"],
            "output/": ["Generated outputs"],
            "templates/": ["Document templates"],
            "samples/": ["Sample files"],
        },
        "docs/": ["Documentation and guides"],
        "tests/": ["Test files and test data"],
        ".github/": {"workflows/": ["GitHub Actions"], "hooks/": ["Git hooks"]},
    }

    print("🏗️ Creating Organized Project Structure")
    print("=" * 45)

    # Create directories
    for main_dir, subdirs in structure.items():
        main_path = Path(main_dir)
        main_path.mkdir(exist_ok=True)
        print(f"📁 Created: {main_dir}")

        if isinstance(subdirs, dict):
            for subdir, description in subdirs.items():
                sub_path = main_path / subdir
                sub_path.mkdir(exist_ok=True)
                print(
                    f"   📂 {subdir} - {description[0] if description else 'Subdirectory'}"
                )
        elif isinstance(subdirs, list):
            print(f"   📝 {subdirs[0]}")

    return structure


def categorize_files():
    """Categorize existing files for organization."""

    file_categories = {
        # Core RTM modules
        "src/rtm/": [
            "generate_rtm.py*",
            "rtm_pipeline.py",
            "rtm_workflow_manager*.py",
            "rtm_document_processor.py",
            "enhanced_requirement_parser.py",
            "Project Requirements.py",
            "start_building_rtm.py",
        ],
        # Document parsers
        "src/parsers/": [
            "*word_to_md*.py",
            "pandoc_converter.py",
            "exact_docx_to_md.py",
            "enhance_document_parsing.py",
            "document_processing_success.py",
            "extract_document_outline.py",
            "digital_twin_parser.py",
        ],
        # Analyzers
        "src/analyzers/": [
            "json_file_analyzer*.py",
            "*quality_check*.py",
            "analyze_config_file.py",
            "verify_*system*.py",
            "comprehensive_rtm_analyzer.py",
        ],
        # Dashboard and UI
        "src/dashboard/": [
            "rtm_web_dashboard.py",
            "rtm_dashboard.py",
            "extension_dashboard.py",
            "port_service_monitor*.py",
        ],
        # Integrations
        "src/integrations/": [
            "jenkins_rtm_integration.py",
            "git_*",
            "*precommit*",
            "lua_bridge.py",
            "create_example_requests.py",
        ],
        # Utilities
        "src/utils/": [
            "file_helpers*",
            "port_manager.py",
            "simple_git_commit.py",
            "install_*.py",
            "setup_*.py",
            "systematic_approach.py",
        ],
        # Setup scripts
        "scripts/setup/": [
            "install_*.sh",
            "install_*.bat",
            "setup_*.sh",
            "setup_*.bat",
            "get_started.py",
            "*dependencies*",
        ],
        # Debug scripts
        "scripts/debug/": [
            "debug_*.py",
            "test_*.py",
            "verify_*.py",
            "run_diagnostic*.py",
            "fix_*.py",
            "release_port.py",
        ],
        # Quality scripts
        "scripts/quality/": [
            "run_*quality*.py",
            "lint.sh",
            "fix_style*.bat",
            "run_code_quality_checks.py",
        ],
        # Automation scripts
        "scripts/automation/": [
            "*.bat",
            "*.sh",
            "run_*.py",
            "process_*.py",
            "start_*.bat",
            "tools_menu.bat",
        ],
        # Configuration
        "config/": [
            "config.json",
            "extension_config.json",
            ".env",
            "keybindings.json",
            "pyproject.toml",
            "requirements*.txt",
            ".yamllint",
            ".pre-commit-config.yaml",
        ],
        # Input data
        "data/input/": ["sample_document.docx", "*.docx"],
        # Output data
        "data/output/": ["outline.json", "*_report.json", "*_success*.json"],
        # Documentation
        "docs/": [
            "*.md",
            "*.txt",
            "QUALITY_CHECKS.md",
            "Usage.txt",
            "requirements_implementation_map.md",
        ],
        # Tests
        "tests/": ["test_*.py", "*test*.json", "test_report.md"],
    }

    return file_categories


def move_files_to_structure(file_categories, dry_run=True):
    """Move files according to the categorization."""

    print(f"\n📦 File Organization {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print("=" * 50)

    moved_count = 0
    current_files = list(Path(".").glob("*"))

    for target_dir, patterns in file_categories.items():
        target_path = Path(target_dir)

        if not dry_run:
            target_path.mkdir(parents=True, exist_ok=True)

        files_for_this_dir = []

        for pattern in patterns:
            # Find matching files
            if "*" in pattern:
                matches = list(Path(".").glob(pattern))
            else:
                matches = [Path(pattern)] if Path(pattern).exists() else []

            for match in matches:
                if match.is_file() and match in current_files:
                    files_for_this_dir.append(match)

        if files_for_this_dir:
            print(f"\n📂 {target_dir}")
            for file_path in files_for_this_dir:
                print(f"   📄 {file_path.name}")

                if not dry_run:
                    try:
                        shutil.move(str(file_path), str(target_path / file_path.name))
                        moved_count += 1
                    except Exception as e:
                        print(f"      ❌ Error moving {file_path}: {e}")

    print(
        f"\n📊 Summary: {moved_count} files {'would be moved' if dry_run else 'moved'}"
    )
    return moved_count


def create_new_main_files():
    """Create new organized main files."""

    # Create new main.py
    main_content = '''#!/usr/bin/env python3
"""
RTM Automation System - Main Entry Point
Organized project structure for enterprise-grade RTM automation
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from rtm.rtm_pipeline import RTMPipeline
from dashboard.rtm_web_dashboard import start_dashboard

def main():
    """Main entry point for RTM system."""
    print("🚀 RTM Automation System v2.0")
    print("=" * 35)
    print("Choose an option:")
    print("1. Process documents")
    print("2. Start web dashboard")
    print("3. Run quality checks")
    print("4. Exit")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        pipeline = RTMPipeline()
        pipeline.run()
    elif choice == "2":
        start_dashboard()
    elif choice == "3":
        from scripts.quality.run_deep_quality_scan import run_quality_scan
        run_quality_scan()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
'''

    with open("main_organized.py", "w", encoding="utf-8") as f:
        f.write(main_content)

    # Create README for new structure
    readme_content = """# RTM Automation System v2.0 - Organized Structure

## 🏗️ Project Structure

```
├── src/                    # Source code
│   ├── rtm/               # Core RTM processing
│   ├── parsers/           # Document parsing
│   ├── analyzers/         # Analysis tools
│   ├── dashboard/         # Web interface
│   ├── integrations/      # External systems
│   └── utils/             # Utilities
├── scripts/               # Automation scripts
│   ├── setup/            # Installation
│   ├── debug/            # Debugging
│   ├── quality/          # Quality checks
│   └── automation/       # Batch operations
├── config/               # Configuration files
├── data/                 # Data files
│   ├── input/           # Input documents
│   ├── output/          # Generated outputs
│   └── templates/       # Templates
├── docs/                # Documentation
├── tests/               # Test files
└── .github/             # GitHub workflows
```

## 🚀 Quick Start

```bash
# Run the organized system
python main_organized.py

# Or use specific components
python src/rtm/rtm_pipeline.py
python src/dashboard/rtm_web_dashboard.py
```

## ✅ Benefits of New Structure

- 📁 **Organized**: Files grouped by function
- 🔍 **Discoverable**: Easy to find components
- 🧪 **Testable**: Separated concerns
- 📦 **Maintainable**: Modular architecture
- 🚀 **Scalable**: Enterprise-ready structure
"""

    with open("README_ORGANIZED.md", "w", encoding="utf-8") as f:
        f.write(readme_content)


def generate_organization_report():
    """Generate a report of the organization process."""

    report = {
        "organization_report": {
            "timestamp": datetime.now().isoformat(),
            "system": "RTM Automation v2.0",
            "action": "Project Structure Organization",
            "benefits": [
                "Reduced root directory clutter (100+ files → organized structure)",
                "Improved maintainability through separation of concerns",
                "Better discoverability of components",
                "Enterprise-ready project structure",
                "Easier onboarding for new developers",
                "Simplified CI/CD integration",
            ],
            "structure_created": {
                "src/": "Core source code modules",
                "scripts/": "Automation and utility scripts",
                "config/": "Configuration files",
                "data/": "Input/output data",
                "docs/": "Documentation",
                "tests/": "Test files",
                ".github/": "GitHub workflows and hooks",
            },
            "recommendations": [
                "Run with dry_run=False to execute the organization",
                "Update import statements in affected files",
                "Update CI/CD paths to match new structure",
                "Consider creating package __init__.py files",
                "Update documentation references",
            ],
        }
    }

    with open("organization_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Main organization function."""

    print("🏗️ RTM Project Structure Organizer")
    print("=" * 45)
    print("Your current root directory has 100+ files!")
    print("This tool will organize them into a proper structure.")
    print()

    # Create structure
    create_organized_structure()

    # Categorize files
    file_categories = categorize_files()

    # Show what would be moved (dry run)
    print("\n🔍 ANALYSIS - What would be organized:")
    move_files_to_structure(file_categories, dry_run=True)

    # Create new main files
    create_new_main_files()

    # Generate report
    generate_organization_report()

    print("\n🎯 ORGANIZATION PLAN READY!")
    print("=" * 35)
    print("✅ Directory structure created")
    print("✅ File categorization analyzed")
    print("✅ New main files prepared")
    print("✅ Organization report generated")
    print()
    print("📋 To execute the organization:")
    print("   1. Review the categorization above")
    print("   2. Backup your current state")
    print("   3. Run: organize_project_structure.py --execute")
    print()
    print("🎊 This will transform your RTM system into")
    print("   an enterprise-grade, organized project!")

    return 0


if __name__ == "__main__":
    import sys

    if "--execute" in sys.argv:
        # Execute the actual move
        file_categories = categorize_files()
        move_files_to_structure(file_categories, dry_run=False)
        print("🎉 Project organization complete!")
    else:
        main()
