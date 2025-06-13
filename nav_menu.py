#!/usr/bin/env python3
"""
Navigation Menu - Interactive menu for RTM automation operations
"""

import subprocess
import sys
from pathlib import Path

def show_menu():
    """Display the main navigation menu"""
    print("🚀 RTM AUTOMATION - NAVIGATION MENU")
    print("=" * 50)
    print()
    print("📋 PIPELINE OPERATIONS:")
    print("  1. Run main RTM pipeline")
    print("  2. Check output files")
    print("  3. Create test document")
    print()
    print("🔍 DIAGNOSTICS & TESTING:")
    print("  4. Comprehensive system test")
    print("  5. Fix environment issues")
    print("  6. Test python-docx")
    print("  7. Simple workflow test")
    print()
    print("🌐 GIT & GITHUB:")
    print("  8. Check GitHub status")
    print("  9. Version manager")
    print(" 10. Smart commit")
    print(" 11. Test GitHub clone")
    print()
    print("🛠️  SETUP & MAINTENANCE:")
    print(" 12. Project scanner")
    print(" 13. Reset environment")
    print(" 14. Install dependencies")
    print(" 15. Setup project")
    print()
    print("📚 DOCUMENTATION:")
    print(" 16. Open starter guide")
    print(" 17. Show project structure")
    print()
    print("  0. Exit")
    print()

def run_command(command, description):
    """Run a command and show results"""
    print(f"\n🔄 {description}")
    print("-" * 60)

    try:
        if isinstance(command, list):
            result = subprocess.run(command, capture_output=False, text=True)
        else:
            result = subprocess.run([sys.executable, command], capture_output=False, text=True)

        print(f"\n✅ {description} completed")
        return result.returncode == 0
    except Exception as e:
        print(f"\n❌ Error running {description}: {e}")
        return False

def open_file(filename):
    """Open a file with the default application"""
    try:
        if sys.platform.startswith('win'):
            subprocess.run(['notepad', filename])
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', filename])
        else:
            subprocess.run(['xdg-open', filename])
        return True
    except Exception as e:
        print(f"❌ Could not open {filename}: {e}")
        return False

def open_starter_guide():
    """Open or create starter guide documentation"""
    print("\n📚 STARTER GUIDE")
    print("=" * 20)

    guide_files = [
        "README.md",
        "STARTER_GUIDE.md",
        "docs/README.md",
        "docs/starter_guide.md",
        "documentation/README.md"
    ]

    found_guide = None
    for guide_file in guide_files:
        guide_path = Path(guide_file)
        if guide_path.exists():
            found_guide = guide_path
            break

    if found_guide:
        print(f"📖 Found guide: {found_guide}")

        # Show content preview instead of trying to open externally
        try:
            with open(found_guide, 'r', encoding='utf-8') as f:
                content = f.read()

            # Show first part of content
            lines = content.split('\n')[:20]  # First 20 lines
            print(f"\n📄 Content preview of {found_guide}:")
            print("-" * 50)
            for line in lines:
                print(line)

            if len(content.split('\n')) > 20:
                print("\n... (more content available)")

            print(f"\n📁 Full file location: {found_guide.absolute()}")

            # Ask if user wants to try opening it
            try:
                open_choice = input("\n🔍 Try to open file externally? (y/N): ").strip().lower()
                if open_choice == 'y':
                    try_open_file_safely(found_guide)
            except KeyboardInterrupt:
                print("\n⚠️  Cancelled by user")

        except Exception as e:
            print(f"⚠️  Could not read file: {e}")
            print(f"📁 Manual path: {found_guide.absolute()}")
    else:
        print("📝 No starter guide found. Showing quick reference...")
        create_quick_reference()

def try_open_file_safely(file_path):
    """Safely try to open a file without hanging"""
    import threading
    import time

    def open_file_thread():
        try:
            import os
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path))
            else:
                import subprocess
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(file_path)],
                             timeout=5)
            return True
        except Exception as e:
            print(f"⚠️  Could not open file: {e}")
            return False

    print("🔄 Attempting to open file...")

    # Run in thread with timeout
    thread = threading.Thread(target=open_file_thread)
    thread.daemon = True
    thread.start()
    thread.join(timeout=3)  # 3 second timeout

    if thread.is_alive():
        print("⚠️  File opening timed out - continuing...")
    else:
        print("✅ File opening completed")

