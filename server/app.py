#!/usr/bin/env python3
"""
Simple web server for DOCX RTM Automation.

This script provides a web interface to the RTM automation functionality.
"""

import os
import sys
import argparse
import uuid
import threading
import time
from pathlib import Path
import logging
from flask import Flask, request, render_template, jsonify, send_from_directory

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the main processing pipeline
sys.path.insert(0, str(PROJECT_ROOT / "code"))
try:
    from main import execute_pipeline, load_config as main_load_config
except ImportError as e:
    logging.error("Could not import main RTM processing module: %s", e)
    execute_pipeline = None
    main_load_config = None

# Configure templates and static folders properly
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Create directories if they don't exist
os.makedirs(template_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rtm_server")

# Store job status information
jobs = {}

@app.route('/')
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except Exception as e: # pylint: disable=broad-except
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

    # Create input directory for this job
    job_input_dir = os.path.join(PROJECT_ROOT, "input", job_id)
    os.makedirs(job_input_dir, exist_ok=True)

    # Save uploaded files
    saved_files = []
    for file in files:
        if file and file.filename:
            filename = os.path.join(job_input_dir, file.filename)
            file.save(filename)
            saved_files.append(file.filename)

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

    # Set up output directory
    job_output_dir = os.path.join(PROJECT_ROOT, "output", job_id)
    os.makedirs(job_output_dir, exist_ok=True)

    # Get input directory
    job_input_dir = os.path.join(PROJECT_ROOT, "input", job_id)

    # Start processing in a separate thread
    def run_pipeline():
        try:
            # Create args object with necessary attributes
            class Args:
                """Helper class to simulate command line arguments for the pipeline."""
                def __init__(self):
                    self.input_dir = job_input_dir
                    self.output_dir = job_output_dir
                    self.config = None
                    self.steps = []
                    self.skip_steps = []
                    self.verbose = False
                    self.dry_run = False

                    # Set steps based on options
                    if options.get("convertToMd"):
                        self.steps.append("word_to_md")
                    if options.get("extractOutline"):
                        self.steps.append("extract_outline")
                    if options.get("extractRequirements"):
                        self.steps.append("extract_requirements")
                    if options.get("extractTestCases"):
                        self.steps.append("extract_test_cases")
                    if options.get("generateRtm"):
                        self.steps.append("generate_rtm")

            # Load configuration
            config = main_load_config() if main_load_config else {}

            # Execute pipeline
            args = Args()
            success = False
            if execute_pipeline:
                success = execute_pipeline(config, args)
            else:
                job["message"] = "Pipeline execution module not loaded."

            # Update job status
            job["status"] = "completed" if success else "failed"
            job["completed_at"] = time.time()
            job["success"] = success
            job["output_dir"] = job_output_dir

            # Get list of generated files
            if success:
                job["output_files"] = [f for f in os.listdir(job_output_dir)]
                job["message"] = f"Generated {len(job['output_files'])} files"
            else:
                job["message"] = "Processing failed"

        except Exception as e:
            logger.error("Error processing job %s: %s", job_id, e)
            job["status"] = "error"
            job["error"] = str(e)
            job["message"] = f"Error: {str(e)}"

    # Start processing thread
    thread = threading.Thread(target=run_pipeline)
    thread.daemon = True
    thread.start()

    return jsonify({
        "status": "success",
        "message": "Processing started",
        "job_id": job_id
    })

@app.route('/api/job/<job_id>')
def get_job_status(job_id):
    """Get job status."""
    if job_id not in jobs:
        return jsonify({"error": "Invalid job ID"}), 404

    job = jobs[job_id]

    # Include output files if job is completed
    if job["status"] == "completed" and "output_files" in job:
        # Create download URLs for each file
        files_with_urls = []
        for file in job["output_files"]:
            files_with_urls.append({
                "name": file,
                "url": f"/download/{job_id}/{file}"
            })
        job_info = dict(job)
        job_info["files"] = files_with_urls
        return jsonify(job_info)

    return jsonify(job)

@app.route('/download/<job_id>/<path:filename>')
def download_file(job_id, filename):
    """Download processed files."""
    output_dir = os.path.join(PROJECT_ROOT, "output", job_id)
    return send_from_directory(output_dir, filename, as_attachment=True)

@app.route('/status/<job_id>')
def job_status_page(job_id):
    """Show job status page."""
    if job_id not in jobs:
        return "Job not found", 404

    return render_template('status.html', job_id=job_id)

def main():
    """Run the web server."""
    parser = argparse.ArgumentParser(description="RTM Automation Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    args = parser.parse_args()

    logger.info("Starting server on %s:%s", args.host, args.port)
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
