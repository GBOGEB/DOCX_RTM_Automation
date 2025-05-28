#!/usr/bin/env python3
"""
DOCX RTM Automation Dashboard
Interactive dashboard to navigate and use the RTM Automation tools
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Rich library not found. Install for better UI: pip install rich")


class RTMDashboard:
    """Interactive dashboard for RTM Automation."""

    def __init__(self):
        """Initialize the dashboard."""
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.is_windows = sys.platform.startswith('win')
        self.console = Console() if HAS_RICH else None

    def check_environment(self):
        """Check the environment for required tools and configuration."""
        results = {
            "python_version": sys.version.split()[0],
            "venv_active": self._is_venv_active(),
            "git_available": self._check_command("git --version"),
            "pandoc_available": self._check_command("pandoc --version"),
            "config_valid": os.path.isfile(os.path.join(self.project_dir, "config", "paths.yaml")),
        }

        return results

    def _is_venv_active(self):
        """Check if a virtual environment is active."""
        return (hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    def _check_command(self, command):
        """Check if a command is available."""
        try:
            subprocess.run(command.split(),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def show_dashboard(self):
        """Display the main dashboard."""
        if HAS_RICH:
            self._show_rich_dashboard()
        else:
            self._show_plain_dashboard()

    def _show_rich_dashboard(self):
        """Display a rich formatted dashboard."""
        self.console.clear()
        env_check = self.check_environment()

        # Title
        self.console.print(Panel.fit("[bold blue]DOCX RTM Automation Dashboard[/bold blue]",
                                     border_style="cyan"))

        # Environment status
        self.console.print("\n[bold]Environment Status:[/bold]")
        env_table = Table()
        env_table.add_column("Component")
        env_table.add_column("Status")

        env_table.add_row("Python Version", f"{env_check['python_version']}")
        env_table.add_row("Virtual Env", "[green]Active[/green]" if env_check['venv_active']
                           else "[red]Inactive[/red] (Run setup_venv.sh)")
        env_table.add_row("Git", "[green]Available[/green]" if env_check['git_available']
                          else "[red]Not Found[/red]")
        env_table.add_row("Pandoc", "[green]Available[/green]" if env_check['pandoc_available']
                          else "[red]Not Found[/red] (Run shell_scripts/install_pandoc.sh)")
        env_table.add_row("Configuration", "[green]Valid[/green]" if env_check['config_valid']
                          else "[red]Missing/Invalid[/red]")

        self.console.print(env_table)

        # Workflows
        self.console.print("\n[bold]Available Workflows:[/bold]")
        workflow_table = Table()
        workflow_table.add_column("Command", style="cyan")
        workflow_table.add_column("Description")

        workflow_table.add_row("run.sh rtm-pipeline", "Complete RTM generation workflow")
        workflow_table.add_row("run.sh word-to-md-dir", "Convert Word documents to Markdown")
        workflow_table.add_row("run.sh extract-rtm-dir output", "Extract RTM from Markdown files")
        workflow_table.add_row("run.sh visualize-rtm", "Generate RTM visualizations")

        self.console.print(workflow_table)

        # Utilities
        self.console.print("\n[bold]Utility Scripts:[/bold]")
        util_table = Table()
        util_table.add_column("Script", style="cyan")
        util_table.add_column("Purpose")

        util_table.add_row("setup_venv.sh", "Create and configure virtual environment")
        util_table.add_row("fix_debugger.bat", "Fix debugging connection issues")
        util_table.add_row("lint.sh", "Run code quality checks")
        util_table.add_row("run_tests.sh", "Execute test suite")
        util_table.add_row("setup_git_hooks.bat", "Configure Git hooks")

        self.console.print(util_table)

        # Documentation
        self.console.print("\n[bold]Documentation:[/bold]")
        docs_table = Table()
        docs_table.add_column("File", style="cyan")
        docs_table.add_column("Content")

        docs_table.add_row("README.md", "Project overview")
        docs_table.add_row("QUICK_START.md", "Getting started guide")
        docs_table.add_row("docs/openai_integration.md", "OpenAI integration guide")
        docs_table.add_row("docs/troubleshooting.md", "Troubleshooting common issues")
        docs_table.add_row("docs/workflow_execution_guide.md", "Detailed workflow guide")

        self.console.print(docs_table)

        # Interactive options
        self.console.print("\n[bold]Interactive Options:[/bold]")
        self.console.print("[1] View README.md")
        self.console.print("[2] View QUICK_START.md")
        self.console.print("[3] Run complete RTM pipeline")
        self.console.print("[4] Run setup and environment check")
        self.console.print("[5] View example files")
        self.console.print("[0] Exit")

        choice = input("\nEnter choice (0-5): ")
        self._handle_choice(choice)

    def _show_plain_dashboard(self):
        """Display a plain text dashboard."""
        print("\n===== DOCX RTM Automation Dashboard =====\n")

        env_check = self.check_environment()

        print("Environment Status:")
        print(f"- Python Version: {env_check['python_version']}")
        print(f"- Virtual Env: {'Active' if env_check['venv_active'] else 'Inactive (Run setup_venv.sh)'}")
        print(f"- Git: {'Available' if env_check['git_available'] else 'Not Found'}")
        print(f"- Pandoc: {'Available' if env_check['pandoc_available'] else 'Not Found (Run shell_scripts/install_pandoc.sh)'}")
        print(f"- Configuration: {'Valid' if env_check['config_valid'] else 'Missing/Invalid'}")

        print("\nAvailable Workflows:")
        print("- run.sh rtm-pipeline            # Complete RTM generation workflow")
        print("- run.sh word-to-md-dir          # Convert Word documents to Markdown")
        print("- run.sh extract-rtm-dir output  # Extract RTM from Markdown files")
        print("- run.sh visualize-rtm           # Generate RTM visualizations")

        print("\nUtility Scripts:")
        print("- setup_venv.sh          # Create and configure virtual environment")
        print("- fix_debugger.bat       # Fix debugging connection issues")
        print("- lint.sh                # Run code quality checks")
        print("- run_tests.sh           # Execute test suite")
        print("- setup_git_hooks.bat    # Configure Git hooks")

        print("\nDocumentation:")
        print("- README.md                       # Project overview")
        print("- QUICK_START.md                  # Getting started guide")
        print("- docs/openai_integration.md      # OpenAI integration guide")
        print("- docs/troubleshooting.md         # Troubleshooting common issues")
        print("- docs/workflow_execution_guide.md # Detailed workflow guide")

        print("\nInteractive Options:")
        print("[1] View README.md")
        print("[2] View QUICK_START.md")
        print("[3] Run complete RTM pipeline")
        print("[4] Run setup and environment check")
        print("[5] View example files")
        print("[0] Exit")

        choice = input("\nEnter choice (0-5): ")
        self._handle_choice(choice)

    def _handle_choice(self, choice):
        """Handle user menu choice."""
        try:
            choice = int(choice)

            if choice == 0:
                print("Exiting dashboard.")
                return

            elif choice == 1:
                self._view_file("README.md")
                input("Press Enter to continue...")
                self.show_dashboard()

            elif choice == 2:
                self._view_file("QUICK_START.md")
                input("Press Enter to continue...")
                self.show_dashboard()

            elif choice == 3:
                self._run_command("run.sh rtm-pipeline" if not self.is_windows else
                                "run.bat rtm-pipeline")
                input("Press Enter to continue...")
                self.show_dashboard()

            elif choice == 4:
                self._run_setup()
                input("Press Enter to continue...")
                self.show_dashboard()

            elif choice == 5:
                self._view_examples()
                input("Press Enter to continue...")
                self.show_dashboard()

            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                self.show_dashboard()

        except ValueError:
            print("Please enter a number.")
            input("Press Enter to continue...")
            self.show_dashboard()

    def _view_file(self, filename):
        """View a markdown file."""
        filepath = os.path.join(self.project_dir, filename)

        if not os.path.isfile(filepath):
            print(f"File not found: {filepath}")
            return

        if HAS_RICH:
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown = Markdown(f.read())
                self.console.print(markdown)
        else:
            try:
                # Try to open in default markdown viewer
                if self.is_windows:
                    os.startfile(filepath)
                else:
                    webbrowser.open(f"file://{filepath}")
            except:
                # Fallback to displaying raw content
                with open(filepath, 'r', encoding='utf-8') as f:
                    print(f.read())

    def _run_command(self, command):
        """Run a shell command."""
        print(f"Running: {command}")
        try:
            if self.is_windows and not command.endswith('.bat'):
                # For Windows, make sure to use batch files
                command = command.replace("run.sh", "run.bat")

            subprocess.run(command, shell=True)
            print("Command completed.")
        except subprocess.SubprocessError as e:
            print(f"Error running command: {e}")

    def _run_setup(self):
        """Run environment setup and checks."""
        print("Running environment setup and checks...")

        # Check virtual environment
        if not self._is_venv_active():
            print("Virtual environment not active. Setting up...")
            self._run_command("setup_venv.sh" if not self.is_windows else "setup_venv.bat")

        # Install dependencies
        print("Installing dependencies...")
        self._run_command("install_dependencies.sh" if not self.is_windows else "pip install -r requirements.txt")

        # Create directory structure if needed
        for directory in ["input", "output", "output/rtm", "output/rtm_viz"]:
            dirpath = os.path.join(self.project_dir, directory)
            if not os.path.exists(dirpath):
                print(f"Creating directory: {directory}")
                os.makedirs(dirpath, exist_ok=True)

        # Check for configuration file
        config_path = os.path.join(self.project_dir, "config", "paths.yaml")
        if not os.path.isfile(config_path):
            print("Configuration file missing. Creating default...")
            os.makedirs(os.path.join(self.project_dir, "config"), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write("input_dir: input\n")
                f.write("output_dir: output\n")

        print("Setup completed.")

    def _view_examples(self):
        """View example files."""
        examples_dir = os.path.join(self.project_dir, "examples")
        if not os.path.isdir(examples_dir):
            print("Examples directory not found.")
            return

        example_files = [f for f in os.listdir(examples_dir)
                         if os.path.isfile(os.path.join(examples_dir, f))]

        print("\nAvailable Example Files:")
        for i, example in enumerate(example_files, 1):
            print(f"[{i}] {example}")
        print("[0] Back to main menu")

        choice = input("\nSelect example to view (0-{0}): ".format(len(example_files)))

        try:
            choice = int(choice)
            if choice == 0:
                return
            elif 1 <= choice <= len(example_files):
                example_file = os.path.join(examples_dir, example_files[choice-1])
                self._view_file(example_file)
        except (ValueError, IndexError):
            print("Invalid selection.")


def main():
    """Main function to run the dashboard."""
    dashboard = RTMDashboard()
    dashboard.show_dashboard()

if __name__ == "__main__":
    main()
