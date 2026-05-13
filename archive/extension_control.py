#!/usr/bin/env python3
"""
RTM Extension Control Interface - Simple commands to manage extensions
"""

import sys
from extension_manager import ExtensionManager


def main():
    """Simple command-line interface for extension control."""
    if len(sys.argv) < 2:
        print(
            """
🔧 RTM Extension Control
========================

Usage:
  python extension_control.py <command> [arguments]

Commands:
  list                     - List all extensions
  status <name>           - Show extension status
  activate <name>         - Activate extension
  deactivate <name>       - Deactivate extension
  dashboard              - Launch monitoring dashboard
  report                 - Generate extension report
  health                 - Show system health

Examples:
  python extension_control.py list
  python extension_control.py activate digital_twin_parser
  python extension_control.py status enhance_document_parsing
"""
        )
        return 1

    manager = ExtensionManager()
    command = sys.argv[1].lower()

    if command == "list":
        print("📦 RTM Extensions:")
        print("=" * 40)

        for name, ext in manager.extensions.items():
            status_icon = (
                "✅"
                if ext.status == "active"
                else "⏸️"
                if ext.status == "inactive"
                else "❌"
            )
            print(f"  {status_icon} {name} ({ext.extension_type})")
            if ext.description:
                print(f"     {ext.description[:60]}...")

        summary = manager.get_summary()
        print(f"\nTotal: {summary['total_extensions']} extensions")

    elif command == "status" and len(sys.argv) > 2:
        name = sys.argv[2]
        status = manager.get_extension_status(name)

        if "error" in status:
            print(f"❌ {status['error']}")
        else:
            print(f"📊 Extension Status: {name}")
            print(f"   Type: {status['type']}")
            print(f"   Status: {status['status']}")
            print(f"   Path: {status['path']}")
            print(f"   File Exists: {'✅' if status['file_exists'] else '❌'}")
            print(f"   Version: {status['version']}")
            print(f"   Last Used: {status['last_used'] or 'Never'}")
            print(f"   Error Count: {status['error_count']}")

            if status["dependencies"]:
                print("   Dependencies:")
                for dep, available in status["dependencies_available"].items():
                    icon = "✅" if available else "❌"
                    print(f"     {icon} {dep}")

    elif command == "activate" and len(sys.argv) > 2:
        name = sys.argv[2]
        if manager.activate_extension(name):
            print(f"✅ Activated extension: {name}")
        else:
            print(f"❌ Failed to activate extension: {name}")

    elif command == "deactivate" and len(sys.argv) > 2:
        name = sys.argv[2]
        if manager.deactivate_extension(name):
            print(f"⏸️ Deactivated extension: {name}")
        else:
            print(f"❌ Failed to deactivate extension: {name}")

    elif command == "dashboard":
        from src.dashboard.extension_dashboard import main as dashboard_main

        dashboard_main()

    elif command == "report":
        report = manager.generate_report()
        print("📊 Extension report generated")
        print(f"   Total Extensions: {report['summary']['total_extensions']}")
        print("   Report saved to: extension_report.json")

    elif command == "health":
        summary = manager.get_summary()
        from src.dashboard.extension_dashboard import calculate_health_score

        health = calculate_health_score(summary)

        print(f"🎯 RTM System Health: {health}/100")
        print(f"   Total Extensions: {summary['total_extensions']}")
        print(f"   Active: {summary['by_status'].get('active', 0)}")
        print(f"   Inactive: {summary['by_status'].get('inactive', 0)}")
        print(f"   Errors: {summary['by_status'].get('error', 0)}")

        if health >= 80:
            print("   Status: 🟢 Excellent")
        elif health >= 60:
            print("   Status: 🟡 Good")
        else:
            print("   Status: 🔴 Needs Attention")

    else:
        print(f"❌ Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
