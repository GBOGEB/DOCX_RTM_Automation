#!/usr/bin/env python3
"""
DOCX RTM Automation - Complete Integration Script

This script brings together all components of the DOCX RTM Automation system:
1. Repository cleanup and organization
2. System diagnostic
3. Pipeline execution
4. Report generation

Use this as a one-stop script to manage the entire workflow.
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("integration.log"), logging.StreamHandler()],
)
logger = logging.getLogger("rtm-integration")


# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def print_header(text):
    """Print a formatted header"""
    logger.info(text)
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))


def run_command(cmd, description):
    """Run a command and return the result"""
    print_header(f"Running: {description}")

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        duration = time.time() - start_time

        print(f"{Colors.GREEN}Command succeeded in {duration:.2f} seconds{Colors.ENDC}")
        logger.info(
            f"Command succeeded: {description} in {duration:.2f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Command failed: {e}{Colors.ENDC}")
        print(f"Error output:\n{e.stderr}")
        logger.error(f"Command failed: {description}")
        logger.error(f"Error output: {e.stderr}")
        return False


def ensure_dependencies():
    """Ensure all dependencies are installed"""
    print_header("Checking Dependencies")

    try:
        # Check if requirements.txt exists
        if not os.path.exists("requirements.txt"):
            print(
                f"{Colors.YELLOW}requirements.txt not found. Creating minimal version...{Colors.ENDC}"
            )
            with open("requirements.txt", "w") as f:
                f.write("pyyaml>=6.0.0\n")
                f.write("python-docx>=0.8.10\n")
                f.write("markdown>=3.3.0\n")
            print(f"{Colors.GREEN}Created requirements.txt{Colors.ENDC}")

        # Install dependencies
        return run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing dependencies",
        )
    except Exception as e:
        print(f"{Colors.RED}Failed to check dependencies: {e}{Colors.ENDC}")
        logger.error(f"Failed to check dependencies: {e}")
        return False


def run_repository_cleanup(simulate=True):
    """Run repository cleanup"""
    cmd = [sys.executable, "clean_repository.py"]
    if simulate:
        cmd.append("--simulate")

    return run_command(
        cmd, "Repository cleanup" + (" (simulation)" if simulate else "")
    )


def run_system_diagnostic():
    """Run system diagnostic if available"""
    if os.path.exists("system_diagnostic.py"):
        return run_command(
            [sys.executable, "system_diagnostic.py"], "System diagnostic"
        )
    else:
        print(
            f"{Colors.YELLOW}system_diagnostic.py not found, skipping...{Colors.ENDC}"
        )
        return True


def run_pipeline():
    """Run the main pipeline"""
    return run_command([sys.executable, "run_pipeline.py"], "Main pipeline execution")


def create_sample_files():
    """Create sample files if they don't exist"""
    print_header("Creating Sample Files")

    # Create sample input directory and file
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    # Create sample Word docx if needed
    try:
        import docx

        sample_docx = input_dir / "MASTER_1805_1144.docx"

        if not sample_docx.exists():
            print(f"{Colors.YELLOW}Creating sample DOCX file...{Colors.ENDC}")
            doc = docx.Document()
            doc.add_heading("Sample Document for RTM Testing", 0)
            doc.add_heading("Introduction", level=1)
            doc.add_paragraph("This is a sample document for testing.")
            doc.add_heading("Requirements", level=1)
            doc.add_paragraph("The system shall provide user authentication.")
            doc.save(str(sample_docx))
            print(
                f"{Colors.GREEN}Created sample DOCX file: {sample_docx}{Colors.ENDC}")
    except ImportError:
        print(
            f"{Colors.YELLOW}python-docx not installed, skipping DOCX creation{Colors.ENDC}"
        )
    except Exception as e:
        print(f"{Colors.RED}Failed to create sample DOCX: {e}{Colors.ENDC}")

    # Create sample outline.yaml if needed
    sample_outline = input_dir / "MASTER_outline.yaml"
    if not sample_outline.exists():
        try:
            print(f"{Colors.YELLOW}Creating sample outline YAML...{Colors.ENDC}")
            import yaml

            outline = {
                "title": "MASTER Document Outline",
                "sections": [
                    {"level": 1, "title": "Introduction", "number": "1"},
                    {"level": 2, "title": "Purpose", "number": "1.1"},
                    {"level": 1, "title": "Requirements", "number": "2"},
                    {"level": 2, "title": "Functional Requirements", "number": "2.1"},
                ],
            }

            with open(sample_outline, "w") as f:
                yaml.dump(outline, f, default_flow_style=False)
            print(
                f"{Colors.GREEN}Created sample outline: {sample_outline}{Colors.ENDC}"
            )
        except Exception as e:
            print(f"{Colors.RED}Failed to create sample outline: {e}{Colors.ENDC}")

    # Create markdown file in output if none exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    md_files = list(output_dir.glob("*.md"))
    if not md_files:
        sample_md = output_dir / "MASTER_1805_1144.md"
        try:
            print(f"{Colors.YELLOW}Creating sample Markdown file...{Colors.ENDC}")
            with open(sample_md, "w") as f:
                f.write("# Sample Document for RTM Testing\n\n")
                f.write("## Introduction\n\n")
                f.write("This is a sample document for testing.\n\n")
                f.write("## Requirements\n\n")
                f.write("The system shall provide user authentication.\n")
            print(f"{Colors.GREEN}Created sample Markdown: {sample_md}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Failed to create sample Markdown: {e}{Colors.ENDC}")


