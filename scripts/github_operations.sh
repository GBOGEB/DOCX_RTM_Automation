#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml
import json
import time
from pathlib import Path

# Global configurations
PYTHON_PATH = "C:\\Users\\gbonthuy\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
BASE_DIR = Path(__file__).parent.absolute()
VENV_PATH = BASE_DIR / ".venv"
VENV_PYTHON = VENV_PATH / "Scripts" / "python.exe"
CONFIG_FILE = BASE_DIR / "global_config.yaml"


def load_config():
    """Load global configuration from YAML file"""
    if not CONFIG_FILE.exists():
        print(f"Warning: Config file {CONFIG_FILE} not found.")
        return {}

    with open(CONFIG_FILE, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return {}


def run_command(command, use_venv=True):
    """Run a command with appropriate Python interpreter"""
    python_exe = str(
        VENV_PYTHON) if use_venv and VENV_PATH.exists() else PYTHON_PATH

    if command.startswith('python '):
        command = command.replace('python ', f'"{python_exe}" ')

    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    return result.returncode


def activate_venv():
    """Ensure virtual environment is activated"""
    if not VENV_PATH.exists():
        print("Virtual environment not found. Setting up...")
        setup_environment()

    # Return the path to the activated Python executable
    return str(VENV_PYTHON)


def setup_environment():
    """Set up the virtual environment and install dependencies"""
    print("Creating virtual environment...")
    run_command(f'"{PYTHON_PATH}" -m venv "{VENV_PATH}"', use_venv=False)

    print("Installing requirements...")
    run_command(f'"{VENV_PYTHON}" -m pip install --upgrade pip')
    run_command(f'"{VENV_PYTHON}" -m pip install -r requirements.txt')


def git_operations():
    """Handle Git operations with proper VENV deactivation"""
    print("\n=== Git Operations ===")
    print("[1] Configure Git")
    print("[2] Push Changes")
    print("[3] Pull Updates")
    print("[4] View Status")
    print("[0] Back to Main Menu")

    choice = input("Select option: ")

    if choice == "1":
        # Temporarily deactivate VENV for Git configuration
        print("Configuring Git...")
        subprocess.run(
            "git config --global user.name \"Your Name\"", shell=True)
        subprocess.run(
            "git config --global user.email \"your.email@example.com\"", shell=True)
        print("Git configured successfully.")
    elif choice == "2":
        print("Pushing changes...")
        run_command(f'"{PYTHON_PATH}" GIT_push.py', use_venv=False)
    elif choice == "3":
        print("Pulling updates...")
        subprocess.run("git pull", shell=True)
    elif choice == "4":
        print("Git status:")
        subprocess.run("git status", shell=True)


def display_menu():
    """Display the main menu"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== DOCX RTM Automation Terminal ===")
    print("Current Date and Time (UTC): " +
          time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print("Current User: " + os.environ.get('USERNAME', 'Unknown'))
    print("\nSelect an option:")
    print("[A] Prepare Environment and Setup")
    print("[B] Convert Word Documents to Markdown")
    print("[C] Generate Requirements Traceability Matrix")
    print("[D] Run Full Pipeline")
    print("[E] Run Tests")
    print("[F] Manual Refactoring Tools")
    print("[G] Close Processes & Fix Permissions")
    print("[H] Git Operations")
    print("[I] Configure Settings")
    print("[J] Help & Documentation")
    print("[Q] Quit")

    return input("\nEnter your choice: ").upper()


def main():
    """Main function to run the terminal interface"""
    while True:
        choice = display_menu()

        if choice == 'A':
            print("\n=== Preparing Environment ===")
            setup_environment()
            print("Setup complete!")

        elif choice == 'B':
            print("\n=== Converting Word Documents to Markdown ===")
            python_exe = activate_venv()
            run_command(f'"{python_exe}" src/core/word_to_md.py')

        elif choice == 'C':
            print("\n=== Generating Requirements Traceability Matrix ===")
            python_exe = activate_venv()
            run_command(f'"{python_exe}" generate_rtm.py')

        elif choice == 'D':
            print("\n=== Running Full Pipeline ===")
            python_exe = activate_venv()
            run_command(f'"{python_exe}" run_pipeline.py')

        elif choice == 'E':
            print("\n=== Running Tests ===")
            python_exe = activate_venv()
            run_command(f'"{python_exe}" run_tests.py')

        elif choice == 'F':
            print("\n=== Manual Refactoring Tools ===")
            python_exe = activate_venv()
            print("[1] Standard Refactor")
            print("[2] Safe Refactor")
            print("[3] Manual Refactor")
            print("[0] Back to Main Menu")

            refactor_choice = input("Select option: ")
            if refactor_choice == "1":
                run_command(f'"{python_exe}" refactor.py')
            elif refactor_choice == "2":
                run_command(f'"{python_exe}" safe_refactor.py')
            elif refactor_choice == "3":
                run_command(f'"{python_exe}" manual_refactor.py')

        elif choice == 'G':
            print("\n=== Maintenance Tools ===")
            python_exe = activate_venv()
            print("[1] Close Processes")
            print("[2] Fix Permissions")
            print("[0] Back to Main Menu")

            maint_choice = input("Select option: ")
            if maint_choice == "1":
                run_command(f'"{python_exe}" close_processes.py')
            elif maint_choice == "2":
                run_command(f'"{python_exe}" fix_permissions.py')

        elif choice == 'H':
            git_operations()

        elif choice == 'I':
            print("\n=== Configure Settings ===")
            # Load current config
            config = load_config()
            print("Current configuration:")
            print(json.dumps(config, indent=2))

            print("\nOptions:")
            print("[1] Edit global_config.yaml")
            print("[2] Reset to defaults")
            print("[0] Back to Main Menu")

            config_choice = input("Select option: ")
            if config_choice == "1":
                # Open config file in default editor
                os.system(f'start global_config.yaml' if os.name ==
                          'nt' else f'open global_config.yaml')

        elif choice == 'J':
            print("\n=== Help & Documentation ===")
            print("Opening README...")
            os.system('start README.md' if os.name ==
                      'nt' else 'cat README.md | less')

        elif choice == 'Q':
            print("Exiting DOCX RTM Automation Terminal. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
