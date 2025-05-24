import os
import shutil
import yaml
import sys
from pathlib import Path


def create_directory_structure():
    """Create a coherent directory structure for the project"""
    directories = [
        'src/core',
        'src/extractors',
        'src/utils',
        'src/modules',  # Added modules directory
        'config/filters',
        'config/secrets',
        'scripts',
        'input/docx',
        'input/external',
        'output/markdown',
        'output/json',
        'output/yaml',
        'output/rtm',
        'docs/guides',
        'docs/setup',
        'tests',     # Added tests directory
        'tools'
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}")
    
    return True


def move_files():
    """Move files to their appropriate locations"""
    # Dictionary mapping current file paths to new locations
    file_moves = {
        # Config files
        'config/paths.yaml': 'config/paths.yaml',
        'config/extend_headings.lua': 'config/filters/extend_headings.lua',
        
        # Code files - assuming these exist based on pipeline config
        'code/word_to_md.py': 'src/core/word_to_md.py',
        'code/extract_outline.py': 'src/extractors/extract_outline.py',
        'code/extract_rtm.py': 'src/extractors/extract_rtm.py',
        'code/md_to_json_yaml.py': 'src/core/md_to_json_yaml.py',
        'code/sync_outline_files.py': 'src/utils/sync_outline_files.py',
        
        # Module files - from external GitHub repo
        'src/modules/ascii_diagram.py': 'src/modules/ascii_diagram.py',
        'src/modules/markdown_lint.py': 'src/modules/markdown_lint.py',
        'src/modules/pandoc_integration.py': 'src/modules/pandoc_integration.py',
        
        # Test files
        'tests/test_pipeline.py': 'tests/test_pipeline.py',
        
        # Main files
        'run_pipeline.py': 'scripts/run_pipeline.py',
        'pipeline/commands.sh': 'scripts/commands.sh',
        'git_setup.md': 'docs/setup/git_setup.md',
        
        # Input file(s)
        'input/MASTER_1805_1144.docx': 'input/docx/MASTER_1805_1144.docx'
    }
    
    print("\nMoving files to new locations...")
    for src, dest in file_moves.items():
        if os.path.exists(src):
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Copy file to new location
            shutil.copy2(src, dest)
            print(f"  Moved: {src} -> {dest}")
        else:
            print(f"  Warning: Source file not found: {src}")
    
    # Create __init__.py files in Python package directories
    init_files = [
        'src/__init__.py',
        'src/core/__init__.py',
        'src/extractors/__init__.py',
        'src/utils/__init__.py',
        'src/modules/__init__.py',
        'tests/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# This file makes the directory a Python package\n')
        print(f"  Created: {init_file}")
    
    return True


