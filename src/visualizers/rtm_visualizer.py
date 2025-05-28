#!/usr/bin/env python3
"""
Visualize Requirements Traceability Matrix data.
"""
import os
import sys
import json
import argparse
import logging
import webbrowser
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class RTMVisualizer:
    """
    Visualize Requirements Traceability Matrix data.
    """

    def __init__(self):
        """Initialize RTM visualizer."""
        self.html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Requirements Traceability Matrix</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1 {{ color: #2c3e50; }}
                .stats {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                .stats-container {{ display: flex; justify-content: space-between; max-width: 600px; }}
                .stat-box {{ padding: 10px; background-color: #e3e3e3; border-radius: 5px; width: 30%; text-align: center; }}
                .stat-box h3 {{ margin-top: 0; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .link-table td {{ padding: 8px; }}
                .req {{ color: #0066cc; }}
                .test {{ color: #cc6600; }}
                .validates {{ color: #009933; }}
                .verifies {{ color: #9900cc; }}
                .references {{ color: #666666; }}
                .matrix {{ overflow-x: auto; }}
                .matrix table {{ border-collapse: collapse; }}
                .matrix th, .matrix td {{
                    border: 1px solid #ddd;
                    padding: 4px;
                    text-align: center;
                    min-width: 30px;
                }}
                .matrix th {{ background-color: #4CAF50; color: white; }}
                .matrix td.covered {{ background-color: #4CAF50; color: white; }}
                .matrix td.not-covered {{ background-color: #f2f2f2; }}
                .matrix td.header {{ background-color: #e3e3e3; font-weight: bold; }}
                .filter-container {{ margin-bottom: 20px; }}
                .search-box {{ padding: 8px; width: 300px; margin-right: 10px; }}
            </style>
        </head>
        <body>
            <h1>Requirements Traceability Matrix</h1>

            <div class="stats">
                <h2>Statistics</h2>
                <div class="stats-container">
                    <div class="stat-box">
                        <h3>Requirements</h3>
                        <p>{req_count}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Test Cases</h3>
                        <p>{test_count}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Links</h3>
                        <p>{link_count}</p>
                    </div>
                </div>
            </div>

            <div class="filter-container">
                <input type="text" id="searchBox" class="search-box" placeholder="Filter by ID or description...">
                <button onclick="resetFilter()">Reset</button>
            </div>

            <h2>Requirements</h2>
            <table id="reqTable">
                <tr>
                    <th>ID</th>
                    <th>Description</th>
                    <th>Test Coverage</th>
                </tr>
                {req_rows}
            </table>

            <h2>Test Cases</h2>
            <table id="testTable">
                <tr>
                    <th>ID</th>
                    <th>Description</th>
                    <th>Verifies Requirements</th>
                </tr>
                {test_rows}
            </table>

            <h2>Traceability Links</h2>
            <table id="linkTable" class="link-table">
                <tr>
                    <th>Source</th>
                    <th>Relationship</th>
                    <th>Target</th>
                </tr>
                {link_rows}
            </table>

            <h2>Coverage Matrix</h2>
            <div class="matrix">
                <table id="matrixTable">
                    {matrix_rows}
                </table>
            </div>

            <script>
                function filterTables() {{
                    const searchText = document.getElementById('searchBox').value.toLowerCase();
                    filterTable('reqTable', searchText);
                    filterTable('testTable', searchText);
                    filterTable('linkTable', searchText);
                }}

                function filterTable(tableId, searchText) {{
                    const table = document.getElementById(tableId);
                    const rows = table.getElementsByTagName('tr');

                    for (let i = 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const cells = row.getElementsByTagName('td');
                        let found = false;

                        for (let j = 0; j < cells.length; j++) {{
                            if (cells[j].textContent.toLowerCase().includes(searchText)) {{
                                found = true;
                                break;
                            }}
                        }}

                        row.style.display = found ? '' : 'none';
                    }}
                }}

                function resetFilter() {{
                    document.getElementById('searchBox').value = '';
                    filterTables();
                }}

                // Add event listener to search box
                document.getElementById('searchBox').addEventListener('keyup', filterTables);
            </script>
        </body>
        </html>
        """

    def visualize(self, rtm_file, output_file=None, open_browser=True):
        """
        Visualize RTM data from a JSON file.

        Args:
            rtm_file: Path to input RTM JSON file
            output_file: Path to output HTML file
            open_browser: Whether to open the visualization in a browser

        Returns:
            Path to the generated HTML file
        """
        # Load RTM data
        rtm_path = Path(rtm_file)
        if not rtm_path.exists():
            logger.error(f"Input file not found: {rtm_file}")
            return None

        try:
            with open(rtm_path, 'r', encoding='utf-8') as f:
                rtm_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load RTM data: {e}")
            return None

        # Determine output file
        if output_file is None:
            output_file = rtm_path.with_suffix('.html')

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html_content = self._generate_html(rtm_data)

        # Write HTML file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"RTM visualization saved to {output_file}")

            if open_browser:
                webbrowser.open(f"file://{output_path.absolute()}")

            return output_file
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            return None

    def _generate_html(self, rtm_data):
        """
        Generate HTML content for RTM visualization.

        Args:
            rtm_data: Dictionary with RTM data

        Returns:
            HTML content as a string
        """
        requirements = rtm_data.get('requirements', {})
        test_cases = rtm_data.get('test_cases', {})
        links = rtm_data.get('links', [])
        stats = rtm_data.get('stats', {})

        # Generate requirement rows
        req_rows = ""
        for req_id, req_data in requirements.items():
            # Find test cases that verify this requirement
            test_coverage = []
            for link in links:
                if link['target'] == req_id and link['source'] in test_cases:
                    test_coverage.append(link['source'])
                elif link['source'] == req_id and link['target'] in test_cases:
                    test_coverage.append(link['target'])

            coverage_text = ", ".join([f'<span class="test">{tc}</span>' for tc in test_coverage])
            if not coverage_text:
                coverage_text = "<span style='color:red'>No coverage</span>"

            req_rows += f"""
            <tr>
                <td class="req">{req_id}</td>
                <td>{req_data.get('description', '')}</td>
                <td>{coverage_text}</td>
            </tr>
            """

        # Generate test case rows
        test_rows = ""
        for tc_id, tc_data in test_cases.items():
            # Find requirements verified by this test case
            verified_reqs = []
            for link in links:
                if link['source'] == tc_id and link['target'] in requirements:
                    verified_reqs.append(link['target'])
                elif link['target'] == tc_id and link['source'] in requirements:
                    verified_reqs.append(link['source'])

            verified_text = ", ".join([f'<span class="req">{req}</span>' for req in verified_reqs])
            if not verified_text:
                verified_text = "<span style='color:orange'>No requirements</span>"

            test_rows += f"""
            <tr>
                <td class="test">{tc_id}</td>
                <td>{tc_data.get('description', '')}</td>
                <td>{verified_text}</td>
            </tr>
            """

        # Generate link rows
        link_rows = ""
        for link in links:
            source_class = "req" if link['source'] in requirements else "test"
            target_class = "req" if link['target'] in requirements else "test"

            link_rows += f"""
            <tr>
                <td class="{source_class}">{link['source']}</td>
                <td class="{link['type']}">{link['type']}</td>
                <td class="{target_class}">{link['target']}</td>
            </tr>
            """

        # Generate matrix rows
        matrix_rows = "<tr><td></td>"
        req_ids = sorted(requirements.keys())
        test_ids = sorted(test_cases.keys())

        # Add requirement headers
        for req_id in req_ids:
            matrix_rows += f'<th>{req_id}</th>'
        matrix_rows += "</tr>"

        # Add test rows
        for tc_id in test_ids:
            matrix_rows += f'<tr><td class="header">{tc_id}</td>'

            for req_id in req_ids:
                # Check if there is a link between this test and requirement
                covered = False
                for link in links:
                    if ((link['source'] == tc_id and link['target'] == req_id) or
                        (link['source'] == req_id and link['target'] == tc_id)):
                        covered = True
                        break

                if covered:
                    matrix_rows += '<td class="covered">✓</td>'
                else:
                    matrix_rows += '<td class="not-covered"></td>'

            matrix_rows += "</tr>"

        # Fill in the template
        html_content = self.html_template.format(
            req_count=stats.get('requirements_count', len(requirements)),
            test_count=stats.get('test_cases_count', len(test_cases)),
            link_count=stats.get('links_count', len(links)),
            req_rows=req_rows,
            test_rows=test_rows,
            link_rows=link_rows,
            matrix_rows=matrix_rows
        )

        return html_content


def visualize_all_rtm_files(input_dir, output_dir=None):
    """
    Visualize all RTM JSON files in a directory.

    Args:
        input_dir: Directory containing RTM JSON files
        output_dir: Directory for output HTML files

    Returns:
        List of paths to output HTML files
    """
    # Create output directory if needed
    if not output_dir:
        output_dir = os.path.join(PROJECT_ROOT, "output", "rtm_viz")

    os.makedirs(output_dir, exist_ok=True)

    # Find all RTM JSON files
    rtm_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('_rtm.json') or file.endswith('.rtm.json'):
                rtm_files.append(os.path.join(root, file))

    if not rtm_files:
        logger.warning(f"No RTM JSON files found in {input_dir}")
        return []

    logger.info(f"Found {len(rtm_files)} RTM files to visualize")

    visualizer = RTMVisualizer()
    output_files = []

    for rtm_file in rtm_files:
        rel_path = os.path.relpath(rtm_file, input_dir)
        output_file = os.path.join(
            output_dir,
            os.path.splitext(rel_path)[0] + ".html"
        )
        result = visualizer.visualize(rtm_file, output_file, open_browser=False)
        if result:
            output_files.append(result)

    # Open the first visualization if any were generated
    if output_files and os.path.exists(output_files[0]):
        webbrowser.open(f"file://{os.path.abspath(output_files[0])}")

    return output_files


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Visualize RTM data")
    parser.add_argument("--input", help="Input RTM JSON file")
    parser.add_argument("-o", "--output", help="Output HTML file")
    parser.add_argument("--input-dir", help="Directory containing input files")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument("--no-browser", action="store_true", help="Don't open in browser")

    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()

    # Process a single file
    if args.input:
        visualizer = RTMVisualizer()
        output = visualizer.visualize(
            args.input,
            args.output,
            not args.no_browser
        )

        if output:
            logger.info(f"Visualization created: {output}")
            return 0
        else:
            logger.error("Visualization failed.")
            return 1

    # Process directory if specified
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = os.path.join(PROJECT_ROOT, "output", "rtm")

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(PROJECT_ROOT, "output", "rtm_viz")

    results = visualize_all_rtm_files(input_dir, output_dir)

    if results:
        logger.info(f"Successfully visualized {len(results)} files:")
        for result in results:
            logger.info(f"  - {result}")
        return 0
    else:
        logger.warning("No files were processed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