def check_git_access():
    """Check if git is available and we can access remote repositories"""
    print_header("Checking Git Access")

    # Check if git is installed
    try:
        result = subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            git_version = result.stdout.strip()
            print(f"{Colors.GREEN}Git is available: {git_version}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Git not found or not working{Colors.ENDC}")
            return False

        # Try to check remote access by testing connection to GitHub
        print("Testing GitHub connectivity...")
        test_result = subprocess.run(
            ["git", "ls-remote", "https://github.com", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if test_result.returncode == 0:
            print(f"{Colors.GREEN}GitHub access successful{Colors.ENDC}")
            return True
        else:
            print(
                f"{Colors.RED}Cannot access GitHub: {test_result.stderr}{Colors.ENDC}"
            )
            return False

    except Exception as e:
        print(f"{Colors.RED}Error checking git access: {e}{Colors.ENDC}")
        return False


def clone_repository(repo_url, target_dir=None, recurse_submodules=False):
    """Clone a Git repository"""
    print_header(f"Cloning Repository: {repo_url}")

    if not target_dir:
        # Extract repository name from URL
        repo_name = repo_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        target_dir = repo_name

    # Check if directory already exists
    if os.path.exists(target_dir):
        print(f"{Colors.YELLOW}Directory {target_dir} already exists{Colors.ENDC}")

        # Check if it's a git repository
        if os.path.exists(os.path.join(target_dir, ".git")):
            print("It's a Git repository. Pulling latest changes instead...")

            # Save current directory
            current_dir = os.getcwd()

            try:
                # Change to target directory
                os.chdir(target_dir)

                # Pull latest changes
                result = subprocess.run(
                    ["git", "pull"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if result.returncode == 0:
                    print(
                        f"{Colors.GREEN}Successfully pulled latest changes:{Colors.ENDC}"
                    )
                    print(result.stdout)
                    return True
                else:
                    print(f"{Colors.RED}Failed to pull changes:{Colors.ENDC}")
                    print(result.stderr)
                    return False
            finally:
                # Restore original directory
                os.chdir(current_dir)
        else:
            print(
                f"{Colors.RED}Directory exists but is not a Git repository.{Colors.ENDC}"
            )
            return False

    # Clone the repository
    try:
        clone_cmd = ["git", "clone"]
        if recurse_submodules:
            clone_cmd.append("--recurse-submodules")
        clone_cmd.extend([repo_url, target_dir])

        result = subprocess.run(
            clone_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            print(
                f"{Colors.GREEN}Successfully cloned repository to {target_dir}{Colors.ENDC}"
            )
            return True
        else:
            print(f"{Colors.RED}Failed to clone repository:{Colors.ENDC}")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"{Colors.RED}Error cloning repository: {e}{Colors.ENDC}")
        return False


def push_changes(directory=".", branch="main", message=None):
    """Push changes to remote Git repository"""
    print_header("Pushing Changes to Git")

    # Save current directory
    current_dir = os.getcwd()

    try:
        # Change to target directory
        if directory != ".":
            os.chdir(directory)

        # Check if there are changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if not status_result.stdout.strip():
            print(f"{Colors.YELLOW}No changes to commit{Colors.ENDC}")
            return True

        # Add all changes
        add_result = subprocess.run(
            ["git", "add", "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if add_result.returncode != 0:
            print(f"{Colors.RED}Failed to stage changes:{Colors.ENDC}")
            print(add_result.stderr)
            return False

        # Commit changes
        commit_cmd = ["git", "commit", "-m"]
        if message:
            commit_cmd.append(message)
        else:
            commit_cmd.append("Automated update via integration script")

        commit_result = subprocess.run(
            commit_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if commit_result.returncode != 0:
            print(f"{Colors.RED}Failed to commit changes:{Colors.ENDC}")
            print(commit_result.stderr)
            return False

        # Push changes
        push_result = subprocess.run(
            ["git", "push", "origin", branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if push_result.returncode != 0:
            print(f"{Colors.RED}Failed to push changes:{Colors.ENDC}")
            print(push_result.stderr)
            return False

        print(f"{Colors.GREEN}Successfully pushed changes to {branch}{Colors.ENDC}")
        return True

    except Exception as e:
        print(f"{Colors.RED}Error pushing changes: {e}{Colors.ENDC}")
        return False
    finally:
        # Restore original directory
        os.chdir(current_dir)


def run_script(script_name):
    """Run a Python script."""
    script_path = Path.cwd() / script_name
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False

    result = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✅ Successfully ran {script_name}")
        return True
    else:
        print(f"❌ Error running {script_name}: {result.stderr}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="DOCX RTM Automation Integration")
    parser.add_argument("--clean", action="store_true",
                        help="Run repository cleanup")
    parser.add_argument(
        "--force", action="store_true", help="Apply cleanup changes (not just simulate)"
    )
    parser.add_argument(
        "--diagnostic", action="store_true", help="Run system diagnostic"
    )
    parser.add_argument("--pipeline", action="store_true",
                        help="Run the main pipeline")
    parser.add_argument("--samples", action="store_true",
                        help="Create sample files")
    parser.add_argument("--all", action="store_true", help="Run everything")
    parser.add_argument(
        "--git-check", action="store_true", help="Check Git connectivity"
    )
    parser.add_argument(
        "--clone", help="Clone a Git repository", metavar="REPO_URL")
    parser.add_argument(
        "--recurse-submodules", action="store_true", help="When cloning, also initialize and update submodules."
    )
    parser.add_argument(
        "--push", action="store_true", help="Push changes to Git repository"
    )
    parser.add_argument("--message", help="Git commit message")
    parser.add_argument(
        "--run-scripts", action="store_true", help="Run additional scripts"
    )

    args = parser.parse_args()

    # If no specific arguments provided, show help
    if not any(
        [
            args.clean,
            args.diagnostic,
            args.pipeline,
            args.samples,
            args.all,
            args.git_check,
            args.clone,
            args.push,
            args.run_scripts,
        ]
    ):
        parser.print_help()
        return 0

    print_header("DOCX RTM Automation Integration")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Check Git access if requested
    if args.git_check or args.clone or args.push:
        git_available = check_git_access()
        if not git_available and (args.clone or args.push):
            print(f"{Colors.RED}Git operations require Git access{Colors.ENDC}")
            return 1

    # Clone repository if requested
    if args.clone:
        success = clone_repository(args.clone, recurse_submodules=args.recurse_submodules)
        if not success:
            print(f"{Colors.RED}Failed to clone repository{Colors.ENDC}")
            return 1

    # Conceptual: Input Source Discovery and Preparation
    print_header("Input Source Discovery and Preparation")
    logger.info("Conceptual step: Discovering inputs from various sources.")
    print(f"{Colors.BLUE}Note: The following are conceptual checks for a full integration:{Colors.ENDC}")
    print(f"{Colors.YELLOW}- Scanning configured input paths (including those within potential sub-repositories).{Colors.ENDC}")
    print(f"{Colors.YELLOW}- If GitHub URLs were provided as direct inputs, they would be downloaded/processed here.{Colors.ENDC}")
    print(f"{Colors.YELLOW}- Markdown files are treated as primary inputs for RTM generation by the downstream pipeline.{Colors.ENDC}")
    print(f"{Colors.YELLOW}- OpenAI interactions for analysis/generation are handled within specific pipeline steps or agents.{Colors.ENDC}")
    # Actual implementation would involve more detailed logic, potentially using a PathsManager
    # or dedicated functions for fetching remote content and scanning submodules.

    # Check dependencies first
    ensure_dependencies()

    # Create sample files if requested
    if args.samples or args.all:
        create_sample_files()

    # Run cleanup if requested
    if args.clean or args.all:
        run_repository_cleanup(simulate=not args.force)

    # Run diagnostic if requested
    if args.diagnostic or args.all:
        run_system_diagnostic()

    # Run pipeline if requested
    if args.pipeline or args.all:
        run_pipeline()

    # Run additional scripts if requested
    if args.run_scripts:
        scripts = ["fix_errors.py", "project_update.py", "verify_setup.py"]

        for script in scripts:
            run_script(script)

    # Push changes if requested
    if args.push:
        success = push_changes(message=args.message)
        if not success:
            print(f"{Colors.RED}Failed to push changes{Colors.ENDC}")
            return 1

    print_header("Integration Complete")
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
