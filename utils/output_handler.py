import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Union, Optional
from enum import Enum, auto

class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    SUCCESS = auto() # Custom level for success messages

class OutputHandler:
    """Handler for managing output files and logging"""

    def __init__(self,
                 output_dir: str,
                 log_level: LogLevel = LogLevel.INFO,
                 log_to_console: bool = True,
                 log_to_file: bool = False,
                 log_file_path: Optional[str] = None,
                 logger_name: str = "dmaic_workflow"):
        """Initialize the output handler"""
        self.output_dir = output_dir
        self.log_level = log_level
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path or os.path.join(output_dir, f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logging.getLogger(logger_name)
        self.interaction_history = []
        self._configure_logger()

    def _configure_logger(self):
        """Configure the logger"""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.SUCCESS: logging.INFO, # Map SUCCESS to INFO for standard logging
        }
        self.logger.setLevel(level_map.get(self.log_level, logging.INFO))

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if self.log_to_console:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        if self.log_to_file:
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            fh = logging.FileHandler(self.log_file_path)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        self.logger.propagate = False

    def _log(self, level: LogLevel, message: str, exc_info=False):
        """Log a message with the specified level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix_map = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARNING: "[WARNING]",
            LogLevel.ERROR: "[ERROR]",
            LogLevel.CRITICAL: "[CRITICAL]",
            LogLevel.SUCCESS: "[SUCCESS]",
        }

        log_prefix = prefix_map.get(level, "[INFO]")

        color_start = ""
        color_end = "\033[0m" # ANSI reset color
        if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
            color_start = "\033[91m" # Red
        elif level == LogLevel.WARNING:
            color_start = "\033[93m" # Yellow
        elif level == LogLevel.SUCCESS:
            color_start = "\033[92m" # Green

        formatted_message = f"{timestamp} {log_prefix} {message}"

        if self.log_to_console:
            print(f"{color_start}{formatted_message}{color_end}")

        if level == LogLevel.DEBUG:
            self.logger.debug(message, exc_info=exc_info)
        elif level == LogLevel.INFO:
            self.logger.info(message, exc_info=exc_info)
        elif level == LogLevel.WARNING:
            self.logger.warning(message, exc_info=exc_info)
        elif level == LogLevel.ERROR:
            self.logger.error(message, exc_info=exc_info)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message, exc_info=exc_info)
        elif level == LogLevel.SUCCESS:
            self.logger.info(f"[SUCCESS] {message}", exc_info=exc_info)

    def log_debug(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.DEBUG.value:
            self._log(LogLevel.DEBUG, message, exc_info=exc_info)

    def log_info(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.INFO.value:
            self._log(LogLevel.INFO, message, exc_info=exc_info)

    def log_warning(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.WARNING.value:
            self._log(LogLevel.WARNING, message, exc_info=exc_info)

    def log_error(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.ERROR.value:
            self._log(LogLevel.ERROR, message, exc_info=exc_info)

    def log_critical(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.CRITICAL.value:
            self._log(LogLevel.CRITICAL, message, exc_info=exc_info)

    def log_success(self, message: str, exc_info=False):
        if self.log_level.value <= LogLevel.INFO.value:
            self._log(LogLevel.SUCCESS, message, exc_info=exc_info)

    def log_interaction(self, question: str, response: str):
        """Log an interaction with the DMAIC system"""
        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response
        })
        self.log_info(f"Q: {question[:50]}... | R: {response[:50]}...")

    def save_results(self, results: Dict[str, Any], filename: str) -> str:
        """Save results to a JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        full_output = {
            "results": results,
            "interaction_history": self.interaction_history,
            "timestamp": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            if filename.endswith('.json'):
                json.dump(full_output, f, indent=2, ensure_ascii=False)
            elif filename.endswith(('.md', '.markdown')):
                f.write(results.get('report_content', str(results)))
            elif filename.endswith('.yml') or filename.endswith('.yaml'):
                import yaml
                yaml.dump(full_output, f, default_flow_style=False)
            else:
                json.dump(full_output, f, indent=2, ensure_ascii=False)

        self.log_success(f"Results saved to {output_path}")
        return output_path
