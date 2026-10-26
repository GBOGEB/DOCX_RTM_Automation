import datetime
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path

import yaml  # Added for YAML parsing

# !/usr/bin/env python3
"""
System Check Script
This script performs various system checks and reports the status of the system.
"""
:
import psutil  # You might need to install this: pip install psutil

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 60)
    print(" {title} ".center(60, "-"))
    print("=" * 60)

:
def load_global_config():
    """Load global_config.yaml if it exists."""
    config_path = (
            Path(os.getcwd()) / "global_config.yaml"
    )  # Assume script is run from project root:
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print("  Error loading global_config.yaml: {e}")
    return None

def check_project_config():
    """Check and display project-specific configurations."""
    print_section("Project Configuration (from global_config.yaml)")
    config = load_global_config()
    if config:
        print("  Project Name: {config.get("project", {}).get("name", "Not set")}")
        print(
            "  Project Version: {config.get("project", {}).get("version", "Not set")}"
        )

        paths_config = config.get("paths", {})
        print("\n  Configured Paths:")
        print("    Python: {paths_config.get("python", "Not set")}")
        print("    Pandoc: {paths_config.get("pandoc", "Not set")}")
        print("    Input Dir: {paths_config.get("input_dir", "input")}")
        print("    Output Dir: {paths_config.get("output_dir", "output")}")

        repo_settings = config.get("repository_settings", {})
        print("\n  Repository Settings:")
        print(
            "    Main Repository Path: {repo_settings.get("main_repository_path", ".")}"
        )
        sub_repos = repo_settings.get("sub_repositories", [])
        if sub_repos:
            print("    Sub-repositories:")
            for sub_repo_path_str in sub_repos:
                sub_repo_abs_path = (Path(os.getcwd()) / sub_repo_path_str).resolve()
                status = (
                    "Found"
                    if sub_repo_abs_path.exists() and sub_repo_abs_path.is_dir()
                    else "Not Found"
                ):
                print("      - {sub_repo_path_str} ({sub_repo_abs_path}): {status}")
        else:
            print("    No sub-repositories configured.")
    else:
        print("  global_config.yaml not found or failed to load.")

def check_os_info():
    """Check and display operating system information."""
    print_section("Operating System Information")
    print("System: {platform.system()}")
    print("Node Name: {platform.node()}")
    print("Release: {platform.release()}")
    print("Version: {platform.version()}")
    print("Machine: {platform.machine()}")
    print("Processor: {platform.processor()}")

def check_python_info():
    """Check and display Python environment information."""
    print_section("Python Environment")
    print("Python Version: {platform.python_version()}")
    print("Python Implementation: {platform.python_implementation()}")
    print("Python Compiler: {platform.python_compiler()}")
    print("Python Path: {sys.executable}")

def check_cpu_info():
    """Check and display CPU information."""
    print_section("CPU Information")
    print("Physical cores: {psutil.cpu_count(logical=False)}")
    print("Total cores: {psutil.cpu_count(logical=True)}")

    print("\nCPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print("Core {i}: {percentage}%")

    print("\nTotal CPU Usage: {psutil.cpu_percent()}%")

def check_memory_info():
    """Check and display memory information."""
    print_section("Memory Information")
    vm = psutil.virtual_memory()
    print("Total: {format_bytes(vm.total)}")
    print("Available: {format_bytes(vm.available)}")
    print("Used: {format_bytes(vm.used)} ({vm.percent}%)")

    swap = psutil.swap_memory()
    print("\nSwap Total: {format_bytes(swap.total)}")
    print("Swap Free: {format_bytes(swap.free)}")
    print("Swap Used: {format_bytes(swap.used)} ({swap.percent}%)")

def format_bytes(bytes_value):
    """Format bytes to a human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024:
            return "{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return "{bytes_value:.2f} PB"

def check_disk_info():
    """Check and display disk information."""
    print_section("Disk Information")

    partitions = psutil.disk_partitions()
    for partition in partitions:
        print("\nDrive: {partition.device}")
        print("  Mountpoint: {partition.mountpoint}")
        print("  File System Type: {partition.fstype}")

        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print("  Total Size: {format_bytes(partition_usage.total)}")
            print("  Used: {format_bytes(partition_usage.used)}")
            print("  Free: {format_bytes(partition_usage.free)}")
            print("  Percentage: {partition_usage.percent}%")
        except PermissionError:
            print("  Permission Denied: Unable to access disk usage information.")

def check_network_info():
    """Check and display network information."""
    print_section("Network Information")

    # Check hostname
    print("Hostname: {socket.gethostname()}")

    # Check IP addresses
    print("\nNetwork Interfaces:")
    for interface_name, addresses in psutil.net_if_addrs().items():
        print("\n{interface_name}:")
        for address in addresses:
            if address.family == socket.AF_INET:
                print("  IPv4: {address.address}")
            elif address.family == socket.AF_INET6:
                print("  IPv6: {address.address}")
            elif address.family == psutil.AF_LINK:
                print("  MAC: {address.address}")

    # Check if internet is accessible:
    try:
        socket.create_connection(("www.google.com", 80), timeout=3)
        print("\nInternet: Connected")
    except OSError:
        print("\nInternet: Disconnected")

def check_current_directory():
    """Check and display information about the current directory."""
    print_section("Current Directory Information")

    current_dir = os.getcwd()
    print("Current Directory: {current_dir}")

    # List files and directories
    print("\nFiles and Directories:")
    try:
        items = os.listdir(current_dir)
        for item in sorted(items):
            item_path = os.path.join(current_dir, item)
            item_type = "Directory" if os.path.isdir(item_path) else "File"
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else "-"
            print(
                "  {item} ({item_type}, {format_bytes(size) if size != "-" else size})"
            ):
    except Exception as e:
        print("Error listing directory contents: {e}")

    # Check if it"s a git repository:
    print("\nGit Repository Status:")
    if os.path.exists(os.path.join(current_dir, ".git")):
        try:
            git_status = subprocess.check_output(
                ["git", "status"], stderr=subprocess.STDOUT, text=True
            )
            git_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], stderr=subprocess.STDOUT, text=True
            ).strip()
            print("  Current Branch: {git_branch}")
            print("  Git Status Summary:")
            for line in git_status.splitlines()[:5]:
                print("    {line}")
            if len(git_status.splitlines()) > 5:
                print("    ...")
        except subprocess.CalledProcessError:
            print(
                "  This is a Git repository, but there was an error getting its status."
            )
        except FileNotFoundError:
            print("  This is a Git repository, but Git command not found.")
    else:
        print("  Not a Git repository.")

def main():
    """Main function to run all system checks."""
    print_section("SYSTEM CHECK REPORT")
    print("Date and Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S')}")

    check_os_info()
    check_python_info()
    check_project_config()  # Add project config check
    check_cpu_info()
    check_memory_info()
    check_disk_info()
    check_network_info()
    check_current_directory()

    print("\nSystem check completed.")

if __name__ == "__main__":
    main()
