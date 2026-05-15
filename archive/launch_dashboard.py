#!/usr/bin/env python3
"""
Direct Dashboard Launcher - Launch RTM web dashboard directly
"""

import sys
import subprocess
from pathlib import Path


def launch_dashboard_direct():
    """Launch dashboard using direct file execution."""

    print("🌐 RTM Web Dashboard Launcher")
    print("=" * 35)

    # Possible dashboard locations
    dashboard_paths = [
        Path("src/dashboard/rtm_web_dashboard.py"),
        Path("rtm_web_dashboard.py"),
        Path("src/dashboard/rtm_dashboard.py"),
        Path("rtm_dashboard.py"),
    ]

    dashboard_found = None

    for dashboard_path in dashboard_paths:
        if dashboard_path.exists():
            dashboard_found = dashboard_path
            print(f"✅ Found dashboard: {dashboard_path}")
            break

    if not dashboard_found:
        print("❌ No dashboard file found!")
        print("💡 Looking for dashboard files...")

        # Search for any file with 'dashboard' in the name
        dashboard_files = list(Path(".").rglob("*dashboard*.py"))
        if dashboard_files:
            print("📁 Found these dashboard files:")
            for i, file_path in enumerate(dashboard_files, 1):
                print(f"   {i}. {file_path}")

            try:
                choice = input(
                    f"\nSelect dashboard (1-{len(dashboard_files)}): "
                ).strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(dashboard_files):
                    dashboard_found = dashboard_files[choice_idx]
                else:
                    print("❌ Invalid choice")
                    return 1
            except (ValueError, EOFError, KeyboardInterrupt):
                print("\n❌ No valid selection made")
                return 1
        else:
            print("❌ No dashboard files found in the entire project")
            return 1

    # Launch the dashboard
    print(f"\n🚀 Launching dashboard: {dashboard_found}")
    print("=" * 50)

    try:
        # Add src to path in case it's needed
        src_path = Path("src")
        env = None
        if src_path.exists():
            import os

            env = os.environ.copy()
            current_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{src_path.absolute()}{os.pathsep}{current_path}"

        result = subprocess.run([sys.executable, str(dashboard_found)], env=env)
        return result.returncode

    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1


def launch_dashboard_import():
    """Try to launch dashboard using imports."""

    print("🔧 Trying import-based launch...")

    try:
        # Add src to path
        src_path = Path("src")
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Try different import methods
        import_attempts = [
            (
                "from dashboard.rtm_web_dashboard import main",
                "dashboard.rtm_web_dashboard",
            ),
            (
                "from src.dashboard.rtm_web_dashboard import main",
                "src.dashboard.rtm_web_dashboard",
            ),
            ("import rtm_web_dashboard", "rtm_web_dashboard"),
        ]

        for import_statement, module_name in import_attempts:
            try:
                print(f"   Trying: {import_statement}")
                exec(import_statement)
                print("   ✅ Success! Calling main()")
                return exec("main()")
            except ImportError as e:
                print(f"   ❌ {e}")
                continue
            except Exception as e:
                print(f"   ⚠️ Import succeeded but execution failed: {e}")
                continue

        print("❌ All import attempts failed")
        return 1

    except Exception as e:
        print(f"❌ Import method failed: {e}")
        return 1


def main():
    """Main launcher function."""

    print("🌐 RTM Dashboard Launcher")
    print("=" * 30)
    print("Attempting to launch RTM web dashboard...")

    # Try import method first
    print("\n🔧 Method 1: Import-based launch")
    import_result = launch_dashboard_import()

    if import_result == 0:
        return 0

    # Fall back to direct execution
    print("\n🔧 Method 2: Direct file execution")
    direct_result = launch_dashboard_direct()

    if direct_result == 0:
        return 0

    # If all methods fail
    print("\n❌ Dashboard launch failed with all methods")
    print("💡 Try these alternatives:")
    print("   1. python main_organized.py")
    print("      Then choose option 3 (Web Dashboard)")
    print("   2. Find dashboard file manually:")
    print("      find . -name '*dashboard*.py'")
    print("   3. Check if dashboard needs additional setup")

    return 1


if __name__ == "__main__":
    sys.exit(main())
