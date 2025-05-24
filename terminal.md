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
PYTHON_PATH = "C:\\Users\\gbonthuy\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
BASE_DIR = Path(__file__).parent.absolute()
VENV_PATH = BASE_DIR / ".venv"
VENV_PYTHON = VENV_PATH / "Scripts" / "python.exe" if os.name == 'nt' else VENV_PATH / "bin" / "python"
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

def setup_environment():
    """Set up the virtual environment and install dependencies"""
    print("Creating virtual environment...")
    run_command(f'"{PYTHON_PATH}" -m venv "{VENV_PATH}"', use_venv=False)
    
    print("Installing requirements...")
    run_command(f'"{VENV_PYTHON}" -m pip install --upgrade pip')
    run_command(f'"{VENV_PYTHON}" -m pip install -r requirements.txt')
    
    # Check for Pandoc installation
    pandoc_installed = False
    if os.name == 'nt':  # Windows
        pandoc_path = shutil.which('pandoc.exe')
        if pandoc_path:
            pandoc_installed = True
    else:  # Linux/Mac
        pandoc_path = shutil.which('pandoc')
        if pandoc_path:
            pandoc_installed = True
    
    if not pandoc_installed:
        print("\nWARNING: Pandoc not found in system PATH!")
        print("Word to Markdown conversion requires Pandoc.")
        print("Please install Pandoc from: https://pandoc.org/installing.html")
        print("After installation, update the configuration with the pandoc path.")
    else:
        # Update config with Pandoc path
        config = load_config()
        config['pandoc_path'] = pandoc_path
        save_config(config)
        print(f"Pandoc found at: {pandoc_path}")
    
    # Create necessary directories
    for dir_name in ['input', 'output', 'config', 'docs']:
        os.makedirs(BASE_DIR / dir_name, exist_ok=True)

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

def git_operations():
    """Handle Git operations with proper VENV deactivation"""
    print("\n=== Git Operations ===")
    print("[1] Configure Git")
    print("[2] Push Changes")
    print("[3] Pull Updates")
    print("[4] View Status")
    print("[5] Set/Change Remote URL")
    print("[0] Back to Main Menu")
    
    choice = input("Select option: ")
    
    if choice == "1":
        # Temporarily deactivate VENV for Git configuration
        username = input("Enter Git username: ")
        email = input("Enter Git email: ")
        
        print("Configuring Git...")
        subprocess.run(f'git config --global user.name "{username}"', shell=True)
        subprocess.run(f'git config --global user.email "{email}"', shell=True)
        print("Git configured successfully.")
    elif choice == "2":
        print("Pushing changes...")
        commit_msg = input("Enter commit message (or press Enter for default): ") or "Update RTM automation files"
        subprocess.run(f'git add .', shell=True)
        subprocess.run(f'git commit -m "{commit_msg}"', shell=True)
        subprocess.run(f'git push', shell=True)
    elif choice == "3":
        print("Pulling updates...")
        subprocess.run("git pull", shell=True)
    elif choice == "4":
        print("Git status:")
        subprocess.run("git status", shell=True)
    elif choice == "5":
        remote_url = input("Enter new remote URL (e.g., https://github.com/username/repo.git): ")
        try:
            # Check if remote exists
            result = subprocess.run('git remote', shell=True, stdout=subprocess.PIPE, text=True)
            if 'origin' in result.stdout:
                subprocess.run(f'git remote set-url origin {remote_url}', shell=True)
                print(f"Remote URL updated to: {remote_url}")
            else:
                subprocess.run(f'git remote add origin {remote_url}', shell=True)
                print(f"Remote added: {remote_url}")
        except Exception as e:
            print(f"Error setting remote URL: {e}")

def fix_word_to_md():
    """Fix the word_to_md.py script to include pandoc_path from config"""
    code_dir = BASE_DIR / "code"
    word_to_md_path = code_dir / "word_to_md.py"
    
    if not word_to_md_path.exists():
        print(f"Error: {word_to_md_path} not found!")
        return False
    
    # Read current file
    with open(word_to_md_path, 'r') as f:
        content = f.read()
    
    # Check for KeyError: 'pandoc_path'
    if "paths['pandoc_path']" in content and "config = load_config()" in content:
        # Add pandoc path checking
        updated_content = content.replace(
            "paths['pandoc_path']",
            "paths.get('pandoc_path', shutil.which('pandoc') or 'pandoc')"
        )
        
        # Add shutil import if not present
        if "import shutil" not in updated_content:
            updated_content = updated_content.replace(
                "import os",
                "import os\nimport shutil"
            )
        
        # Save fixed file
        with open(word_to_md_path, 'w') as f:
            f.write(updated_content)
        
        print(f"Fixed {word_to_md_path} to handle missing pandoc_path!")
        return True
    else:
        print(f"Could not automatically fix {word_to_md_path}.")
        print("Consider manually editing the file to handle missing pandoc_path.")
        return False

