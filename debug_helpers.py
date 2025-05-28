#!/usr/bin/env python3
"""
Debug helper utilities for the DOCX RTM Automation project.
This script helps diagnose common issues with configurations and dependencies.
"""

import os
import sys
import socket
import importlib
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print(f"Python version: {platform.python_version()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")

    # Check if it's the expected virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_path = os.path.join(Path(__file__).parent, ".venv")
    is_project_venv = os.path.exists(venv_path) and (venv_path in sys.executable or '.venv' in sys.executable)

    if in_venv:
        print("✅ Running in a virtual environment")
        if is_project_venv:
            print("✅ Using project's virtual environment")
        else:
            print("⚠️ Not using project's virtual environment")
    else:
        print("⚠️ Not running in a virtual environment")

def check_project_structure():
    """Check project directory structure."""
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")

    # Expected directories
    expected_dirs = ["src", "agents", "tests", "output", "input", "config"]

    print("\nDirectory structure:")
    for d in expected_dirs:
        path = project_root / d
        if path.exists():
            print(f"✅ {d}/")

            # For some key directories, list their contents
            if d in ["src", "agents"]:
                files = list(path.glob("*.py"))
                subdirs = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith("__")]

                if files:
                    for f in files[:5]:  # Show up to 5 files
                        print(f"    |- {f.name}")
                    if len(files) > 5:
                        print(f"    |- ... ({len(files) - 5} more files)")

                if subdirs:
                    for s in subdirs:
                        subfiles = list(s.glob("*.py"))
                        print(f"    |- {s.name}/")
                        if subfiles:
                            for sf in subfiles[:3]:  # Show up to 3 files per subdir
                                print(f"        |- {sf.name}")
                            if len(subfiles) > 3:
                                print(f"        |- ... ({len(subfiles) - 3} more files)")
        else:
            print(f"❌ {d}/ (not found)")

def check_imports():
    """Check if key modules can be imported."""
    print("\nChecking imports:")
    modules_to_check = [
        "agents.agent_common",
        "agents.git_agent",
        "agents.requirement_analyzer",
        "agents.copilot_agent",
        "src.core.word_to_md",
        "src.extractors.extract_rtm",
        "src.visualizers.rtm_visualizer"
    ]

    for module in modules_to_check:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")

def check_network_connection(host="127.0.0.1", ports=[8000, 5678, 9229]):
    """Check if debug ports are open and accessible."""
    print("\nChecking network connections for debugging:")

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"✅ Port {port} is open")
        else:
            print(f"❌ Port {port} is closed or blocked")
        sock.close()

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\nChecking dependencies:")
    required_packages = [
        "pytest", "pyyaml", "docx2python", "markdown", "rich", "lxml",
        "flake8", "black", "isort", "mypy", "pylint"
    ]

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")

def check_vscode_debugger():
    """Check if VSCode debugger extension is correctly installed."""
    print("\nChecking VSCode debugger:")
    vscode_dir = os.path.expanduser("~/.vscode/extensions")

    if os.path.exists(vscode_dir):
        debugpy_extensions = [d for d in os.listdir(vscode_dir) if "debugpy" in d.lower()]
        if debugpy_extensions:
            print(f"✅ VSCode Python debugger extensions found:")
            for ext in debugpy_extensions:
                print(f"  - {ext}")
        else:
            print("❌ VSCode Python debugger extension not found")
    else:
        print("❓ VSCode extensions directory not found at usual location")

    # Check if debugpy can be imported
    try:
        import debugpy
        print(f"✅ debugpy module is installed (version {debugpy.__version__})")
    except ImportError:
        print("❌ debugpy module not installed")
    except AttributeError:
        print("✅ debugpy module is installed (version unknown)")

def check_file_permissions():
    """Check if key files have execution permission (on Unix systems)."""
    if os.name == 'posix':  # Unix-like system
        print("\nChecking file permissions:")
        scripts = [
            "run.sh", "run_tests.sh", "setup_venv.sh",
            "lint.sh", "fix_imports.sh", "install_dependencies.sh"
        ]

        for script in scripts:
            path = Path(__file__).parent / script
            if path.exists():
                is_executable = os.access(path, os.X_OK)
                if is_executable:
                    print(f"✅ {script} is executable")
                else:
                    print(f"❌ {script} is not executable")
            else:
                print(f"❓ {script} not found")

def run_diagnostics():
    """Run all diagnostic checks."""
    print("==== DOCX RTM Automation Diagnostics ====\n")

    check_python_version()
    check_project_structure()
    check_imports()
    check_dependencies()
    check_network_connection()
    check_vscode_debugger()
    check_file_permissions()

    print("\n==== End of Diagnostics ====")
    print("\nIf you're encountering connection errors with the debugger:")
    print("1. Try restarting VS Code")
    print("2. Check if another debugger session is already running")
    print("3. Verify the port isn't blocked by a firewall")
    print("4. Try using a different port for debugging")

if __name__ == "__main__":
    run_diagnostics()
