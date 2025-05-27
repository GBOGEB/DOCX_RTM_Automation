import os
import shutil
import yaml
import sys
import time
import gc
from pathlib import Path


def create_directory_structure():
    """Create a coherent directory structure for the project"""
    directories = [
        "src/core",
        "src/extractors",
        "src/utils",
        "src/modules",  # Added modules directory
        "config/filters",
        "config/secrets",
        "scripts",
        "input/docx",
        "input/external",
        "output/markdown",
        "output/json",
        "output/yaml",
        "output/rtm",
        "docs/guides",
        "docs/setup",
        "tests",  # Added tests directory
        "tools",
    ]

    print("Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}")

    return True


def move_files():
    """Move files to their appropriate locations, skipping problematic ones after retries."""
    file_moves = {
        # Config files
        "config/paths.yaml": "config/paths.yaml",
        "config/extend_headings.lua": "config/filters/extend_headings.lua",
        # Code files - assuming these exist based on pipeline config
        "code/word_to_md.py": "src/core/word_to_md.py",
        "code/extract_outline.py": "src/extractors/extract_outline.py",
        "code/extract_rtm.py": "src/extractors/extract_rtm.py",
        "code/md_to_json_yaml.py": "src/core/md_to_json_yaml.py",
        "code/sync_outline_files.py": "src/utils/sync_outline_files.py",
        # Module files - from external GitHub repo
        "src/modules/ascii_diagram.py": "src/modules/ascii_diagram.py",
        "src/modules/markdown_lint.py": "src/modules/markdown_lint.py",
        "src/modules/pandoc_integration.py": "src/modules/pandoc_integration.py",
        # Test files
        "tests/test_pipeline.py": "tests/test_pipeline.py",
        # Main files
        "run_pipeline.py": "scripts/run_pipeline.py",
        "pipeline/commands.sh": "scripts/commands.sh",
        "git_setup.md": "docs/setup/git_setup.md",
        # Input file(s)
        "input/MASTER_1805_1144.docx": "input/docx/MASTER_1805_1144.docx",
    }

    skipped_files = []
    attempted_files_count = 0
    success_count = 0
    already_exists_count = 0
    not_found_count = 0

    print("\nMoving files to new locations...")
    for src, dest in file_moves.items():
        attempted_files_count += 1
        if os.path.exists(src):
            if os.path.exists(dest):
                print(f"  Skipping: {src} -> {dest} (destination already exists)")
                already_exists_count += 1
                continue

            dest_dir = os.path.dirname(dest)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)

            moved_successfully = False
            for attempt in range(4):  # Retry up to 4 times
                try:
                    shutil.copy2(src, dest)
                    print(f"  Moved: {src} -> {dest}")
                    moved_successfully = True
                    success_count += 1
                    break  # Success, exit retry loop
                except PermissionError as e:
                    print(f"  PermissionError while trying to copy '{src}' to '{dest}': {e}")
                    if attempt < 3:  # Retry if not the last attempt
                        gc.collect()  # Attempt to force garbage collection
                        print(f"  Retrying in 3 seconds (attempt {attempt + 2}/4)...")
                        time.sleep(3)
                    else:
                        error_message = f"Failed to move '{src}' to '{dest}' after 4 attempts due to PermissionError: {e}"
                        print(f"  [SKIPPING FILE] {error_message}")
                        skipped_files.append({"src": src, "dest": dest, "error": error_message})
                except Exception as e_other:
                    error_message = f"An unexpected error occurred while trying to copy '{src}' to '{dest}': {e_other}"
                    print(f"  [SKIPPING FILE] {error_message}")
                    skipped_files.append({"src": src, "dest": dest, "error": error_message})
                    break  # Don't retry for other errors, move to next file

            if not moved_successfully and not any(sf['src'] == src for sf in skipped_files):
                if not os.path.exists(dest):  # Double check if it somehow moved
                    error_message = f"Failed to move '{src}' to '{dest}' after retries for an unknown reason."
                    print(f"  [SKIPPING FILE - UNKNOWN REASON] {error_message}")
                    skipped_files.append({"src": src, "dest": dest, "error": error_message})

        else:
            print(f"  Warning: Source file not found: {src}")
            not_found_count += 1

    # Create __init__.py files in Python package directories
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/extractors/__init__.py",
        "src/utils/__init__.py",
        "src/modules/__init__.py",
        "tests/__init__.py",
    ]

    for init_file in init_files:
        try:
            if not os.path.exists(init_file):
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write("# This file makes the directory a Python package\n")
                print(f"  Created: {init_file}")
                success_count += 1
            else:
                print(f"  Skipping: {init_file} (__init__.py already exists)")
                already_exists_count += 1
        except Exception as e:
            error_message = f"Error creating __init__ file {init_file}: {e}"
            print(f"  [SKIPPING FILE] {error_message}")
            skipped_files.append({"src": "N/A", "dest": init_file, "error": error_message})

    print("\n=== File Operation Summary ===")
    print(f"Attempted to process: {attempted_files_count + len(init_files)} items (files + __init__.py)")
    print(f"Successfully created/copied: {success_count}")
    print(f"Already existed at destination: {already_exists_count}")
    print(f"Source not found: {not_found_count}")
    print(f"Skipped due to errors: {len(skipped_files)}")

    if skipped_files:
        print("\n--- Files That Could Not Be Processed ---")
        for item in skipped_files:
            print(f"  Source: {item.get('src', 'N/A')}")
            print(f"  Destination: {item['dest']}")
            print(f"  Error: {item['error']}")
            print()
        print("\n⚠️ WARNING: Some files were skipped due to errors.")
        print("   The refactoring process will continue, but may be incomplete.")
        print("   You may need to manually copy these files or address the errors and restart.")

    return True