def update_paths_config():
    """Update the paths.yaml configuration to reflect new folder structure"""
    config_path = 'config/paths.yaml'
    new_config_path = 'config/paths.yaml'
    
    if not os.path.exists(config_path):
        print(f"Error: Could not find config file at {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Update paths to reflect new structure
        updated_config = config.copy()
        
        # Update input/output paths
        if 'word_master' in updated_config:
            updated_config['word_master'] = "input/docx/MASTER_1805_1144.docx"
        if 'md_output' in updated_config:
            updated_config['md_output'] = "output/markdown/MASTER_1805_1144.md"
        if 'yaml_output' in updated_config:
            updated_config['yaml_output'] = "output/yaml/MASTER_1805_1144.yaml"
        if 'json_output' in updated_config:
            updated_config['json_output'] = "output/json/MASTER_1805_1144.json"
        if 'outline_yaml' in updated_config:
            updated_config['outline_yaml'] = "output/yaml/MASTER_outline.yaml"
        if 'rtm_yaml' in updated_config:
            updated_config['rtm_yaml'] = "output/rtm/RTM_QQQ.yaml"
        
        # Update pipeline steps to reflect new file locations
        if 'pipeline' in updated_config and 'steps' in updated_config['pipeline']:
            for i, step in enumerate(updated_config['pipeline']['steps']):
                if 'script' in step:
                    script_name = os.path.basename(step['script'])
                    if script_name == 'word_to_md.py':
                        updated_config['pipeline']['steps'][i]['script'] = "src/core/word_to_md.py"
                    elif script_name == 'extract_outline.py':
                        updated_config['pipeline']['steps'][i]['script'] = "src/extractors/extract_outline.py"
                    elif script_name == 'extract_rtm.py':
                        updated_config['pipeline']['steps'][i]['script'] = "src/extractors/extract_rtm.py"
                    elif script_name == 'md_to_json_yaml.py':
                        updated_config['pipeline']['steps'][i]['script'] = "src/core/md_to_json_yaml.py"
                    elif script_name == 'sync_outline_files.py':
                        updated_config['pipeline']['steps'][i]['script'] = "src/utils/sync_outline_files.py"
        
        # Update pandoc options
        if 'pandoc_options' in updated_config and 'lua_filter' in updated_config['pandoc_options']:
            updated_config['pandoc_options']['lua_filter'] = "config/filters/extend_headings.lua"
        
        # Save updated config
        with open(new_config_path, 'w') as file:
            yaml.dump(updated_config, file, default_flow_style=False, sort_keys=False)
        
        print(f"Updated configuration file: {new_config_path}")
        return True
    
    except Exception as e:
        print(f"Error updating config: {e}")
        return False


def update_script_imports():
    """Update import statements in Python files to reflect new structure"""
    # Define the files to update
    python_files = [
        'src/core/word_to_md.py',
        'src/extractors/extract_outline.py',
        'src/extractors/extract_rtm.py',
        'src/core/md_to_json_yaml.py',
        'src/utils/sync_outline_files.py',
        'scripts/run_pipeline.py'
    ]
    
    print("\nUpdating import statements in Python files...")
    for file_path in python_files:
        if not os.path.exists(file_path):
            print(f"  Warning: File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Add sys.path modification to allow imports from src directory
            if 'import sys' not in content:
                modified_content = "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n" + content
            else:
                # Add path append after the import sys line
                lines = content.split('\n')
                sys_import_idx = next((i for i, line in enumerate(lines) if 'import sys' in line), -1)
                if sys_import_idx >= 0:
                    lines.insert(sys_import_idx + 1, "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))")
                    modified_content = '\n'.join(lines)
                else:
                    modified_content = content
            
            with open(file_path, 'w') as file:
                file.write(modified_content)
            
            print(f"  Updated imports in: {file_path}")
        
        except Exception as e:
            print(f"  Error updating {file_path}: {e}")
    
    return True


def create_readme():
    """Create a README.md file for the repository"""
    readme_content = """# DOCX RTM Automation

A tool for extracting Requirements Traceability Matrix (RTM) from DOCX documents and converting them to various formats.

## Repository Structure

```
/DOCX_RTM_Automation
├── config/                # All configuration files
│   ├── paths.yaml         # Main configuration 
│   ├── filters/           # Pandoc Lua filters
│   └── secrets/           # For API keys (gitignored)
├── src/                   # All source code
│   ├── core/              # Core processing modules
│   ├── extractors/        # Document extraction modules
│   ├── utils/             # Utility functions
│   └── modules/           # Additional modules
├── scripts/               # Runner scripts
│   ├── run_pipeline.py    # Main pipeline runner
│   └── commands.sh        # Shell commands
├── input/                 # Input documents
│   ├── docx/              # Original Word documents
│   └── external/          # External input files
├── output/                # Generated outputs
│   ├── markdown/          # Markdown outputs
│   ├── json/              # JSON outputs
│   ├── yaml/              # YAML outputs
│   └── rtm/               # RTM specific outputs
├── docs/                  # Documentation
│   ├── guides/            # User guides
│   └── setup/             # Setup instructions
├── tests/                 # Unit tests
└── tools/                 # Additional tools
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
    
    with open('README.md', 'w') as file:
        file.write(readme_content)
    
    print("\nCreated README.md file")
    return True


def update_run_pipeline():
    """Update the run_pipeline.py script to handle new paths"""
    source_path = 'run_pipeline.py'
    dest_path = 'scripts/run_pipeline.py'
    
    if not os.path.exists(source_path) and os.path.exists(dest_path):
        print("run_pipeline.py already moved to scripts directory")
        source_path = dest_path
    
    try:
        with open(source_path, 'r') as file:
            content = file.read()
        
        # Update config file path
        modified_content = content.replace(
            "with open('config/paths.yaml', 'r') as file:",
            "with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'paths.yaml'), 'r') as file:"
        )
        
        with open(dest_path, 'w') as file:
            file.write(modified_content)
        
        print("Updated run_pipeline.py script to handle new directory structure")
        return True
    
    except Exception as e:
        print(f"Error updating run_pipeline.py: {e}")
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
    
    with open('run.py', 'w') as file:
        file.write(content)
    
    print("\nCreated root-level runner script: run.py")
    return True


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
    
    with open('run_tests.py', 'w') as file:
        file.write(content)
    
    print("\nCreated test runner script: run_tests.py")
    return True


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
    
    with open('requirements.txt', 'w') as file:
        file.write(content)
    
    print("\nCreated requirements.txt file")
    return True


def main():
    """Main refactoring function"""
    print("\n" + "="*50)
    print("DOCX RTM Automation Repository Refactoring")
    print("="*50 + "\n")
    
    # Create new directory structure
    create_directory_structure()
    
    # Copy files to new locations
    move_files()
    
    # Update paths in configuration
    update_paths_config()
    
    # Update Python imports
    update_script_imports()
    
    # Update run_pipeline.py
    update_run_pipeline()
    
    # Create README
    create_readme()
    
    # Create project runner
    create_project_runner()
    
    # Create test runner
    create_test_runner()
    
    # Create requirements file
    create_requirements_file()
    
    print("\n" + "="*50)
    print("Refactoring completed successfully!")
    print("="*50)
    print("\nTo start using the refactored repository:")
    print("1. Review the README.md file")
    print("2. Run the pipeline with: python run.py")
    print("3. Run tests with: python run_tests.py") 
    print("4. Check the new directory structure for correctness")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


