import subprocess


def run_precommit_hooks():
    """Run pre-commit hooks."""
    try:
        print("Running pre-commit hooks...")
        subprocess.run(["pre-commit", "run", "--all-files"], check=True)
        print("Pre-commit hooks completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while running pre-commit hooks: {e}")
        exit(1)


def commit_changes(commit_message):
    """Commit changes to the repository."""
    try:
        print("Adding changes...")
        subprocess.run(["git", "add", "."], check=True)
        print("Committing changes...")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("Changes committed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while committing changes: {e}")
        exit(1)


if __name__ == "__main__":
    commit_message = input("Enter commit message: ").strip()
    if not commit_message:
        print("Commit message cannot be empty.")
        exit(1)

    run_precommit_hooks()
    commit_changes(commit_message)
