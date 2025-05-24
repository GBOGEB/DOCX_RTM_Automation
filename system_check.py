import os
import sys
import platform
import socket
import datetime
import shutil
import subprocess

#!/usr/bin/env python3
"""
System Check Script
This script performs various system checks and reports the status of the system.
"""

import psutil  # You might need to install this: pip install psutil


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "-"))
    print("=" * 60)


def check_os_info():
    """Check and display operating system information."""
    print_section("Operating System Information")
    print(f"System: {platform.system()}")
    print(f"Node Name: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")


def check_python_info():
    """Check and display Python environment information."""
    print_section("Python Environment")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Implementation: {platform.python_implementation()}")
    print(f"Python Compiler: {platform.python_compiler()}")
    print(f"Python Path: {sys.executable}")


def check_cpu_info():
    """Check and display CPU information."""
    print_section("CPU Information")
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    
    print("\nCPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    
    print(f"\nTotal CPU Usage: {psutil.cpu_percent()}%")


def check_memory_info():
    """Check and display memory information."""
    print_section("Memory Information")
    vm = psutil.virtual_memory()
    print(f"Total: {format_bytes(vm.total)}")
    print(f"Available: {format_bytes(vm.available)}")
    print(f"Used: {format_bytes(vm.used)} ({vm.percent}%)")
    
    swap = psutil.swap_memory()
    print(f"\nSwap Total: {format_bytes(swap.total)}")
    print(f"Swap Free: {format_bytes(swap.free)}")
    print(f"Swap Used: {format_bytes(swap.used)} ({swap.percent}%)")


def format_bytes(bytes_value):
    """Format bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"


def check_disk_info():
    """Check and display disk information."""
    print_section("Disk Information")
    
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"\nDrive: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File System Type: {partition.fstype}")
        
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Total Size: {format_bytes(partition_usage.total)}")
            print(f"  Used: {format_bytes(partition_usage.used)}")
            print(f"  Free: {format_bytes(partition_usage.free)}")
            print(f"  Percentage: {partition_usage.percent}%")
        except PermissionError:
            print("  Permission Denied: Unable to access disk usage information.")


def check_network_info():
    """Check and display network information."""
    print_section("Network Information")
    
    # Check hostname
    print(f"Hostname: {socket.gethostname()}")
    
    # Check IP addresses
    print("\nNetwork Interfaces:")
    for interface_name, addresses in psutil.net_if_addrs().items():
        print(f"\n{interface_name}:")
        for address in addresses:
            if address.family == socket.AF_INET:
                print(f"  IPv4: {address.address}")
            elif address.family == socket.AF_INET6:
                print(f"  IPv6: {address.address}")
            elif address.family == psutil.AF_LINK:
                print(f"  MAC: {address.address}")
    
    # Check if internet is accessible
    try:
        socket.create_connection(("www.google.com", 80), timeout=3)
        print("\nInternet: Connected")
    except OSError:
        print("\nInternet: Disconnected")


def check_current_directory():
    """Check and display information about the current directory."""
    print_section("Current Directory Information")
    
    current_dir = os.getcwd()
    print(f"Current Directory: {current_dir}")
    
    # List files and directories
    print("\nFiles and Directories:")
    try:
        items = os.listdir(current_dir)
        for item in sorted(items):
            item_path = os.path.join(current_dir, item)
            item_type = "Directory" if os.path.isdir(item_path) else "File"
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else "-"
            print(f"  {item} ({item_type}, {format_bytes(size) if size != '-' else size})")
    except Exception as e:
        print(f"Error listing directory contents: {e}")
        
    # Check if it's a git repository
    print("\nGit Repository Status:")
    if os.path.exists(os.path.join(current_dir, ".git")):
        try:
            git_status = subprocess.check_output(["git", "status"], stderr=subprocess.STDOUT, text=True)
            git_branch = subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.STDOUT, text=True).strip()
            print(f"  Current Branch: {git_branch}")
            print("  Git Status Summary:")
            for line in git_status.splitlines()[:5]:
                print(f"    {line}")
            if len(git_status.splitlines()) > 5:
                print("    ...")
        except subprocess.CalledProcessError:
            print("  This is a Git repository, but there was an error getting its status.")
        except FileNotFoundError:
            print("  This is a Git repository, but Git command not found.")
    else:
        print("  Not a Git repository.")


def main():
    """Main function to run all system checks."""
    print_section("SYSTEM CHECK REPORT")
    print(f"Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_os_info()
    check_python_info()
    check_cpu_info()
    check_memory_info()
    check_disk_info()
    check_network_info()
    check_current_directory()
    
    print("\nSystem check completed.")


if __name__ == "__main__":
    main()