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
VENV_PATH = BASE_DIR / ".venv"
VENV_PYTHON = VENV_PATH / "Scripts" / "python.exe" if os.name == 'nt' else VENV_PATH / "bin" / "python"
CONFIG_FILE = BASE_DIR / "global_config.yaml"
# Default to system Python if specific path not available
PYTHON_PATH = "C:\\Users\\gbonthuy\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" if os.path.exists("C:\\Users\\gbonthuy\\AppData\\Local\\Programs\\Python\\Python312\\python.exe") else sys.executable

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

def save_config(config):
    """Save configuration to global_config.yaml"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration saved to {CONFIG_FILE}")

def run_command(command, use_venv=True, show_output=True):
    """Run a command with appropriate Python interpreter"""
    python_exe = str(VENV_PYTHON) if use_venv and VENV_PATH.exists() else PYTHON_PATH
    
    if command.startswith('python '):
        command = command.replace('python ', f'"{python_exe}" ')
    
    print(f"Executing: {command}")
    
    if show_output:
        result = subprocess.run(command, shell=True)
        return result.returncode
    else:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode, result.stdout.decode('utf-8', errors='ignore'), result.stderr.decode('utf-8', errors='ignore')

def activate_venv():
    """Ensure virtual environment is activated"""
    if not VENV_PATH.exists():
        print("Virtual environment not found. Setting up...")
        setup_environment()
    
    # Return the path to the activated Python executable
    return str(VENV_PYTHON)

def setup_environment(force_new=False):
    """Set up the virtual environment and install dependencies"""
    print("Setting up environment...")
    
    # Check if venv already exists
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
    run_command(f'"{PYTHON_PATH}" -m venv "{VENV_PATH}"', use_venv=False)
    
    print("Installing requirements...")
    run_command(f'"{VENV_PYTHON}" -m pip install --upgrade pip')
    run_command(f'"{VENV_PYTHON}" -m pip install -r requirements.txt')
    
    # Add Project LCP phase information to configuration
    config = load_config() or {}
    if 'lcp_phases' not in config:
        config['lcp_phases'] = {
            '0': 'Procurement',
            '1': 'Concept',
            '2': 'Detailed Design (FEED)',
            '3': 'Construction & Factory Acceptance',
            '4': 'Installation & Hook-up',
            '5': 'Commissioning & RCM Start',
            '6': 'SAT & RCM Training',
            '7': 'Operational & User Commissioning',
            '8': 'Integrated Commissioning'
        }
        save_config(config)
        print("Added LCP phase information to configuration")
    
    # Check for Pandoc installation
    detect_pandoc()
    
    # Create necessary directories
    for dir_name in ['input', 'output', 'config', 'docs']:
        os.makedirs(BASE_DIR / dir_name, exist_ok=True)
    
    print("Environment setup complete!")
    return True

def detect_pandoc():
    """Detect Pandoc installation and update config"""
    print("Detecting Pandoc installation...")
    
    # Check in common installation paths
    pandoc_paths = []
    
    # System PATH
    system_pandoc = shutil.which('pandoc.exe' if os.name == 'nt' else 'pandoc')
    if system_pandoc:
        pandoc_paths.append(system_pandoc)
    
    # Common installation directories on Windows
    if os.name == 'nt':
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        
        for pf in program_files:
            pandoc_dir = os.path.join(pf, 'Pandoc')
            if os.path.exists(pandoc_dir):
                for root, dirs, files in os.walk(pandoc_dir):
                    for file in files:
                        if file.lower() == 'pandoc.exe':
                            pandoc_paths.append(os.path.join(root, file))
    
    # Ask user to select or enter path
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
        selected_path = input("Enter full path to pandoc executable (leave empty to skip): ")
    
    if selected_path:
        # Verify the path works
        try:
            result = subprocess.run([selected_path, "--version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f"Verified Pandoc at: {selected_path}")
                # Update config
                config = load_config()
                config['pandoc_path'] = selected_path
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

def extract_rtm(input_mode='auto'):
    """Extract RTM from markdown files"""
    print("\n=== Extracting Requirements Traceability Matrix ===")
    python_exe = activate_venv()
    
    if input_mode == 'auto':
        # Try to find markdown files in output directory
        output_dir = BASE_DIR / "output"
        if output_dir.exists():
            md_files = list(output_dir.glob("*.md")) + list(output_dir.glob("**/*.md"))
            if md_files:
                print(f"Found {len(md_files)} markdown files for processing")
                # Use generate_rtm.py
                if (BASE_DIR / "generate_rtm.py").exists():
                    md_paths = " ".join(f'"{str(f)}"' for f in md_files)
                    run_command(f'"{python_exe}" generate_rtm.py --input {md_paths}')
                else:
                    print("Error: generate_rtm.py not found")
            else:
                print("No markdown files found in output directory")
                
                # Offer to process DOCX files directly
                docx_files = list((BASE_DIR / "input").glob("**/*.docx"))
                if docx_files:
                    print(f"Found {len(docx_files)} DOCX files in input directory")
                    if user_confirm("Would you like to process these DOCX files first?"):
                        convert_docx_to_markdown()
                        # Try RTM extraction again
                        extract_rtm(input_mode='auto')
    elif input_mode == 'manual':
        # Let user select files
        print("Please select input files for RTM extraction:")
        # Implementation for manual selection...
        
    # Update the configuration with LCP phase information
    update_lcp_phases()

def update_lcp_phases():
    """Update or display LCP phase information"""
    print("\n=== Project LCP Phase Information ===")
    config = load_config() or {}
    
    if 'lcp_phases' not in config:
        config['lcp_phases'] = {
            '0': 'Procurement',
            '1': 'Concept',
            '2': 'Detailed Design (FEED)',
            '3': 'Construction & Factory Acceptance',
            '4': 'Installation & Hook-up',
            '5': 'Commissioning & RCM Start',
            '6': 'SAT & RCM Training',
            '7': 'Operational & User Commissioning',
            '8': 'Integrated Commissioning'
        }
        save_config(config)
    
    # Display the phases
    print("\nLCP Phase definitions:")
    for phase, description in config['lcp_phases'].items():
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
    return response[0] == 'y'

def convert_docx_to_markdown():
    """Convert DOCX files to Markdown"""
    print("\n=== Converting Word Documents to Markdown ===")
    python_exe = activate_venv()
    
    # List available Word files
    input_dir = BASE_DIR / "input"
    word_files = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.doc"))
    
    if not word_files:
        print("No Word documents found in 'input' directory!")
        add_file = input("Do you want to add a Word document? (y/n): ")
        if add_file.lower() == 'y':
            print("Please copy your Word documents to the 'input' directory.")
            input("Press Enter when ready...")
            # Refresh file list
            word_files = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.doc"))
    
    if word_files:
        print("\nFound Word documents:")
        for i, file in enumerate(word_files, 1):
            print(f"[{i}] {file.name}")
        
        idx = input("\nSelect a file to convert (or 'a' for all): ")
        
        # Fix the word_to_md script first if needed
        fix_word_to_md()
        
        if idx.lower() == 'a':
            print("Converting all files...")
            for file in word_files:
                run_command(f'"{python_exe}" code/word_to_md.py "{file}"')
        elif idx.isdigit() and 1 <= int(idx) <= len(word_files):
            selected_file = word_files[int(idx) - 1]
            print(f"Converting {selected_file.name}...")
            run_command(f'"{python_exe}" code/word_to_md.py "{selected_file}"')
        else:
            print("Invalid selection.")

def display_menu():
    """Display the main menu"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== DOCX RTM Automation Terminal ===")
    print("Current Date and Time (UTC): " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print("Current User: " + os.environ.get('USERNAME', os.environ.get('USER', 'Unknown')))
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
    # Check if this is first run
    if not os.path.exists("config/paths.yaml") or not VENV_PATH.exists():
        print("First-time setup detected!")
        if user_confirm("Would you like to set up the environment now?"):
            setup_environment()
            print("\nSetup complete. Press Enter to continue to the main menu.")
            input()
    
    while True:
        choice = display_menu()
        
        if choice == 'A':
            print("\n=== Complete Setup ===")
            force_new = user_confirm("Recreate virtual environment if it exists?", default=False)
            setup_environment(force_new=force_new)
            
        elif choice == 'B':
            convert_docx_to_markdown()
            
        elif choice == 'C':
            extract_rtm(input_mode='auto')
            
        elif choice == 'D':
            update_lcp_phases()
            
        elif choice == 'E':
            print("\n=== Running Full Pipeline ===")
            python_exe = activate_venv()
            
            # First, make sure common issues are fixed
            fix_word_to_md()
            
            print("Running full pipeline...")
            print("This will execute the complete RTM automation workflow.")
            confirm = input("Continue? (y/n): ")
            
            if confirm.lower() == 'y':
                pipeline_script = BASE_DIR / "run_pipeline.py"
                if pipeline_script.exists():
                    run_command(f'"{python_exe}" run_pipeline.py')
                else:
                    print(f"Error: {pipeline_script} not found!")
            
        elif choice == 'F':
            print("\n=== Running Tests ===")
            python_exe = activate_venv()
            
            # Check if tests directory exists
            tests_dir = BASE_DIR / "tests"
            if not tests_dir.exists() or not list(tests_dir.glob('*.py')):
                print("No tests found in 'tests' directory!")
            else:
                tests_script = BASE_DIR / "run_tests.py"
                if tests_script.exists():
                    run_command(f'"{python_exe}" run_tests.py')
                else:
                    print("Running pytest directly...")
                    run_command(f'"{python_exe}" -m pytest')
            
        elif choice == 'G':
            git_operations()
            
        elif choice == 'H':
            print("\n=== Configure Settings ===")
            # Load current config
            config = load_config()
            
            while True:
                print("\nCurrent configuration:")
                for key, value in config.items():
                    print(f"  {key}: {value}")
                
                print("\nOptions:")
                print("[1] Edit pandoc_path")
                print("[2] Edit input/output paths")
                print("[3] Add/Edit custom setting")
                print("[4] Reset to defaults")
                print("[0] Back to Main Menu")
                
                config_choice = input("Select option: ")
                
                if config_choice == "1":
                    detect_pandoc()
                elif config_choice == "2":
                    input_dir = input("Enter input directory path [input]: ") or "input"
                    output_dir = input("Enter output directory path [output]: ") or "output"
                    config['input_dir'] = input_dir
                    config['output_dir'] = output_dir
                    save_config(config)
                elif config_choice == "3":
                    key = input("Enter setting name: ")
                    value = input("Enter setting value: ")
                    config[key] = value
                    save_config(config)
                elif config_choice == "4":
                    confirm = input("Reset all settings to defaults? (y/n): ")
                    if confirm.lower() == 'y':
                        default_config = {
                            'input_dir': 'input',
                            'output_dir': 'output',
                            'python_path': str(PYTHON_PATH)
                        }
                        # Add pandoc path if found
                        pandoc_path = shutil.which('pandoc.exe' if os.name == 'nt' else 'pandoc')
                        if pandoc_path:
                            default_config['pandoc_path'] = pandoc_path
                        
                        config = default_config
                        save_config(config)
                elif config_choice == "0":
                    break
            
        elif choice == 'I':
            print("\n=== Help & Documentation ===")
            readme_file = BASE_DIR / "README.md"
            
            if readme_file.exists():
                # Show README content
                if os.name == 'nt':  # Windows
                    os.system(f'type "{readme_file}"')
                else:  # Linux/Mac
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
            
        elif choice == 'Q':
            print("Exiting DOCX RTM Automation Terminal. Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()