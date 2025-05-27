#!/usr/bin/env python3
"""
Repository Cleanup Tool

This script cleans up the repository by:
1. Removing empty files
2. Deleting empty directories
3. Organizing files into appropriate directories
4. Creating consistent directory structure
"""

import os
import sys
import shutil
from pathlib import Path
import re
import hashlib
import time


# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def print_header(text):
    """Print header with formatting"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))


def print_status(status, message, details=None):
    """Print status with color coding"""
    if status == "DONE":
        color = Colors.GREEN
    elif status == "SKIP":
        color = Colors.YELLOW
    elif status == "ERROR":
        color = Colors.RED
    else:
        color = Colors.BLUE

    print(f"{color}{status}{Colors.ENDC}: {message}")
    if details:
        print(f"     {details}")


def get_file_hash(file_path: Path):
    """Get hash of file contents"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except IOError as e:
        print_status("ERROR", f"Could not read file {file_path} for hashing: {e}")
        return None


def find_empty_files(root_dir: Path = Path(".")):
    """Find all empty files in the repository"""
    print_header("Finding Empty Files")
    empty_files = []
    skip_dirs = {".git", ".idea", ".vscode", "venv", "__pycache__", "external", "node_modules"}

    for file_path in root_dir.rglob("*"):
        if file_path.is_file():
            if any(part.startswith(".") or part in skip_dirs for part in file_path.parts):
                if not (file_path.name == ".gitkeep" and file_path.parent.name in {"input", "output"}):
                    continue

            try:
                if file_path.stat().st_size == 0:
                    empty_files.append(file_path)
                    print_status("FOUND", f"Empty file: {file_path}")
            except Exception as e:
                print_status("ERROR", f"Error checking {file_path}: {e}")

    if not empty_files:
        print_status("INFO", "No empty files found")
    return empty_files


def find_empty_directories(root_dir: Path = Path(".")):
    """Find all empty directories in the repository"""
    print_header("Finding Empty Directories")
    empty_dirs = []
    skip_dirs = {".git", ".idea", ".vscode", "venv", "__pycache__", "external", "node_modules"}

    for dir_path in sorted(list(root_dir.rglob("*/")), key=lambda p: len(p.parts), reverse=True):
        if not dir_path.is_dir():
            continue

        if any(part.startswith(".") or part in skip_dirs for part in dir_path.parts):
            continue

        if not any(dir_path.iterdir()):
            empty_dirs.append(dir_path)
            print_status("FOUND", f"Empty directory: {dir_path}")

    if not empty_dirs:
        print_status("INFO", "No empty directories found")
    return empty_dirs


def find_duplicate_files(root_dir: Path = Path(".")):
    """Find duplicate files based on content"""
    print_header("Finding Duplicate Files")
    file_hashes = {}
    duplicates = []
    skip_dirs = {".git", ".idea", ".vscode", "venv", "__pycache__", "external", "node_modules"}

    for file_path in root_dir.rglob("*"):
        if file_path.is_file():
            if any(part.startswith(".") or part in skip_dirs for part in file_path.parts):
                if file_path.name != ".gitkeep":
                     continue

            file_hash = get_file_hash(file_path)
            if file_hash:
                if file_hash in file_hashes:
                    duplicates.append((file_path, file_hashes[file_hash]))
                    print_status(
                        "FOUND",
                        f"Duplicate: {file_path}",
                        f"Same as: {file_hashes[file_hash]}",
                    )
                else:
                    file_hashes[file_hash] = file_path

    if not duplicates:
        print_status("INFO", "No duplicate files found")
    return duplicates


def create_directory_structure():
    """Create standard directory structure for the project"""
    print_header("Creating Directory Structure")

    directories = [
        Path("src/core"),
        Path("src/modules"),
        Path("src/extractors"),
        Path("src/utils"),
        Path("config"),
        Path("input"),
        Path("output/markdown"),
        Path("output/json"),
        Path("output/yaml"),
        Path("output/rtm"),
        Path("scripts"),
        Path("docs"),
        Path("tests"),
        Path("external"),
    ]

    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print_status("DONE", f"Ensured directory exists: {directory}")
        except Exception as e:
            print_status("ERROR", f"Failed to create {directory}: {e}")

    init_dirs = [Path("src"), Path("src/core"), Path("src/modules"),
                 Path("src/extractors"), Path("src/utils")]

    for directory in init_dirs:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            try:
                with open(init_file, "w", encoding="utf-8") as f:
                    module_name = directory.name
                    f.write(
                        f'"""\n{module_name.capitalize()} module for DOCX RTM Automation.\n"""\n'
                    )
                print_status("DONE", f"Created __init__.py in {directory}")
            except IOError as e:
                print_status(
                    "ERROR", f"Failed to create __init__.py in {directory}: {e}"
                )


