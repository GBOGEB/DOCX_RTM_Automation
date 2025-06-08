#!/usr/bin/env python3
"""
RTM Main Entry Point - Works with organized project structure
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

def run_json_analyzer():
    """Run JSON analysis."""
    try:
        from analyzers.json_file_analyzer_safe import main
        print("🔍 Running JSON Analyzer...")
        return main()
    except ImportError as e:
        print(f"❌ Could not import JSON analyzer: {e}")
        # Fallback to direct execution
        import subprocess
        analyzer_path = src_path / "analyzers" / "json_file_analyzer_safe.py"
        if analyzer_path.exists():
            return subprocess.run([sys.executable, str(analyzer_path)]).returncode
        return 1

def run_rtm_pipeline():
    """Run RTM processing pipeline."""
    try:
        from rtm.rtm_pipeline import main
        print("🚀 Running RTM Pipeline...")
        return main()
    except ImportError as e:
        print(f"❌ Could not import RTM pipeline: {e}")
        print("💡 Import paths may need fixing.")
        return 1

def run_web_dashboard():
    """Run web dashboard."""
    try:
        from dashboard.rtm_web_dashboard import main
        print("🌐 Starting Web Dashboard...")
        return main()
    except ImportError as e:
        print(f"❌ Could not import web dashboard: {e}")
        # Fallback to direct execution
        import subprocess
        dashboard_path = src_path / "dashboard" / "rtm_web_dashboard.py"
        if dashboard_path.exists():
            return subprocess.run([sys.executable, str(dashboard_path)]).returncode
        return 1

def run_quality_check():
    """Run quality checks."""
    try:
        from analyzers.simple_quality_check import main
        print("🔍 Running Quality Check...")
        return main()
    except ImportError as e:
        print(f"❌ Could not import quality check: {e}")
        return 1

def show_status():
    """Show system status."""
    print("📊 RTM System Status")
    print("=" * 25)

    # Check key components
    components = {
        "JSON Analyzer": src_path / "analyzers" / "json_file_analyzer_safe.py",
        "RTM Pipeline": src_path / "rtm" / "rtm_pipeline.py",
        "Web Dashboard": src_path / "dashboard" / "rtm_web_dashboard.py",
        "Config File": Path("config") / "config.json"
    }

    for name, path in components.items():
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {name}: {path}")

    # Check organization
    organized_dirs = ["src/rtm", "src/parsers", "src/analyzers", "src/dashboard", "config", "docs"]
    organized_count = sum(1 for d in organized_dirs if Path(d).exists())

    print(f"\n📁 Project Organization: {organized_count}/{len(organized_dirs)} directories")
    print(f"🎯 Organization Status: {'✅ ORGANIZED' if organized_count >= 4 else '⚠️ PARTIAL'}")

def main():
    """Main entry point."""
    print("🚀 RTM Automation System (Organized)")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "analyze":
            return run_json_analyzer()
        elif command == "pipeline":
            return run_rtm_pipeline()
        elif command == "dashboard":
            return run_web_dashboard()
        elif command == "quality":
            return run_quality_check()
        elif command == "status":
            show_status()
            return 0
        else:
            print(f"❌ Unknown command: {command}")
            return 1

    # Interactive menu
    print("Choose an option:")
    print("1. Run JSON Analysis")
    print("2. Run RTM Pipeline")
    print("3. Start Web Dashboard")
    print("4. Run Quality Check")
    print("5. Show System Status")
    print("6. Exit")

    try:
        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            return run_json_analyzer()
        elif choice == "2":
            return run_rtm_pipeline()
        elif choice == "3":
            return run_web_dashboard()
        elif choice == "4":
            return run_quality_check()
        elif choice == "5":
            show_status()
            return 0
        elif choice == "6":
            print("👋 Goodbye!")
            return 0
        else:
            print("❌ Invalid choice")
            return 1

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
