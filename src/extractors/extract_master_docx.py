#!/usr/bin/env python3
"""
Extract structured requirements from a master Word document (.docx).

Reads the 137-page master requirements DOCX and emits a canonical JSON artefact
keyed by requirement ID containing:
  - req_id       : stable identifier derived from listnum (e.g. "REQ-1.2.3")
  - listnum      : raw list numbering string from the document
  - listnum_heading : heading text of the nearest enclosing numbered heading
  - section_path : breadcrumb of parent heading texts (list, root-first)
  - paragraph_text : full text of the paragraph
  - style        : paragraph style name from Word
  - page_approx  : approximate paragraph index (proxy for page location)
"""

import hashlib
import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LISTNUM_RE = re.compile(
    r"^(\d+(?:\.\d+)*)[\.\)]\s+|"   # "1.2.3. " or "1.2.3) "
    r"^\((\d+(?:\.\d+)*)\)\s+"       # "(1.2.3) "
)


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def _derive_req_id(listnum: str, paragraph_index: int) -> str:
    """Create a stable req_id from a listnum string or fall back to index."""
    if listnum:
        slug = re.sub(r"[^0-9a-zA-Z\-]", "-", listnum.strip(". )")).strip("-")
        return f"REQ-{slug}"
    return f"REQ-P{paragraph_index}"


def _extract_listnum(text: str) -> str:
    """Pull the leading numbering prefix from paragraph text, if present."""
    m = _LISTNUM_RE.match(text.strip())
    if not m:
        return ""
    return (m.group(1) or m.group(2) or "").strip()


def _is_heading_style(style_name: str) -> bool:
    sn = (style_name or "").lower()
    return "heading" in sn or sn.startswith("h1") or sn.startswith("h2")


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_from_docx(docx_path: Path) -> list[dict]:
    """
    Parse a DOCX file and return a list of requirement records.

    Each record contains: req_id, listnum, listnum_heading, section_path,
    paragraph_text, style, page_approx.
    """
    try:
        from docx import Document  # type: ignore
    except ImportError:
        logger.error("python-docx is required: pip install python-docx")
        raise

    doc = Document(str(docx_path))
    records: list[dict] = []

    # Track heading stack for section_path breadcrumbs
    heading_stack: list[tuple[int, str]] = []  # (level, text)
    current_numbered_heading = ""

    for idx, para in enumerate(doc.paragraphs):
        text = _clean_text(para.text)
        if not text:
            continue

        style_name = para.style.name if para.style else ""
        is_heading = _is_heading_style(style_name)

        # Maintain heading stack
        if is_heading:
            level = int(re.search(r"\d+", style_name).group()) if re.search(r"\d+", style_name) else 1
            # Pop entries at same or deeper level
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, text))

            # Track numbered headings for listnum_heading
            listnum = _extract_listnum(text)
            if listnum:
                current_numbered_heading = text
            continue  # Headings are structural, not requirements

        # Extract listnum from paragraph text
        listnum = _extract_listnum(text)

        section_path = [h[1] for h in heading_stack]
        listnum_heading = current_numbered_heading

        req_id = _derive_req_id(listnum, idx)

        records.append(
            {
                "req_id": req_id,
                "listnum": listnum,
                "listnum_heading": listnum_heading,
                "section_path": section_path,
                "paragraph_text": text,
                "style": style_name,
                "page_approx": idx,
            }
        )

    return records


def run(docx_path: Path, output_path: Path) -> dict:
    """
    Extract requirements from *docx_path* and write canonical JSON to *output_path*.

    Returns the canonical artefact dict (without _meta, which is added by the
    manifest engine).
    """
    logger.info("Extracting master requirements from: %s", docx_path)
    records = extract_from_docx(docx_path)

    # Key by req_id; last-write-wins for duplicate IDs (document ordering preserved)
    keyed: dict[str, dict] = {}
    for r in records:
        key = r["req_id"]
        if key in keyed:
            # Append a suffix to de-duplicate within the same doc
            suffix = 1
            while f"{key}-{suffix}" in keyed:
                suffix += 1
            key = f"{key}-{suffix}"
            r = dict(r, req_id=key)
        keyed[key] = r

    artefact = {
        "type": "master_requirements",
        "source": docx_path.name,
        "record_count": len(keyed),
        "requirements": keyed,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(artefact, fh, indent=2, ensure_ascii=False)

    logger.info("Written %d requirements to %s", len(keyed), output_path)
    return artefact


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Extract master requirements from DOCX")
    parser.add_argument("docx", help="Path to source .docx file")
    parser.add_argument(
        "-o",
        "--output",
        default="canonical/artefacts/master_requirements_v1.json",
        help="Output JSON path (default: canonical/artefacts/master_requirements_v1.json)",
    )
    args = parser.parse_args()
    run(Path(args.docx), Path(args.output))


if __name__ == "__main__":
    _cli()
