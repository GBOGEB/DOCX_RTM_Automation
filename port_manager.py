#!/usr/bin/env python3
"""
Port management utility for debugging.

Helps identify and resolve port conflicts for debugging purposes.
"""

import os
import sys
import socket
import subprocess
import argparse
import time
import logging
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PortManager:
    def __init__(self):
        self.ports = {}

    def add_port(self, port_name, port_number):
        """Add a new port to the manager."""
        if port_name in self.ports:
            raise ValueError(f"Port {port_name} already exists.")
        self.ports[port_name] = port_number

    def remove_port(self, port_name):
        """Remove a port from the manager."""
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} does not exist.")
        del self.ports[port_name]

    def get_port(self, port_name):
        """Retrieve the port number for a given port name."""
        return self.ports.get(port_name, None)

    def list_ports(self):
        """List all ports managed."""
        return self.ports

def check_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            s.bind(("0.0.0.0", port))
            return False  # Port is available on both addresses
        except OSError:
            return True  # Port is in use

def find_available_port(start_port: int, end_port: int = None) -> Optional[int]:
    """Find an available port in a range."""
    if end_port is None:
        end_port = start_port + 10

    for port in range(start_port, end_port + 1):
        if not check_port_in_use(port):
            return port

    return None

def get_process_using_port(port: int) -> Tuple[Optional[int], Optional[str]]:
    """
    Get information about the process using a specific port.

    Returns:
        Tuple of (pid, process_name) or (None, None) if not found
    """
    if sys.platform == "win32":
        try:
            # On Windows, use netstat
            output = subprocess.check_output(
                ["netstat", "-ano", "-p", "TCP"],
                text=True
            )

            # Parse the output to find the process
            for line in output.splitlines():
                if f":{port}" in line and ("LISTENING" in line or "ESTABLISHED" in line):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = int(parts[-1])
                        try:
                            proc_info = subprocess.check_output(
                                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                text=True
                            )
                            if '","' in proc_info:
                                # Extract process name from CSV format
                                process_name = proc_info.splitlines()[1].split('","')[0].strip('"')
                                return pid, process_name
                        except subprocess.SubprocessError:
                            return pid, "Unknown"
        except subprocess.SubprocessError as e:
            logger.error(f"Error running netstat: {e}")
    else:
        try:
            # On Unix/Linux, use lsof
            output = subprocess.check_output(
                ["lsof", "-i", f":{port}", "-P", "-n"],
                text=True
            )

            if len(output.splitlines()) > 1:  # Header + at least one process
                # Parse the second line
                parts = output.splitlines()[1].split()
                if len(parts) >= 2:
                    process_name = parts[0]
                    pid = int(parts[1])
                    return pid, process_name
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Error running lsof: {e}")

    return None, None

def kill_process(pid: int) -> bool:
    """Kill a process by PID."""
    try:
        if sys.platform == "win32":
            subprocess.check_call(["taskkill", "/F", "/PID", str(pid)])
        else:
            subprocess.check_call(["kill", "-9", str(pid)])
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Error killing process with PID {pid}: {e}")
        return False

def release_port(port: int) -> bool:
    """Attempt to release a port that's in use."""
    pid, process_name = get_process_using_port(port)

    if pid:
        logger.info(f"Port {port} is used by process {process_name} (PID: {pid})")
        confirmation = input(f"Do you want to terminate process {process_name} (PID: {pid})? (y/n): ")

        if confirmation.lower() == 'y':
            if kill_process(pid):
                logger.info(f"Process {process_name} (PID: {pid}) terminated successfully")

                # Verify the port is now free
                time.sleep(0.5)  # Give OS time to release the port
                if not check_port_in_use(port):
                    logger.info(f"Port {port} is now available")
                    return True
                else:
                    logger.warning(f"Port {port} is still in use by another process")
            else:
                logger.error(f"Failed to terminate process {process_name} (PID: {pid})")
        else:
            logger.info("Process termination cancelled by user")
    else:
        logger.warning(f"Could not identify the process using port {port}")

    return False

def list_debug_ports(debug_ports: List[int] = None) -> Dict[int, Dict[str, Union[bool, int, str]]]:
    """List the status of common debug ports."""
    if debug_ports is None:
        debug_ports = [5678, 8000, 9229, 3000, 4000]

    results = {}

    print("\nChecking debug ports status:\n")
    print(f"{'Port':<8} {'Status':<12} {'PID':<8} {'Process'}")
    print("-" * 40)

    for port in debug_ports:
        in_use = check_port_in_use(port)
        pid, process_name = get_process_using_port(port) if in_use else (None, None)

        status = "IN USE" if in_use else "AVAILABLE"
        pid_str = str(pid) if pid else "N/A"
        process_str = process_name or "N/A"

        print(f"{port:<8} {status:<12} {pid_str:<8} {process_str}")

        results[port] = {
            "in_use": in_use,
            "pid": pid,
            "process_name": process_name
        }

    print("\n")
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Debug port management utility")
    parser.add_argument("--list", action="store_true", help="List status of common debug ports")
    parser.add_argument("--check", type=int, help="Check if a specific port is in use")
    parser.add_argument("--release", type=int, help="Attempt to release a specific port")
    parser.add_argument("--find", type=int, help="Find available port starting from this number")

    args = parser.parse_args()

    if args.list:
        list_debug_ports()
    elif args.check is not None:
        port = args.check
        if check_port_in_use(port):
            pid, process_name = get_process_using_port(port)
            if pid:
                print(f"Port {port} is in use by process {process_name} (PID: {pid})")
            else:
                print(f"Port {port} is in use, but could not identify the process")
        else:
            print(f"Port {port} is available")
    elif args.release is not None:
        port = args.release
        if check_port_in_use(port):
            if release_port(port):
                print(f"Port {port} was successfully released")
            else:
                print(f"Failed to release port {port}")
        else:
            print(f"Port {port} is already available")
    elif args.find is not None:
        port = find_available_port(args.find, args.find + 20)
        if port:
            print(f"Available port found: {port}")
        else:
            print(f"No available ports found in range {args.find}-{args.find+20}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()