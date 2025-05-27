import subprocess
import os

# Navigate to your project directory
os.chdir("C:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0")

# Make sure your local Git repository is initialized
subprocess.run(["git", "init"], check=True)

# Check your Git identity is set
subprocess.run(["git", "config", "--global",
               "user.name", "GBOGEB"], check=True)
subprocess.run(
    ["git", "config", "--global", "user.email", "gerkotze.bonthuys@sckcen.be"],
    check=True,
)

# Add the remote repository
subprocess.run(
    [
        "git",
        "remote",
        "add",
        "origin",
        "https://github.com/GBOGEB/DOCX_RTM_Automation.git",
    ],
    check=True,
)


def git_push(commit_message="Update project"):
    """Push changes to GitHub."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Changes pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")


if __name__ == "__main__":
    git_push("Automated commit")
    subprocess.run(["python", "GIT_push.py"], check=True)
