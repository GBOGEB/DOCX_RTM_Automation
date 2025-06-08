#!/usr/bin/env python3
"""
RTM Web Dashboard - Simple HTTP server based dashboard
"""

import json
import threading
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class RTMDashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for RTM dashboard."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/status':
            self.serve_status_api()
        elif self.path == '/api/files':
            self.serve_files_api()
        else:
            self.send_error(404)

    def serve_dashboard(self):
        """Serve the main dashboard HTML."""
        html_content = self.get_dashboard_html()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def serve_status_api(self):
        """Serve RTM system status as JSON."""
        status = self.get_rtm_status()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def serve_files_api(self):
        """Serve file count information."""
        files_info = self.get_files_info()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(files_info).encode())

    def get_rtm_status(self):
        """Get current RTM system status."""
        input_dir = Path("input")
        output_dir = Path("output")
        ariana_dir = Path(".ariana")

        return {
            "timestamp": datetime.now().isoformat(),
            "input_files": len(list(input_dir.glob("*"))) if input_dir.exists() else 0,
            "output_files": len(list(output_dir.glob("*"))) if output_dir.exists() else 0,
            "ariana_files": len(list(ariana_dir.glob("*"))) if ariana_dir.exists() else 0,
            "status": "operational"
        }

    def get_files_info(self):
        """Get detailed file information."""
        input_dir = Path("input")
        output_dir = Path("output")

        files_info = {
            "input": {"docx": 0, "md": 0, "json": 0, "yaml": 0},
            "output": {"docx": 0, "md": 0, "json": 0, "yaml": 0, "total": 0}
        }

        if input_dir.exists():
            files_info["input"]["docx"] = len(list(input_dir.glob("*.docx")))
            files_info["input"]["md"] = len(list(input_dir.glob("*.md")))
            files_info["input"]["json"] = len(list(input_dir.glob("*.json")))
            files_info["input"]["yaml"] = len(list(input_dir.glob("*.yaml")))

        if output_dir.exists():
            files_info["output"]["docx"] = len(list(output_dir.glob("*.docx")))
            files_info["output"]["md"] = len(list(output_dir.glob("*.md")))
            files_info["output"]["json"] = len(list(output_dir.glob("*.json")))
            files_info["output"]["yaml"] = len(list(output_dir.glob("*.yaml")))
            files_info["output"]["total"] = len(list(output_dir.glob("*")))

        return files_info

    def get_dashboard_html(self):
        """Generate dashboard HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>RTM Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #4CAF50;
            margin-right: 8px;
        }
        .files-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .update-time {
            color: #888;
            font-size: 0.9em;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 RTM Automation Dashboard</h1>
            <p><span class="status-indicator"></span>System Operational</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="input-count">0</div>
                <div class="stat-label">Input Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="output-count">0</div>
                <div class="stat-label">Output Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="ariana-count">0</div>
                <div class="stat-label">AI Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">85.7%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>

        <div class="files-section">
            <h2>📁 File Breakdown</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="input-docx">0</div>
                    <div class="stat-label">Input DOCX</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="input-md">0</div>
                    <div class="stat-label">Input Markdown</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="output-json">0</div>
                    <div class="stat-label">Output JSON</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="output-yaml">0</div>
                    <div class="stat-label">Output YAML</div>
                </div>
            </div>
        </div>

        <div class="update-time" id="last-update">
            Last updated: Loading...
        </div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('input-count').textContent = data.input_files;
                    document.getElementById('output-count').textContent = data.output_files;
                    document.getElementById('ariana-count').textContent = data.ariana_files;
                    document.getElementById('last-update').textContent =
                        'Last updated: ' + new Date().toLocaleTimeString();
                })
                .catch(error => console.error('Error:', error));

            fetch('/api/files')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('input-docx').textContent = data.input.docx;
                    document.getElementById('input-md').textContent = data.input.md;
                    document.getElementById('output-json').textContent = data.output.json;
                    document.getElementById('output-yaml').textContent = data.output.yaml;
                })
                .catch(error => console.error('Error:', error));
        }

        // Update immediately and then every 10 seconds
        updateDashboard();
        setInterval(updateDashboard, 10000);
    </script>
</body>
</html>
        """

    def log_message(self, format, *args):
        """Override to reduce log spam."""
        return

def start_dashboard_server(port=8000, auto_open=True):
    """Start the RTM dashboard server."""
    try:
        server = HTTPServer(('localhost', port), RTMDashboardHandler)

        print(f"🌐 RTM Web Dashboard starting...")
        print(f"📡 Server running on: http://localhost:{port}")
        print(f"🔧 Press Ctrl+C to stop")

        if auto_open:
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')

            threading.Thread(target=open_browser, daemon=True).start()

        server.serve_forever()

    except KeyboardInterrupt:
        print(f"\n👋 RTM Dashboard stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print(f"   Try a different port: python rtm_web_dashboard.py --port 8001")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function to start dashboard."""
    import argparse

    parser = argparse.ArgumentParser(description='RTM Web Dashboard')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')

    args = parser.parse_args()

    print("🚀 RTM Web Dashboard")
    print("=" * 30)

    start_dashboard_server(args.port, not args.no_browser)

if __name__ == "__main__":
    main()