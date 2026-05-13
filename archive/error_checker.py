"""
Error Checker - Comprehensive error detection and monitoring for RTM system
"""

import json
import os
import sys
import traceback
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class RTMErrorChecker:
    """Comprehensive error checking and monitoring system"""

    def __init__(self):
        self.setup_logging()
        self.error_patterns = self._load_error_patterns()
        self.critical_files = [
            "setup_and_run_pipeline.py",
            "debug_console.py",
            "word_markdown_pipeline_fixed.py",
            "rtm_master_control.py"
        ]

    def setup_logging(self):
        """Setup error logging"""
        os.makedirs("logs", exist_ok=True)

        self.logger = logging.getLogger("ErrorChecker")
        self.logger.setLevel(logging.DEBUG)

        # Create error log handler
        error_handler = logging.FileHandler(
            f"logs/error_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        error_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load common error patterns to look for"""
        return {
            "critical_errors": [
                "ImportError", "ModuleNotFoundError", "FileNotFoundError",
                "PermissionError", "OSError", "SystemError", "MemoryError"
            ],
            "runtime_errors": [
                "AttributeError", "TypeError", "ValueError", "KeyError",
                "IndexError", "NameError", "UnboundLocalError"
            ],
            "pipeline_errors": [
                "Pipeline failed", "Processing failed", "Conversion failed",
                "RTM processing error", "Debug console error"
            ],
            "warning_patterns": [
                "WARNING", "WARN", "deprecated", "compatibility",
                "unsupported", "missing"
            ]
        }

    def scan_log_files_for_errors(self) -> Dict[str, Any]:
        """Scan all log files for errors and issues"""
        print("🔍 Scanning log files for errors...")

        error_report = {
            "timestamp": datetime.now().isoformat(),
            "log_files_scanned": [],
            "errors_found": {
                "critical": [],
                "runtime": [],
                "pipeline": [],
                "warnings": []
            },
            "error_summary": {},
            "recent_errors": [],
            "error_trends": {}
        }

        logs_dir = Path("logs")
        if not logs_dir.exists():
            print("📁 No logs directory found")
            return error_report

        # Scan all log files
        for log_file in logs_dir.glob("*.log"):
            try:
                error_report["log_files_scanned"].append(str(log_file))
                print(f"📄 Scanning: {log_file.name}")

                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check for different error types
                for error_type, patterns in self.error_patterns.items():
                    for pattern in patterns:
                        matches = self._find_error_matches(content, pattern, str(log_file))
                        if matches:
                            error_report["errors_found"][error_type].extend(matches)

            except Exception as e:
                self.logger.error(f"Error scanning {log_file}: {e}")

        # Generate summary
        for error_type, errors in error_report["errors_found"].items():
            error_report["error_summary"][error_type] = len(errors)

        # Find recent errors (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        for error_type, errors in error_report["errors_found"].items():
            for error in errors:
                if error.get("timestamp") and self._parse_timestamp(error["timestamp"]) > recent_cutoff:
                    error_report["recent_errors"].append(error)

        print(f"📊 Error scan complete:")
        for error_type, count in error_report["error_summary"].items():
            if count > 0:
                print(f"   {error_type}: {count} found")

        return error_report

    def _find_error_matches(self, content: str, pattern: str, file_path: str) -> List[Dict]:
        """Find error pattern matches in content"""
        matches = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            if pattern.lower() in line.lower():
                matches.append({
                    "file": file_path,
                    "line_number": line_num,
                    "pattern": pattern,
                    "content": line.strip(),
                    "timestamp": self._extract_timestamp(line),
                    "severity": self._determine_severity(line, pattern)
                })

        return matches

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line"""
        # Look for common timestamp patterns
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{2}:\d{2}:\d{2}'
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()

        return None

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime"""
        try:
            if 'T' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', ''))
            elif len(timestamp_str) == 8:  # HH:MM:SS
                today = datetime.now().date()
                time_part = datetime.strptime(timestamp_str, '%H:%M:%S').time()
                return datetime.combine(today, time_part)
            else:
                return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.min

    def _determine_severity(self, line: str, pattern: str) -> str:
        """Determine error severity"""
        line_lower = line.lower()

        if any(critical in line_lower for critical in ['critical', 'fatal', 'error']):
            return "HIGH"
        elif any(warning in line_lower for warning in ['warning', 'warn']):
            return "MEDIUM"
        else:
            return "LOW"

    def check_system_integrity(self) -> Dict[str, Any]:
        """Check system file integrity and availability"""
        print("🔧 Checking system integrity...")

        integrity_report = {
            "timestamp": datetime.now().isoformat(),
            "file_checks": {},
            "directory_checks": {},
            "import_checks": {},
            "permission_checks": {},
            "issues_found": []
        }

        # Check critical files
        for file_path in self.critical_files:
            check_result = self._check_file_integrity(file_path)
            integrity_report["file_checks"][file_path] = check_result

            if not check_result["exists"] or check_result["errors"]:
                integrity_report["issues_found"].append({
                    "type": "file_integrity",
                    "item": file_path,
                    "issue": check_result
                })

        # Check directories
        required_dirs = ["input", "output", "temp_processing", "logs"]
        for dir_path in required_dirs:
            check_result = self._check_directory_integrity(dir_path)
            integrity_report["directory_checks"][dir_path] = check_result

            if check_result["issues"]:
                integrity_report["issues_found"].append({
                    "type": "directory_integrity",
                    "item": dir_path,
                    "issue": check_result
                })

        # Check imports
        critical_modules = [
            "json", "os", "sys", "pathlib", "datetime", "logging",
            "traceback", "subprocess", "psutil"
        ]
        for module in critical_modules:
            check_result = self._check_import(module)
            integrity_report["import_checks"][module] = check_result

            if not check_result["available"]:
                integrity_report["issues_found"].append({
                    "type": "import_error",
                    "item": module,
                    "issue": check_result
                })

        print(f"🎯 Integrity check complete: {len(integrity_report['issues_found'])} issues found")

        return integrity_report

    def _check_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """Check individual file integrity"""
        result = {
            "exists": False,
            "readable": False,
            "size_bytes": 0,
            "last_modified": None,
            "syntax_valid": False,
            "errors": []
        }

        try:
            if os.path.exists(file_path):
                result["exists"] = True
                result["size_bytes"] = os.path.getsize(file_path)
                result["last_modified"] = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat()

                # Check readability
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        result["readable"] = True

                    # Check Python syntax if .py file
                    if file_path.endswith('.py'):
                        try:
                            compile(content, file_path, 'exec')
                            result["syntax_valid"] = True
                        except SyntaxError as e:
                            result["errors"].append(f"Syntax error: {e}")

                except Exception as e:
                    result["errors"].append(f"Read error: {e}")

        except Exception as e:
            result["errors"].append(f"File check error: {e}")

        return result

    def _check_directory_integrity(self, dir_path: str) -> Dict[str, Any]:
        """Check directory integrity"""
        result = {
            "exists": False,
            "accessible": False,
            "file_count": 0,
            "total_size": 0,
            "issues": []
        }

        try:
            if os.path.exists(dir_path):
                result["exists"] = True

                try:
                    files = os.listdir(dir_path)
                    result["accessible"] = True
                    result["file_count"] = len([f for f in files
                                             if os.path.isfile(os.path.join(dir_path, f))])

                    # Calculate total size
                    total_size = 0
                    for file in files:
                        file_path = os.path.join(dir_path, file)
                        if os.path.isfile(file_path):
                            total_size += os.path.getsize(file_path)
                    result["total_size"] = total_size

                except PermissionError:
                    result["issues"].append("Permission denied")
                except Exception as e:
                    result["issues"].append(f"Access error: {e}")

        except Exception as e:
            result["issues"].append(f"Directory check error: {e}")

        return result

    def _check_import(self, module_name: str) -> Dict[str, Any]:
        """Check if module can be imported"""
        result = {
            "available": False,
            "version": None,
            "location": None,
            "error": None
        }

        try:
            module = __import__(module_name)
            result["available"] = True

            # Try to get version
            if hasattr(module, '__version__'):
                result["version"] = module.__version__

            # Try to get location
            if hasattr(module, '__file__'):
                result["location"] = module.__file__

        except Exception as e:
            result["error"] = str(e)

        return result

    def generate_comprehensive_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report combining all checks"""
        print("📋 Generating comprehensive error report...")

        comprehensive_report = {
            "timestamp": datetime.now().isoformat(),
            "report_type": "comprehensive_error_analysis",
            "log_scan_results": self.scan_log_files_for_errors(),
            "integrity_check_results": self.check_system_integrity(),
            "summary": {},
            "recommendations": [],
            "severity_assessment": "LOW"
        }

        # Generate summary
        total_errors = 0
        critical_issues = 0

        # Count log errors
        for error_type, errors in comprehensive_report["log_scan_results"]["errors_found"].items():
            error_count = len(errors)
            total_errors += error_count

            if error_type in ["critical_errors", "runtime_errors"] and error_count > 0:
                critical_issues += error_count

        # Count integrity issues
        integrity_issues = len(comprehensive_report["integrity_check_results"]["issues_found"])
        total_errors += integrity_issues

        if integrity_issues > 0:
            critical_issues += integrity_issues

        comprehensive_report["summary"] = {
            "total_errors_found": total_errors,
            "critical_issues": critical_issues,
            "integrity_issues": integrity_issues,
            "recent_errors": len(comprehensive_report["log_scan_results"]["recent_errors"])
        }

        # Determine severity
        if critical_issues > 5:
            comprehensive_report["severity_assessment"] = "HIGH"
        elif critical_issues > 0 or total_errors > 10:
            comprehensive_report["severity_assessment"] = "MEDIUM"
        else:
            comprehensive_report["severity_assessment"] = "LOW"

        # Generate recommendations
        comprehensive_report["recommendations"] = self._generate_recommendations(comprehensive_report)

        # Save report
        report_file = f"logs/comprehensive_error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)

        print(f"📄 Comprehensive error report saved to: {report_file}")
        print(f"🎯 Summary: {total_errors} total issues, {critical_issues} critical, severity: {comprehensive_report['severity_assessment']}")

        return comprehensive_report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on error analysis"""
        recommendations = []

        # Check for critical issues
        if report["summary"]["critical_issues"] > 0:
            recommendations.append("🔴 Critical issues detected - run debug console for detailed analysis")

        # Check for integrity issues
        integrity_issues = report["integrity_check_results"]["issues_found"]
        if integrity_issues:
            recommendations.append("🔧 File integrity issues found - check file permissions and availability")

        # Check for recent errors
        if report["summary"]["recent_errors"] > 5:
            recommendations.append("⚠️ Multiple recent errors - consider restarting the pipeline")

        # Check for import errors
        import_issues = [issue for issue in integrity_issues if issue["type"] == "import_error"]
        if import_issues:
            recommendations.append("📦 Missing modules detected - run 'pip install -r requirements.txt'")

        # General recommendations
        if report["summary"]["total_errors_found"] == 0:
            recommendations.append("✅ No significant errors detected - system is healthy")
        else:
            recommendations.append("🔍 Use debug console for detailed error investigation")
            recommendations.append("📊 Run full diagnostics export for complete analysis")

        return recommendations

    def monitor_real_time_errors(self, duration_minutes: int = 5):
        """Monitor for real-time errors"""
        print(f"👁️ Starting real-time error monitoring for {duration_minutes} minutes...")

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        monitored_files = []

        # Find recent log files to monitor
        logs_dir = Path("logs")
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).total_seconds() < 3600:
                    monitored_files.append(log_file)

        print(f"📁 Monitoring {len(monitored_files)} recent log files...")

        errors_detected = []

        try:
            while datetime.now() < end_time:
                for log_file in monitored_files:
                    try:
                        # Check for new content
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()

                        # Check last few lines for errors
                        for line in lines[-5:]:
                            for error_type, patterns in self.error_patterns.items():
                                for pattern in patterns:
                                    if pattern.lower() in line.lower():
                                        error_info = {
                                            "timestamp": datetime.now().isoformat(),
                                            "file": str(log_file),
                                            "pattern": pattern,
                                            "content": line.strip()
                                        }
                                        if error_info not in errors_detected:
                                            errors_detected.append(error_info)
                                            print(f"🚨 Error detected: {pattern} in {log_file.name}")

                    except Exception as e:
                        self.logger.error(f"Error monitoring {log_file}: {e}")

                # Sleep for a short interval
                import time
                time.sleep(5)

        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")

        print(f"📊 Monitoring complete. {len(errors_detected)} errors detected during monitoring period.")

        return errors_detected

