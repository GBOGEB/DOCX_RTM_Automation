"""
DMAIC Framework for DOCX RTM Automation
Define, Measure, Analyze, Improve, Control
"""

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json
import yaml
import sys

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class DMAICFramework:
    """Implementation of DMAIC methodology for document automation pipeline"""

    def __init__(self, config_path_str: str = "config/paths.yaml", output_base_dir_str: str = "output/dmaic_records"):
        """Initialize DMAIC framework with configuration"""
        self.logger = logging.getLogger(__name__)
        # Ensure logging is configured if this class is used standalone early
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.config_file_path = PROJECT_ROOT / config_path_str
        self.config = self._load_config()

        self.output_base_dir = PROJECT_ROOT / output_base_dir_str
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = {}
        self.start_time = datetime.now()

    def _load_config(self):
        """Load configuration file"""
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load DMAIC configuration from {self.config_file_path}: {e}")
            return {}

    def define(self, component_name, description):
        """Define phase: document component purpose"""
        self.logger.info(f"DEFINE: {component_name}")
        definition = {
            "name": component_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_to_file("define", component_name, definition)
        return definition

    def measure(self, input_file):
        """Measure phase: collect metrics about input files"""
        self.logger.info(f"MEASURE: {input_file}")
        input_path = Path(input_file)
        if not input_path.exists():
            self.logger.error(f"Input file not found: {input_file}")
            return None

        metrics = {
            "file_path": str(input_path.resolve()),
            "file_size": input_path.stat().st_size,
            "modification_time": datetime.fromtimestamp(
                input_path.stat().st_mtime
            ).isoformat(),
        }
        self._save_to_file("measure", input_path.stem, metrics)
        return metrics

    def analyze(self, input_file, output_file):
        """Analyze phase: compare input and output files"""
        self.logger.info(f"ANALYZE: Comparing {input_file} and {output_file}")
        input_path = Path(input_file)
        output_path = Path(output_file)

        # Resolve paths if they are not absolute, assuming they might be relative to project root
        if not input_path.is_absolute():
            input_path = PROJECT_ROOT / input_path
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path

        if not input_path.exists() or not output_path.exists():
            self.logger.error(f"Input ({input_path}) or output ({output_path}) file not found for analysis.")
            return None

        diff_command = ["diff", str(input_path), str(output_path)]
        # On Windows, 'diff' might not be available. Consider alternative or skip.
        if sys.platform == "win32":
            # 'fc' is a Windows alternative, but output format is different.
            # For simplicity, we'll note that 'diff' might fail.
            self.logger.warning("Running 'diff' command on Windows. It might not be available or behave as expected.")
            # diff_command = ["fc", str(input_path), str(output_path)] # Example alternative

        try:
            diff_result = subprocess.run(
                diff_command,
                capture_output=True,
                text=True,
                check=False # Don't raise error if diff finds differences (non-zero exit code)
            )
            diff_output = diff_result.stdout
            if diff_result.returncode != 0 and diff_result.returncode != 1: # 0 no diff, 1 diffs found
                 self.logger.warning(f"'diff' command exited with {diff_result.returncode}. Stderr: {diff_result.stderr}")

        except FileNotFoundError:
            self.logger.error(f"'diff' command not found. Please ensure it's installed and in PATH.")
            diff_output = "Diff command not found or failed."
        except Exception as e:
            self.logger.error(f"Error running diff command: {e}")
            diff_output = f"Error running diff: {e}"


        analysis = {
            "input_file": str(input_path),
            "output_file": str(output_path),
            "diff": diff_output,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_to_file(
            "analyze", f"{input_path.stem}_vs_{output_path.stem}", analysis
        )
        return analysis

    def improve(self, component_name, improvement_description):
        """Improve phase: document improvements"""
        self.logger.info(f"IMPROVE: {component_name}")
        improvement = {
            "component": component_name,
            "description": improvement_description,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_to_file("improve", component_name, improvement)
        return improvement

    def control(self, component_name):
        """Control phase: ensure changes are tracked and tested"""
        self.logger.info(f"CONTROL: {component_name}")
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Control phase for {component_name}"],
                check=True,
            )
            self.logger.info("Changes committed to Git.")
        except Exception as e:
            self.logger.error(f"Git commit failed: {e}")

    def _save_to_file(self, phase, name, data):
        """Save phase data to a file"""
        # Output directory is now relative to project root, set in __init__
        # self.output_base_dir.mkdir(exist_ok=True) # Already created in __init__

        file_path = self.output_base_dir / f"{phase}_{name}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.logger.debug(f"{phase.capitalize()} data saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save {phase} data to {file_path}: {e}")

if __name__ == '__main__':
    # Example Usage for DMAICFramework
    print("Testing DMAICFramework...")
    # Configure logging for the test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    dmaic = DMAICFramework()

    # DEFINE
    dmaic.define("DocConversion", "Component for converting DOCX to Markdown.")

    # MEASURE (Create dummy files for testing)
    dummy_input_path = PROJECT_ROOT / "input" / "dummy_measure_input.txt"
    dummy_input_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dummy_input_path, "w", encoding="utf-8") as f:
        f.write("This is a dummy input file for DMAIC measure phase.")
    dmaic.measure(str(dummy_input_path))

    # ANALYZE (Create dummy output file for testing)
    dummy_output_path = PROJECT_ROOT / "output" / "dummy_analyze_output.txt"
    dummy_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dummy_output_path, "w", encoding="utf-8") as f:
        f.write("This is a dummy output file for DMAIC analyze phase.\nIt has some differences.")
    dmaic.analyze(str(dummy_input_path), str(dummy_output_path))

    # IMPROVE
    dmaic.improve("DocConversion", "Switched to Pandoc for better table handling.")

    # CONTROL
    print("Skipping CONTROL phase (Git commit) in this standalone test.")
    # dmaic.control("DocConversion") # This would attempt a git commit

    print(f"DMAIC records should be in: {dmaic.output_base_dir}")
    # Clean up dummy files
    # dummy_input_path.unlink(missing_ok=True)
    # dummy_output_path.unlink(missing_ok=True)
    print("DMAICFramework test finished.")