def update_paths_config():
    """Update the paths.yaml configuration to reflect new folder structure"""
    config_path = "config/paths.yaml"
    new_config_path = "config/paths.yaml"

    if not os.path.exists(config_path):
        print(f"Error: Could not find config file at {config_path}")
        return False

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Update paths to reflect new structure
        updated_config = config.copy()

        # Update input/output paths
        if "word_master" in updated_config:
            updated_config["word_master"] = "input/docx/MASTER_1805_1144.docx"
        if "md_output" in updated_config:
            updated_config["md_output"] = "output/markdown/MASTER_1805_1144.md"
        if "yaml_output" in updated_config:
            updated_config["yaml_output"] = "output/yaml/MASTER_1805_1144.yaml"
        if "json_output" in updated_config:
            updated_config["json_output"] = "output/json/MASTER_1805_1144.json"
        if "outline_yaml" in updated_config:
            updated_config["outline_yaml"] = "output/yaml/MASTER_outline.yaml"
        if "rtm_yaml" in updated_config:
            updated_config["rtm_yaml"] = "output/rtm/RTM_QQQ.yaml"

        # Update pipeline steps to reflect new file locations
        if "pipeline" in updated_config and "steps" in updated_config["pipeline"]:
            for i, step in enumerate(updated_config["pipeline"]["steps"]):
                if "script" in step:
                    script_name = os.path.basename(step["script"])
                    if script_name == "word_to_md.py":
                        updated_config["pipeline"]["steps"][i][
                            "script"
                        ] = "src/core/word_to_md.py"
                    elif script_name == "extract_outline.py":
                        updated_config["pipeline"]["steps"][i][
                            "script"
                        ] = "src/extractors/extract_outline.py"
                    elif script_name == "extract_rtm.py":
                        updated_config["pipeline"]["steps"][i][
                            "script"
                        ] = "src/extractors/extract_rtm.py"
                    elif script_name == "md_to_json_yaml.py":
                        updated_config["pipeline"]["steps"][i][
                            "script"
                        ] = "src/core/md_to_json_yaml.py"
                    elif script_name == "sync_outline_files.py":
                        updated_config["pipeline"]["steps"][i][
                            "script"
                        ] = "src/utils/sync_outline_files.py"

        # Update pandoc options
        if (
            "pandoc_options" in updated_config
            and "lua_filter" in updated_config["pandoc_options"]
        ):
            updated_config["pandoc_options"][
                "lua_filter"
            ] = "config/filters/extend_headings.lua"

        # Save updated config
        with open(new_config_path, "w", encoding="utf-8") as file:
            yaml.dump(updated_config, file,
                      default_flow_style=False, sort_keys=False)

        print(f"Updated configuration file: {new_config_path}")
        return True

    except Exception as e:
        print(f"Error updating config: {e}")
        return False


