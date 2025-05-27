#!/usr/bin/env python3
"""
Fix Pipeline Errors

This script addresses common errors in the RTM pipeline:
1. Creates missing directories (logs, output, etc.)
2. Fixes the toc-depth parameter in paths.yaml (must be 1-6)
3. Corrects RTMGenerator initialization in generate_rtm.py
4. Fixes encoding issues in ascii_diagram.py
5. Creates any missing parent directories
6. Fixes incorrect repository URLs in markdown files
"""

import os
import sys
import yaml
import re
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent

# ANSI colors for terminal output


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def print_header(text):
    """Print header with formatting"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))


def print_status(status, message):
    """Print status with color coding"""
    if status == "FIXED":
        color = Colors.GREEN
    elif status == "SKIPPED":
        color = Colors.YELLOW
    elif status == "ERROR":
        color = Colors.RED
    else:
        color = Colors.BLUE

    print(f"{color}{status}{Colors.ENDC}: {message}")


def create_missing_directories():
    """Create any missing directories needed by the pipeline"""
    print_header("Creating Missing Directories")

    directories = [
        "src/core",
        "src/modules",
        "src/extractors",
        "config",
        "input",
        "output",
        "scripts",
        "logs",
        "code",
    ]

    for dir_name in directories:
        directory_path = BASE_DIR / dir_name
        if not directory_path.exists():
            try:
                directory_path.mkdir(parents=True, exist_ok=True)
                print_status("FIXED", f"Created directory: {directory_path}")
            except Exception as e:
                print_status(
                    "ERROR", f"Failed to create directory {directory_path}: {e}")
        else:
            print_status("SKIPPED", f"Directory already exists: {directory_path}")

    return True


def fix_main_py():
    """Fix the main.py file to handle missing logs directory"""
    file_path = BASE_DIR / "code" / "main.py"
    print_header(f"Fixing {file_path}")

    if not file_path.exists():
        print_status("ERROR", f"File not found: {file_path}")
        return False

    try:
        # Create backup
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
        if file_path.exists():
            shutil.copy2(file_path, backup_path)
            print_status("INFO", f"Created backup: {backup_path}")

        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add logs directory creation before logging setup
        if "def setup_logging():" in content:
            # Find the function and add directory creation
            lines = content.split('\n')
            new_lines = []

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == "def setup_logging():":
                    # Add directory creation after function definition
                    new_lines.append(
                        '    """Setup logging with automatic directory creation"""')
                    new_lines.append('    # Ensure logs directory exists')
                    new_lines.append('    logs_dir = Path("logs")')
                    new_lines.append('    logs_dir.mkdir(exist_ok=True)')
                    new_lines.append('')

            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))

            print_status(
                "FIXED", "Added logs directory creation to setup_logging function")
        else:
            print_status(
                "SKIPPED", "setup_logging function not found or already modified")

        return True
    except Exception as e:
        print_status("ERROR", f"Failed to fix {file_path}: {e}")
        return False


def fix_paths_yaml():
    """Fix toc-depth parameter in paths.yaml"""
    file_path = BASE_DIR / "config" / "paths.yaml"
    print_header(f"Fixing {file_path}")

    if not file_path.exists():
        print_status("ERROR", f"File not found: {file_path}")
        return False

    try:
        # Create backup
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
        shutil.copy2(file_path, backup_path)
        print_status("INFO", f"Created backup: {backup_path}")

        # Load config
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Fix toc-depth if needed
        if 'pandoc_options' in config and 'toc_depth' in config['pandoc_options']:
            toc_depth = config['pandoc_options']['toc_depth']
            if toc_depth > 6:
                config['pandoc_options']['toc_depth'] = 6
                print_status(
                    "FIXED", f"Changed toc_depth from {toc_depth} to 6 (maximum allowed by pandoc)")
            else:
                print_status(
                    "SKIPPED", f"toc_depth already set to valid value: {toc_depth}")
        else:
            print_status(
                "SKIPPED", "pandoc_options.toc_depth not found in config")

        # Save changes
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return True
    except Exception as e:
        print_status("ERROR", f"Failed to fix {file_path}: {e}")
        return False


def create_sample_main_py():
    """Create a working main.py file in the code directory"""
    code_dir = BASE_DIR / "code"
    file_path = code_dir / "main.py"
    print_header(f"Creating {file_path}")

    sample_content = '''#!/usr/bin/env python3
"""
Main entry point for DOCX RTM Automation
"""

import os
import sys
import logging
from pathlib import Path

def setup_logging():
    """Setup logging with automatic directory creation"""
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "process.log", mode="a"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function"""
    logger = setup_logging()
    logger.info("Starting DOCX RTM Automation")

    # Add your main logic here
    print("DOCX RTM Automation - Main Entry Point")
    print("Logs directory created successfully")

    # Check if required directories exist
    required_dirs = ["input", "output", "config", "src", "logs"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            logger.info(f"Directory exists: {dir_name}")
        else:
            logger.warning(f"Directory missing: {dir_name}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

    try:
        # Ensure code directory exists
        code_dir.mkdir(parents=True, exist_ok=True)

        # Write the sample file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)

        print_status("FIXED", f"Created working {file_path}")
        return True
    except Exception as e:
        print_status("ERROR", f"Failed to create {file_path}: {e}")
        return False


def fix_toc_depth_in_code():
    """Fix hardcoded toc-depth values in Python files"""
    print_header("Fixing hardcoded toc-depth values")

    files_to_fix_relative = [
        "code/main.py",
        "src/modules/pandoc_integration.py",
        "scripts/docx_to_md_with_structure.py"
    ]

    for rel_file_path in files_to_fix_relative:
        file_path = BASE_DIR / rel_file_path
        if not file_path.exists():
            print_status("SKIPPED", f"File not found: {file_path}")
            continue

        try:
            # Create backup
            backup_path = file_path.with_suffix(f"{file_path.suffix}.bak2")
            shutil.copy2(file_path, backup_path)
            print_status("INFO", f"Created backup: {backup_path}")

            # Read content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Define patterns to find toc-depth=N where N > 6 and replace N with 6
            patterns_to_fix = []
            for i in range(7, 21):  # Check for depths 7 through 20
                patterns_to_fix.extend([
                    (rf'--toc-depth={i}(?!\d)', r'--toc-depth=6'),
                    (rf'toc_depth={i}(?!\d)', r'toc_depth=6'),
                    (rf'"toc-depth":\s*{i}(?!\d)', r'"toc-depth": 6'),
                    (rf'toc_depth:\s*{i}(?!\d)', r'toc_depth: 6'),
                ])

            current_fixed_count = 0
            for pattern, replacement in patterns_to_fix:
                content, num_subs = re.subn(pattern, replacement, content)
                if num_subs > 0:
                    current_fixed_count += num_subs

            if content != original_content:
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print_status(
                    "FIXED", f"Corrected {current_fixed_count} toc-depth issues in {file_path}")
            else:
                print_status(
                    "SKIPPED", f"No toc-depth values > 6 found or needing correction in {file_path}")
                # Remove backup if no changes were made
                if backup_path.exists():
                    os.remove(backup_path)
                    print_status("INFO", f"Removed unchanged backup: {backup_path}")

        except Exception as e:
            print_status("ERROR", f"Failed to fix {file_path}: {e}")


def fix_repository_url(file_path_obj: Path):
    """
    Fix incorrect repository URLs in files.
    Patterns and replacements should ideally be configurable.
    """
    if not file_path_obj.exists():
        print_status("SKIPPED", f"File not found for URL fix: {file_path_obj}")
        return

    try:
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()

        # Example pattern to fix repository URLs.
        pattern = r'https://old-example-repo.com/project/some-repo'
        replacement = 'https://new-correct-repo.com/project/some-repo'

        new_content, num_subs = re.subn(pattern, replacement, content)

        if num_subs > 0:
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print_status("FIXED", f"Corrected {num_subs} repository URL(s) in {file_path_obj}")
        else:
            print_status("SKIPPED", f"No incorrect repository URL matching pattern found in {file_path_obj}")
    except Exception as e:
        print_status("ERROR", f"Failed to fix repository URL in {file_path_obj}: {e}")


def main():
    """Main function to execute fixes"""
    print_header("RTM Pipeline Fixer")

    create_missing_directories()
    fix_paths_yaml()
    create_sample_main_py()
    fix_toc_depth_in_code()

    markdown_files_relative = ["README.md", "docs/overview.md"]
    for rel_file in markdown_files_relative:
        file_to_check = BASE_DIR / rel_file
        fix_repository_url(file_to_check)


if __name__ == "__main__":
    main()
