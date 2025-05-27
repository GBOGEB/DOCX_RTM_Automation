import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

class PathsManager:
    """Utility for managing file paths across the application"""

    def __init__(self):
        """Initialize path manager with default paths"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ensure_project_on_path()

        # Define standard directories
        self.config_dir = os.path.join(self.project_root, 'config')
        self.output_dir = os.path.join(self.project_root, 'outputs')
        self.data_dir = os.path.join(self.project_root, 'data')
        self.templates_dir = os.path.join(self.project_root, 'templates')

        # Ensure directories exist
        for directory in [self.output_dir, self.data_dir]:
            os.makedirs(directory, exist_ok=True)

    def ensure_project_on_path(self):
        """Ensure the project root is in sys.path"""
        if self.project_root not in sys.path:
            sys.path.append(self.project_root)

    def get_output_dir(self, create_timestamped: bool = False) -> str:
        """Get the output directory path, optionally with timestamp"""
        if not create_timestamped:
            return self.output_dir

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(timestamped_dir, exist_ok=True)
        return timestamped_dir

    def get_template_path(self, template_name: str) -> str:
        """Get the path to a specific template file"""
        return os.path.join(self.templates_dir, template_name)

    def get_data_path(self, filename: str = None) -> str:
        """Get the path to the data directory or a specific data file"""
        if filename:
            return os.path.join(self.data_dir, filename)
        return self.data_dir

    def get_config_path(self, config_name: str) -> str:
        """Get the path to a specific configuration file"""
        return os.path.join(self.config_dir, config_name)