def display_menu():
    """Display the main menu"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== DOCX RTM Automation Terminal ===")
    print("Current Date and Time (UTC): " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print("Current User: " + os.environ.get('USERNAME', os.environ.get('USER', 'Unknown')))
    print("\nSelect an option:")
    print("[A] Prepare Environment and Setup")
    print("[B] Fix Common Issues")
    print("[C] Convert Word Documents to Markdown")
    print("[D] Generate Requirements Traceability Matrix")
    print("[E] Run Full Pipeline")
    print("[F] Run Tests")
    print("[G] Git Operations")
    print("[H] Configure Settings")
    print("[I] Help & Documentation")
    print("[Q] Quit")
    
    return input("\nEnter your choice: ").upper()

def main():
    """Main function to run the terminal interface"""
    while True:
        choice = display_menu()
        
        if choice == 'A':
            print("\n=== Preparing Environment ===")
            setup_environment()
            # Check/configure Pandoc
            detect_pandoc()
            print("Setup complete!")
            
        elif choice == 'B':
            print("\n=== Fixing Common Issues ===")
            print("[1] Fix word_to_md.py (pandoc_path error)")
            print("[2] Fix Git remote issues")
            print("[3] Check directory structure")
            print("[4] Check Python dependencies")
            print("[0] Back to Main Menu")
            
            fix_choice = input("Select option: ")
            if fix_choice == "1":
                fix_word_to_md()
            elif fix_choice == "2":
                print("Checking Git configuration...")
                result = subprocess.run("git remote -v", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "origin" in result.stdout:
                    print("Remote 'origin' exists:")
                    print(result.stdout)
                    change = input("Do you want to change the remote URL? (y/n): ")
                    if change.lower() == 'y':
                        new_url = input("Enter new remote URL: ")
                        subprocess.run(f'git remote set-url origin {new_url}', shell=True)
                        print("Remote URL updated.")
                else:
                    print("Remote 'origin' not found.")
                    add = input("Do you want to add a remote URL? (y/n): ")
                    if add.lower() == 'y':
                        new_url = input("Enter remote URL: ")
                        subprocess.run(f'git remote add origin {new_url}', shell=True)
                        print("Remote URL added.")
            elif fix_choice == "3":
                print("Checking directory structure...")
                for dir_name in ['input', 'output', 'config', 'docs', 'code', 'scripts', 'src']:
                    dir_path = BASE_DIR / dir_name
                    if dir_path.exists():
                        print(f"✓ {dir_name} directory exists")
                    else:
                        print(f"✗ {dir_name} directory missing")
                        create = input(f"Create {dir_name} directory? (y/n): ")
                        if create.lower() == 'y':
                            os.makedirs(dir_path, exist_ok=True)
                            print(f"Created {dir_name} directory")
            elif fix_choice == "4":
                python_exe = activate_venv()
                print("Checking Python dependencies...")
                run_command(f'"{python_exe}" -m pip install -r requirements.txt')
            
        elif choice == 'C':
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
            
        elif choice == 'D':
            print("\n=== Generating Requirements Traceability Matrix ===")
            python_exe = activate_venv()
            
            # Check if the script exists
            rtm_script = BASE_DIR / "generate_rtm.py"
            if rtm_script.exists():
                run_command(f'"{python_exe}" generate_rtm.py')
            else:
                print(f"Error: {rtm_script} not found!")
                print("Would you like to create a basic RTM generator script?")
                create = input("Create basic RTM generator? (y/n): ")
                if create.lower() == 'y':
                    # Create basic RTM generator script
                    with open(rtm_script, 'w') as f:
                        f.write('''#!/usr/bin/env python3
"""
Requirements Traceability Matrix Generator
"""
import os
import sys
import yaml
import json
from pathlib import Path

def load_config():
    """Load global configuration"""
    config_file = Path('global_config.yaml')
    if not config_file.exists():
        print("Error: global_config.yaml not found!")
        return {}
    
    with open(config_file, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return {}

def generate_rtm():
    """Generate the Requirements Traceability Matrix"""
    print("Generating Requirements Traceability Matrix...")
    
    # Load configuration
    config = load_config()
    
    # Get input/output paths
    output_dir = Path(config.get('output_dir', 'output'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Find markdown files in output directory (converted from Word)
    md_files = list(output_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found in output directory!")
        print("Please convert Word documents to Markdown first.")
        return False
    
    # Create a basic RTM
    requirements = []
    
    for md_file in md_files:
        print(f"Processing {md_file.name}...")
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract requirements (very basic implementation)
        # This would need to be enhanced based on your specific format
        req_counter = 0
        for line in content.split('\\n'):
            if 'requirement' in line.lower() or 'shall' in line.lower():
                req_counter += 1
                requirements.append({
                    'id': f"REQ-{md_file.stem}-{req_counter}",
                    'description': line.strip(),
                    'source': md_file.name,
                    'status': 'Identified'
                })
    
    # Generate RTM output
    rtm_file = output_dir / 'requirements_traceability_matrix.json'
    with open(rtm_file, 'w', encoding='utf-8') as f:
        json.dump(requirements, f, indent=2)
    
    print(f"Generated RTM with {len(requirements)} requirements")
    print(f"Output saved to: {rtm_file}")
    
    # Also generate a markdown report
    rtm_md_file = output_dir / 'requirements_traceability_matrix.md'
    with open(rtm_md_file, 'w', encoding='utf-8') as f:
        f.write("# Requirements Traceability Matrix\\n\\n")
        f.write("| ID | Description | Source | Status |\\n")
        f.write("|---|---|---|---|\\n")
        
        for req in requirements:
            f.write(f"| {req['id']} | {req['description']} | {req['source']} | {req['status']} |\\n")
    
    print(f"Generated Markdown report: {rtm_md_file}")
    return True

if __name__ == "__main__":
    generate_rtm()
''')
                    print(f"Created basic RTM generator: {rtm_script}")
                    run_command(f'"{python_exe}" generate_rtm.py')
            
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
            print("2. Convert them to Markdown using Option C")
            print("3. Generate an RTM using Option D")
            print("4. Or run the full pipeline with Option E")
            
        elif choice == 'Q':
            print("Exiting DOCX RTM Automation Terminal. Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
```

## Quick Start Guide

1. **Installation and Setup**
   - Select option [A] to prepare the environment
   - This will create a virtual environment and install dependencies
   - It will also detect and configure Pandoc which is necessary for Word-to-Markdown conversion

2. **Fix Common Issues**
   - If you encounter errors, use option [B] to fix them
   - The most common issue is the missing pandoc_path configuration

3. **Convert Word Documents**
   - Place your Word (.docx or .doc) files in the 'input' directory
   - Select option [C] to convert them to Markdown

4. **Generate RTM**
   - After converting documents, select option [D] to generate an RTM
   - The RTM will be saved in the 'output' directory

5. **Run Full Pipeline**
   - Option [E] runs the complete automation process end-to-end

## Common Issues and Solutions

### pandoc_path KeyError
If you see this error:
```
KeyError: 'pandoc_path'
```

Use option [B] -> [1] to fix the word_to_md.py script by adding proper error handling for missing pandoc_path.

### Git Remote Issues
If you see this error:
```
Failed to add remote: error: remote origin already exists.
```

Use option [G] -> [5] to set or change the remote URL.

### Missing Files or Directories
Use option [B] -> [3] to check and create missing directories in the project structure.

## Setup Checklist

- [x] Python 3.6+ installed
- [ ] Pandoc installed (https://pandoc.org/installing.html)
- [ ] Virtual environment created and activated
- [ ] Word documents placed in 'input' directory
- [ ] Git configured (if using version control)

## Terminal Launcher

Save this markdown file as 'terminal.md', then create a 'terminal.py' file with the following content:

```python
#!/usr/bin/env python3

import os
import re
import sys

def extract_python_code(md_file):
    """Extract Python code from terminal.md"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Python code blocks
    python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
    
    if not python_blocks:
        print("Error: No Python code found in terminal.md")
        sys.exit(1)
    
    # Return the largest Python code block (main script)
    return max(python_blocks, key=len)

def main():
    """Run the terminal script from terminal.md"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    terminal_md = os.path.join(script_dir, "terminal.md")
    
    if not os.path.exists(terminal_md):
        print(f"Error: terminal.md not found in {script_dir}")
        sys.exit(1)
    
    # Extract Python code
    code = extract_python_code(terminal_md)
    
    # Execute the code
    exec(code)

if __name__ == "__main__":
    main()
```

Run the terminal interface by executing:
```
python terminal.py
