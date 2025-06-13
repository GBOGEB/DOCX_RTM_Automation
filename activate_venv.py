#!/usr/bin/env python3
"""
Virtual Environment Activation Helper
Finds and provides correct activation commands for your system
"""

import os
import sys
from pathlib import Path

def find_virtual_environments():
    """Find all virtual environments in the project"""
    print("🔍 SEARCHING FOR VIRTUAL ENVIRONMENTS")
    print("=" * 45)

    venv_locations = [
        "scripts/venv",
        "venv",
        ".venv",
        "env",
        "Scripts/venv",
        "scripts\\venv"
    ]

    found_venvs = []

    for location in venv_locations:
        venv_path = Path(location)
        if venv_path.exists() and venv_path.is_dir():
            print(f"📁 Found: {venv_path.absolute()}")
            found_venvs.append(venv_path)

            # Check contents
            contents = list(venv_path.iterdir())
            print(f"   Contents: {[f.name for f in contents[:5]]}")

    if not found_venvs:
        print("❌ No virtual environments found")
        return []

    return found_venvs

def get_activation_commands(venv_path):
    """Get the correct activation commands for a virtual environment"""
    commands = []

    if os.name == 'nt':  # Windows
        # Command Prompt
        cmd_activate = venv_path / "Scripts" / "activate.bat"
        if cmd_activate.exists():
            commands.append(("Command Prompt", str(cmd_activate)))

        # PowerShell
        ps_activate = venv_path / "Scripts" / "Activate.ps1"
        if ps_activate.exists():
            commands.append(("PowerShell", f"& {ps_activate}"))

        # Git Bash (Unix-style on Windows)
        bash_activate = venv_path / "Scripts" / "activate"
        if bash_activate.exists():
            commands.append(("Git Bash", f"source {bash_activate}"))

    else:  # Unix/Linux/Mac
        unix_activate = venv_path / "bin" / "activate"
        if unix_activate.exists():
            commands.append(("Terminal", f"source {unix_activate}"))

    return commands

def show_activation_instructions():
    """Show detailed activation instructions"""
    print("\n🚀 VIRTUAL ENVIRONMENT ACTIVATION")
    print("=" * 40)

    venvs = find_virtual_environments()

    if not venvs:
        print("\n💡 No virtual environment found. Options:")
        print("   1. Create one: python -m venv scripts/venv")
        print("   2. Use system Python: python quick_start_system_python.py")
        return False

    for i, venv_path in enumerate(venvs, 1):
        print(f"\n📦 Virtual Environment #{i}: {venv_path}")
        print("-" * 30)

        commands = get_activation_commands(venv_path)

        if commands:
            print("✅ Activation commands:")
            for shell, command in commands:
                print(f"   {shell:15}: {command}")
        else:
            print("❌ No activation scripts found")

        # Show what's inside
        scripts_dir = venv_path / "Scripts" if os.name == 'nt' else venv_path / "bin"
        if scripts_dir.exists():
            scripts = [f.name for f in scripts_dir.iterdir() if f.name.startswith('activate')]
            print(f"   Available scripts: {scripts}")

    return True

def test_current_environment():
    """Test if we're currently in a virtual environment"""
    print("\n🧪 CURRENT ENVIRONMENT TEST")
    print("=" * 35)

    print(f"Python executable: {sys.executable}")

    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Currently IN a virtual environment")
        if hasattr(sys, 'base_prefix'):
            print(f"   Base Python: {sys.base_prefix}")
        print(f"   Virtual env: {sys.prefix}")
        return True
    else:
        print("❌ NOT in a virtual environment")
        print("   Using system Python")
        return False

def main():
    """Main function"""
    print("🔧 VIRTUAL ENVIRONMENT HELPER")
    print("=" * 35)

    # Test current environment
    in_venv = test_current_environment()

    if in_venv:
        print("\n🎉 You're already in a virtual environment!")
        print("You can now run your Python scripts normally.")
    else:
        # Show activation instructions
        found = show_activation_instructions()

        if found:
            print("\n💡 QUICK TIPS:")
            print("   • Copy and paste the activation command for your shell")
            print("   • On Windows, try Command Prompt if PowerShell fails")
            print("   • After activation, your prompt should show (venv)")

    print("\n🚀 Next steps after activation:")
    print("   python quick_start_system_python.py")
    print("   python main.py")

if __name__ == "__main__":
    main()
