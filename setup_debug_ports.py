#!/usr/bin/env python3
"""
Debugging port configuration helper for RTM Automation.

This script helps configure and test ports needed for debugging,
and creates necessary configuration files for VSCode.
"""
import os
import sys
import socket
import subprocess
import json
from pathlib import Path


def check_port_availability(port):
    """Check if a port is available for listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True  # Port is available
        except OSError:
            return False  # Port is in use


def test_port_connectivity(port):
    """Test if a specific port can be connected to."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                return True  # Port is open and connectable
            else:
                return False  # Port is not connectable
    except Exception:
        return False


def create_vscode_launch_config():
    """Create or update VSCode launch.json for debugging."""
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)

    launch_path = vscode_dir / 'launch.json'

    # Default configuration
    debug_configs = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": False,
                "env": {"PYTHONPATH": "${workspaceFolder}"}
            },
            {
                "name": "Python: Remote Attach (Port 5678)",
                "type": "python",
                "request": "attach",
                "connect": {"host": "localhost", "port": 5678},
                "pathMappings": [{"localRoot": "${workspaceFolder}", "remoteRoot": "."}],
                "justMyCode": False
            },
            {
                "name": "Python: Web Server (Port 8000)",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/path/to/your/server.py",  # Change this to your server script
                "console": "integratedTerminal",
                "env": {"PORT": "8000"},
                "args": ["--port", "8000"]
            },
            {
                "name": "Python: Debug Test",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "purpose": ["debug-test"],
                "console": "integratedTerminal",
                "justMyCode": False
            }
        ]
    }

    # Try to load existing config
    if launch_path.exists():
        try:
            with open(launch_path, 'r') as f:
                existing_config = json.load(f)

            # Merge with existing configurations
            if "configurations" in existing_config:
                # Keep non-python configurations and add our debug configs
                non_python_configs = [
                    cfg for cfg in existing_config["configurations"]
                    if cfg.get("type") != "python"
                ]

                # Replace python configs with our updated ones
                debug_configs["configurations"].extend(non_python_configs)
        except Exception as e:
            print(f"Error reading existing launch.json: {e}")
            print("Creating new launch.json file")

    # Write the configuration
    with open(launch_path, 'w') as f:
        json.dump(debug_configs, f, indent=4)

    print(f"Created VSCode launch configuration in {launch_path}")


def create_debug_sample_script():
    """Create a sample script for testing debugging."""
    sample_path = Path('debug_sample.py')

    script_content = """#!/usr/bin/env python3
\"\"\"
Sample script for testing debugging configuration.
\"\"\"
import os
import sys
import debugpy


def setup_debugger(port=5678):
    \"\"\"
    Set up the debugger to listen on a specific port.

    Args:
        port: Port to listen on (default: 5678)
    \"\"\"
    # Enable debugging based on environment variable or direct call
    should_debug = os.environ.get('ENABLE_DEBUGGER', 'False').lower() == 'true'

    if should_debug:
        print(f"Enabling debugger on port {port}")
        debugpy.listen(("0.0.0.0", port))
        print(f"Debugger is now listening on port {port}")

        # Uncomment to pause execution until a debugger attaches
        # debugpy.wait_for_client()
        # print("Debugger attached. Continuing execution.")


def main():
    \"\"\"Main function with debugging example.\"\"\"
    # Set up debugger
    setup_debugger()

    # Simple debugging demonstration
    a = 10
    b = 5

    # Good place to set a breakpoint
    result = a + b
    print(f"Result: {result}")

    # More complex calculation (step through this in debugger)
    values = [1, 2, 3, 4, 5]
    sum_result = 0

    for i, val in enumerate(values):
        # Another good place for a breakpoint
        sum_result += val * i

    print(f"Sum result: {sum_result}")

    # Wait for user input before exiting
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
"""

    with open(sample_path, 'w') as f:
        f.write(script_content)

    print(f"Created debugging sample script: {sample_path}")
    print("Run with: python debug_sample.py")
    print("To enable debugger: set ENABLE_DEBUGGER=true before running")


def check_firewall_for_ports(ports):
    """Check if ports are allowed through Windows Firewall."""
    if sys.platform != "win32":
        print("Firewall check is only available on Windows.")
        return

    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print("Error checking firewall rules. You may need administrator privileges.")
            return

        rules = result.stdout

        print("\nChecking ports in Windows Firewall...")
        for port in ports:
            if f"LocalPort={port}" in rules:
                print(f"✅ Port {port} is configured in Windows Firewall")
            else:
                print(f"❌ Port {port} is not explicitly configured in Windows Firewall")

    except Exception as e:
        print(f"Error checking firewall: {e}")


def create_firewall_rule_script():
    """Create a script to add firewall rules for debugging ports."""
    script_path = Path('allow_debug_ports.bat')

    script_content = """@echo off
REM This script needs to be run as Administrator
echo Creating Windows Firewall rules for debugging ports

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator.
    echo Please right-click and select "Run as Administrator".
    pause
    exit /b 1
)

REM Add rules for debugging ports
echo Adding rule for port 5678 (Python debugpy)...
netsh advfirewall firewall add rule name="Python Debugger (5678)" dir=in action=allow protocol=TCP localport=5678

echo Adding rule for port 8000 (Web Debug Server)...
netsh advfirewall firewall add rule name="Web Debug Server (8000)" dir=in action=allow protocol=TCP localport=8000

echo Adding rule for port 9229 (Node.js Debugger)...
netsh advfirewall firewall add rule name="Node.js Debugger (9229)" dir=in action=allow protocol=TCP localport=9229

echo.
echo Firewall rules have been added.
echo.
pause
"""

    with open(script_path, 'w') as f:
        f.write(script_content)

    print(f"\nCreated firewall rule script: {script_path}")
    print("Run this script as Administrator to open debugging ports in Windows Firewall")


def main():
    """Main function."""
    debug_ports = [5678, 8000, 9229]

    print("======================================")
    print("Debugging Port Configuration Assistant")
    print("======================================")

    # Check port status
    print("\nChecking debugging ports...")
    for port in debug_ports:
        if check_port_availability(port):
            print(f"✅ Port {port} is available")
        else:
            print(f"❌ Port {port} is in use")

    # Create VSCode configuration
    print("\nCreating VSCode debugging configuration...")
    create_vscode_launch_config()

    # Create example debugging script
    print("\nCreating sample debugging script...")
    create_debug_sample_script()

    # Check Windows Firewall if on Windows
    check_firewall_for_ports(debug_ports)

    # Create firewall script for Windows
    if sys.platform == "win32":
        create_firewall_rule_script()

    print("\n======================================")
    print("Debugging Setup Complete!")
    print("======================================")
    print("\nTo enable debugging:")
    print("1. Install debugpy: pip install debugpy")
    print("2. Run the sample script: python debug_sample.py")
    print("3. In VSCode, open the Debug panel and select 'Python: Remote Attach (Port 5678)'")
    print("4. Set breakpoints and click Start Debugging (F5)")
    print("\nTo open debugging ports in Windows Firewall:")
    print("- Run 'allow_debug_ports.bat' as Administrator")


if __name__ == "__main__":
    main()
