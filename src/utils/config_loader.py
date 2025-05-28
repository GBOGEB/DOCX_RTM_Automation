#!/usr/bin/env python3
"""
Configuration loader utility for RTM Automation.

This module provides functionality to load, validate, and access
configuration settings from YAML files with environment-specific overrides.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

class ConfigLoader:
    """
    Configuration loader that handles YAML configuration files with environment-specific overrides.
    """

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        environment: Optional[str] = None,
        default_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Directory containing configuration files (defaults to PROJECT_ROOT/config)
            environment: Environment name for overrides (e.g., 'dev', 'prod')
            default_config: Default configuration to use if no files are found
        """
        # Set config directory
        self.config_dir = Path(config_dir) if config_dir else PROJECT_ROOT / "config"

        # Set environment (default to ENV environment variable or 'dev')
        self.environment = environment or os.environ.get("ENV", "dev")

        # Default configuration
        self.default_config = default_config or {
            "paths": {
                "input_dir": "input",
                "output_dir": "output",
                "temp_dir": "temp"
            },
            "settings": {
                "verbose": False,
                "debug": False,
                "overwrite_existing": False
            },
            "processing": {
                "max_threads": 4,
                "chunk_size": 1000
            }
        }

        # Loaded configuration
        self.config = {}

        # Load configuration files
        self._load_config()

    def _load_config(self) -> None:
        """
        Load configuration from files and environment variables.
        """
        # Start with default configuration
        self.config = self.default_config.copy()

        # Check if config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            return

        # Load base configuration
        base_config_path = self.config_dir / "config.yaml"
        if base_config_path.exists():
            try:
                with open(base_config_path, 'r') as f:
                    base_config = yaml.safe_load(f) or {}
                self._update_config(base_config)
                logger.info(f"Loaded base configuration from {base_config_path}")
            except Exception as e:
                logger.error(f"Failed to load base configuration: {e}")
        else:
            logger.warning(f"Base configuration file not found: {base_config_path}")

        # Load environment-specific configuration
        env_config_path = self.config_dir / f"config.{self.environment}.yaml"
        if env_config_path.exists():
            try:
                with open(env_config_path, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                self._update_config(env_config)
                logger.info(f"Loaded environment configuration from {env_config_path}")
            except Exception as e:
                logger.error(f"Failed to load environment configuration: {e}")
        else:
            logger.debug(f"Environment configuration file not found: {env_config_path}")

        # Load local overrides (not version controlled)
        local_config_path = self.config_dir / "config.local.yaml"
        if local_config_path.exists():
            try:
                with open(local_config_path, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                self._update_config(local_config)
                logger.info(f"Loaded local configuration from {local_config_path}")
            except Exception as e:
                logger.error(f"Failed to load local configuration: {e}")

        # Apply environment variable overrides
        self._apply_env_overrides()

        # Validate configuration
        self._validate_config()

    def _update_config(self, config_updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values, using deep merge.

        Args:
            config_updates: New configuration values to apply
        """
        self.config = self._deep_merge(self.config, config_updates)

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a deep merge of dictionaries.

        Args:
            base: Base dictionary
            updates: Dictionary with updates

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in updates.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursively update nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Update or add the value
                result[key] = value

        return result

    def _apply_env_overrides(self) -> None:
        """
        Apply overrides from environment variables.

        Environment variables starting with RTM_ will be applied as configuration overrides.
        Examples:
          - RTM_PATHS_INPUT_DIR=/custom/input/path -> config['paths']['input_dir'] = '/custom/input/path'
          - RTM_SETTINGS_DEBUG=true -> config['settings']['debug'] = True
        """
        for env_var, value in os.environ.items():
            if env_var.startswith("RTM_"):
                # Remove prefix and split by underscore
                config_path = env_var[4:].lower().split('_')

                # Try to convert to appropriate type
                if value.lower() == 'true':
                    typed_value = True
                elif value.lower() == 'false':
                    typed_value = False
                elif value.isdigit():
                    typed_value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                    typed_value = float(value)
                else:
                    typed_value = value

                # Apply the override
                self._set_nested_value(self.config, config_path, typed_value)
                logger.debug(f"Applied environment override: {env_var}={typed_value}")

    def _set_nested_value(self, config: Dict[str, Any], path: List[str], value: Any) -> None:
        """
        Set a value in a nested dictionary based on a path.

        Args:
            config: Configuration dictionary to modify
            path: Path to the value, as a list of keys
            value: Value to set
        """
        if len(path) == 1:
            config[path[0]] = value
        elif len(path) > 1:
            key = path[0]
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            self._set_nested_value(config[key], path[1:], value)

    def _validate_config(self) -> None:
        """
        Validate the configuration.

        Raises:
            ConfigurationError: If validation fails
        """
        # Check required paths
        required_paths = ['input_dir', 'output_dir', 'temp_dir']
        for path_name in required_paths:
            if path_name not in self.get("paths", {}):
                raise ConfigurationError(f"Missing required path: {path_name}")

        # Validate that max_threads is positive
        max_threads = self.get("processing", {}).get("max_threads", 0)
        if max_threads <= 0:
            logger.warning("Invalid max_threads value, setting to 1")
            if "processing" in self.config:
                self.config["processing"]["max_threads"] = 1

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.

        Args:
            *keys: Sequence of keys to navigate the nested configuration
            default: Default value if not found

        Returns:
            Configuration value or default if not found
        """
        if not keys:
            return self.config

        current = self.config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current

    def set(self, *keys_and_value: Any) -> None:
        """
        Set a configuration value by key path.

        Args:
            *keys_and_value: Sequence of keys followed by the value

        Raises:
            ValueError: If keys_and_value has fewer than two elements
        """
        if len(keys_and_value) < 2:
            raise ValueError("At least one key and a value are required")

        keys = keys_and_value[:-1]
        value = keys_and_value[-1]

        self._set_nested_value(self.config, keys, value)

    def create_default_config_files(self) -> None:
        """
        Create default configuration files if they don't exist.
        """
        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)

        # Create base configuration
        base_config_path = self.config_dir / "config.yaml"
        if not base_config_path.exists():
            with open(base_config_path, 'w') as f:
                yaml.dump(self.default_config, f, default_flow_style=False)
            logger.info(f"Created default base configuration: {base_config_path}")

        # Create environment configuration
        env_config_path = self.config_dir / f"config.{self.environment}.yaml"
        if not env_config_path.exists():
            env_config = {
                "environment": self.environment,
                "settings": {
                    "verbose": self.environment == "dev",
                    "debug": self.environment == "dev"
                }
            }
            with open(env_config_path, 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False)
            logger.info(f"Created default environment configuration: {env_config_path}")

        # Create .gitignore to exclude local config
        gitignore_path = self.config_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write("config.local.yaml\n")
            logger.info(f"Created .gitignore to exclude local config: {gitignore_path}")

    def get_paths(self, make_absolute: bool = True) -> Dict[str, Path]:
        """
        Get configured paths as Path objects.

        Args:
            make_absolute: Convert relative paths to absolute

        Returns:
            Dictionary of Path objects
        """
        paths = {}
        path_config = self.get("paths", {})

        for key, value in path_config.items():
            path = Path(value)
            if make_absolute and not path.is_absolute():
                path = PROJECT_ROOT / path
            paths[key] = path

            # Create directories if they don't exist
            if key.endswith("_dir") and not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {path}")

        return paths

    def __str__(self) -> str:
        """String representation of the configuration."""
        return yaml.dump(self.config, default_flow_style=False)


# Global configuration instance
_config_instance = None

def get_config(
    config_dir: Optional[Union[str, Path]] = None,
    environment: Optional[str] = None,
    reload: bool = False
) -> ConfigLoader:
    """
    Get a singleton configuration instance.

    Args:
        config_dir: Directory containing configuration files
        environment: Environment name for overrides
        reload: Force configuration reload

    Returns:
        ConfigLoader instance
    """
    global _config_instance

    if _config_instance is None or reload:
        _config_instance = ConfigLoader(config_dir, environment)

    return _config_instance


def main():
    """Main function for testing the configuration loader."""
    import argparse

    parser = argparse.ArgumentParser(description="Configuration loader utility")
    parser.add_argument("--env", help="Environment (dev, test, prod)")
    parser.add_argument("--create-default", action="store_true", help="Create default configuration files")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--get", help="Get a specific configuration value (dot notation)")

    args = parser.parse_args()

    # Set up logging for CLI
    logging.getLogger().setLevel(logging.INFO)

    try:
        # Initialize config loader
        config = get_config(environment=args.env, reload=True)

        # Create default configuration files if requested
        if args.create_default:
            config.create_default_config_files()
            print(f"Default configuration files created in {config.config_dir}")

        # Show current configuration if requested
        if args.show:
            print("Current configuration:")
            print(config)

        # Get a specific value if requested
        if args.get:
            keys = args.get.split('.')
            value = config.get(*keys)
            print(f"{args.get}: {value}")

        # If no action specified, show help
        if not (args.create_default or args.show or args.get):
            parser.print_help()

    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
