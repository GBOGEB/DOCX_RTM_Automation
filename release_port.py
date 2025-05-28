#!/usr/bin/env python3
"""
Enhanced port release utility for persistent port conflicts.

This script addresses situations where a port remains in use
even after terminating the process that was initially detected.
"""
import os
import sys
import time
import socket
import subprocess
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            # Also try binding to all interfaces
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                try:
                    s2.bind(("0.0.0.0", port))
                    return False  # Port is available on all interfaces
                except OSError:
                    return True  # Port is in use on 0.0.0.0
        except OSError:
            return True  # Port is in use on 127.0.0.1

def get_all_processes_using_port_windows(port):
    """Get all processes using a specific port on Windows."""
    processes = []

    try:
        # Use netstat to find processes using the port
        output = subprocess.check_output(
            ["netstat", "-ano", "-p", "TCP"],
            text=True
        )

        # Parse output to find PIDs
        for line in output.splitlines():
            if f":{port}" in line and ("LISTENING" in line or "ESTABLISHED" in line):
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = int(parts[-1])

                    # Get process name
                    try:
                        proc_info = subprocess.check_output(
                            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                            text=True
                        )
                        if '","' in proc_info:
                            # Extract process name from CSV format
                            process_name = proc_info.splitlines()[1].split('","')[0].strip('"')
                            processes.append((pid, process_name))
                    except subprocess.SubprocessError:
                        processes.append((pid, "Unknown"))
    except subprocess.SubprocessError as e:
        logger.error(f"Error executing netstat: {e}")

    return processes

def get_all_processes_using_port(port):
    """Get all processes using a specific port."""
    if sys.platform == "win32":
        return get_all_processes_using_port_windows(port)
    else:
        # Linux/Unix implementation using lsof
        processes = []
        try:
            output = subprocess.check_output(
                ["lsof", "-i", f":{port}", "-P", "-n"],
                text=True
            )

            # Skip header line
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    process_name = parts[0]
                    pid = int(parts[1])
                    processes.append((pid, process_name))
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Error running lsof: {e}")

        return processes

def force_kill_process_windows(pid):
    """Forcefully kill a process on Windows."""
    try:
        # Use taskkill with /F to force termination
        subprocess.check_call(["taskkill", "/F", "/PID", str(pid)])
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Error killing process with PID {pid}: {e}")
        return False

def force_kill_process(pid):
    """Forcefully kill a process."""
    if sys.platform == "win32":
        return force_kill_process_windows(pid)
    else:
        try:
            # Use kill -9 (SIGKILL) for forceful termination
            subprocess.check_call(["kill", "-9", str(pid)])
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Error killing process with PID {pid}: {e}")
            return False

def release_port_aggressively(port):
    """
    Aggressively try to release a port by identifying and killing all processes using it.

    Returns:
        True if the port was successfully released, False otherwise.
    """
    if not check_port_in_use(port):
        logger.info(f"Port {port} is already available")
        return True

    # Get all processes using the port
    processes = get_all_processes_using_port(port)

    if not processes:
        logger.warning(f"Could not identify processes using port {port}, but port is in use")
        return False

    logger.info(f"Found {len(processes)} processes using port {port}")

    # Try to kill each process
    for pid, name in processes:
        logger.info(f"Attempting to terminate process: {name} (PID: {pid})")
        force_kill_process(pid)
        time.sleep(0.5)  # Give system time to release resources

    # Verify port is now available
    attempts = 5
    while attempts > 0:
        if not check_port_in_use(port):
            logger.info(f"Port {port} has been successfully released")
            return True

        logger.info(f"Port {port} still in use. Waiting... ({attempts} attempts left)")
        attempts -= 1
        time.sleep(1)

    return not check_port_in_use(port)

def run_special_commands():
    """Run special commands to resolve persistent port issues."""
    logger.info("Attempting special cleanup steps for persistent port issues")

    if sys.platform == "win32":
        # Use netsh to reset Windows networking stack components
        try:
            logger.info("Resetting TCP/IP stack... (this may take a moment)")
            subprocess.run(
                ["netsh", "winsock", "reset"],
                capture_output=True, text=True, check=False
            )
            logger.info("Winsock reset completed")
        except Exception as e:
            logger.error(f"Failed to reset Winsock: {e}")
    else:
        # On Unix systems we might use different approaches
        logger.info("No special commands defined for this platform")

def display_process_info_windows():
    """Display extended process info for Windows."""
    try:
        # List all TCP connections and listeners
        tcp_info = subprocess.check_output(
            ["netstat", "-ano", "-p", "TCP"],
            text=True
        )

        print("\nActive TCP Connections:")
        print("=" * 80)
        print(tcp_info)
    except Exception as e:
        logger.error(f"Error getting TCP connection info: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Enhanced Port Release Utility")
    parser.add_argument("port", type=int, help="Port number to release")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Use aggressive methods to release port")
    parser.add_argument("--advanced", "-a", action="store_true",
                        help="Run advanced system commands that may require restart")
    parser.add_argument("--info", "-i", action="store_true",
                        help="Display extended process information")

    args = parser.parse_args()

    port = args.port

    if args.info and sys.platform == "win32":
        display_process_info_windows()
        return 0

    print(f"Checking port {port}...")
    if not check_port_in_use(port):
        print(f"Port {port} is already available!")
        return 0

    print(f"Port {port} is currently in use.")
    processes = get_all_processes_using_port(port)

    if processes:
        print(f"Found {len(processes)} processes using port {port}:")
        for pid, name in processes:
            print(f"  - {name} (PID: {pid})")
    else:
        print("Could not identify specific processes using this port.")

    if args.force or args.advanced:
        print("\nAttempting aggressive port release...")
        if release_port_aggressively(port):
            print(f"\nSUCCESS: Port {port} has been released!")
        else:
            print(f"\nFAILED: Port {port} is still in use after attempted release.")

            if args.advanced:
                print("\nAttempting special system commands...")
                run_special_commands()
                print("\nSystem commands completed. Some changes may require a restart.")
                print("Please check if port is released after these operations.")
    else:
        print("\nTo forcefully release this port, use:")
        print(f"  python release_port.py {port} --force")
        print("\nFor advanced system-level operations (may require restart):")
        print(f"  python release_port.py {port} --advanced")

    return 0

if __name__ == "__main__":
    sys.exit(main())
