"""
RTM Monitoring Dashboard - Real-time system monitoring and status display
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import threading

class RTMMonitoringDashboard:
    """Real-time monitoring dashboard for RTM system"""

    def __init__(self):
        self.running = False
        self.refresh_interval = 5  # seconds
        self.metrics_history = []
        self.max_history = 50

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            import psutil

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('.').percent,
                "process_count": len(psutil.pids()),
                "python_memory": psutil.Process().memory_info().rss / 1024 / 1024  # MB
            }
        except ImportError:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": "N/A",
                "memory_percent": "N/A",
                "disk_percent": "N/A",
                "process_count": "N/A",
                "python_memory": "N/A"
            }

        return metrics

    def get_file_metrics(self) -> Dict[str, Any]:
        """Get file system metrics"""
        directories = ["input", "output", "temp_processing", "logs"]
        metrics = {}

        for dir_name in directories:
            if os.path.exists(dir_name):
                file_count = len([f for f in os.listdir(dir_name)
                                if os.path.isfile(os.path.join(dir_name, f))])
                total_size = sum(os.path.getsize(os.path.join(dir_name, f))
                               for f in os.listdir(dir_name)
                               if os.path.isfile(os.path.join(dir_name, f)))
                metrics[dir_name] = {
                    "file_count": file_count,
                    "total_size": total_size,
                    "size_mb": round(total_size / 1024 / 1024, 2)
                }
            else:
                metrics[dir_name] = {
                    "file_count": 0,
                    "total_size": 0,
                    "size_mb": 0
                }

        return metrics

    def get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity metrics"""
        activity = {
            "recent_logs": [],
            "recent_outputs": [],
            "last_error_check": None,
            "last_health_check": None
        }

        # Check for recent log files
        logs_dir = Path("logs")
        if logs_dir.exists():
            recent_logs = []
            cutoff_time = datetime.now() - timedelta(hours=1)

            for log_file in logs_dir.glob("*.log"):
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime > cutoff_time:
                    recent_logs.append({
                        "filename": log_file.name,
                        "modified": mtime.isoformat(),
                        "size": log_file.stat().st_size
                    })

            activity["recent_logs"] = sorted(recent_logs,
                                           key=lambda x: x["modified"],
                                           reverse=True)[:5]

            # Check for recent error check
            error_files = list(logs_dir.glob("comprehensive_error_report_*.json"))
            if error_files:
                latest_error = max(error_files, key=lambda x: x.stat().st_mtime)
                activity["last_error_check"] = datetime.fromtimestamp(
                    latest_error.stat().st_mtime
                ).isoformat()

            # Check for recent health check
            health_files = list(logs_dir.glob("health_report_*.json"))
            if health_files:
                latest_health = max(health_files, key=lambda x: x.stat().st_mtime)
                activity["last_health_check"] = datetime.fromtimestamp(
                    latest_health.stat().st_mtime
                ).isoformat()

        # Check for recent output files
        output_dir = Path("output")
        if output_dir.exists():
            recent_outputs = []
            cutoff_time = datetime.now() - timedelta(hours=1)

            for output_file in output_dir.glob("*"):
                if output_file.is_file():
                    mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
                    if mtime > cutoff_time:
                        recent_outputs.append({
                            "filename": output_file.name,
                            "modified": mtime.isoformat(),
                            "size": output_file.stat().st_size
                        })

            activity["recent_outputs"] = sorted(recent_outputs,
                                              key=lambda x: x["modified"],
                                              reverse=True)[:5]

        return activity

    def get_error_summary(self) -> Dict[str, Any]:
        """Get latest error summary"""
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"status": "no_logs", "message": "No logs directory found"}

        # Find latest error report
        error_files = list(logs_dir.glob("comprehensive_error_report_*.json"))
        if not error_files:
            return {"status": "no_reports", "message": "No error reports found"}

        latest_report = max(error_files, key=lambda x: x.stat().st_mtime)

        try:
            with open(latest_report, 'r') as f:
                error_data = json.load(f)

            return {
                "status": "available",
                "timestamp": error_data.get("timestamp"),
                "severity": error_data.get("severity_assessment", "UNKNOWN"),
                "total_errors": error_data.get("summary", {}).get("total_errors_found", 0),
                "critical_issues": error_data.get("summary", {}).get("critical_issues", 0),
                "report_file": latest_report.name
            }
        except Exception as e:
            return {"status": "error", "message": f"Error reading report: {e}"}

    def display_dashboard(self):
        """Display the monitoring dashboard"""
        # Clear screen (works on both Windows and Unix)
        os.system('cls' if os.name == 'nt' else 'clear')

        print("╔" + "═" * 78 + "╗")
        print("║" + " RTM SYSTEM MONITORING DASHBOARD".center(78) + "║")
        print("║" + f" Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "║")
        print("╚" + "═" * 78 + "╝")

        # Get current metrics
        system_metrics = self.get_system_metrics()
        file_metrics = self.get_file_metrics()
        activity = self.get_recent_activity()
        error_summary = self.get_error_summary()

        # Store metrics history
        self.metrics_history.append({
            "timestamp": datetime.now(),
            "system": system_metrics,
            "files": file_metrics
        })

        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]

        # System Resources Section
        print("\n🖥️  SYSTEM RESOURCES")
        print("─" * 50)
        if system_metrics["cpu_percent"] != "N/A":
            cpu_bar = self.create_progress_bar(system_metrics["cpu_percent"], 100)
            mem_bar = self.create_progress_bar(system_metrics["memory_percent"], 100)
            disk_bar = self.create_progress_bar(system_metrics["disk_percent"], 100)

            print(f"CPU Usage:    {system_metrics['cpu_percent']:5.1f}% {cpu_bar}")
            print(f"Memory Usage: {system_metrics['memory_percent']:5.1f}% {mem_bar}")
            print(f"Disk Usage:   {system_metrics['disk_percent']:5.1f}% {disk_bar}")
            print(f"Python Memory: {system_metrics['python_memory']:5.1f} MB")
        else:
            print("System monitoring not available (psutil not installed)")

        # File System Section
        print("\n📁 FILE SYSTEM STATUS")
        print("─" * 50)
        for dir_name, metrics in file_metrics.items():
            status_icon = "✅" if metrics["file_count"] > 0 else "📂"
            print(f"{status_icon} {dir_name:15} {metrics['file_count']:4} files ({metrics['size_mb']:6.1f} MB)")

        # Error Status Section
        print("\n🔍 ERROR STATUS")
        print("─" * 50)
        if error_summary["status"] == "available":
            severity_icon = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🔴",
                "UNKNOWN": "⚪"
            }.get(error_summary["severity"], "⚪")

            print(f"{severity_icon} Severity: {error_summary['severity']}")
            print(f"📊 Total Issues: {error_summary['total_errors']}")
            print(f"🚨 Critical: {error_summary['critical_issues']}")
            print(f"📄 Latest Report: {error_summary['report_file']}")
        else:
            print(f"⚠️  {error_summary['message']}")

        # Recent Activity Section
        print("\n⚡ RECENT ACTIVITY")
        print("─" * 50)

        if activity["last_health_check"]:
            health_time = datetime.fromisoformat(activity["last_health_check"])
            time_ago = self.time_ago(health_time)
            print(f"🏥 Last Health Check: {time_ago}")

        if activity["last_error_check"]:
            error_time = datetime.fromisoformat(activity["last_error_check"])
            time_ago = self.time_ago(error_time)
            print(f"🔍 Last Error Check: {time_ago}")

        if activity["recent_logs"]:
            print(f"📋 Recent Logs: {len(activity['recent_logs'])} files")
            for log in activity["recent_logs"][:3]:
                log_time = datetime.fromisoformat(log["modified"])
                time_ago = self.time_ago(log_time)
                print(f"   • {log['filename']} ({time_ago})")

        if activity["recent_outputs"]:
            print(f"📤 Recent Outputs: {len(activity['recent_outputs'])} files")
            for output in activity["recent_outputs"][:3]:
                output_time = datetime.fromisoformat(output["modified"])
                time_ago = self.time_ago(output_time)
                print(f"   • {output['filename']} ({time_ago})")

        # Performance Trends Section
        if len(self.metrics_history) > 5:
            print("\n📈 PERFORMANCE TRENDS (Last 5 readings)")
            print("─" * 50)

            # Calculate averages
            recent_metrics = self.metrics_history[-5:]
            if recent_metrics[0]["system"]["cpu_percent"] != "N/A":
                avg_cpu = sum(m["system"]["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m["system"]["memory_percent"] for m in recent_metrics) / len(recent_metrics)

                print(f"📊 Average CPU: {avg_cpu:.1f}%")
                print(f"📊 Average Memory: {avg_memory:.1f}%")

                # Show trend
                cpu_trend = "📈" if recent_metrics[-1]["system"]["cpu_percent"] > recent_metrics[0]["system"]["cpu_percent"] else "📉"
                memory_trend = "📈" if recent_metrics[-1]["system"]["memory_percent"] > recent_metrics[0]["system"]["memory_percent"] else "📉"

                print(f"📊 CPU Trend: {cpu_trend}")
                print(f"📊 Memory Trend: {memory_trend}")

        # Quick Actions Section
        print("\n🎯 QUICK ACTIONS")
        print("─" * 50)
        print("Press 'h' for health check | 'e' for error scan | 'd' for debug console")
        print("Press 'q' to quit | 'r' to refresh now")

        print(f"\n⏱️  Auto-refresh in {self.refresh_interval} seconds...")

    def create_progress_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        if value == "N/A":
            return "[" + "?" * width + "]"

        filled = int((value / max_value) * width)
        bar = "█" * filled + "░" * (width - filled)

        # Color coding based on value
        if value < 50:
            return f"[{bar}]"  # Normal
        elif value < 80:
            return f"[{bar}]"  # Warning (we can't do colors in simple terminal)
        else:
            return f"[{bar}]"  # Critical

    def time_ago(self, timestamp: datetime) -> str:
        """Calculate time ago string"""
        now = datetime.now()
        if timestamp.tzinfo is None:
            # Make timezone-naive for comparison
            pass
        else:
            # Handle timezone-aware timestamps
            timestamp = timestamp.replace(tzinfo=None)

        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"

    def handle_user_input(self):
        """Handle user input while dashboard is running"""
        while self.running:
            try:
                # Non-blocking input simulation
                if hasattr(sys.stdin, 'read'):
                    pass  # Could implement non-blocking input here
                time.sleep(0.1)
            except:
                pass

    def run_dashboard(self, duration_minutes: int = None):
        """Run the monitoring dashboard"""
        self.running = True

        print("🖥️  Starting RTM Monitoring Dashboard...")
        print("Press Ctrl+C to exit")

        if duration_minutes:
            print(f"Running for {duration_minutes} minutes")
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
        else:
            end_time = None

        try:
            while self.running:
                self.display_dashboard()

                # Check if duration expired
                if end_time and datetime.now() >= end_time:
                    print(f"\n⏰ Monitoring duration completed.")
                    break

                # Wait for refresh interval
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")
        finally:
            self.running = False

    def save_current_status(self):
        """Save current system status to file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.get_system_metrics(),
            "file_metrics": self.get_file_metrics(),
            "activity": self.get_recent_activity(),
            "error_summary": self.get_error_summary()
        }

        os.makedirs("logs", exist_ok=True)
        status_file = f"logs/dashboard_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)

        print(f"💾 Status saved to: {status_file}")
        return status_file

def main():
    """Main function for dashboard"""
    print("🖥️  RTM Monitoring Dashboard")
    print("=" * 50)

    dashboard = RTMMonitoringDashboard()

    print("\nSelect monitoring mode:")
    print("1. 🔄 Continuous Monitoring (Press Ctrl+C to stop)")
    print("2. ⏰ Timed Monitoring (Specify duration)")
    print("3. 📸 Single Status Snapshot")
    print("4. 💾 Save Current Status to File")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            dashboard.run_dashboard()
        elif choice == '2':
            duration = input("Enter duration in minutes (default 10): ").strip()
            duration = int(duration) if duration.isdigit() else 10
            dashboard.run_dashboard(duration)
        elif choice == '3':
            dashboard.display_dashboard()
            input("\nPress Enter to exit...")
        elif choice == '4':
            status_file = dashboard.save_current_status()
            print(f"Status saved! View with: cat {status_file}")
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n👋 Dashboard terminated by user")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")

if __name__ == "__main__":
    main()
