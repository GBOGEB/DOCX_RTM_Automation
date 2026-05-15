import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
import subprocess
import psutil

class RTMDebugConsole:
    def __init__(self, config_path="debug_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        self.health_status = {}

        # Handle debugger conflicts
        try:
            import debugpy
            if debugpy.is_client_connected():
                print("Debug client detected - running in compatibility mode")
        except ImportError:
            pass  # debugpy not available, continue normally
        except Exception as e:
            print(f"Debug setup warning: {e}")

    def load_config(self):
        """Load debug configuration from JSON file"""
        default_config = {
            "debug_level": "DEBUG",
            "log_to_file": True,
            "log_to_console": True,
            "health_check_interval": 30,
            "trace_all_operations": True,
            "include_ariana_extensions": True,
            "extensions_to_monitor": [
                ".docx", ".pdf", ".txt", ".rtf", ".odt",
                ".html", ".xml", ".json", ".log"
            ],
            "output_formats": ["json", "console", "file"],
            "diagnostic_depth": "full"
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
                    return default_config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return default_config
        else:
            # Create default config file
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_level = getattr(logging, self.config.get("debug_level", "DEBUG"))

        # Create logs directory
        os.makedirs("logs", exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger("RTM_Debug")
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # File handler
        if self.config.get("log_to_file", True):
            file_handler = logging.FileHandler(
                f"logs/rtm_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Console handler
        if self.config.get("log_to_console", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def system_health_check(self):
        """Comprehensive system health check"""
        print("\n" + "="*60)
        print("RTM SYSTEM HEALTH CHECK")
        print("="*60)

        health_report = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "directories": {},
            "extensions": {},
            "processes": {},
            "errors": [],
            "warnings": []
        }

        # System resources
        try:
            health_report["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('.').percent,
                "python_version": sys.version,
                "platform": sys.platform
            }
            print(f"✓ System Resources: CPU {health_report['system']['cpu_percent']}%, "
                  f"Memory {health_report['system']['memory_percent']}%, "
                  f"Disk {health_report['system']['disk_usage']}%")
        except Exception as e:
            health_report["errors"].append(f"System check failed: {str(e)}")
            print(f"✗ System Resources: Error - {e}")

        # Directory structure
        required_dirs = ["input", "output", "temp_processing", "logs"]
        for dir_name in required_dirs:
            try:
                if os.path.exists(dir_name):
                    dir_size = sum(os.path.getsize(os.path.join(dir_name, f))
                                 for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f)))
                    file_count = len([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))])
                    health_report["directories"][dir_name] = {
                        "exists": True,
                        "size_bytes": dir_size,
                        "file_count": file_count
                    }
                    print(f"✓ Directory {dir_name}: {file_count} files, {dir_size} bytes")
                else:
                    health_report["directories"][dir_name] = {"exists": False}
                    health_report["warnings"].append(f"Directory {dir_name} missing")
                    print(f"⚠ Directory {dir_name}: Missing")
            except Exception as e:
                health_report["errors"].append(f"Directory check failed for {dir_name}: {str(e)}")
                print(f"✗ Directory {dir_name}: Error - {e}")

        # Extension health check
        for ext in self.config.get("extensions_to_monitor", []):
            try:
                count = self.count_files_by_extension(ext)
                health_report["extensions"][ext] = count
                print(f"✓ Extension {ext}: {count} files found")
            except Exception as e:
                health_report["errors"].append(f"Extension check failed for {ext}: {str(e)}")
                print(f"✗ Extension {ext}: Error - {e}")

        # Process health
        try:
            current_process = psutil.Process()
            health_report["processes"]["current"] = {
                "pid": current_process.pid,
                "memory_info": current_process.memory_info()._asdict(),
                "cpu_percent": current_process.cpu_percent()
            }
            print(f"✓ Current Process: PID {current_process.pid}, "
                  f"Memory {current_process.memory_info().rss / 1024 / 1024:.1f}MB")
        except Exception as e:
            health_report["errors"].append(f"Process check failed: {str(e)}")
            print(f"✗ Process Check: Error - {e}")

        # Save health report
        with open(f"logs/health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(health_report, f, indent=2)

        self.health_status = health_report

        # Summary
        print(f"\nHealth Check Summary:")
        print(f"  Errors: {len(health_report['errors'])}")
        print(f"  Warnings: {len(health_report['warnings'])}")

        if health_report['errors']:
            print("\nERRORS:")
            for error in health_report['errors']:
                print(f"  ✗ {error}")

        if health_report['warnings']:
            print("\nWARNINGS:")
            for warning in health_report['warnings']:
                print(f"  ⚠ {warning}")

        return health_report

    def count_files_by_extension(self, extension):
        """Count files by extension across all directories"""
        count = 0
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(extension.lower()):
                    count += 1
        return count

    def trace_operation(self, operation_name, func, *args, **kwargs):
        """Trace and log operation execution"""
        start_time = datetime.now()
        operation_id = f"{operation_name}_{start_time.strftime('%H%M%S_%f')}"

        self.logger.info(f"TRACE START: {operation_id}")
        self.logger.debug(f"TRACE ARGS: {args}")
        self.logger.debug(f"TRACE KWARGS: {kwargs}")

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.logger.info(f"TRACE SUCCESS: {operation_id} completed in {duration:.3f}s")
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.logger.error(f"TRACE ERROR: {operation_id} failed after {duration:.3f}s")
            self.logger.error(f"ERROR DETAILS: {str(e)}")
            self.logger.error(f"TRACEBACK: {traceback.format_exc()}")

            raise

    def diagnose_outstanding_issues(self):
        """Diagnose and report outstanding issues"""
        print("\n" + "="*60)
        print("OUTSTANDING ISSUES DIAGNOSIS")
        print("="*60)

        issues = []

        # Check for common issues
        if not os.path.exists("input"):
            issues.append({
                "type": "CRITICAL",
                "category": "Directory",
                "description": "Input directory missing",
                "solution": "Create input directory and add source documents"
            })

        if not os.path.exists("output"):
            issues.append({
                "type": "WARNING",
                "category": "Directory",
                "description": "Output directory missing",
                "solution": "Directory will be created automatically"
            })

        # Check for file processing issues
        input_files = []
        if os.path.exists("input"):
            input_files = [f for f in os.listdir("input") if os.path.isfile(os.path.join("input", f))]

        if not input_files:
            issues.append({
                "type": "INFO",
                "category": "Files",
                "description": "No input files found",
                "solution": "Add documents to the input directory"
            })

        # Check for extension support
        unsupported_files = []
        supported_extensions = ['.docx', '.pdf', '.txt', '.rtf', '.odt']

        for file in input_files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_extensions:
                unsupported_files.append(file)

        if unsupported_files:
            issues.append({
                "type": "WARNING",
                "category": "Compatibility",
                "description": f"Unsupported file types found: {', '.join(unsupported_files)}",
                "solution": "Convert files to supported formats or add format handlers"
            })

        # Log and display issues
        if issues:
            print(f"Found {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. [{issue['type']}] {issue['category']}: {issue['description']}")
                print(f"   Solution: {issue['solution']}")
        else:
            print("No outstanding issues found.")

        # Save issues report
        issues_report = {
            "timestamp": datetime.now().isoformat(),
            "issues": issues,
            "system_status": self.health_status
        }

        with open(f"logs/issues_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(issues_report, f, indent=2)

        return issues

    def interactive_debug_menu(self):
        """Interactive debug menu with error handling"""
        print("\n🔧 RTM Debug Console Starting...")
        print("Press Ctrl+C at any time to exit safely")

        try:
            while True:
                self.show_menu()
                choice = self.get_user_choice()

                if choice == '8':
                    print("👋 Exiting debug console...")
                    break

                self.execute_choice(choice)

        except KeyboardInterrupt:
            print("\n\n⚠️  Debug console interrupted by user")
            print("Cleaning up and exiting safely...")
        except Exception as e:
            print(f"\n❌ Unexpected error in debug console: {e}")
            print("Saving error log and exiting...")
            self.logger.error(f"Debug console error: {traceback.format_exc()}")

    def show_menu(self):
        """Display the debug menu"""
        print("\n" + "="*60)
        print("🔧 RTM DEBUG CONSOLE")
        print("="*60)
        print("1. 🏥 System Health Check")
        print("2. 🔍 Diagnose Outstanding Issues")
        print("3. ⚙️  View Current Configuration")
        print("4. 🚀 Run Full Pipeline with Tracing")
        print("5. 📁 View Logs Directory")
        print("6. 🌟 Generate Ariana Extension Report")
        print("7. 📊 Export All Diagnostics to JSON")
        print("8. 🚪 Exit")
        print("-"*60)

    def get_user_choice(self):
        """Get user choice with validation"""
        while True:
            try:
                choice = input("Enter your choice (1-8): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter a number between 1-8.")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Input error: {e}. Please try again.")

    def execute_choice(self, choice):
        """Execute the selected menu choice"""
        try:
            if choice == '1':
                print("\n🏥 Running System Health Check...")
                self.system_health_check()
            elif choice == '2':
                print("\n🔍 Diagnosing Outstanding Issues...")
                self.diagnose_outstanding_issues()
            elif choice == '3':
                print("\n⚙️  Displaying Current Configuration...")
                self.display_configuration()
            elif choice == '4':
                print("\n🚀 Running Pipeline with Tracing...")
                self.run_traced_pipeline()
            elif choice == '5':
                print("\n📁 Showing Logs Directory...")
                self.show_logs_directory()
            elif choice == '6':
                print("\n🌟 Generating Ariana Extension Report...")
                self.generate_ariana_report()
            elif choice == '7':
                print("\n📊 Exporting All Diagnostics...")
                self.export_all_diagnostics()

        except Exception as e:
            print(f"\n❌ Error executing choice {choice}: {e}")
            self.logger.error(f"Menu choice {choice} failed: {traceback.format_exc()}")

        # Always pause after execution
        try:
            input("\n⏸️  Press Enter to continue (or Ctrl+C to exit)...")
        except KeyboardInterrupt:
            raise

    def display_configuration(self):
        """Display current configuration"""
        print("\nCurrent Configuration:")
        print(json.dumps(self.config, indent=2))

    def run_traced_pipeline(self):
        """Run pipeline with full tracing and error handling"""
        print("\n🚀 Running RTM Pipeline with full tracing...")
        try:
            # Check if pipeline module exists
            pipeline_file = "setup_and_run_pipeline.py"
            if not os.path.exists(pipeline_file):
                print(f"❌ Pipeline file not found: {pipeline_file}")
                print("Please ensure the pipeline file exists in the current directory.")
                return

            print("📂 Pipeline file found, starting execution...")

            # Import and run the main pipeline
            import setup_and_run_pipeline
            result = self.trace_operation("full_pipeline", setup_and_run_pipeline.main)

            print("✅ Pipeline execution completed successfully!")
            return result

        except ImportError as e:
            print(f"❌ Pipeline import failed: {e}")
            print("Please check that all required modules are available.")
            self.logger.error(f"Pipeline import failed: {str(e)}")
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
            print("Check the logs for detailed error information.")
            self.logger.error(f"Pipeline failed: {traceback.format_exc()}")

    def safe_run_pipeline(self):
        """Safe pipeline execution without tracing"""
        print("\n🔄 Running Pipeline in Safe Mode...")
        try:
            import setup_and_run_pipeline
            return setup_and_run_pipeline.main()
        except Exception as e:
            print(f"❌ Safe pipeline execution failed: {e}")
            return None

    def show_logs_directory(self):
        """Show contents of logs directory"""
        print("\nLogs Directory Contents:")
        if os.path.exists("logs"):
            for file in sorted(os.listdir("logs")):
                file_path = os.path.join("logs", file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {file} - {size} bytes - {mtime}")
        else:
            print("  Logs directory not found")

    def generate_ariana_report(self):
        """Generate Ariana extension compatibility report"""
        print("\nGenerating Ariana Extension Report...")

        ariana_report = {
            "timestamp": datetime.now().isoformat(),
            "ariana_support": self.config.get("include_ariana_extensions", False),
            "extensions_analysis": {},
            "compatibility_matrix": {}
        }

        # Analyze Ariana-specific extensions
        ariana_extensions = ['.aria', '.ari', '.arx', '.docx', '.rtf']

        for ext in ariana_extensions:
            count = self.count_files_by_extension(ext)
            ariana_report["extensions_analysis"][ext] = {
                "file_count": count,
                "supported": ext in ['.docx', '.rtf', '.txt'],
                "processing_method": "standard" if ext in ['.docx', '.rtf'] else "custom"
            }

        print("Ariana Extension Analysis:")
        for ext, info in ariana_report["extensions_analysis"].items():
            status = "✓" if info["supported"] else "✗"
            print(f"  {status} {ext}: {info['file_count']} files, {info['processing_method']} processing")

        # Save report
        with open(f"logs/ariana_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(ariana_report, f, indent=2)

        return ariana_report

    def export_all_diagnostics(self):
        """Export comprehensive diagnostics to JSON"""
        print("\nExporting comprehensive diagnostics...")

        comprehensive_report = {
            "timestamp": datetime.now().isoformat(),
            "health_check": self.system_health_check(),
            "outstanding_issues": self.diagnose_outstanding_issues(),
            "ariana_report": self.generate_ariana_report(),
            "configuration": self.config,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
                "environment_variables": dict(os.environ)
            }
        }

        export_file = f"logs/comprehensive_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)

        print(f"Comprehensive diagnostics exported to: {export_file}")
        return comprehensive_report

def main():
    """Main function with improved error handling"""
    print("🔧 Starting RTM Debug Console...")

    try:
        console = RTMDebugConsole()
        console.interactive_debug_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Debug console terminated by user")
    except Exception as e:
        print(f"\n❌ Fatal error in debug console: {e}")
        print("Please check the logs for more information.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
