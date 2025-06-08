#!/usr/bin/env python3
"""
Enhanced Word to Markdown converter with metadata preservation.
Extracts and preserves document structure, formatting, and generates outline files.
"""

import os
import sys
import yaml
from pathlib import Path


def check_docx_module():
    """Check if python-docx is installed."""
    try:
        from docx import Document

        return True
    except ImportError:
        print("python-docx module not found. Install it with: pip install python-docx")
        try:
            import subprocess

            subprocess.run(["pip", "install", "python-docx"], check=True)

            print("Successfully installed python-docx.")
            return True
        except Exception as e:
            print(f"Error installing python-docx: {e}")
            return False


def convert_docx_to_markdown_with_metadata(
    docx_file, output_file=None, extract_outline=True
):
    """
    Convert a DOCX file to Markdown while preserving metadata and generating outline files.

    Args:
        docx_file: Path to the DOCX file
        output_file: Path to save the markdown output
        extract_outline: Whether to extract and save document outline

    Returns:
        Tuple of (markdown_path, outline_json_path, outline_yaml_path)
    """
    if not check_docx_module():
        return None, None, None

    from docx import Document

    print(f"Converting {docx_file} to Markdown with metadata...")
    doc = Document(docx_file)

    # Setup output paths
    if output_file is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        base_name = Path(docx_file).stem
        output_file = output_dir / f"{base_name}.md"
    else:
        output_file = Path(output_file)
        output_dir = output_file.parent
        base_name = output_file.stem

    # Initialize document structure for outline
    outline_data = {
        "document_name": base_name,
        "source_file": str(docx_file),
        "sections": [],
        "metadata": {
            "total_paragraphs": len(doc.paragraphs),
            "total_sections": len(doc.sections),
            "total_tables": len(doc.tables),
        },
    }

    # Extract document properties/metadata if available
    if hasattr(doc, "core_properties"):
        props = doc.core_properties
        outline_data["metadata"]["title"] = props.title or base_name
        outline_data["metadata"]["author"] = props.author or "Unknown"
        outline_data["metadata"]["created"] = (
            str(props.created) if props.created else "Unknown"
        )
        outline_data["metadata"]["modified"] = (
            str(props.modified) if props.modified else "Unknown"
        )

    # Track section hierarchy
    current_section = {"title": base_name, "level": 0, "content": [], "subsections": []}
    section_stack = [current_section]
    outline_data["sections"].append(current_section)

    # Convert content with enhanced metadata
    with open(output_file, "w", encoding="utf-8") as out_file:
        # Write document title
        out_file.write(f"# {base_name}\n\n")
        out_file.write(f"*Converted from {Path(docx_file).name}*\n\n")

        # Process paragraphs
        for para_idx, para in enumerate(doc.paragraphs):
            # Skip empty paragraphs
            if not para.text.strip():
                out_file.write("\n")
                continue

            # Extract paragraph style information
            style_name = para.style.name

            # Handle heading styles
            if style_name.startswith("Heading"):
                try:
                    level = int(style_name[-1])
                    heading_text = para.text.strip()

                    # Write to markdown
                    out_file.write("#" * level + " " + heading_text + "\n\n")

                    # Update section hierarchy for outline
                    while (
                        len(section_stack) > 1 and section_stack[-1]["level"] >= level
                    ):
                        section_stack.pop()

                    new_section = {
                        "title": heading_text,
                        "level": level,
                        "content": [],
                        "subsections": [],
                        "paragraph_index": para_idx,
                    }

                    section_stack[-1]["subsections"].append(new_section)
                    section_stack.append(new_section)

                except ValueError:
                    # If we can't extract a level, default to h2
                    out_file.write("## " + para.text + "\n\n")

            # Handle list styles
            elif style_name in ("List Bullet", "ListBullet"):
                # Extract bullet style/type if possible
                bullet_info = "- "  # Default bullet

                # For nested bullets, we need to determine the level
                indent_level = 0
                if hasattr(para, "_element") and hasattr(para._element, "pPr"):
                    if (
                        para._element.pPr is not None
                        and para._element.pPr.ind is not None
                    ):
                        if hasattr(para._element.pPr.ind, "left"):
                            # Try to determine indentation level from left indentation
                            left_indent = para._element.pPr.ind.left
                            if left_indent is not None:
                                try:
                                    # Convert to integer if possible
                                    indent_val = int(
                                        left_indent.pt
                                        if hasattr(left_indent, "pt")
                                        else left_indent
                                    )
                                    indent_level = (
                                        indent_val // 720
                                    )  # Rough estimate, 720 twips = 1 standard indentation level
                                except (AttributeError, TypeError, ValueError):
                                    pass

                # Write indented bullet
                out_file.write("  " * indent_level + bullet_info + para.text + "\n")

                # Add to section content
                section_stack[-1]["content"].append(
                    {
                        "type": "bullet_list",
                        "text": para.text,
                        "level": indent_level,
                        "paragraph_index": para_idx,
                    }
                )

            elif style_name in ("List Number", "ListNumber"):
                # For simplicity in markdown, we'll use 1. for all numbered list items
                # Extract indentation level similar to bullet lists
                indent_level = 0
                if hasattr(para, "_element") and hasattr(para._element, "pPr"):
                    if (
                        para._element.pPr is not None
                        and para._element.pPr.ind is not None
                    ):
                        if hasattr(para._element.pPr.ind, "left"):
                            left_indent = para._element.pPr.ind.left
                            if left_indent is not None:
                                try:
                                    indent_val = int(
                                        left_indent.pt
                                        if hasattr(left_indent, "pt")
                                        else left_indent
                                    )
                                    indent_level = indent_val // 720
                                except (AttributeError, TypeError, ValueError):
                                    pass

                out_file.write("  " * indent_level + "1. " + para.text + "\n")

                # Add to section content
                section_stack[-1]["content"].append(
                    {
                        "type": "numbered_list",
                        "text": para.text,
                        "level": indent_level,
                        "paragraph_index": para_idx,
                    }
                )

            # Default: regular paragraph with formatting
            else:
                # Process runs to extract formatting
                formatted_text = ""
                for run in para.runs:
                    text = run.text

                    # Skip empty runs
                    if not text.strip():
                        formatted_text += text
                        continue

                    # Extract font information for metadata
                    font_info = {
                        "name": run.font.name,
                        "size": (
                            run.font.size.pt
                            if hasattr(run.font, "size") and run.font.size
                            else None
                        ),
                        "bold": run.bold,
                        "italic": run.italic,
                        "underline": run.underline,
                    }

                    # Extract color if available
                    if (
                        hasattr(run.font, "color")
                        and run.font.color
                        and run.font.color.rgb
                    ):
                        color = run.font.color.rgb
                        font_info["color"] = (
                            f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                        )

                    # Apply markdown formatting
                    if run.bold and run.italic:
                        formatted_text += f"***{text}***"
                    elif run.bold:
                        formatted_text += f"**{text}**"
                    elif run.italic:
                        formatted_text += f"*{text}*"
                    elif run.underline:
                        if text.lower().startswith(("http://", "https://")):
                            formatted_text += f"[{text}]({text})"
                        else:
                            formatted_text += f"__{text}__"
                    else:
                        formatted_text += text

                # Write the formatted paragraph
                out_file.write(formatted_text + "\n\n")

                # Add to section content
                section_stack[-1]["content"].append(
                    {
                        "type": "paragraph",
                        "text": formatted_text,
                        "style": style_name,
                        "paragraph_index": para_idx,
                    }
                )

        # Process tables with formatting and metadata
        for table_idx, table in enumerate(doc.tables):
            # Create header row
            header_row = []
            for cell in table.rows[0].cells:
                header_row.append(cell.text.strip() or " ")
            out_file.write("| " + " | ".join(header_row) + " |\n")

            # Create separator row
            out_file.write("| " + " | ".join(["---"] * len(header_row)) + " |\n")

            # Create data rows
            rows_data = []
            for row_idx, row in enumerate(table.rows):
                if row_idx == 0:  # Skip header, already handled
                    continue

                row_cells = []
                cell_data = []
                for cell in row.cells:
                    cell_text = cell.text.strip() or " "
                    row_cells.append(cell_text)
                    cell_data.append({"text": cell_text})
                out_file.write("| " + " | ".join(row_cells) + " |\n")
                rows_data.append(cell_data)

            out_file.write("\n")

            # Add to section content
            table_info = {
                "type": "table",
                "headers": header_row,
                "rows": rows_data,
                "row_count": len(table.rows),
                "column_count": len(header_row),
            }
            section_stack[-1]["content"].append(table_info)

    # If requested, generate outline files in JSON and YAML formats
    outline_files = {}
    if extract_outline:
        # Generate JSON outline
        json_path = output_dir / f"{base_name}_outline.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(outline_data, f, indent=2)
        outline_files["json"] = json_path

        # Generate YAML outline
        yaml_path = output_dir / f"{base_name}_outline.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(outline_data, f, default_flow_style=False)
        outline_files["yaml"] = yaml_path

    print(f"Conversion with metadata complete! Output saved to {output_file}")
    if extract_outline:
        print(f"Document outline saved as JSON: {outline_files['json']}")
        print(f"Document outline saved as YAML: {outline_files['yaml']}")

    return output_file, outline_files.get("json"), outline_files.get("yaml")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        # Look for test_document.docx in input directory
        test_doc = Path("input/test_document.docx")
        if test_doc.exists():
            docx_file = str(test_doc)
        else:
            print(
                "Usage: python enhanced_word_to_md.py <docx_file> [output_md_file] [--no-outline]"
            )
            return 1
    else:
        docx_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    extract_outline = "--no-outline" not in sys.argv

    if not os.path.exists(docx_file):
        print(f"Error: File not found - {docx_file}")
        return 1

    try:
        md_file, json_outline, yaml_outline = convert_docx_to_markdown_with_metadata(
            docx_file, output_file, extract_outline
        )
        print(f"\nSuccess! Converted {docx_file} to {md_file}")
        if extract_outline:
            print(f"Generated outline files: {json_outline}, {yaml_outline}")
        print("Now you can use these files with the RTM pipeline")
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
