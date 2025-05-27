#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml
import json
import time
import shutil
from pathlib import Path

# Global configurations
BASE_DIR = Path(__file__).parent.absolute()
CONFIG_FILE = BASE_DIR / "global_config.yaml"

# Initialize PYTHON_PATH and VENV_PATH, will be refined after loading config
_initial_python_path = sys.executable
VENV_PATH = BASE_DIR / ".venv"  # Default, can be overridden by config if needed

# Function to get the Python executable path
def get_python_executable():
    config = load_config()
    # 1. From config's specific python_path for the project
    configured_python = config.get("paths", {}).get("python")
    if configured_python and Path(configured_python).exists():
        return str(Path(configured_python).resolve())

    # 2. Default to system Python (current interpreter)
    return sys.executable

PYTHON_PATH = get_python_executable()  # Set initial global PYTHON_PATH

VENV_PYTHON = (
    VENV_PATH / "Scripts" / "python.exe"
    if os.name == "nt"
    else VENV_PATH / "bin" / "python"
)


def load_config():
    """Load global configuration from YAML file"""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"Error parsing config file {CONFIG_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"Error reading config file {CONFIG_FILE}: {e}")
        return {}


def save_config(config):
    """Save configuration to global_config.yaml"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config file {CONFIG_FILE}: {e}")


def run_command(command, use_venv=True, show_output=True, cwd=None):
    """Run a command with appropriate Python interpreter"""
    python_exe_to_use = str(VENV_PYTHON) if use_venv and VENV_PYTHON.exists() else PYTHON_PATH

    if isinstance(command, list):
        if command[0] == "python":
            command[0] = python_exe_to_use
        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in command)
    elif command.startswith("python "):
        command = command.replace("python ", f'"{python_exe_to_use}" ', 1)
        cmd_str = command
    else:
        cmd_str = command

    print(f"Executing (in {cwd or BASE_DIR}): {cmd_str}")

    try:
        if show_output:
            result = subprocess.run(cmd_str, shell=True, check=False, cwd=cwd or BASE_DIR)
            return result.returncode
        else:
            result = subprocess.run(
                cmd_str, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd or BASE_DIR
            )
            return (
                result.returncode,
                result.stdout.decode("utf-8", errors="ignore"),
                result.stderr.decode("utf-8", errors="ignore"),
            )
    except Exception as e:
        print(f"Error running command '{cmd_str}': {e}")
        if not show_output:
            return -1, "", str(e)
        return -1


def activate_venv():
    """Ensure virtual environment is set up and return its Python executable."""
    global PYTHON_PATH
    PYTHON_PATH = get_python_executable()

    if not VENV_PATH.exists():
        print("Virtual environment not found. Setting up...")
        if not setup_environment():
            print("Failed to setup environment. Venv activation might fail.")
            return PYTHON_PATH

    return str(VENV_PYTHON)


def setup_environment(force_new=False):
    """Set up the virtual environment and install dependencies"""
    global PYTHON_PATH
    PYTHON_PATH = get_python_executable()

    print("Setting up environment...")

    if VENV_PATH.exists() and not force_new:
        print(f"Virtual environment already exists at {VENV_PATH}")
        print("Using existing environment. Use --force-new to recreate it.")
        return True
    elif VENV_PATH.exists() and force_new:
        print(f"Removing existing virtual environment at {VENV_PATH}...")
        try:
            shutil.rmtree(VENV_PATH)
            print("Removed existing environment.")
        except Exception as e:
            print(f"Error removing environment: {e}")
            return False

    print("Creating virtual environment...")
    return_code = run_command(f'"{PYTHON_PATH}" -m venv "{VENV_PATH}"', use_venv=False)
    if return_code != 0:
        print(f"Error: Failed to create virtual environment using {PYTHON_PATH}.")
        return False

    print("Installing requirements...")
    pip_upgrade_cmd = f'"{VENV_PYTHON}" -m pip install --upgrade pip'
    requirements_cmd = f'"{VENV_PYTHON}" -m pip install -r requirements.txt'

    if run_command(pip_upgrade_cmd) != 0:
        print("Error: Failed to upgrade pip.")

    if run_command(requirements_cmd) != 0:
        print("Error: Failed to install requirements from requirements.txt.")
        print("Please ensure requirements.txt exists and is valid.")

    config = load_config()
    input_dir_name = config.get("paths", {}).get("input_dir", "input")
    output_dir_name = config.get("paths", {}).get("output_dir", "output")
    config_dir_name = config.get("paths", {}).get("config_dir", "config")
    docs_dir_name = config.get("paths", {}).get("docs_dir", "docs")

    for dir_name in [input_dir_name, output_dir_name, config_dir_name, docs_dir_name]:
        (BASE_DIR / dir_name).mkdir(parents=True, exist_ok=True)

    print("Environment setup complete!")
    return True


def detect_pandoc():
    """Detect Pandoc installation and update config"""
    print("Detecting Pandoc installation...")
    config = load_config()
    current_pandoc_path = config.get("paths", {}).get("pandoc")

    if current_pandoc_path and Path(current_pandoc_path).exists():
        print(f"Pandoc already configured at: {current_pandoc_path}")
        if not user_confirm("Do you want to re-detect or change Pandoc path?", default=False):
            return True

    pandoc_paths = []

    system_pandoc = shutil.which("pandoc.exe" if os.name == "nt" else "pandoc")
    if system_pandoc:
        pandoc_paths.append(system_pandoc)

    if os.name == "nt":
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]

        for pf in program_files:
            pandoc_dir = os.path.join(pf, "Pandoc")
            if os.path.exists(pandoc_dir):
                for root, dirs, files in os.walk(pandoc_dir):
                    for file in files:
                        if file.lower() == "pandoc.exe":
                            pandoc_paths.append(os.path.join(root, file))

    if pandoc_paths:
        print("\nFound Pandoc installations:")
        for i, path in enumerate(pandoc_paths, 1):
            print(f"[{i}] {path}")
        print(f"[{len(pandoc_paths) + 1}] Enter custom path")

        choice = input("\nSelect Pandoc installation or enter custom path [1]: ") or "1"

        if choice.isdigit() and 1 <= int(choice) <= len(pandoc_paths):
            selected_path = pandoc_paths[int(choice) - 1]
        elif choice.isdigit() and int(choice) == len(pandoc_paths) + 1:
            selected_path = input("Enter full path to pandoc executable: ")
        else:
            selected_path = input("Enter full path to pandoc executable: ")
    else:
        print("No Pandoc installation detected.")
        selected_path = input(
            "Enter full path to pandoc executable (leave empty to skip): "
        )

    if selected_path:
        try:
            result = subprocess.run(
                [selected_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode == 0:
                print(f"Verified Pandoc at: {selected_path}")
                if "paths" not in config:
                    config["paths"] = {}
                config["paths"]["pandoc"] = str(Path(selected_path).resolve())
                save_config(config)
                return True
            else:
                print(f"Error: Could not verify Pandoc at {selected_path}")
                return False
        except Exception as e:
            print(f"Error verifying Pandoc: {e}")
            return False
    else:
        print("Pandoc path not set. Word to Markdown conversion may not work.")
        return False


def display_menu():
    """Display the main menu"""
    os.system("cls" if os.name == "nt" else "clear")
    config = load_config()
    python_to_display = config.get("paths", {}).get("python", PYTHON_PATH)
    pandoc_to_display = config.get("paths", {}).get("pandoc", "Not configured")

    print("\n=== DOCX RTM Automation Terminal ===")
    print(
        "Current Date and Time (UTC): "
        + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    )
    print(
        "Current User: " +
        os.environ.get("USERNAME", os.environ.get("USER", "Unknown"))
    )
    print(f"Python Interpreter: {python_to_display}")
    print(f"Pandoc Path: {pandoc_to_display}")
    print(f"Virtual Env Active: {VENV_PYTHON.exists()}")
    print("\nSelect an option:")
    print("[A] Complete Setup (Environment, Pandoc, Directories)")
    print("[B] Convert Word Documents to Markdown")
    print("[C] Extract Requirements & Generate RTM")
    print("[D] View/Update LCP Phase Definitions")
    print("[E] Run Full Pipeline")
    print("[F] Run Tests")
    print("[G] Git Operations")
    print("[H] Configure Settings")
    print("[I] Help & Documentation")
    print("[Q] Quit")

    return input("\nEnter your choice: ").upper()


def main():
    """Main function to run the terminal interface"""
    global PYTHON_PATH
    PYTHON_PATH = get_python_executable()

    if not CONFIG_FILE.exists():
        print(f"{CONFIG_FILE} not found.")
        if user_confirm("Would you like to run initial setup to create config and environment?", default=True):
            setup_environment(force_new=False)
            print("\nInitial setup complete. Press Enter to continue to the main menu.")
            input()
    elif not VENV_PATH.exists():
        print("Virtual environment not found.")
        if user_confirm("Would you like to set up the virtual environment now?", default=True):
            setup_environment(force_new=False)
            print("\nEnvironment setup complete. Press Enter to continue to the main menu.")
            input()

    while True:
        choice = display_menu()

        if choice == "A":
            print("\n=== Complete Setup ===")
            force_new = user_confirm(
                "Recreate virtual environment if it exists?", default=False
            )
            setup_environment(force_new=force_new)

        elif choice == "B":
            convert_docx_to_markdown()

        elif choice == "C":
            extract_rtm(input_mode="auto")

        elif choice == "D":
            update_lcp_phases()

        elif choice == "E":
            print("\n=== Running Full Pipeline ===")
            python_exe = activate_venv()

            print("Running full pipeline...")
            print("This will execute the complete RTM automation workflow.")
            confirm = input("Continue? (y/n): ")

            if confirm.lower() == "y":
                pipeline_script = BASE_DIR / "run_pipeline.py"
                if pipeline_script.exists():
                    run_command(f'"{python_exe}" run_pipeline.py')
                else:
                    print(f"Error: {pipeline_script} not found!")

        elif choice == "F":
            print("\n=== Running Tests ===")
            python_exe = activate_venv()

            tests_dir = BASE_DIR / "tests"
            if not tests_dir.exists() or not list(tests_dir.glob("*.py")):
                print("No tests found in 'tests' directory!")
            else:
                tests_script = BASE_DIR / "run_tests.py"
                if tests_script.exists():
                    run_command(f'"{python_exe}" run_tests.py')
                else:
                    print("Running pytest directly...")
                    run_command(f'"{python_exe}" -m pytest')

        elif choice == "G":
            print("\n=== Git Operations ===")
            print("[1] Status (Main Repo)")
            print("[2] Status (All Repos including Submodules)")
            print("[3] Pull (Main Repo)")
            print("[4] Pull (All Repos including Submodules)")
            print("[5] Configure Git User")
            print("[6] Set/Change Remote URL (Main Repo)")
            print("[0] Back to Main Menu")

            git_choice = input("Select Git option: ")
            config = load_config()
            main_repo_path = BASE_DIR / config.get("repository_settings", {}).get("main_repository_path", ".")

            if git_choice == "1":
                run_command("git status", cwd=main_repo_path)
            elif git_choice == "2":
                run_command("git status", cwd=main_repo_path)
                run_command("git submodule status --recursive", cwd=main_repo_path)
                sub_repos = config.get("repository_settings", {}).get("sub_repositories", [])
                for sub_repo_rel_path in sub_repos:
                    sub_repo_abs_path = (BASE_DIR / sub_repo_rel_path).resolve()
                    if sub_repo_abs_path.is_dir():
                        print(f"\n--- Status for Sub-repository: {sub_repo_rel_path} ---")
                        run_command("git status", cwd=sub_repo_abs_path)
            elif git_choice == "3":
                run_command("git pull", cwd=main_repo_path)
            elif git_choice == "4":
                run_command("git pull", cwd=main_repo_path)
                run_command("git submodule update --remote --recursive", cwd=main_repo_path)
            elif git_choice == "5":
                username = input("Enter Git username: ")
                email = input("Enter Git email: ")
                run_command(f'git config user.name "{username}"', cwd=main_repo_path)
                run_command(f'git config user.email "{email}"', cwd=main_repo_path)
                print("Git user configured for the main repository.")
            elif git_choice == "6":
                remote_url = input("Enter new remote URL for main repo (e.g., https://github.com/user/repo.git): ")
                ret_code, stdout, _ = run_command("git remote", use_venv=False, show_output=False, cwd=main_repo_path)
                if ret_code == 0 and 'origin' in stdout:
                    run_command(f'git remote set-url origin "{remote_url}"', cwd=main_repo_path)
                else:
                    run_command(f'git remote add origin "{remote_url}"', cwd=main_repo_path)
                print(f"Remote URL for main repository set to: {remote_url}")
            elif git_choice == "0":
                pass
            else:
                print("Invalid Git option.")

        elif choice == "H":
            print("\n=== Configure Settings ===")
            config = load_config()

            while True:
                print("\nCurrent configuration:")
                for key, value in config.items():
                    print(f"  {key}: {value}")

                print("\nOptions:")
                print("[1] Edit Python interpreter path")
                print("[2] Detect/Edit Pandoc path")
                print("[3] Edit input/output paths")
                print("[4] Add/Edit custom setting")
                print("[5] Reset to defaults")
                print("[0] Back to Main Menu")

                config_choice = input("Select option: ")

                if config_choice == "1":
                    new_python_path = input(f"Enter Python interpreter path [{PYTHON_PATH}]: ").strip()
                    if new_python_path and Path(new_python_path).exists():
                        if "paths" not in config:
                            config["paths"] = {}
                        config["paths"]["python"] = str(Path(new_python_path).resolve())
                        save_config(config)
                        global PYTHON_PATH
                        PYTHON_PATH = get_python_executable()
                        print(f"Python path updated to: {PYTHON_PATH}")
                    elif not new_python_path:
                        print("No change made.")
                    else:
                        print(f"Error: Path '{new_python_path}' does not exist.")
                elif config_choice == "2":
                    detect_pandoc()
                elif config_choice == "3":
                    if "paths" not in config:
                        config["paths"] = {}
                    input_dir = input(f"Enter input directory path [{config.get('paths', {}).get('input_dir', 'input')}]: ") or config.get('paths', {}).get('input_dir', 'input')
                    output_dir = input(f"Enter output directory path [{config.get('paths', {}).get('output_dir', 'output')}]: ") or config.get('paths', {}).get('output_dir', 'output')
                    config["paths"]["input_dir"] = input_dir
                    config["paths"]["output_dir"] = output_dir
                    save_config(config)
                elif config_choice == "4":
                    key = input("Enter setting name: ")
                    value = input("Enter setting value: ")
                    config[key] = value
                    save_config(config)
                elif config_choice == "5":
                    confirm = input("Reset all settings in global_config.yaml to minimal defaults? (y/n): ")
                    if confirm.lower() == "y":
                        default_config = {
                            "paths": {
                                "input_dir": "input",
                                "output_dir": "output",
                                "python": sys.executable,
                            },
                            "repository_settings": {
                                "main_repository_path": ".",
                                "sub_repositories": []
                            }
                        }
                        pandoc_exe_name = "pandoc.exe" if os.name == "nt" else "pandoc"
                        found_pandoc = shutil.which(pandoc_exe_name)
                        if found_pandoc:
                            default_config["paths"]["pandoc"] = str(Path(found_pandoc).resolve())

                        config = default_config
                        save_config(config)
                        global PYTHON_PATH
                        PYTHON_PATH = get_python_executable()
                elif config_choice == "0":
                    break

        elif choice == "I":
            print("\n=== Help & Documentation ===")
            readme_file = BASE_DIR / "README.md"

            if readme_file.exists():
                if os.name == "nt":
                    os.system(f'type "{readme_file}"')
                else:
                    os.system(f'cat "{readme_file}"')
            else:
                print("README.md not found!")

            print("\nDOCX RTM Automation Quick Help:")
            print("--------------------------------")
            print("This tool helps convert Word documents to Markdown")
            print("and generate Requirements Traceability Matrices (RTM).")
            print("\nBasic Workflow:")
            print("1. Place Word documents in the 'input' folder")
            print("2. Convert them to Markdown using Option B")
            print("3. Generate an RTM using Option C")
            print("4. Or run the full pipeline with Option E")

        elif choice == "Q":
            print("Exiting DOCX RTM Automation Terminal. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
