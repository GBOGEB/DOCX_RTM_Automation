#!/usr/bin/env python3
"""
Logging System - Replace print statements with file-based logging
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import json

class RTMLogger:
    """Enhanced logging system for RTM automation"""

    def __init__(self, name="rtm_automation", log_dir="logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create multiple log files
        self.workflow_log = self.log_dir / "workflow.log"
        self.pipeline_log = self.log_dir / "pipeline.log"
        self.github_log = self.log_dir / "github_operations.log"
        self.status_log = self.log_dir / "status_reports.txt"

        self.setup_loggers()

    def setup_loggers(self):
        """Setup different loggers for different purposes"""

        # Main workflow logger
        self.workflow_logger = logging.getLogger(f"{self.name}.workflow")
        self.workflow_logger.setLevel(logging.INFO)

        # Clear any existing handlers
        self.workflow_logger.handlers.clear()

        workflow_handler = logging.FileHandler(self.workflow_log, encoding='utf-8')
        workflow_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        workflow_handler.setFormatter(workflow_formatter)
        self.workflow_logger.addHandler(workflow_handler)

        # Pipeline logger
        self.pipeline_logger = logging.getLogger(f"{self.name}.pipeline")
        self.pipeline_logger.setLevel(logging.INFO)
        self.pipeline_logger.handlers.clear()

        pipeline_handler = logging.FileHandler(self.pipeline_log, encoding='utf-8')
        pipeline_handler.setFormatter(workflow_formatter)
        self.pipeline_logger.addHandler(pipeline_handler)

        # GitHub operations logger
        self.github_logger = logging.getLogger(f"{self.name}.github")
        self.github_logger.setLevel(logging.INFO)
        self.github_logger.handlers.clear()

        github_handler = logging.FileHandler(self.github_log, encoding='utf-8')
        github_handler.setFormatter(workflow_formatter)
        self.github_logger.addHandler(github_handler)

    def log_workflow_step(self, step_name, status, details=None):
        """Log workflow step to file instead of print"""
        timestamp = datetime.now().isoformat()

        # Log to workflow logger
        self.workflow_logger.info(f"STEP: {step_name} - {status}")
        if details:
            self.workflow_logger.info(f"DETAILS: {details}")

        # Also write to status file
        try:
            with open(self.status_log, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {step_name}: {status}\n")
                if details:
                    f.write(f"  Details: {details}\n")
        except Exception as e:
            # If file logging fails, continue
            print(f"Warning: Could not write to status log: {e}")

    def log_pipeline_result(self, operation, result_data):
        """Log pipeline results to structured format"""
        timestamp = datetime.now().isoformat()

        # Log to pipeline logger
        self.pipeline_logger.info(f"OPERATION: {operation}")
        self.pipeline_logger.info(f"RESULT: {json.dumps(result_data, indent=2)}")

        # Write structured result to file
        try:
            result_file = self.log_dir / f"pipeline_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'operation': operation,
                    'result': result_data
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write pipeline result: {e}")

    def log_github_operation(self, operation, status, details=None):
        """Log GitHub operations"""
        self.github_logger.info(f"GITHUB: {operation} - {status}")
        if details:
            self.github_logger.info(f"DETAILS: {details}")

    def create_status_report(self, report_data):
        """Create comprehensive status report file"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_file = self.log_dir / f"status_report_{timestamp}.txt"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RTM AUTOMATION STATUS REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")

                for section, data in report_data.items():
                    f.write(f"{section.upper()}\n")
                    f.write("-" * len(section) + "\n")

                    if isinstance(data, dict):
                        for key, value in data.items():
                            f.write(f"{key}: {value}\n")
                    elif isinstance(data, list):
                        for item in data:
                            f.write(f"• {item}\n")
                    else:
                        f.write(f"{data}\n")
                    f.write("\n")

            return report_file
        except Exception as e:
            print(f"Warning: Could not create status report: {e}")
            return None

# Global logger instance
rtm_logger = RTMLogger()

def log_step(step_name, status, details=None):
    """Convenience function to replace print statements"""
    try:
        rtm_logger.log_workflow_step(step_name, status, details)
        # Also print to console for immediate feedback
        print(f"📋 {step_name}: {status}")
        if details:
            print(f"   Details: {details}")
    except Exception as e:
        # Fallback to simple print if logging fails
        print(f"📋 {step_name}: {status}")
        if details:
            print(f"   Details: {details}")

def log_pipeline(operation, result_data):
    """Convenience function for pipeline logging"""
    try:
        rtm_logger.log_pipeline_result(operation, result_data)
        print(f"🔧 Pipeline: {operation} completed")
    except Exception as e:
        print(f"🔧 Pipeline: {operation} completed (logging error: {e})")

def log_github(operation, status, details=None):
    """Convenience function for GitHub operations"""
    try:
        rtm_logger.log_github_operation(operation, status, details)
        print(f"🌐 GitHub: {operation} - {status}")
    except Exception as e:
        print(f"🌐 GitHub: {operation} - {status} (logging error: {e})")

def create_report(report_data):
    """Convenience function to create status report"""
    try:
        return rtm_logger.create_status_report(report_data)
    except Exception as e:
        print(f"Warning: Could not create report: {e}")
        return None