def main():
    """Main function for error checking"""
    print("🔍 RTM Error Checker - Comprehensive Error Detection")
    print("=" * 60)

    checker = RTMErrorChecker()

    print("\nSelect error checking mode:")
    print("1. 📋 Comprehensive Error Report (Recommended)")
    print("2. 🔍 Log File Error Scan Only")
    print("3. 🔧 System Integrity Check Only")
    print("4. 👁️ Real-time Error Monitoring")
    print("5. 📊 All Checks + JSON Export")

    try:
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            report = checker.generate_comprehensive_error_report()

        elif choice == '2':
            report = checker.scan_log_files_for_errors()
            print(f"📄 Log scan report saved to logs/")

        elif choice == '3':
            report = checker.check_system_integrity()
            print(f"🔧 Integrity check complete")

        elif choice == '4':
            duration = input("Enter monitoring duration in minutes (default 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            errors = checker.monitor_real_time_errors(duration)

        elif choice == '5':
            print("📊 Running all error checks and exporting to JSON...")
            report = checker.generate_comprehensive_error_report()

            # Also run debug console diagnostics
            try:
                from debug_console import RTMDebugConsole
                debug_console = RTMDebugConsole()
                debug_report = debug_console.export_all_diagnostics()
                print("✅ Debug console diagnostics also exported")
            except Exception as e:
                print(f"⚠️ Could not run debug console: {e}")

        else:
            print("❌ Invalid choice")
            return

        print("\n✅ Error checking complete!")
        print("📁 Check the logs/ directory for detailed reports")

    except KeyboardInterrupt:
        print("\n⏹️ Error checking interrupted by user")
    except Exception as e:
        print(f"\n❌ Error checking failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
