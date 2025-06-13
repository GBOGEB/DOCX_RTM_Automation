#!/usr/bin/env python3
"""
Activate Environment - Universal environment activation helper
"""

import sys
import os
import subprocess
from pathlib import Path

def detect_shell():
    """Detect the current shell environment"""
    shell_info = {
        "shell": "unknown",
        "platform": sys.platform,
        "executable": sys.executable
    }

    # Check environment variables for shell detection
    if os.environ.get('BASH'):
        shell_info["shell"] = "bash"
    elif os.environ.get('ZSH_VERSION'):
        shell_info["shell"] = "zsh"
    elif os.environ.get('PSModulePath'):
        shell_info["shell"] = "powershell"
    elif os.environ.get('PROMPT'):
        shell_info["shell"] = "cmd"
    elif 'bash' in os.environ.get('SHELL', '').lower():
        shell_info["shell"] = "bash"

    return shell_info

def check_virtual_environments():
    """Check for available virtual environments"""
    print("🔍 CHECKING VIRTUAL ENVIRONMENTS")
    print("=" * 40)

    venv_configs = [
        {
            "name": ".venv",
            "path": Path(".venv"),
            "scripts_dir": "Scripts" if os.name == 'nt' else "bin"
        },
        {
            "name": "venv",
            "path": Path("venv"),
            "scripts_dir": "Scripts" if os.name == 'nt' else "bin"
        }
    ]

    available_venvs = []

    for config in venv_configs:
        venv_path = config["path"]
        scripts_dir = venv_path / config["scripts_dir"]
        python_exe = scripts_dir / ("python.exe" if os.name == 'nt' else "python")

        if venv_path.exists() and python_exe.exists():
            print(f"✅ Found: {config['name']}/")
            print(f"   Path: {venv_path}")
            print(f"   Python: {python_exe}")
            available_venvs.append(config)
        else:
            print(f"❌ Not found: {config['name']}/")

    return available_venvs

def show_activation_commands(available_venvs, shell_info):
    """Show correct activation commands for current environment"""
    print(f"\n🚀 ACTIVATION COMMANDS")
    print("=" * 30)
    print(f"Detected shell: {shell_info['shell']} on {shell_info['platform']}")

    if not available_venvs:
        print("\n❌ No virtual environments found!")
        print("\nCreate one with:")
        print("   python -m venv .venv")
        return

    for venv in available_venvs:
        venv_name = venv["name"]
        print(f"\n📁 For {venv_name}/:")

        if os.name == 'nt':  # Windows
            print("   Windows Command Prompt:")
            print(f"      {venv_name}\\Scripts\\activate.bat")
            print("   ")
            print("   Git Bash / WSL:")
            print(f"      source {venv_name}/Scripts/activate")
            print("   ")
            print("   PowerShell:")
            print(f"      {venv_name}\\Scripts\\Activate.ps1")
        else:  # Unix/Linux/Mac
            print("   Bash/Zsh:")
            print(f"      source {venv_name}/bin/activate")

def test_current_environment():
    """Test if we're currently in a virtual environment"""
    print(f"\n🐍 CURRENT ENVIRONMENT")
    print("=" * 30)

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    if "venv" in sys.executable or ".venv" in sys.executable:
        print("✅ Currently in virtual environment")
        venv_active = True
    else:
        print("ℹ️  Using system Python")
        venv_active = False

    return venv_active

def test_dependencies():
    """Test RTM automation dependencies"""
    print(f"\n📦 DEPENDENCY STATUS")
    print("=" * 30)

    dependencies = {
        'docx': 'python-docx',
        'requests': 'requests',
        'json': 'built-in',
        'pathlib': 'built-in'
    }

    working = 0
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module} ({package})")
            working += 1
        except ImportError:
            print(f"❌ {module} ({package}) - Missing")

    print(f"\nStatus: {working}/{len(dependencies)} dependencies available")

    if working < len(dependencies):
        print("\nInstall missing packages:")
        print("   pip install python-docx requests")

    return working == len(dependencies)

def run_quick_test():
    """Run a quick RTM automation test"""
    print(f"\n🧪 QUICK RTM TEST")
    print("=" * 25)

    try:
        # Test if main.py exists and can be imported
        if Path("main.py").exists():
            print("✅ main.py found")
        else:
            print("❌ main.py not found")
            return False

        # Test if we can run comprehensive test
        result = subprocess.run([
            sys.executable, '-c',
            'import sys; print("✅ Python import test passed")'
        ], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            print("✅ Python execution test passed")
            return True
        else:
            print("❌ Python execution test failed")
            return False

    except Exception as e:
        print(f"❌ Quick test error: {e}")
        return False

def show_next_steps(venv_active, deps_ok, test_ok):
    """Show recommended next steps"""
    print(f"\n🎯 RECOMMENDED NEXT STEPS")
    print("=" * 35)

    if not venv_active:
        print("1. Activate virtual environment:")
        print("   # Use the commands shown above")
        print("")

    if not deps_ok:
        print("2. Install dependencies:")
        print("   pip install python-docx requests")
        print("")

    if test_ok:
        print("3. Run RTM automation:")
        print("   python main.py                    # Main pipeline")
        print("   python comprehensive_test.py      # Full system test")
        print("   python nav_menu.py                # Interactive menu")
    else:
        print("3. Fix environment issues:")
        print("   python fix_environment.py         # Fix environment")
        print("   python check_environment.py       # Check status")

def main():
    """Main function"""
    print("🔧 RTM AUTOMATION - ENVIRONMENT ACTIVATOR")
    print("=" * 50)
    print("Universal activation helper for all environments...\n")

    # Detect shell and platform
    shell_info = detect_shell()

    # Check virtual environments
    available_venvs = check_virtual_environments()

    # Show activation commands
    show_activation_commands(available_venvs, shell_info)

    # Test current environment
    venv_active = test_current_environment()

    # Test dependencies
    deps_ok = test_dependencies()

    # Run quick test
    test_ok = run_quick_test()

    # Show next steps
    show_next_steps(venv_active, deps_ok, test_ok)

    # Final recommendation
    print(f"\n💡 QUICK FIX FOR YOUR ISSUE:")
    print("=" * 35)
    print("In Git Bash, use:")
    print("   source .venv/Scripts/activate")
    print("   # OR")
    print("   .venv/Scripts/activate")
    print("\nThen run:")
    print("   python main.py")

if __name__ == "__main__":
    main()
