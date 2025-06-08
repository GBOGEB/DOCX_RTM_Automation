import subprocess


def run_command(command):
    """
    Run a shell command and return the output, error, and exit code.

    Args:
        command (str): The command to execute.

    Returns:
        tuple: A tuple containing (output, error, exit_code).
    """
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


if __name__ == "__main__":
    # Example usage
    cmd = "echo Hello, World!"
    output, error, exit_code = run_command(cmd)
    print("Output:", output)
    print("Error:", error)
    print("Exit Code:", exit_code)
