#!/usr/bin/env python3
"""
Requirements Traceability Matrix (RTM) generator.
Creates comprehensive traceability matrices from parsed document data.
Supports large tables with up to 700 rows and 20 columns.
"""
import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from collections import defaultdict
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rtm_generator')

def load_rtm_data(rtm_file):
    """
    Load RTM data from JSON file.

    Args:
        rtm_file: Path to RTM data JSON file

    Returns:
        Dictionary containing RTM data
    """
    if not os.path.exists(rtm_file):
        logger.error(f"RTM data file not found: {rtm_file}")
        return None

    try:
        with open(rtm_file, 'r', encoding='utf-8') as f:
            rtm_data = json.load(f)
        logger.info(f"Loaded RTM data with {rtm_data.get('requirement_count', 0)} requirements")
        return rtm_data
    except Exception as e:
        logger.error(f"Error loading RTM data: {e}")
        return None


def generate_requirement_list(rtm_data, output_file):
    """
    Generate a simple requirements list.

    Args:
        rtm_data: Dictionary containing RTM data
        output_file: Path to save the requirements list

    Returns:
        Path to the generated file
    """
    try:
        # Extract requirements
        requirements = rtm_data.get('requirements', {})

        # Prepare data for CSV
        rows = []
        headers = ['ID', 'Type', 'Section', 'References', 'Content']

        for req_id, req_info in sorted(requirements.items()):
            # Format section path
            section_path = []
            for num, title in req_info.get('sections', []):
                section_path.append(f"{num} {title}")
            section_str = " > ".join(section_path) if section_path else ""

            # Format references
            references = ", ".join(req_info.get('references', []))

            # Format content (truncate if too long)
            content = req_info.get('content', '')
            if len(content) > 200:
                content = content[:197] + "..."

            rows.append([
                req_id,
                req_info.get('type', 'Unknown'),
                section_str,
                references,
                content
            ])

        # Save as CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info(f"Generated requirements list saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error generating requirements list: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_traceability_matrix(rtm_data, output_file, matrix_type="forward"):
    """
    Generate a requirements traceability matrix.

    Args:
        rtm_data: Dictionary containing RTM data
        output_file: Path to save the matrix
        matrix_type: Type of matrix to generate (forward, backward, bidirectional)

    Returns:
        Path to the generated file
    """
    try:
        # Extract requirements
        requirements = rtm_data.get('requirements', {})

        # Prepare data for matrix
        if matrix_type == "forward":
            # "From" requirements on rows, "To" requirements on columns
            title = "Forward Traceability Matrix"
            column_prefix = "To: "
        elif matrix_type == "backward":
            # "To" requirements on rows, "From" requirements on columns
            title = "Backward Traceability Matrix"
            column_prefix = "From: "
        else:  # bidirectional
            title = "Bidirectional Traceability Matrix"
            column_prefix = ""

        # Create a DataFrame for the matrix
        req_ids = sorted(requirements.keys())
        df = pd.DataFrame(index=req_ids, columns=[f"{column_prefix}{r}" for r in req_ids])

        # Fill the matrix
        for from_req in req_ids:
            for to_req in req_ids:
                if matrix_type == "forward":
                    # Check if to_req is referenced by from_req
                    if to_req in requirements[from_req].get('references', []):
                        df.loc[from_req, f"{column_prefix}{to_req}"] = "X"
                elif matrix_type == "backward":
                    # Check if from_req is referenced by to_req
                    if from_req in requirements[to_req].get('references', []):
                        df.loc[from_req, f"{column_prefix}{to_req}"] = "X"
                else:  # bidirectional
                    # Check both directions
                    if to_req in requirements[from_req].get('references', []):
                        df.loc[from_req, f"{column_prefix}{to_req}"] = "↓"  # Forward
                    elif from_req in requirements[to_req].get('references', []):
                        df.loc[from_req, f"{column_prefix}{to_req}"] = "↑"  # Backward

                    # Check both directions (bidirectional trace)
                    if (to_req in requirements[from_req].get('references', []) and
                        from_req in requirements[to_req].get('references', [])):
                        df.loc[from_req, f"{column_prefix}{to_req}"] = "↕"  # Both directions

        # Replace NaN with empty string
        df = df.fillna('')

        # Save as Excel with formatting
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=matrix_type.capitalize())

            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[matrix_type.capitalize()]

            # Add a header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # Apply header format to column headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num + 1, value, header_format)

            # Set the first column format
            first_col_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })

            # Apply first column format
            for row_num, value in enumerate(df.index.values):
                worksheet.write(row_num + 1, 0, value, first_col_format)

            # Auto-fit columns
            worksheet.autofit()

        logger.info(f"Generated {matrix_type} traceability matrix saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error generating traceability matrix: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_rtm_report(rtm_data, output_file):
    """
    Generate a comprehensive RTM report in Markdown format.

    Args:
        rtm_data: Dictionary containing RTM data
        output_file: Path to save the report

    Returns:
        Path to the generated file
    """
    try:
        # Extract requirements
        requirements = rtm_data.get('requirements', {})

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write title and summary
            f.write("# Requirements Traceability Matrix Report\n\n")

            # Write summary statistics
            f.write("## Summary\n\n")
            f.write(f"- Total Requirements: {rtm_data.get('requirement_count', 0)}\n")

            # Requirements by type
            f.write("- Requirements by Type:\n")
            for req_type, count in rtm_data.get('type_counts', {}).items():
                f.write(f"  - {req_type}: {count}\n")
            f.write("\n")

            # Source file
            source_file = rtm_data.get('source_file', '')
            if source_file:
                f.write(f"Source: {source_file}\n\n")

            # Requirements List
            f.write("## Requirements List\n\n")
            f.write("| ID | Type | Section | References |\n")
            f.write("|---|---|---|---|\n")

            for req_id, req_info in sorted(requirements.items()):
                # Format section path
                section_path = []
                for num, title in req_info.get('sections', []):
                    section_path.append(f"{num} {title}")
                section_str = " > ".join(section_path) if section_path else ""

                # Format references
                references = ", ".join(req_info.get('references', []))

                f.write(f"| {req_id} | {req_info.get('type', 'Unknown')} | {section_str} | {references} |\n")

            # Detailed Requirements
            f.write("\n## Detailed Requirements\n\n")

            for req_id, req_info in sorted(requirements.items()):
                f.write(f"### {req_id}\n\n")

                # Type
                f.write(f"- **Type**: {req_info.get('type', 'Unknown')}\n")

                # Section
                section_path = []
                for num, title in req_info.get('sections', []):
                    section_path.append(f"{num} {title}")
                section_str = " > ".join(section_path) if section_path else ""
                f.write(f"- **Section**: {section_str}\n")

                # Content
                content = req_info.get('content', '')
                f.write(f"- **Content**: {content}\n")

                # References
                references = req_info.get('references', [])
                if references:
                    f.write("- **References**:\n")
                    for ref in references:
                        f.write(f"  - {ref}\n")
                else:
                    f.write("- **References**: None\n")

                f.write("\n")

        logger.info(f"Generated RTM report saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error generating RTM report: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_all_rtm_files(rtm_data_file, output_dir=None):
    """
    Generate all RTM files from RTM data.

    Args:
        rtm_data_file: Path to RTM data JSON file
        output_dir: Directory to save output files (default: same as RTM data file)

    Returns:
        Dictionary with paths to generated files
    """
    # Load RTM data
    rtm_data = load_rtm_data(rtm_data_file)
    if not rtm_data:
        return {}

    # Setup output directory
    if output_dir is None:
        output_dir = Path(rtm_data_file).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    base_name = Path(rtm_data_file).stem.replace('_rtm_data', '')

    # Generate files
    output_files = {}

    # Requirements list
    req_list_file = output_dir / f"{base_name}_requirements_list.csv"
    output_files['requirements_list'] = generate_requirement_list(rtm_data, req_list_file)

    # Forward traceability matrix
    forward_matrix_file = output_dir / f"{base_name}_forward_matrix.xlsx"
    output_files['forward_matrix'] = generate_traceability_matrix(
        rtm_data, forward_matrix_file, "forward"
    )

    # Backward traceability matrix
    backward_matrix_file = output_dir / f"{base_name}_backward_matrix.xlsx"
    output_files['backward_matrix'] = generate_traceability_matrix(
        rtm_data, backward_matrix_file, "backward"
    )

    # Bidirectional traceability matrix
    bidir_matrix_file = output_dir / f"{base_name}_bidirectional_matrix.xlsx"
    output_files['bidirectional_matrix'] = generate_traceability_matrix(
        rtm_data, bidir_matrix_file, "bidirectional"
    )

    # RTM report
    report_file = output_dir / f"{base_name}_rtm_report.md"
    output_files['rtm_report'] = generate_rtm_report(rtm_data, report_file)

    return output_files


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Requirements Traceability Matrix (RTM) files"
    )
    parser.add_argument(
        "rtm_data_file",
        help="Path to RTM data JSON file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save output files"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    output_files = generate_all_rtm_files(args.rtm_data_file, args.output_dir)

    if output_files:
        logger.info("RTM generation completed successfully")
        return 0
    else:
        logger.error("RTM generation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