def organize_files(root_dir: Path = Path(".")):
    """Organize files into appropriate directories based on patterns"""
    print_header("Organizing Files")

    file_patterns = [
        (r"clean_.*\.py$", Path("scripts")),
        (r"fix_.*\.py$", Path("scripts")),
        (r"check_.*\.py$", Path("scripts")),
        (r"clone_.*\.py$", Path("scripts")),
        (r"generate_rtm\.py$", Path("src/core")),
        (r".*_outline\.py$", Path("src/extractors")),
        (r"test_.*\.py$", Path("tests")),
        (r".*\.md$", Path("docs"), ["README.md", "CONTRIBUTING.md"]),
        (r".*\.ya?ml$", Path("config"), ["docker-compose.yml"]),
        (r".*\.json$", Path("config"), ["package.json", "tsconfig.json"]),
    ]

    root_files_exact = {
        "run_pipeline.py",
        "README.md",
        "requirements.txt",
        "setup.py",
        "run_tests.py",
        "clean_repository.py",
        ".gitignore",
        "LICENSE",
        "CONTRIBUTING.md",
        "docker-compose.yml",
        "package.json",
        "tsconfig.json"
    }

    ignore_files = {".gitkeep"}

    files_to_consider = [f for f in root_dir.iterdir() if f.is_file()]

    for file_path in files_to_consider:
        if file_path.name in ignore_files:
            continue

        if file_path.name in root_files_exact:
            print_status("SKIP", f"Keeping {file_path.name} in root directory")
            continue

        moved = False
        for pattern, target_dir_relative, *exclusions in file_patterns:
            exclusions = exclusions[0] if exclusions else []
            if file_path.name in exclusions:
                continue

            if re.search(pattern, file_path.name, re.IGNORECASE):
                target_dir = root_dir / target_dir_relative
                target_path = target_dir / file_path.name

                if target_path.exists():
                    print_status("SKIP", f"{file_path.name} already exists in {target_dir_relative}")
                else:
                    print_status("SUGGEST", f"Move {file_path.name} to {target_dir_relative}/")
                moved = True
                break

        if not moved and file_path.suffix == ".py":
            default_target_dir = root_dir / "src/modules"
            target_path = default_target_dir / file_path.name
            if target_path.exists():
                print_status("SKIP", f"{file_path.name} already exists in src/modules")
            else:
                print_status("SUGGEST", f"Move {file_path.name} to src/modules/")


def clean_empty_files(files: list[Path], simulate=True):
    """Delete empty files"""
    print_header("Cleaning Empty Files")

    if not files:
        print_status("SKIP", "No empty files to remove")
        return

    for file_path in files:
        if file_path.name == ".gitkeep":
            print_status("SKIP", f"Keeping .gitkeep file: {file_path}")
            continue
        try:
            if simulate:
                print_status("SIMULATE", f"Would remove: {file_path}")
            else:
                file_path.unlink()
                print_status("DONE", f"Removed: {file_path}")
        except Exception as e:
            print_status("ERROR", f"Failed to remove {file_path}: {e}")


def clean_empty_dirs(dirs: list[Path], simulate=True):
    """Delete empty directories"""
    print_header("Cleaning Empty Directories")

    if not dirs:
        print_status("SKIP", "No empty directories to remove")
        return

    sorted_dirs = sorted(dirs, key=lambda p: len(p.parts), reverse=True)

    for dir_path in sorted_dirs:
        try:
            if not any(dir_path.iterdir()):
                if simulate:
                    print_status("SIMULATE", f"Would remove directory: {dir_path}")
                else:
                    dir_path.rmdir()
                    print_status("DONE", f"Removed directory: {dir_path}")
            else:
                print_status("SKIP", f"Directory {dir_path} is no longer empty.")
        except Exception as e:
            print_status(
                "ERROR", f"Failed to remove directory {dir_path}: {e}")


