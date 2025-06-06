#!/usr/bin/env python3
"""
Exact DOCX to Markdown converter that preserves all formatting details.
Creates an identical markdown representation of the Word document.
"""
import os
import sys
import re
from pathlib import Path
from collections import defaultdict


def convert_docx_to_markdown_exact(docx_file, output_file=None):
    """
    Convert a DOCX file to Markdown with precise preservation of all details.

    Args:
        docx_file: Path to the DOCX file
        output_file: Path where to save the output markdown

    Returns:
        Path to the created markdown file
    """
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    except ImportError:
        print("Installing python-docx...")
        import subprocess

        subprocess.run([sys.executable, "-m", "pip", "install", "python-docx"])
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

    print(f"Converting {docx_file} to exact Markdown representation...")
    doc = Document(docx_file)

    # Setup output file path
    if output_file is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / Path(docx_file).with_suffix(".exact.md").name

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    # Collect document metadata
    doc_metadata = {}
    if hasattr(doc, "core_properties"):
        props = doc.core_properties
        doc_metadata["title"] = props.title
        doc_metadata["author"] = props.author
        doc_metadata["created"] = props.created
        doc_metadata["modified"] = props.modified

    # Track section hierarchy
    section_info = {}
    current_section = None
    outline_levels = [0] * 10  # To track the outline numbers at different levels

    with open(output_file, "w", encoding="utf-8") as out_file:
        # Write metadata header as HTML comments
        out_file.write(f"<!-- Document: {os.path.basename(docx_file)} -->\n")
        for key, value in doc_metadata.items():
            if value:
                out_file.write(f"<!-- {key}: {value} -->\n")
        out_file.write("\n")

        # Process all paragraphs with exact preservation
        for para_idx, para in enumerate(doc.paragraphs):
            # Get paragraph style and attributes
            style_name = para.style.name
            text = para.text

            # Skip completely empty paragraphs, but preserve blank lines
            if not text:
                out_file.write("\n")
                continue

            # Handle heading styles with outline numbering
            if style_name.startswith("Heading"):
                try:
                    # Extract heading level
                    match = re.search(r"(\d+)$", style_name)
                    if match:
                        level = int(match.group(1))
                    else:
                        # Default level based on style
                        if "title" in style_name.lower():
                            level = 1
                        else:
                            level = 2

                    # Extract outline number from text if present
                    outline_number = ""
                    clean_text = text
                    outline_match = re.match(r"^(\d+(\.\d+)*)\s+(.*)", text)
                    if outline_match:
                        outline_number = outline_match.group(1)
                        clean_text = outline_match.group(3)

                        # Update outline levels
                        number_parts = [int(p) for p in outline_number.split(".")]
                        outline_levels[level - 1] = number_parts[-1]
                        # Reset lower levels
                        for i in range(level, len(outline_levels)):
                            outline_levels[i] = 0

                    # Store section info for later use
                    section_id = f"section-{para_idx}"
                    section_info[section_id] = {
                        "level": level,
                        "number": outline_number,
                        "title": clean_text,
                        "full_title": text,
                        "index": para_idx,
                    }
                    current_section = section_id

                    # Write heading with original text and an HTML comment for metadata
                    out_file.write(f"{'#' * level} {text}\n")
                    out_file.write(
                        f"<!-- section-level: {level}, section-id: {section_id} -->\n\n"
                    )

                except (ValueError, AttributeError) as e:
                    # Fallback for headings
                    print(f"Warning when processing heading: {e}")
                    out_file.write(f"## {text}\n\n")

            # Handle list styles with exact indentation
            elif style_name in ("List Bullet", "ListBullet"):
                # Try to determine list level
                indent_level = 0
                if hasattr(para, "_element") and hasattr(para._element, "pPr"):
                    if (
                        para._element.pPr is not None
                        and para._element.pPr.ind is not None
                    ):
                        if hasattr(para._element.pPr.ind, "left"):
                            try:
                                indent = para._element.pPr.ind.left
                                if hasattr(indent, "pt"):
                                    indent_level = (
                                        int(indent.pt) // 36
                                    )  # Approximate level calculation
                                else:
                                    indent_level = int(indent) // 720  # For raw values
                            except (AttributeError, TypeError, ValueError):
                                pass

                # Preserve original indentation spaces and bullet character
                spaces = "  " * indent_level
                out_file.write(f"{spaces}- {text}\n")

            elif style_name in ("List Number", "ListNumber"):
                # Try to determine list level and numbering
                indent_level = 0
                if hasattr(para, "_element") and hasattr(para._element, "pPr"):
                    # Similar to bullet list, extract indentation
                    if (
                        para._element.pPr is not None
                        and para._element.pPr.ind is not None
                    ):
                        if hasattr(para._element.pPr.ind, "left"):
                            try:
                                indent = para._element.pPr.ind.left
                                if hasattr(indent, "pt"):
                                    indent_level = int(indent.pt) // 36
                                else:
                                    indent_level = int(indent) // 720
                            except (AttributeError, TypeError, ValueError):
                                pass

                # Determine number from text or use default
                number_match = re.match(r"^(\d+\.|\w+\.)\s*(.*)", text)
                if number_match:
                    number_part = number_match.group(1)
                    text_part = number_match.group(2)
                    spaces = "  " * indent_level
                    out_file.write(f"{spaces}{number_part} {text_part}\n")
                else:
                    spaces = "  " * indent_level
                    out_file.write(f"{spaces}1. {text}\n")

            # Regular paragraph with all formatting preserved
            else:
                # Process runs to extract exact formatting
                formatted_parts = []
                contains_formatting = False

                for run in para.runs:
                    text = run.text
                    if not text:
                        continue

                    # Build formatting markers
                    format_start = ""
                    format_end = ""

                    if run.bold and run.italic:
                        format_start += "***"
                        format_end = "***" + format_end
                        contains_formatting = True
                    elif run.bold:
                        format_start += "**"
                        format_end = "**" + format_end
                        contains_formatting = True
                    elif run.italic:
                        format_start += "*"
                        format_end = "*" + format_end
                        contains_formatting = True

                    if run.underline:
                        format_start += "__"
                        format_end = "__" + format_end
                        contains_formatting = True

                    # Additional formatting as HTML comment if needed (color, size, etc.)
                    extra_format = []
                    if (
                        hasattr(run.font, "color")
                        and run.font.color
                        and run.font.color.rgb
                    ):
                        rgb = run.font.color.rgb
                        if rgb:
                            # Convert RGB to hex color
                            try:
                                color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                                extra_format.append(f"color:{color}")
                            except (IndexError, TypeError):
                                pass

                    if hasattr(run.font, "size") and run.font.size:
                        size = run.font.size
                        if size:
                            extra_format.append(f"size:{size.pt}pt")

                    if hasattr(run.font, "name") and run.font.name:
                        extra_format.append(f"font:{run.font.name}")

                    # Add extra formatting as HTML comment if present
                    if extra_format:
                        extra_format_str = ";".join(extra_format)
                        formatted_parts.append(
                            f"{format_start}{text}{format_end}<!-- {extra_format_str} -->"
                        )
                    else:
                        formatted_parts.append(f"{format_start}{text}{format_end}")

                # Combine all formatted parts
                para_text = "".join(formatted_parts)

                # Write paragraph with alignment info if available
                if hasattr(para, "alignment") and para.alignment:
                    alignment = para.alignment
                    align_str = ""
                    if alignment == WD_PARAGRAPH_ALIGNMENT.CENTER:
                        align_str = "center"
                    elif alignment == WD_PARAGRAPH_ALIGNMENT.RIGHT:
                        align_str = "right"
                    elif alignment == WD_PARAGRAPH_ALIGNMENT.JUSTIFY:
                        align_str = "justify"

                    if align_str:
                        out_file.write(f"<!-- align: {align_str} -->\n")

                # Write paragraph text with double newline for spacing
                out_file.write(f"{para_text}\n\n")

        # Process tables with exact formatting
        for table_idx, table in enumerate(doc.tables):
            # Table metadata as HTML comment
            rows = len(table.rows)
            cols = len(table.rows[0].cells) if rows > 0 else 0
            out_file.write(f"<!-- Table {table_idx+1}: {rows}x{cols} -->\n")

            # Process all table rows
            for row_idx, row in enumerate(table.rows):
                cells = []

                for cell in row.cells:
                    # Process cell content
                    cell_text = cell.text.strip()
                    # Replace empty cells with space
                    cells.append(cell_text if cell_text else " ")

                # Write table row
                out_file.write("| " + " | ".join(cells) + " |\n")

                # Add separator row after header
                if row_idx == 0:
                    separator = ["---"] * cols
                    out_file.write("| " + " | ".join(separator) + " |\n")

            # Add extra newline after table
            out_file.write("\n\n")

    print(f"Exact conversion completed! Output saved to {output_file}")
    return output_file


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        # Look for default document in input directory
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                docx_file = str(docx_files[0])
                print(f"Using found document: {docx_file}")
            else:
                print("Usage: python exact_docx_to_md.py <docx_file> [output_md_file]")
                return 1
        else:
            print("Usage: python exact_docx_to_md.py <docx_file> [output_md_file]")
            return 1
    else:
        docx_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(docx_file):
        print(f"Error: File not found - {docx_file}")
        return 1

    try:
        result = convert_docx_to_markdown_exact(docx_file, output_file)
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
