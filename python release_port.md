python release_port.py 5678 --force
$ python release_port.py 5678 --force
Checking port 5678...
Port 5678 is currently in use.
Found 1 processes using port 5678:

- python.exe (PID: 18940)

Attempting aggressive port release...
2025-05-28 22:57:37,138 - INFO - Found 1 processes using port 5678
2025-05-28 22:57:37,138 - INFO - Attempting to terminate process: python.exe (PID: 18940)
SUCCESS: The process with PID 18940 has been terminated.
2025-05-28 22:57:37,816 - INFO - Port 5678 has been successfully released
