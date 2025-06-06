import subprocess


def pre_commit_hook():
    """Simple pre-commit hook to check for Python syntax errors."""
    print("Running pre-commit hook...")

    # Get the list of staged files
    staged_files = (
        subprocess.check_output(["git", "diff", "--cached", "--name-only"])
        .decode()
        .splitlines()
    )

    # Filter Python files
    python_files = [file for file in staged_files if file.endswith(".py")]

    if not python_files:
        print("No Python files staged for commit.")
        return

    # Check syntax for each Python file
    for file in python_files:
        print(f"Checking syntax for {file}...")
        try:
            subprocess.check_call(["python", "-m", "py_compile", file])
        except subprocess.CalledProcessError:
            print(f"Syntax error in {file}. Commit aborted.")
            exit(1)

    print("All Python files passed syntax check.")


if __name__ == "__main__":
    pre_commit_hook()
