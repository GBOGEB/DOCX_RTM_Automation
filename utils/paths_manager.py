import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import yaml

# --- Start of sys.path modification ---
_UTILS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT_PATHS_MANAGER = _UTILS_DIR.parent
if str(_PROJECT_ROOT_PATHS_MANAGER) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT_PATHS_MANAGER))
# --- End of sys.path modification ---


class PathsManager:
    """
    Manages project paths defined in config/paths.yaml.
    Provides easy access to various directories and file paths.
    """

    def __init__(self, config_file_name: str = "paths.yaml"):
        """
        Initializes PathsManager by loading paths from the specified config file.

        Args:
            config_file_name (str): The name of the YAML configuration file
                                    expected to be in the 'config' directory.
        """
        self.project_root = _PROJECT_ROOT_PATHS_MANAGER
        self.config_dir = self.project_root / "config"
        self.config_file_path = self.config_dir / config_file_name
        self.paths_config: Dict[str, Any] = {}
        self._load_config()

        self.input_dir = self._get_path("paths.input_dir", self.project_root / "input")
        self.output_dir = self._get_path("paths.output_dir", self.project_root / "output")
        self.logs_dir = self._get_path("paths.logs_dir", self.project_root / "logs")
        self.data_dir = self._get_path("paths.data_dir", self.project_root / "data")
        self.docs_dir = self._get_path("paths.docs_dir", self.project_root / "docs")

        self._ensure_core_dirs_exist()

    def _load_config(self):
        """Loads the paths configuration from the YAML file."""
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                self.paths_config = yaml.safe_load(f)
            if not isinstance(self.paths_config, dict):
                print(f"Warning: Paths configuration in '{self.config_file_path}' is not a dictionary. Using defaults.")
                self.paths_config = {}
        except FileNotFoundError:
            print(f"Warning: Paths configuration file '{self.config_file_path}' not found. Using default paths.")
            self.paths_config = {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML from '{self.config_file_path}': {e}. Using default paths.")
            self.paths_config = {}
        except Exception as e:
            print(f"An unexpected error occurred loading '{self.config_file_path}': {e}. Using default paths.")
            self.paths_config = {}

    def _get_path_from_config(self, key_path: str) -> Optional[Path]:
        """
        Retrieves a path from the loaded configuration using a dot-separated key.
        Example: "github.local_path"
        Returns an absolute Path object if found, otherwise None.
        """
        keys = key_path.split('.')
        current_level = self.paths_config
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                return None

        if isinstance(current_level, str):
            path_obj = Path(current_level)
            if not path_obj.is_absolute():
                return (self.project_root / path_obj).resolve()
            return path_obj.resolve()
        return None

    def _get_path(self, key_path: str, default_path: Path) -> Path:
        """
        Gets a path from config or returns a default. Ensures path is absolute.
        """
        config_path = self._get_path_from_config(key_path)
        if config_path:
            return config_path

        if not default_path.is_absolute():
            return (self.project_root / default_path).resolve()
        return default_path.resolve()

    def _ensure_core_dirs_exist(self):
        """Creates the core directories if they don't exist."""
        core_dirs = [
            self.input_dir,
            self.output_dir,
            self.logs_dir,
            self.config_dir,
            self.data_dir,
            self.docs_dir
        ]
        for directory in core_dirs:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory {directory}: {e}")

    def get_project_root(self) -> Path:
        return self.project_root

    def get_config_dir(self) -> Path:
        return self.config_dir

    def get_input_dir(self) -> Path:
        return self.input_dir

    def get_output_dir(self) -> Path:
        return self.output_dir

    def get_logs_dir(self) -> Path:
        return self.logs_dir

    def get_data_dir(self) -> Path:
        return self.data_dir

    def get_docs_dir(self) -> Path:
        return self.docs_dir

    def get_path_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a specific path string or general configuration value from the 'paths' section
        or the root of paths_config.
        """
        paths_section = self.paths_config.get("paths", {})
        if isinstance(paths_section, dict) and key in paths_section:
            return str(paths_section[key])

        if key in self.paths_config:
            return str(self.paths_config[key])

        return default

    def get_timestamped_output_path(self, prefix: str = "output", suffix: str = ".txt") -> Path:
        """Generates a timestamped path in the output directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}{suffix}"
        return self.output_dir / filename

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieves any value from the loaded configuration using a dot-separated key.
        Example: "github.user_name"
        """
        keys = key_path.split('.')
        current_level = self.paths_config
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                return default
        return current_level


# Example usage (for testing or direct script run)
if __name__ == "__main__":
    print(f"--- Running PathsManager Directly ({Path(__file__).name}) ---")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Detected Project Root (_PROJECT_ROOT_PATHS_MANAGER): {_PROJECT_ROOT_PATHS_MANAGER}")
    print(f"System Path (sys.path includes):")
    for p in sys.path:
        print(f"  - {p}")
    print("---")

    try:
        paths_manager = PathsManager() # Uses default "paths.yaml"
        print(f"\nPathsManager initialized successfully.")
        print(f"  Config file expected at: {paths_manager.config_file_path}")
        if paths_manager.paths_config:
            print(f"  Successfully loaded configuration from: {paths_manager.config_file_path}")
        else:
            print(f"  Could not load or parse configuration from: {paths_manager.config_file_path}. Using defaults or empty config.")

        print("\n--- Resolved Paths ---")
        print(f"Project Root: {paths_manager.get_project_root()}")
        print(f"Config Dir: {paths_manager.get_config_dir()}")
        print(f"Input Dir: {paths_manager.get_input_dir()}")
        print(f"Output Dir: {paths_manager.get_output_dir()}")
        print(f"Logs Dir: {paths_manager.get_logs_dir()}")
        print(f"Data Dir: {paths_manager.get_data_dir()}")
        print(f"Docs Dir: {paths_manager.get_docs_dir()}")

        print("\n--- Specific Config Value Retrieval ---")
        # Test a value expected to be at the root of paths.yaml
        pandoc_exe_from_config = paths_manager.get_config_value("pandoc_path", "pandoc_path_not_in_config")
        print(f"Value for 'pandoc_path' (from root): {pandoc_exe_from_config}")

        # Test a nested value
        github_repo_url = paths_manager.get_config_value("github.repo_url", "github.repo_url_not_in_config")
        print(f"Value for 'github.repo_url': {github_repo_url}")

        # Test a value from the 'paths' section specifically using get_path_config
        input_dir_from_paths_section = paths_manager.get_path_config("input_dir", "paths.input_dir_not_in_config")
        print(f"Value for 'input_dir' (from 'paths' section via get_path_config): {input_dir_from_paths_section}")

        openai_key_path_val = paths_manager.get_config_value("secrets.openai_key_path", "secrets.openai_key_path_not_in_config")
        print(f"Value for 'secrets.openai_key_path': {openai_key_path_val}")

        print("\n--- Timestamped Path Generation ---")
        ts_path = paths_manager.get_timestamped_output_path("direct_run_test", ".log")
        print(f"Example Timestamped Path: {ts_path}")
        # Ensure the directory for this path exists if we were to write to it
        ts_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"  (Parent directory {ts_path.parent} ensured)")

        print("\n--- PathsManager Direct Run Test Complete ---")

    except Exception as e:
        print(f"\n--- ERROR during PathsManager direct run ---")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        import traceback
        print("\n--- Traceback ---")
        traceback.print_exc()
        print("--- End of Error Report ---")