def create_quick_reference():
    """Create a quick reference guide"""
    quick_guide = """
🚀 RTM AUTOMATION QUICK START
===============================

🎯 MAIN COMMANDS:
   python main.py                    # Process DOCX files
   python nav_menu.py                # This interactive menu
   python comprehensive_test.py      # Full system test

📦 SETUP COMMANDS:
   python setup_environment.py      # Universal setup
   python quick_start_system_python.py  # System Python mode

🔧 VIRTUAL ENVIRONMENT:
   source .venv/Scripts/activate     # Git Bash activation
   .venv\\Scripts\\activate.bat      # Command Prompt

📁 KEY DIRECTORIES:
   input/          # Place your DOCX files here
   output/         # Generated RTM files appear here
   scripts/        # Automation scripts

💡 TROUBLESHOOTING:
   1. Run: python setup_environment.py
   2. Check: python comprehensive_test.py
   3. Reset: python nav_menu.py (option 13)

📧 Need help? Check the project files or run comprehensive_test.py
    """

    print(quick_guide)

    # Save to file
    try:
        with open("QUICK_START.md", "w", encoding="utf-8") as f:
            f.write(quick_guide)
        print("💾 Saved as QUICK_START.md")
    except Exception as e:
        print(f"⚠️  Could not save guide: {e}")

def show_project_structure():
    """Show the project structure"""
    print("\n📁 PROJECT STRUCTURE")
    print("-" * 30)

    structure = """
DOCX_RTM_Automation_v1.0/
├── 📄 main.py                      ← Main pipeline
├── 📄 comprehensive_test.py        ← Test everything
├── 📄 find_output_files.py         ← Check results
├── 📄 nav_menu.py                  ← This menu
│
├── 📁 src/rtm/                     ← Core processing
├── 📁 scripts/automation/          ← Automated workflows
├── 📁 scripts/quality/             ← Testing tools
├── 📁 scripts/debug/               ← Debug utilities
├── 📁 scripts/setup/               ← Setup tools
│
├── 📁 input/                       ← Place DOCX files here
├── 📁 output/                      ← Generated results
├── 📁 logs/                        ← Log files
├── 📁 docs/guides/                 ← Documentation
│
├── 📄 VERSION.json                 ← Version info
├── 📄 CHANGELOG.md                 ← Change history
└── 📄 STARTER_GUIDE.md             ← Complete guide
"""
    print(structure)

def main():
    """Main menu loop"""
    while True:
        show_menu()

        try:
            choice = input("Enter your choice (0-17): ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break

        if choice == "0":
            print("\nGoodbye! 👋")
            break

        # Pipeline Operations
        elif choice == "1":
            run_command("main.py", "Main RTM pipeline")
        elif choice == "2":
            run_command("find_output_files.py", "Check output files")
        elif choice == "3":
            run_command("create_test_document.py", "Create test document")

        # Diagnostics & Testing
        elif choice == "4":
            run_command("comprehensive_test.py", "Comprehensive system test")
        elif choice == "5":
            run_command("fix_environment.py", "Fix environment issues")
        elif choice == "6":
            run_command("test_python_docx.py", "Test python-docx")
        elif choice == "7":
            run_command("simple_workflow_test.py", "Simple workflow test")

        # Git & GitHub
        elif choice == "8":
            run_command("scripts/quality/verify_github_status.py", "Check GitHub status")
        elif choice == "9":
            run_command("scripts/automation/version_manager.py", "Version manager")
        elif choice == "10":
            run_command("scripts/automation/smart_cleanup_commit.py", "Smart commit")
        elif choice == "11":
            run_command("scripts/quality/simple_clone_test.py", "Test GitHub clone")

        # Setup & Maintenance
        elif choice == "12":
            run_command("project_scanner.py", "Project scanner")
        elif choice == "13":
            run_command("reset_environment.py", "Reset environment")
        elif choice == "14":
            run_command("install_dependencies.py", "Install dependencies")
        elif choice == "15":
            run_command("scripts/setup/setup_project.py", "Setup project")

        # Documentation
        elif choice == "16":
            open_starter_guide()
        elif choice == "17":
            show_project_structure()

        else:
            print("❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("🚀 Starting RTM Automation Navigation Menu...")
    main()