def create_gitkeep_files(root_dir: Path = Path(".")):
    """Create .gitkeep files to keep empty directories in git"""
    print_header("Creating .gitkeep Files")

    important_dirs_relative = [
        Path("input"),
        Path("output"),
        Path("output/markdown"),
        Path("output/json"),
        Path("output/yaml"),
        Path("output/rtm"),
        Path("tests"),
        Path("src/modules"),
    ]

    important_dirs = [root_dir / d for d in important_dirs_relative]

    for directory in important_dirs:
        if not directory.exists():
            print_status("INFO", f"Directory {directory} does not exist, skipping .gitkeep creation.")
            continue

        contents = list(directory.iterdir())
        is_empty_or_only_gitkeep = not contents or (len(contents) == 1 and contents[0].name == ".gitkeep")

        if is_empty_or_only_gitkeep:
            gitkeep_path = directory / ".gitkeep"
            if not gitkeep_path.exists():
                try:
                    with open(gitkeep_path, "w", encoding="utf-8") as f:
                        f.write(
                            "# This file ensures the directory is tracked by Git.\n")
                    print_status("DONE", f"Created .gitkeep in {directory}")
                except IOError as e:
                    print_status(
                        "ERROR", f"Failed to create .gitkeep in {directory}: {e}"
                    )
            else:
                print_status("SKIP", f".gitkeep already exists in {directory}")


def integrate_with_pipeline(root_dir: Path = Path(".")):
    """Integrate the clean repository functionality with the pipeline"""
    print_header("Integrating with Pipeline")

    try:
        import yaml
    except ImportError:
        print_status("WARNING", "PyYAML not installed. Skipping pipeline integration.")
        return

    config_path = root_dir / "config/paths.yaml"
    if not config_path.exists():
        print_status(
            "INFO", f"Pipeline configuration file not found: {config_path}. Skipping integration."
        )
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            print_status("ERROR", f"Invalid YAML format in {config_path}. Expected a dictionary.")
            return

        if "pipeline" not in config:
            config["pipeline"] = {}
        if "steps" not in config["pipeline"] or not isinstance(config["pipeline"]["steps"], list):
            config["pipeline"]["steps"] = []

        step_exists = any(
            isinstance(step, dict) and step.get("name") == "clean_repository"
            for step in config["pipeline"]["steps"]
        )

        if not step_exists:
            clean_step = {
                "name": "clean_repository",
                "script": "scripts/clean_repository.py",
                "enabled": False,
                "args": ["--simulate"],
            }
            config["pipeline"]["steps"].append(clean_step)

            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                print_status(
                    "DONE", "Added clean_repository step to pipeline configuration"
                )
            except IOError as e:
                print_status("ERROR", f"Failed to write updated pipeline configuration to {config_path}: {e}")
        else:
            print_status(
                "SKIP",
                "clean_repository step already exists in pipeline configuration.",
            )
    except yaml.YAMLError as e:
        print_status("ERROR", f"Failed to parse YAML in {config_path}: {e}")
    except Exception as e:
        print_status("ERROR", f"Failed to update pipeline configuration: {e}")


def main():
    """Main function"""
    print_header("DOCX RTM Automation Repository Cleanup")
    print("This utility helps clean up and organize your repository structure.\n")

    simulate = "--simulate" in sys.argv or "-s" in sys.argv
    force = "--force" in sys.argv or "-f" in sys.argv

    if simulate:
        print(
            f"{Colors.YELLOW}Running in simulation mode. No changes will be made.{Colors.ENDC}"
        )
    else:
        print(
            f"{Colors.RED}Running in execution mode. Changes will be applied.{Colors.ENDC}"
        )
        if not force:
            confirmation = input("Do you want to continue? (y/n): ")
            if confirmation.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                return 0

    start_time = time.time()

    current_dir = Path(".")

    create_directory_structure()

    empty_files = find_empty_files(current_dir)

    empty_dirs = find_empty_directories(current_dir)

    duplicates = find_duplicate_files(current_dir)

    clean_empty_files(empty_files, simulate=simulate)

    clean_empty_dirs(empty_dirs, simulate=simulate)

    organize_files(current_dir)

    create_gitkeep_files(current_dir)

    integrate_with_pipeline(current_dir)

    elapsed_time = time.time() - start_time
    print_header("Cleanup Summary")
    print(f"Found {len(empty_files)} empty files")
    print(f"Found {len(empty_dirs)} empty directories")
    print(f"Found {len(duplicates)} duplicate files")
    print(f"Executed in {elapsed_time:.2f} seconds")

    if simulate:
        print(
            f"\n{Colors.YELLOW}This was a simulation. Run without --simulate to apply changes.{Colors.ENDC}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
