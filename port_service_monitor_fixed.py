#!/usr/bin/env python3
"""
RTM Port and Service Monitor - Fixed version without infinite loops
"""

import socket
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def check_port_status(port, host='localhost'):
    """Check if a port is open/listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def find_rtm_services():
    """Find RTM-related services and processes."""
    print("🔍 RTM Service Discovery")
    print("=" * 35)

    # Common development ports to check
    common_ports = {
        3000: "React/Node.js Development Server",
        5000: "Flask Development Server",
        8000: "Django/HTTP Development Server",
        8080: "Alternative HTTP Server",
        8888: "Jupyter Notebook",
        9000: "Various Development Servers",
        4000: "Jekyll/Static Site Server",
        5173: "Vite Development Server",
        3001: "Alternative React Server"
    }

    print("📊 Checking Common Development Ports:")
    active_ports = []

    for port, description in common_ports.items():
        is_open = check_port_status(port)
        status = "🟢 ACTIVE" if is_open else "⚪ INACTIVE"
        print(f"   Port {port:4d}: {status} - {description}")

        if is_open:
            active_ports.append({"port": port, "description": description})

    return active_ports

def check_python_processes():
    """Check for running Python processes related to RTM."""
    print(f"\n🐍 Python Processes Check:")
    print("-" * 30)

    try:
        # Try to find Python processes
        if sys.platform == "win32":
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True, text=True, timeout=10
            )
        else:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True, text=True, timeout=10
            )

        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            python_processes = [line for line in output_lines if 'python' in line.lower()]

            if python_processes:
                print(f"   Found {len(python_processes)} Python process(es):")
                for i, process in enumerate(python_processes[:5], 1):
                    print(f"   {i}. {process.strip()}")

                if len(python_processes) > 5:
                    print(f"   ... and {len(python_processes) - 5} more")
            else:
                print("   No Python processes found")
        else:
            print("   Could not check processes")

    except Exception as e:
        print(f"   Error checking processes: {e}")

def check_rtm_files_running():
    """Check if any RTM files might be running as services."""
    print(f"\n📁 RTM File Service Check:")
    print("-" * 32)

    # Check for common RTM service files
    service_files = [
        "extension_dashboard.py",
        "rtm_workflow_manager.py",
        "extension_manager.py",
        "simple_quality_check.py",
        "rtm_web_dashboard.py"
    ]

    running_services = []

    for service_file in service_files:
        file_path = Path(service_file)

        if file_path.exists():
            print(f"   📄 {service_file}: ✅ Available")

            # Check if it might be designed to run as a service
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                service_indicators = [
                    'dashboard', 'monitor', 'server', 'listen',
                    'host=', 'port=', 'app.run', 'serve', 'flask'
                ]

                has_service_code = any(indicator in content.lower() for indicator in service_indicators)

                if has_service_code:
                    print(f"      🔧 May support service mode")
                    running_services.append(service_file)
                else:
                    print(f"      📋 Script/utility file")
            except Exception:
                print(f"      ❓ Could not analyze file")
        else:
            print(f"   📄 {service_file}: ❌ Not found")

    return running_services

def check_vscode_extensions():
    """Check VS Code extension status (if applicable)."""
    print(f"\n🔧 VS Code Extension Check:")
    print("-" * 32)

    # Check for VS Code workspace/settings
    vscode_dir = Path(".vscode")
    if vscode_dir.exists():
        print("   📁 .vscode directory found")

        settings_file = vscode_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                print(f"   ⚙️ VS Code settings configured")

                # Check for relevant settings
                relevant_keys = [
                    'python.defaultInterpreterPath',
                    'python.terminal.activateEnvironment',
                    'files.associations'
                ]

                for key in relevant_keys:
                    if key in settings:
                        print(f"      {key}: ✅")

            except Exception as e:
                print(f"   ⚠️ Could not read settings: {e}")

        extensions_file = vscode_dir / "extensions.json"
        if extensions_file.exists():
            print("   📦 Extensions configuration found")
    else:
        print("   ℹ️ No VS Code configuration found")

def generate_service_report():
    """Generate a comprehensive service report."""
    print(f"\n📊 RTM SERVICE REPORT")
    print("=" * 30)

    report = {
        "timestamp": datetime.now().isoformat(),
        "active_ports": find_rtm_services(),
        "rtm_directory": str(Path.cwd()),
        "python_executable": sys.executable,
        "platform": sys.platform
    }

    # Save report
    report_path = Path("rtm_service_report.json")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n📋 Service report saved to: {report_path}")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")

    return report

def explain_port_tabs():
    """Explain what PORT tabs typically show."""
    print(f"\n❓ ABOUT PORT TABS:")
    print("=" * 25)
    print("""
PORT tabs typically show:

🌐 WEB SERVERS:
   • Development servers (React, Flask, Django)
   • Local web applications running
   • API endpoints and services

📊 DEVELOPMENT TOOLS:
   • Jupyter notebooks (port 8888)
   • Documentation servers
   • Hot-reload development servers

🔧 RTM SYSTEM CONTEXT:
   • Your RTM system is primarily file-based
   • Scripts run and exit (no persistent servers)
   • No web interface by default
   • Extensions work through file processing

💡 NORMAL BEHAVIOR:
   • Empty PORT tabs are expected for RTM
   • RTM processes documents and exits
   • No background services running
   • This is the correct operation mode

🚀 IF YOU WANT WEB INTERFACE:
   • Run: python rtm_web_dashboard.py
   • Or create a Flask/FastAPI wrapper
   • Monitor real-time processing
""")

def main():
    """Main monitoring function."""
    print("🔍 RTM Port and Service Monitor (Fixed)")
    print("=" * 45)
    print("Checking what services and ports are active...")

    # Find active services
    active_ports = find_rtm_services()

    # Check Python processes
    check_python_processes()

    # Check RTM service files
    service_files = check_rtm_files_running()

    # Check VS Code setup
    check_vscode_extensions()

    # Generate report
    report = generate_service_report()

    # Explain PORT tabs
    explain_port_tabs()

    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"   Active Ports: {len(active_ports)}")
    print(f"   Service-capable RTM Files: {len(service_files)}")
    print(f"   RTM System Status: File-based processing (no persistent services)")

    if not active_ports:
        print(f"\n✅ NORMAL: No active ports detected")
        print(f"   This is expected for your RTM system")
        print(f"   RTM processes files and exits cleanly")
    else:
        print(f"\n🔍 ACTIVE SERVICES DETECTED:")
        for port_info in active_ports:
            print(f"   Port {port_info['port']}: {port_info['description']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
