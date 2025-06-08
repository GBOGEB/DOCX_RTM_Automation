#!/usr/bin/env python3
"""
RTM Extension Dashboard - Visual monitoring interface
"""

import json
import time
from pathlib import Path
from datetime import datetime
from extension_manager import ExtensionManager

def display_dashboard():
    """Display a real-time dashboard of extension status."""
    manager = ExtensionManager()

    while True:
        # Clear screen (works on most terminals)
        print("\033[2J\033[H")

        print("🔧 RTM EXTENSION DASHBOARD")
        print("=" * 60)
        print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        summary = manager.get_summary()

        # System Overview
        print(f"\n📊 SYSTEM OVERVIEW:")
        print(f"   📦 Total Extensions: {summary['total_extensions']}")
        print(f"   ✅ Active: {summary['by_status'].get('active', 0)}")
        print(f"   ⏸️  Inactive: {summary['by_status'].get('inactive', 0)}")
        print(f"   ❌ Errors: {summary['by_status'].get('error', 0)}")

        # Extension Types
        print(f"\n🏷️ EXTENSION TYPES:")
        for ext_type, count in sorted(summary['by_type'].items()):
            status_indicator = "🟢" if count > 0 else "⚪"
            print(f"   {status_indicator} {ext_type.replace('_', ' ').title()}: {count}")

        # Active Extensions
        if summary['active_extensions']:
            print(f"\n⚡ ACTIVE EXTENSIONS:")
            for ext_name in summary['active_extensions'][:8]:
                ext = manager.extensions[ext_name]
                last_used = ext.last_used or "Never"
                if ext.last_used:
                    last_used = datetime.fromisoformat(ext.last_used).strftime('%H:%M')
                print(f"   🟢 {ext_name} ({ext.extension_type}) - {last_used}")

        # Error Extensions
        if summary['error_extensions']:
            print(f"\n❌ EXTENSIONS WITH ERRORS:")
            for ext_name in summary['error_extensions'][:5]:
                ext = manager.extensions[ext_name]
                print(f"   🔴 {ext_name} - Errors: {ext.error_count}")

        # Recent Activity
        if summary['recent_activity']:
            print(f"\n📈 RECENT ACTIVITY:")
            for activity in summary['recent_activity'][:5]:
                time_str = datetime.fromisoformat(activity['last_used']).strftime('%H:%M')
                print(f"   📍 {activity['name']} - {time_str}")

        # AI Extensions Status
        ai_extensions = [name for name, ext in manager.extensions.items()
                        if 'ai' in ext.extension_type or 'ariana' in name.lower()]
        if ai_extensions:
            print(f"\n🤖 AI EXTENSIONS ({len(ai_extensions)}):")
            for ext_name in ai_extensions[:5]:
                ext = manager.extensions[ext_name]
                status_icon = "🟢" if ext.status == "active" else "⚪"
                print(f"   {status_icon} {ext_name}")

        # System Health
        health_score = calculate_health_score(summary)
        health_color = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🔴"
        print(f"\n🎯 SYSTEM HEALTH: {health_color} {health_score}/100")

        print(f"\n⌨️  Commands: [q]uit | [r]efresh | [a]ctivate | [d]eactivate")
        print(f"📊 Press Ctrl+C to exit dashboard")

        # Auto-refresh every 10 seconds
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n👋 Dashboard closed")
            break

def calculate_health_score(summary):
    """Calculate system health score based on extension status."""
    total = summary['total_extensions']
    if total == 0:
        return 100

    active = summary['by_status'].get('active', 0)
    errors = summary['by_status'].get('error', 0)

    # Score based on active percentage minus error penalty
    active_score = (active / total) * 70
    error_penalty = (errors / total) * 30
    base_score = 30  # Base score for having extensions

    return max(0, min(100, int(active_score + base_score - error_penalty)))

def main():
    """Main dashboard function."""
    print("🚀 Starting RTM Extension Dashboard...")
    display_dashboard()

if __name__ == "__main__":
    main()
