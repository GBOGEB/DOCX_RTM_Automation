import socket
import time

def check_port(host, port, timeout=5):
    """
    Check if a specific port on a host is open.

    :param host: Hostname or IP address to check.
    :param port: Port number to check.
    :param timeout: Timeout in seconds for the connection attempt.
    :return: True if the port is open, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def monitor_ports(host, ports, interval=10):
    """
    Monitor a list of ports on a host at regular intervals.

    :param host: Hostname or IP address to monitor.
    :param ports: List of port numbers to monitor.
    :param interval: Time in seconds between checks.
    """
    while True:
        for port in ports:
            status = "open" if check_port(host, port) else "closed"
            print(f"Port {port} on {host} is {status}.")
        time.sleep(interval)

if __name__ == "__main__":
    # Example usage
    host_to_monitor = "127.0.0.1"
    ports_to_monitor = [22, 80, 443]
    monitor_interval = 15  # seconds

    print(f"Starting port monitoring for {host_to_monitor}...")
    monitor_ports(host_to_monitor, ports_to_monitor, monitor_interval)