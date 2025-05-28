import sys  # Added: sys is used in the sys.path modification block
import pandas as pd  # Added: pandas is used later in the script
from pathlib import Path
import json  # Added: For JSON operations if needed, good practice
import os  # Added: For OS path operations if needed

# --- Start of sys.path modification ---
# Assuming this script is in DOCX_RTM_Automation_v1.0/pipelines/
# Project root is one level up from 'pipelines'
_PROJECT_ROOT_PIPELINE = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT_PIPELINE) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT_PIPELINE))  # Added this line
# --- End of sys.path modification ---

from config.openai_integration import initialize_openai
from agents.requirement_analyzer import (
    analyze_requirement_function as analyze_requirement,
    check_traceability_function as check_traceability,
)
from markdown_it import MarkdownIt
from markdown_it.token import Token


def extract_requirements_from_markdown_table(document_path):
    """
    Parses a Markdown document and extracts requirements from the first table
    found under a '## Requirements' heading.
    Handles different row structures for requirements.
    """
    requirements_data = []
    with open(document_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    md = MarkdownIt()
    tokens = md.parse(md_content)

    in_requirements_section = False
    table_tokens_start_index = -1

    # Find the '## Requirements' section and the start of the table
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            next_token_idx = i + 1
            if (
                next_token_idx < len(tokens)
                and tokens[next_token_idx].type == "text"
                and tokens[next_token_idx].content.strip() == "Requirements"
            ):
                in_requirements_section = True
            else:
                in_requirements_section = False  # Reset if not the "Requirements" heading

        if in_requirements_section:
            # Look for the table immediately following the "Requirements" heading
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == "table_open":
                    table_tokens_start_index = j
                    break
            if table_tokens_start_index != -1:
                break  # Found the table, exit the outer loop

    if table_tokens_start_index == -1:
        print("Warning: '## Requirements' section or table not found.")
        return []

    header_row_content = []
    data_rows_content = []
    current_row_cells = []
    current_cell_texts = []

    is_processing_header = True
    in_cell_token = False  # Tracks if we are inside a th_open/td_open and th_close/td_close

    for token_idx in range(table_tokens_start_index, len(tokens)):
        token = tokens[token_idx]

        if token.type == "tr_open":
            current_row_cells = []  # Start a new row
        elif token.type == "th_open" or token.type == "td_open":
            in_cell_token = True  # Start a new cell
            current_cell_texts = []
        elif token.type == "text" and in_cell_token:
            current_cell_texts.append(token.content)  # Accumulate text within a cell
        elif token.type == "th_close" or token.type == "td_close":
            if in_cell_token:
                full_cell_text = "".join(current_cell_texts).strip()
                current_row_cells.append(full_cell_text)
                in_cell_token = False  # End of cell
                current_cell_texts = []
        elif token.type == "tr_close":
            if is_processing_header:
                header_row_content = list(current_row_cells)  # Capture header
                is_processing_header = False
            elif current_row_cells:  # Avoid adding empty rows if any
                data_rows_content.append(list(current_row_cells))  # Capture data row
        elif token.type == "table_close":
            break  # End of table processing

    # Process extracted rows based on cell count and content
    for row_cells in data_rows_content:
        if not row_cells or not row_cells[0].startswith("REQ-"):
            continue  # Skip rows that don't start with REQ- or are empty

        req_id = row_cells[0]
        req_text = ""
        req_section = ""
        req_priority = ""
        req_status = ""

        num_cells = len(row_cells)

        # Heuristic for special rows (like REQ-MAS-018 to REQ-MAS-023)
        # These have ID in cell 0, empty cell 1, "Term" in cell 2, Definition in cell 3, empty cell 4, Section in cell 5, etc.
        if num_cells >= 8 and not row_cells[1] and (num_cells > 4 and not row_cells[4]):
            term = row_cells[2] if num_cells > 2 else ""
            definition = row_cells[3] if num_cells > 3 else ""
            if term and definition:
                req_text = f"{term}: {definition}"
            elif definition:  # Fallback if term is missing
                req_text = definition
            elif term:  # Fallback if definition is missing
                req_text = term
            else:
                req_text = "N/A (special row format, missing content)"

            req_section = row_cells[5] if num_cells > 5 else "N/A"
            req_priority = row_cells[6] if num_cells > 6 else "N/A"
            req_status = row_cells[7] if num_cells > 7 else "N/A"
        elif num_cells >= 5:  # Standard rows
            req_text = row_cells[1] if num_cells > 1 else "N/A"
            req_section = row_cells[2] if num_cells > 2 else "N/A"
            req_priority = row_cells[3] if num_cells > 3 else "N/A"
            req_status = row_cells[4] if num_cells > 4 else "N/A"
        elif num_cells > 0:  # Fallback for rows with fewer cells but a REQ ID
            req_text = row_cells[1] if num_cells > 1 else "N/A (incomplete row)"
            req_section = row_cells[2] if num_cells > 2 else "N/A"
            req_priority = row_cells[3] if num_cells > 3 else "N/A"
            req_status = row_cells[4] if num_cells > 4 else "N/A"
        else:
            continue  # Should not happen if first check passed

        requirements_data.append(
            {
                "id": req_id,
                "text": req_text,
                "section": req_section,
                "priority": req_priority,
                "status": req_status,
            }
        )

    return requirements_data


def process_requirements_document(document_path):
    """Process a requirements document (Markdown table) and generate analysis"""

    extracted_requirements = extract_requirements_from_markdown_table(document_path)

    results = []
    if not extracted_requirements:
        print("No requirements extracted. Skipping analysis.")
        return pd.DataFrame(), None  # Return empty DataFrame and None for traceability

    for req_data in extracted_requirements:
        analysis = analyze_requirement(req_data["text"])
        results.append(
            {
                "requirement_id": req_data["id"],
                "requirement_text": req_data["text"],
                "section": req_data["section"],
                "priority": req_data["priority"],
                "status": req_data["status"],
                "analysis": analysis,
            }
        )

    # Pass the actual texts for semantic traceability analysis
    requirement_texts = [r["text"] for r in extracted_requirements]
    traceability_matrix = check_traceability(requirement_texts)

    return pd.DataFrame(results), traceability_matrix


# Usage example
if __name__ == "__main__":
    # Define paths relative to the project root
    # _PROJECT_ROOT_PIPELINE is defined at the top of the script
    input_md_filename = "sample_requirements_for_pipeline.md"
    # Assume a 'data' directory at the project root for input files
    example_input_doc_path = _PROJECT_ROOT_PIPELINE / "data" / input_md_filename

    output_excel_path = (
        _PROJECT_ROOT_PIPELINE
        / "output"
        / "pipeline_analysis"
        / "requirements_analysis.xlsx"
    )
    output_traceability_txt_path = (
        _PROJECT_ROOT_PIPELINE
        / "output"
        / "pipeline_analysis"
        / "traceability_matrix_output.txt"
    )

    # Ensure output directories exist
    output_excel_path.parent.mkdir(parents=True, exist_ok=True)
    output_traceability_txt_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if the example input file exists, create a dummy if not
    if not example_input_doc_path.exists():
        print(f"Warning: Example input file not found at {example_input_doc_path}")
        print("Creating a dummy sample_requirements_for_pipeline.md for demonstration.")
        example_input_doc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(example_input_doc_path, "w", encoding="utf-8") as f_ex:
            f_ex.write("# Sample Document\n\n")
            f_ex.write("## Requirements\n\n")
            f_ex.write(
                "| ID        | Requirement Text                      | Section   | Priority | Status   |\n"
            )
            f_ex.write(
                "|-----------|---------------------------------------|-----------|----------|----------|\n"
            )
            f_ex.write(
                "| REQ-SYS-001 | The system shall allow user login.    | Auth      | High     | Defined  |\n"
            )
            f_ex.write(
                "| REQ-SYS-002 | The system shall display dashboard.   | UI        | Medium   | Defined  |\n"
            )
            # Example of a "special row"
            f_ex.write(
                "| REQ-MAS-018 |           | Glossary Term | The definition of the term. |          | General  | High     | Defined  |\n"
            )
        print(f"Dummy file created at {example_input_doc_path}")

    print(f"Processing document: {example_input_doc_path}")
    results_df, traceability_matrix_output = process_requirements_document(
        str(example_input_doc_path)
    )

    if not results_df.empty:
        results_df.to_excel(output_excel_path, index=False)
        print(f"Requirements analysis saved to: {output_excel_path}")
    else:
        print("No results to save to Excel.")

    if traceability_matrix_output is not None:
        # Assuming traceability_matrix_output is a string or can be converted to string
        # If it's a complex object (e.g., DataFrame), format it appropriately
        trace_output_str = str(traceability_matrix_output)
        if isinstance(traceability_matrix_output, pd.DataFrame):
            trace_output_str = traceability_matrix_output.to_string()

        with open(output_traceability_txt_path, "w", encoding="utf-8") as f_trace:
            f_trace.write("Traceability Matrix Output:\n")
            f_trace.write(trace_output_str)
        print(f"Traceability matrix output saved to: {output_traceability_txt_path}")
    else:
        print("No traceability matrix generated.")