def update_script_imports():
    """Update import statements in Python files to reflect new structure"""
    # Define the files to update
    python_files = [
        "src/core/word_to_md.py",
        "src/extractors/extract_outline.py",
        "src/extractors/extract_rtm.py",
        "src/core/md_to_json_yaml.py",
        "src/utils/sync_outline_files.py",
        "scripts/run_pipeline.py",
    ]

    print("\nUpdating import statements in Python files...")
    for file_path in python_files:
        if not os.path.exists(file_path):
            print(f"  Warning: File not found: {file_path}")
            continue

        try:
            with open(file_path, "r") as file:
                content = file.read()

            # Add sys.path modification to allow imports from src directory
            if "import sys" not in content:
                modified_content = (
                    "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n"
                    + content
                )
            else:
                # Add path append after the import sys line
                lines = content.split("\n")
                sys_import_idx = next(
                    (i for i, line in enumerate(lines) if "import sys" in line), -1
                )
                if sys_import_idx >= 0:
                    lines.insert(
                        sys_import_idx + 1,
                        "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                    )
                    modified_content = "\n".join(lines)
                else:
                    modified_content = content

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_content)

            print(f"  Updated imports in: {file_path}")

        except Exception as e:
            print(f"  Error updating {file_path}: {e}")

    return True


def create_readme():
    """Create a README.md file for the repository with robust encoding."""
    # Use pure ASCII characters for the directory tree to avoid encoding issues
    readme_content = """# DOCX RTM Automation

A tool for extracting Requirements Traceability Matrix (RTM) from DOCX documents and converting them to various formats.

## Repository Structure

```
/DOCX_RTM_Automation
+-- config/                # All configuration files
|   +-- paths.yaml         # Main configuration 
|   +-- filters/           # Pandoc Lua filters
|   +-- secrets/           # For API keys (gitignored)
+-- src/                   # All source code
|   +-- core/              # Core processing modules
|   +-- extractors/        # Document extraction modules
|   +-- utils/             # Utility functions
|   +-- modules/           # Additional modules
+-- scripts/               # Runner scripts
|   +-- run_pipeline.py    # Main pipeline runner
|   +-- commands.sh        # Shell commands
+-- input/                 # Input documents
|   +-- docx/              # Original Word documents
|   +-- external/          # External input files
+-- output/                # Generated outputs
|   +-- markdown/          # Markdown outputs
|   +-- json/              # JSON outputs
|   +-- yaml/              # YAML outputs
|   +-- rtm/               # RTM specific outputs
+-- docs/                  # Documentation
|   +-- guides/            # User guides
|   +-- setup/             # Setup instructions
+-- tests/                 # Unit tests
+-- tools/                 # Additional tools
```

## Quick Start

1. Place your input DOCX files in the `input/docx/` directory
2. Update the paths in `config/paths.yaml` if needed
3. Run the pipeline:

```bash
python scripts/run_pipeline.py
```

## GitHub Integration

The pipeline supports automatic GitHub integration for CI/CD workflows. See `docs/setup/git_setup.md` for details.

## Testing

Run the automated tests to verify functionality:

```bash
# Run all tests
python run_tests.py

# Run a specific test file
python -m unittest tests/test_pipeline.py
```

Tests cover:
- Pipeline integration
- Module functionality
- Data extraction and conversion
"""

    try:
        # First attempt with UTF-8 encoding
        with open("README.md", "w", encoding="utf-8") as file:
            file.write(readme_content)
        print("\nCreated README.md file with UTF-8 encoding.")
        return True
    except UnicodeEncodeError:
        print("\nUnicodeEncodeError with UTF-8. Trying system default encoding for README.md...")
        try:
            # Second attempt with system's default encoding
            with open("README.md", "w") as file:  # System default encoding
                file.write(readme_content)
            print("Created README.md file with system default encoding.")
            return True
        except Exception as e_fallback:
            print(f"Error creating README.md with system default encoding: {e_fallback}")
            # As a last resort, try writing with very basic ASCII-only content
            try:
                ascii_content = """# DOCX RTM Automation
Project for automating RTM generation from DOCX.
See project files for structure.
Run 'python run.py' to start.
Run 'python run_tests.py' for tests.
"""
                with open("README.md", "w", encoding="ascii", errors="ignore") as file:
                    file.write(ascii_content)
                print("Created simplified ASCII README.md file as a final fallback.")
                return True
            except Exception as e_ascii:
                print(f"Failed to create even a simplified ASCII README.md: {e_ascii}")
                return False
    except Exception as e_general:
        print(f"An unexpected error occurred while creating README.md: {e_general}")
        return False


