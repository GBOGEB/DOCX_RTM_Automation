# DOCX RTM Automation Terminal Interface

```python
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
VENV_PATH = BASE_DIR / ".venv" # Default, can be overridden by config if needed

# Function to get the Python executable path
def get_python_executable():
    config = load_config()
    # 1. From config's specific python_path for the project
    configured_python = config.get("paths", {}).get("python")
    if configured_python and Path(configured_python).exists():
        return str(Path(configured_python).resolve())

    # 2. Default to system Python (current interpreter)
    return sys.executable

PYTHON_PATH = get_python_executable() # Set initial global PYTHON_PATH

VENV_PYTHON = (
    VENV_PATH / "Scripts" / "python.exe"
    if os.name == "nt"
    else VENV_PATH / "bin" / "python"
)


def load_config():
    """Load global configuration from YAML file"""
    if not CONFIG_FILE.exists():
        # print(f"Warning: Config file {CONFIG_FILE} not found. Returning empty config.") # Less verbose
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
    # Determine Python executable: venv if exists and use_venv, else global PYTHON_PATH
    python_exe_to_use = str(VENV_PYTHON) if use_venv and VENV_PYTHON.exists() else PYTHON_PATH

    if isinstance(command, list):
        if command[0] == "python":
            command[0] = python_exe_to_use
        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in command)
    elif command.startswith("python "):
        command = command.replace("python ", f'"{python_exe_to_use}" ', 1)
        cmd_str = command
    else: # Not a python command, or python is not the first word.
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
    global PYTHON_PATH # Ensure global PYTHON_PATH is updated if config changes
    PYTHON_PATH = get_python_executable()

    if not VENV_PATH.exists():
        print("Virtual environment not found. Setting up...")
        if not setup_environment():
            print("Failed to setup environment. Venv activation might fail.")
            return PYTHON_PATH # Fallback to global python

    return str(VENV_PYTHON)


def setup_environment(force_new=False):
    """Set up the virtual environment and install dependencies"""
    global PYTHON_PATH # Access the global PYTHON_PATH
    PYTHON_PATH = get_python_executable() # Refresh in case config changed it

    print("Setting up environment...")

    # Check if venv already exists
    if VENV_PATH.exists() and not force_new:
        print(f"Virtual environment already exists at {VENV_PATH}")
        print("Using existing environment. Use --force-new to recreate it.")
        # return True # Original logic, but let's ensure deps and config are checked
    elif VENV_PATH.exists() and force_new:
        print(f"Removing existing virtual environment at {VENV_PATH}...")
        try:
            shutil.rmtree(VENV_PATH)
            print("Removed existing environment.")
        except Exception as e:
            print(f"Error removing environment: {e}")
            return False

    print("Creating virtual environment...")
    # Use the resolved PYTHON_PATH for creating the venv
    return_code = run_command(f'"{PYTHON_PATH}" -m venv "{VENV_PATH}"', use_venv=False)
    if return_code != 0:
        print(f"Error: Failed to create virtual environment using {PYTHON_PATH}.")
        return False

    print("Installing requirements...")
    pip_upgrade_cmd = f'"{VENV_PYTHON}" -m pip install --upgrade pip'
    requirements_cmd = f'"{VENV_PYTHON}" -m pip install -r requirements.txt'

    if run_command(pip_upgrade_cmd) != 0:
        print("Error: Failed to upgrade pip.")
        # Continue with requirements installation

    if run_command(requirements_cmd) != 0:
        print("Error: Failed to install requirements from requirements.txt.")
        print("Please ensure requirements.txt exists and is valid.")
        # Optionally, you could return False here if requirements are critical

    # Add Project LCP phase information to configuration
    config = load_config() or {}
    if "lcp_phases" not in config:
        config["lcp_phases"] = {
            "0": "Procurement",
            "1": "Concept",
            "2": "Detailed Design (FEED)",
            "3": "Construction & Factory Acceptance",
            "4": "Installation & Hook-up",
            "5": "Commissioning & RCM Start",
            "6": "SAT & RCM Training",
            "7": "Operational & User Commissioning",
            "8": "Integrated Commissioning",
        }
        save_config(config)
        print("Added LCP phase information to configuration")

    # Check for Pandoc installation
    detect_pandoc() # This will save to config

    # Create necessary directories from config or defaults
    config = load_config()
    input_dir_name = config.get("paths", {}).get("input_dir", "input")
    output_dir_name = config.get("paths", {}).get("output_dir", "output")
    config_dir_name = config.get("paths", {}).get("config_dir", "config")
    docs_dir_name = config.get("paths", {}).get("docs_dir", "docs") # Assuming 'docs_dir' for consistency

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

    # Check in common installation paths
    pandoc_paths = []

    # System PATH
    system_pandoc = shutil.which("pandoc.exe" if os.name == "nt" else "pandoc")
    if system_pandoc:
        pandoc_paths.append(system_pandoc)

    # Common installation directories on Windows
    if os.name == "nt":
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]

        for pf in program_files:
            pandoc_dir = os.path.join(pf, "Pandoc")
            if os.path.exists(pandoc_dir):
                for root, dirs, files in os.walk(pandoc_dir):
                    for file_item in files: # Renamed to avoid conflict with 'file' module
                        if file_item.lower() == "pandoc.exe":
                            pandoc_paths.append(os.path.join(root, file_item))

    # Ask user to select or enter path
    if pandoc_paths:
        print("\nFound Pandoc installations:")
        for i, path in enumerate(pandoc_paths, 1):
            print(f"[{i}] {path}")
        print(f"[{len(pandoc_paths) + 1}] Enter custom path")

        choice = input(
            "\nSelect Pandoc installation or enter custom path [1]: ") or "1"

        if choice.isdigit() and 1 <= int(choice) <= len(pandoc_paths):
            selected_path = pandoc_paths[int(choice) - 1]
        elif choice.isdigit() and int(choice) == len(pandoc_paths) + 1:
            selected_path = input("Enter full path to pandoc executable: ")
        else: # Default to custom path if input is not a valid choice number
            selected_path = input("Enter full path to pandoc executable: ")
    else:
        print("No Pandoc installation detected automatically.")
        selected_path = input(
            "Enter full path to pandoc executable (leave empty to skip): "
        )

    if selected_path and Path(selected_path).exists(): # Check if path exists before verifying
        # Verify the path works
        try:
            result = subprocess.run(
                [selected_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False # Don't raise exception on non-zero exit
            )
            if result.returncode == 0:
                print(f"Verified Pandoc at: {selected_path}")
                # Update config under paths.pandoc
                if "paths" not in config:
                    config["paths"] = {}
                config["paths"]["pandoc"] = str(Path(selected_path).resolve()) # Store resolved absolute path
                save_config(config)
                return True
            else:
                print(f"Error: Could not verify Pandoc at {selected_path}. Stderr: {result.stderr.decode(errors='ignore')}")
                return False
        except Exception as e:
            print(f"Error verifying Pandoc at {selected_path}: {e}")
            return False
    elif selected_path: # Path was entered but doesn't exist
        print(f"Error: Entered Pandoc path '{selected_path}' does not exist.")
        return False
    else: # No path entered
        print("Pandoc path not set. Word to Markdown conversion may not work.")
        return False


def extract_rtm(input_mode="auto"):
    """Extract RTM from markdown files"""
    print("\n=== Extracting Requirements Traceability Matrix ===")
    python_exe = activate_venv()
    config = load_config()
    output_dir_name = config.get("paths", {}).get("output_dir", "output")
    output_dir = BASE_DIR / output_dir_name
    md_files = []

    if input_mode == "auto":
        # Scan main output directory
        if output_dir.exists():
            md_files.extend(list(output_dir.glob("*.md")))
            md_files.extend(list(output_dir.glob("**/*.md"))) # Recursive

        # Scan sub-repository output directories
        sub_repos = config.get("repository_settings", {}).get("sub_repositories", [])
        for sub_repo_rel_path in sub_repos:
            sub_repo_abs_path = (BASE_DIR / sub_repo_rel_path).resolve()
            sub_output_dir = sub_repo_abs_path / output_dir_name # Assume same output dir name
            if sub_output_dir.exists():
                print(f"Scanning for .md files in sub-repository output: {sub_output_dir}")
                md_files.extend(list(sub_output_dir.glob("*.md")))
                md_files.extend(list(sub_output_dir.glob("**/*.md")))

        md_files = sorted(list(set(md_files))) # Remove duplicates and sort

        if md_files:
            print(f"Found {len(md_files)} markdown files for processing:")
            for f_path in md_files: # Renamed to avoid conflict
                print(f"  - {f_path}")

            generate_rtm_script = BASE_DIR / "generate_rtm.py"
            if generate_rtm_script.exists():
                md_paths_str = " ".join(f'"{str(f_path)}"' for f_path in md_files)
                # The generate_rtm.py script itself should handle multiple --input flags or a list of files
                run_command(f'"{python_exe}" "{generate_rtm_script}" --input {md_paths_str} --output-dir "{output_dir}"')
            else:
                print(f"Error: {generate_rtm_script} not found.")
        else:
            print("No markdown files found in main or sub-repository output directories.")
            # Conceptual: Offer to generate sample Markdown from OpenAI
            # if user_confirm("No Markdown files. Generate sample from OpenAI?", default=False):
            #    run_command(f'"{python_exe}" some_openai_script.py --action generate_sample_md --output "{output_dir / "sample_from_ai.md"}"')


            # Offer to process DOCX files directly
            if user_confirm("Would you like to try converting DOCX files first?"):
                convert_docx_to_markdown()
                # Try RTM extraction again
                extract_rtm(input_mode="auto")

    elif input_mode == "manual_github_url":
        github_url = input("Enter GitHub URL of the Markdown file: ")
        if github_url:
            print(f"Conceptual: Downloading {github_url}...")
            # downloaded_file = download_from_github(github_url, output_dir) # Placeholder
            # if downloaded_file and Path(downloaded_file).exists():
            #    run_command(f'"{python_exe}" generate_rtm.py --input "{downloaded_file}" --output-dir "{output_dir}"')
            # else:
            #    print("Failed to download or invalid file.")
            print("GitHub URL processing not yet implemented.")
        else:
            print("No URL provided.")
    elif input_mode == "manual_local":
        # Let user select files
        print("Please select input files for RTM extraction (manual local selection not fully implemented).")
        # Implementation for manual selection...

    # Update the configuration with LCP phase information
    update_lcp_phases()


def update_lcp_phases():
    """Update or display LCP phase information"""
    print("\n=== Project LCP Phase Information ===")
    config = load_config() or {}

    if "lcp_phases" not in config:
        config["lcp_phases"] = {
            "0": "Procurement",
            "1": "Concept",
            "2": "Detailed Design (FEED)",
            "3": "Construction & Factory Acceptance",
            "4": "Installation & Hook-up",
            "5": "Commissioning & RCM Start",
            "6": "SAT & RCM Training",
            "7": "Operational & User Commissioning",
            "8": "Integrated Commissioning",
        }
        save_config(config)

    # Display the phases
    print("\nLCP Phase definitions:")
    for phase, description in config.get("lcp_phases", {}).items(): # Use .get for safety
        print(f"  LH2: {phase} = {description}")

    print("\nNote: These phases are used for requirement categorization.")
    print("      LH1 refers to location hooks in the document.")
    print("      LH2 refers to the project phase.")


def user_confirm(prompt="Continue?", default=True):
    """Ask user for confirmation"""
    default_txt = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_txt}]: ").strip().lower()
    if not response:
        return default
    return response.startswith("y") # More robust check for 'y'


def convert_docx_to_markdown():
    """Convert DOCX files to Markdown"""
    print("\n=== Converting Word Documents to Markdown ===")
    python_exe = activate_venv()
    config = load_config()
    input_dir_name = config.get("paths", {}).get("input_dir", "input")
    main_input_dir = BASE_DIR / input_dir_name

    word_files = []
    # Scan main input directory
    if main_input_dir.exists():
        word_files.extend(list(main_input_dir.glob("*.docx")))
        word_files.extend(list(main_input_dir.glob("*.doc")))

    # Scan sub-repository input directories
    sub_repos = config.get("repository_settings", {}).get("sub_repositories", [])
    for sub_repo_rel_path in sub_repos:
        sub_repo_abs_path = (BASE_DIR / sub_repo_rel_path).resolve()
        sub_input_dir = sub_repo_abs_path / input_dir_name # Assume same input dir name
        if sub_input_dir.exists():
            print(f"Scanning for .docx/.doc files in sub-repository input: {sub_input_dir}")
            word_files.extend(list(sub_input_dir.glob("*.docx")))
            word_files.extend(list(sub_input_dir.glob("*.doc")))

    word_files = sorted(list(set(word_files))) # Remove duplicates and sort

    if not word_files:
        print(f"No Word documents found in '{main_input_dir}' or configured sub-repository input directories.")
        # Conceptual: Offer to download from GitHub
        # if user_confirm("Download DOCX from GitHub URL instead?", default=False):
        #    github_url = input("Enter GitHub URL of the DOCX file: ")
        #    if github_url:
        #        print(f"Conceptual: Downloading {github_url}...")
        #        # downloaded_file = download_from_github(github_url, main_input_dir) # Placeholder
        #        # if downloaded_file: word_files.append(Path(downloaded_file))
        #    else:
        #        print("No URL provided.")
        # else:
        # (original logic for adding files manually)
        add_file_q = input(f"Do you want to add a Word document to '{main_input_dir}'? (y/n): ") # Renamed variable
        if add_file_q.lower() == "y":
            print(f"Please copy your Word documents to the '{main_input_dir}' directory.")
            input("Press Enter when ready...")
            # Refresh file list
            word_files = [] # Reset and re-scan
            if main_input_dir.exists():
                 word_files.extend(list(main_input_dir.glob("*.docx")))
                 word_files.extend(list(main_input_dir.glob("*.doc")))
            # Re-scan sub-repos as well if needed, or assume user added to main_input_dir
            word_files = sorted(list(set(word_files)))


    if word_files:
        print("\nFound Word documents:")
        for i, file_path_obj in enumerate(word_files, 1):
            # Display relative path if it's within BASE_DIR for brevity
            try:
                display_path = file_path_obj.relative_to(BASE_DIR)
            except ValueError:
                display_path = file_path_obj # Absolute if not relative
            print(f"[{i}] {display_path}")

        idx = input("\nSelect a file to convert (or 'a' for all): ")
        word_to_md_script = BASE_DIR / "code" / "word_to_md.py" # Assuming script location

        if not word_to_md_script.exists():
            print(f"Error: Conversion script {word_to_md_script} not found.")
            return

        # Fix the word_to_md script first if needed (conceptual, or call a helper)
        # fix_word_to_md_script_if_needed()

        if idx.lower() == "a":
            print("Converting all files...")
            for file_path_obj_convert in word_files: # Renamed variable
                run_command(f'"{python_exe}" "{word_to_md_script}" "{file_path_obj_convert}"')
        elif idx.isdigit() and 1 <= int(idx) <= len(word_files):
            selected_file = word_files[int(idx) - 1]
            print(f"Converting {selected_file.name}...")
            run_command(f'"{python_exe}" "{word_to_md_script}" "{selected_file}"')
        else:
            print("Invalid selection.")


def display_menu():
    """Display the main menu"""
    os.system("cls" if os.name == "nt" else "clear")
    config = load_config() # Load fresh config for display
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
    print(f"Project Base: {BASE_DIR}")
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
    # Ensure PYTHON_PATH is set correctly at start
    global PYTHON_PATH
    PYTHON_PATH = get_python_executable()

    # Check if global_config.yaml exists, if not, prompt for setup.
    if not CONFIG_FILE.exists():
        print(f"{CONFIG_FILE} not found.")
        if user_confirm("Would you like to run initial setup to create config and environment?", default=True):
            setup_environment(force_new=False) # force_new=False to avoid deleting existing venv if any
            print("\nInitial setup complete. Press Enter to continue to the main menu.")
            input()
    elif not VENV_PATH.exists(): # Config exists, but venv doesn't
        print("Virtual environment not found.")
        if user_confirm("Would you like to set up the virtual environment now?", default=True):
            setup_environment(force_new=False)
            print("\nEnvironment setup complete. Press Enter to continue to the main menu.")
            input()


    while True:
        choice = display_menu()

        if choice == "A":
            print("\n=== Complete Setup ===")
            force_new_env = user_confirm( # Renamed variable
                "Recreate virtual environment if it exists?", default=False
            )
            setup_environment(force_new=force_new_env)

        elif choice == "B":
            convert_docx_to_markdown()

        elif choice == "C":
            extract_rtm(input_mode="auto") # Default to auto, could add sub-menu for other modes

        elif choice == "D":
            update_lcp_phases()

        elif choice == "E":
            print("\n=== Running Full Pipeline ===")
            python_exe = activate_venv()

            # First, make sure common issues are fixed (conceptual)
            # fix_word_to_md() # Example if this was a common fix needed

            print("Running full pipeline...")
            print("This will execute the complete RTM automation workflow.")
            confirm_run = input("Continue? (y/n): ") # Renamed variable

            if confirm_run.lower() == "y":
                pipeline_script = BASE_DIR / "run_pipeline.py" # Assuming this script exists
                if pipeline_script.exists():
                    run_command(f'"{python_exe}" "{pipeline_script}"')
                else:
                    print(f"Error: Pipeline script {pipeline_script} not found!")

        elif choice == "F":
            print("\n=== Running Tests ===")
            python_exe = activate_venv()

            # Check if tests directory exists
            tests_dir = BASE_DIR / "tests"
            if not tests_dir.exists() or not any(tests_dir.glob("test_*.py")): # Check for actual test files
                print("No tests found in 'tests' directory or no files matching 'test_*.py' pattern!")
            else:
                tests_script = BASE_DIR / "run_tests.py" # Assuming this script exists
                if tests_script.exists():
                    run_command(f'"{python_exe}" "{tests_script}"')
                else:
                    print("Test runner script 'run_tests.py' not found. Running pytest directly...")
                    run_command(f'"{python_exe}" -m pytest')

        elif choice == "G":
            # git_operations() # Call the git operations handler
            print("\n=== Git Operations ===")
            # Menu for Git operations
            print("[1] Status (Main Repo)")
            print("[2] Status (All Repos including Submodules)")
            print("[3] Pull (Main Repo)")
            print("[4] Pull (All Repos including Submodules)")
            print("[5] Configure Git User")
            print("[6] Set/Change Remote URL (Main Repo)")
            print("[0] Back to Main Menu")

            git_choice = input("Select Git option: ")
            config = load_config()
            main_repo_path_str = config.get("repository_settings", {}).get("main_repository_path", ".")
            main_repo_path = (BASE_DIR / main_repo_path_str).resolve() # Resolve main repo path

            if git_choice == "1":
                run_command("git status", cwd=main_repo_path)
            elif git_choice == "2":
                run_command("git status", cwd=main_repo_path) # Main repo
                run_command("git submodule status --recursive", cwd=main_repo_path) # Submodules status
                # Optionally iterate and run status in each sub_repo_paths
                sub_repos = config.get("repository_settings", {}).get("sub_repositories", [])
                for sub_repo_rel_path in sub_repos:
                    sub_repo_abs_path = (BASE_DIR / sub_repo_rel_path).resolve()
                    if sub_repo_abs_path.is_dir():
                        print(f"\n--- Status for Sub-repository: {sub_repo_rel_path} ---")
                        run_command("git status", cwd=sub_repo_abs_path)
            elif git_choice == "3":
                run_command("git pull", cwd=main_repo_path)
            elif git_choice == "4":
                run_command("git pull", cwd=main_repo_path) # Main repo
                run_command("git submodule update --remote --recursive", cwd=main_repo_path) # Pulls submodules
            elif git_choice == "5":
                username = input("Enter Git username: ")
                email = input("Enter Git email: ")
                run_command(f'git config user.name "{username}"', cwd=main_repo_path)
                run_command(f'git config user.email "{email}"', cwd=main_repo_path)
                print("Git user configured for the main repository.")
            elif git_choice == "6":
                remote_url = input("Enter new remote URL for main repo (e.g., https://github.com/user/repo.git): ")
                # Check if remote 'origin' exists
                ret_code, stdout_val, _ = run_command("git remote", use_venv=False, show_output=False, cwd=main_repo_path) # Renamed
                if ret_code == 0 and 'origin' in stdout_val:
                    run_command(f'git remote set-url origin "{remote_url}"', cwd=main_repo_path)
                else:
                    run_command(f'git remote add origin "{remote_url}"', cwd=main_repo_path)
                print(f"Remote URL for main repository set to: {remote_url}")
            elif git_choice == "0":
                pass # Back to main menu
            else:
                print("Invalid Git option.")

        elif choice == "H":
            print("\n=== Configure Settings ===")
            # Load current config
            # config = load_config() # Already loaded for menu display

            while True: # Inner loop for settings menu
                # Display current config again or relevant parts
                print("\nCurrent Configuration Snippet:")
                print(f"  Python Path: {config.get('paths', {}).get('python', PYTHON_PATH)}")
                print(f"  Pandoc Path: {config.get('paths', {}).get('pandoc', 'Not configured')}")
                print(f"  Input Dir: {config.get('paths', {}).get('input_dir', 'input')}")
                print(f"  Output Dir: {config.get('paths', {}).get('output_dir', 'output')}")


                print("\nOptions:")
                print("[1] Edit Python interpreter path")
                print("[2] Detect/Edit Pandoc path")
                print("[3] Edit input/output paths")
                print("[4] Add/Edit custom setting")
                print("[5] Reset to defaults")
                print("[0] Back to Main Menu")

                config_choice = input("Select option: ")
                config = load_config() # Ensure fresh config before modification

                if config_choice == "1":
                    new_python_path = input(f"Enter Python interpreter path [{config.get('paths',{}).get('python', PYTHON_PATH)}]: ").strip()
                    if new_python_path and Path(new_python_path).exists() and Path(new_python_path).is_file():
                        if "paths" not in config: config["paths"] = {}
                        config["paths"]["python"] = str(Path(new_python_path).resolve())
                        save_config(config)
                        global PYTHON_PATH # Update global
                        PYTHON_PATH = get_python_executable() # This will re-read from config
                        print(f"Python path updated to: {PYTHON_PATH}")
                    elif not new_python_path:
                        print("No change made.")
                    else:
                        print(f"Error: Path '{new_python_path}' does not exist or is not a file.")
                elif config_choice == "2":
                    detect_pandoc() # This function now handles loading/saving config
                    config = load_config() # Reload config as detect_pandoc might change it
                elif config_choice == "3":
                    if "paths" not in config: config["paths"] = {}
                    input_dir_val = input(f"Enter input directory path [{config.get('paths',{}).get('input_dir','input')}]: ") or config.get('paths',{}).get('input_dir','input') # Renamed
                    output_dir_val = input(f"Enter output directory path [{config.get('paths',{}).get('output_dir','output')}]: ") or config.get('paths',{}).get('output_dir','output') # Renamed
                    config["paths"]["input_dir"] = input_dir_val
                    config["paths"]["output_dir"] = output_dir_val
                    save_config(config)
                elif config_choice == "4":
                    key_name = input("Enter setting name (e.g., 'feature_flags.new_parser'): ") # Renamed
                    value_data = input("Enter setting value: ") # Renamed
                    # Basic support for nested keys, e.g. "paths.temp_dir"
                    keys = key_name.split('.')
                    temp_config = config
                    for k_idx, k_val in enumerate(keys[:-1]): # Iterate up to the second to last key
                        temp_config = temp_config.setdefault(k_val, {})
                    temp_config[keys[-1]] = value_data
                    save_config(config)
                elif config_choice == "5":
                    confirm_reset = input("Reset all settings in global_config.yaml to minimal defaults? (y/n): ") # Renamed
                    if confirm_reset.lower() == "y":
                        default_config = {
                            "paths": {
                                "input_dir": "input",
                                "output_dir": "output",
                                "python": sys.executable, # Default to current interpreter
                            },
                            "repository_settings": {
                                "main_repository_path": ".",
                                "sub_repositories": []
                            }
                        }
                        # Try to find pandoc and add it
                        pandoc_exe_name = "pandoc.exe" if os.name == "nt" else "pandoc"
                        found_pandoc = shutil.which(pandoc_exe_name)
                        if found_pandoc:
                            default_config["paths"]["pandoc"] = str(Path(found_pandoc).resolve())

                        config = default_config # Update local copy
                        save_config(config) # Save to file
                        # Reload global PYTHON_PATH after reset
                        global PYTHON_PATH
                        PYTHON_PATH = get_python_executable()
                elif config_choice == "0":
                    break # Exit settings sub-menu
                else:
                    print("Invalid settings option.")
                input("Press Enter to continue settings configuration or 0 to exit...")


        elif choice == "I":
            print("\n=== Help & Documentation ===")
            readme_file = BASE_DIR / "README.md"

            if readme_file.exists():
                # Show README content (simplified)
                try:
                    with open(readme_file, "r", encoding="utf-8") as f_readme: # Renamed
                        print(f_readme.read(1000) + "\n... (content truncated, view full file for details)")
                except Exception as e_readme: # Renamed
                    print(f"Error reading README.md: {e_readme}")
            else:
                print("README.md not found!")

            print("\nDOCX RTM Automation Quick Help:")
            print("--------------------------------")
            print("This tool helps convert Word documents to Markdown")
            print("and generate Requirements Traceability Matrices (RTM).")
            print("\nBasic Workflow:")
            print("1. Place Word documents in the 'input' folder (and/or configured sub-repo input folders)")
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
```

## Quick Start Guide
// ... existing quick start guide ...

## Common Issues and Solutions
// ... existing common issues ...

## Setup Checklist
// ... existing setup checklist ...

## Terminal Launcher
// ... existing terminal launcher ...
