#!/usr/bin/env python3
"""
Simple web server for DOCX RTM Automation.

This script provides a web interface to the RTM automation functionality.
"""

import os
import sys
from pathlib import Path

# --- Start of standard boilerplate for scripts in packages ---
_self_path = Path(__file__).resolve()
# project_root/server/app.py -> project_root is parents[1]
_project_root = _self_path.parents[1]

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

if __name__ == "__main__" and not __package__:
    _package_path = _self_path.parent.relative_to(_project_root)
    __package__ = str(_package_path).replace(os.sep, '.')
# --- End of standard boilerplate ---

import argparse
import uuid
import threading
import time
import logging
from flask import Flask, request, render_template, jsonify, send_from_directory
import jinja2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rtm_server")

# Import the main processing pipeline
_code_dir = _project_root / "code"
if str(_code_dir) not in sys.path:
    sys.path.insert(0, str(_code_dir))

# Define variables outside the try block to ensure they're available
execute_pipeline = None
main_load_config = None

try:
    # Use a conditional import to handle the case where main might not exist
    import importlib.util
    main_spec = importlib.util.find_spec("main", [str(_code_dir)])
    if main_spec is not None:
        # Import the module
        main_module = importlib.util.module_from_spec(main_spec)
        main_spec.loader.exec_module(main_module)
        # Extract the required functions
        if hasattr(main_module, 'execute_pipeline'):
            execute_pipeline = main_module.execute_pipeline
        if hasattr(main_module, 'load_config'):
            main_load_config = main_module.load_config

        logger.info("Successfully imported main RTM processing module")
    else:
        logger.warning("Could not find main RTM processing module")
except ImportError as e:
    logger.error("Could not import main RTM processing module: %s", e)

# Configure templates and static folders properly
template_dir = _project_root / "server" / "templates"
static_dir = _project_root / "server" / "static"

# Create directories if they don't exist
template_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

app = Flask(__name__,
           template_folder=str(template_dir),  # Flask expects string paths
           static_folder=str(static_dir))     # Flask expects string paths

# Store job status information
jobs = {}

@app.route('/')
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except jinja2.exceptions.TemplateNotFound:  # More specific exception
        logger.error("Index template not found.")
        return "Error: Main page template not found.", 404
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error rendering index template: %s", e)
        return f"Error loading template: {str(e)}", 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'files[]' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files[]')

    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Create a temporary job ID
    job_id = str(uuid.uuid4())

    # Create input directory for this job using Path
    job_input_dir = _project_root / "input" / job_id
    job_input_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    saved_files = []
    for file_item in files:  # Renamed 'file' to 'file_item' to avoid conflict
        if file_item and file_item.filename:
            # Use Path object for filename construction
            filename_path = job_input_dir / file_item.filename
            try:
                file_item.save(str(filename_path))  # .save() expects a string path
                saved_files.append(file_item.filename)
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error saving uploaded file %s: %s", file_item.filename, e)
                # Optionally, decide if one file failing should stop the whole upload
                # For now, we continue and report only successfully saved files

    # Store job information
    jobs[job_id] = {
        "id": job_id,
        "status": "uploaded",
        "files": saved_files,
        "created_at": time.time(),
        "message": f"Uploaded {len(saved_files)} files"
    }

    return jsonify({
        "status": "success",
        "message": f"Uploaded {len(saved_files)} files",
        "job_id": job_id,
        "files": saved_files
    })

@app.route('/api/process', methods=['POST'])
def process_files():
    """Process uploaded files using the RTM pipeline."""
    data = request.get_json()

    if not data or "job_id" not in data:
        return jsonify({"error": "No job ID provided"}), 400

    job_id = data["job_id"]
    options = data.get("options", {})

    if job_id not in jobs:
        return jsonify({"error": "Invalid job ID"}), 400

    job = jobs[job_id]
    job["status"] = "processing"
    job["options"] = options
    job["started_at"] = time.time()

    # Set up output directory using Path
    job_output_dir = _project_root / "output" / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    # Get input directory using Path
    job_input_dir = _project_root / "input" / job_id
                    self.input_dir = str(job_input_dir)
                    self.output_dir = str(job_output_dir)
                    self.config_file = options.get("config_file")
                    self.verbose = options.get("verbose", False)
                    self.format = options.get("format", "json")
                    # Add other attributes based on options or use defaults

            # Create args instance
            args = Args()
"'"'"'