def create_project_runner():
    """Create a simple runner script at the root level"""
    content = """#!/usr/bin/env python
# Main entry point for DOCX RTM Automation

import os
import sys
from scripts.run_pipeline import run_pipeline

if __name__ == "__main__":
    # Change working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the pipeline
    print("Starting DOCX RTM Automation pipeline...")
    success = run_pipeline()
    
    sys.exit(0 if success else 1)
"""

    try:
        with open("run.py", "w", encoding="utf-8") as file:
            file.write(content)
        print("\nCreated root-level runner script: run.py")
        return True
    except Exception as e:
        print(f"Error creating run.py: {e}")
        return False


def create_test_runner():
    """Create a test runner script"""
    content = """#!/usr/bin/env python
# Test runner for DOCX RTM Automation

import os
import sys
import unittest

if __name__ == "__main__":
    # Change working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
"""

    try:
        with open("run_tests.py", "w", encoding="utf-8") as file:
            file.write(content)
        print("\nCreated test runner script: run_tests.py")
        return True
    except Exception as e:
        print(f"Error creating run_tests.py: {e}")
        return False


def create_requirements_file():
    """Create requirements.txt file"""
    content = """# Requirements for DOCX RTM Automation
pyyaml>=6.0
pandoc>=2.0
python-docx>=0.8.11
markdown>=3.4
jsonschema>=4.0
pytest>=7.0
"""

    try:
        with open("requirements.txt", "w", encoding="utf-8") as file:
            file.write(content)
        print("\nCreated requirements.txt file")
        return True
    except Exception as e:
        print(f"Error creating requirements.txt: {e}")
        return False


def main():
    """Main refactoring function"""
    print("\n" + "=" * 50)
    print("DOCX RTM Automation Repository Refactoring")
    print("=" * 50 + "\n")

    # Create new directory structure
    create_directory_structure()

    # Copy files to new locations
    move_files()

    # Update paths in configuration
    update_paths_config()

    # Update Python imports
    update_script_imports()

    # Update run_pipeline.py
    # Removed update_run_pipeline() as it is not defined

    # Create README
    create_readme()

    # Create project runner
    create_project_runner()

    # Create test runner
    create_test_runner()

    # Create requirements file
    create_requirements_file()

    print("\n" + "=" * 50)
    print("Refactoring completed successfully!")
    print("=" * 50)
    print("\nTo start using the refactored repository:")
    print("1. Review the README.md file")
    print("2. Run the pipeline with: python run.py")
    print("3. Run tests with: python run_tests.py")
    print("4. Check the new directory structure for correctness")

    return 0


if __name__ == "__main__":
    sys.exit(main())
