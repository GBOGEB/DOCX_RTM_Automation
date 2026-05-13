#!/usr/bin/env python3
"""
Extract RTM data from an Excel workbook (.xlsx).

Reads RTM_EXTRACTED.xlsx (or equivalent) and maps columns to the canonical
RTM matrix schema:
  - rtm_id           : stable RTM identifier (e.g. "RTM-001")
  - req_id           : linked requirement identifier (cross-ref to master_requirements)
  - document_location: document name / section reference
  - listnum          : list-numbering hook in the source document
  - listnum_heading  : heading title at that listnum position
  - status           : coverage status (e.g. "Covered", "Gap", "Partial")
  - notes            : freeform notes column
"""

import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name normalisation
# ---------------------------------------------------------------------------

# Flexible column aliases: keys are canonical field names, values are possible
# header strings (lowercased, stripped) found in the workbook.
_COLUMN_ALIASES: dict[str, list[str]] = {
    "rtm_id": ["rtm id", "rtm_id", "rtm number", "rtm#", "id"],
    "req_id": [
        "req id", "req_id", "requirement id", "requirement number",
        "req number", "req#", "requirement",
    ],
    "document_location": [
        "document location", "doc location", "document", "location",
        "source document", "document name",
    ],
    "listnum": [
        "listnum", "list num", "list number", "list_num",
        "numbering", "outline number",
    ],
    "listnum_heading": [
        "listnum heading", "heading", "section heading", "section title",
        "heading title", "title",
    ],
    "status": ["status", "coverage", "coverage status", "state"],
    "notes": ["notes", "note", "comments", "comment", "remarks"],
}


def _normalise_header(header: str) -> str:
    return str(header).lower().strip()


def _map_columns(headers: list[str]) -> dict[str, int]:
    """Return {canonical_field: column_index} for found headers."""
    norm = [_normalise_header(h) for h in headers]
    mapping: dict[str, int] = {}
    for field, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in norm:
                mapping[field] = norm.index(alias)
                break
    return mapping


def _cell_value(row, col_idx: int) -> str:
    try:
        val = row[col_idx].value
        return str(val).strip() if val is not None else ""
    except (IndexError, AttributeError):
        return ""


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_from_xlsx(xlsx_path: Path, sheet_name: str | None = None) -> list[dict]:
    """
    Parse an Excel workbook and return a list of RTM records.

    If *sheet_name* is None, the first sheet is used.
    """
    try:
        import openpyxl  # type: ignore
    except ImportError:
        logger.error("openpyxl is required: pip install openpyxl")
        raise

    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.active

    rows = list(ws.iter_rows())
    if not rows:
        logger.warning("Workbook sheet is empty: %s", xlsx_path)
        return []

    # First row is the header
    header_row = [str(c.value or "").strip() for c in rows[0]]
    col_map = _map_columns(header_row)

    if not col_map:
        logger.warning(
            "No recognised columns found in %s. Headers: %s", xlsx_path, header_row
        )

    records: list[dict] = []
    for row_idx, row in enumerate(rows[1:], start=2):
        # Skip fully empty rows
        if all((c.value is None or str(c.value).strip() == "") for c in row):
            continue

        def get(field: str) -> str:
            idx = col_map.get(field)
            return _cell_value(row, idx) if idx is not None else ""

        rtm_id_raw = get("rtm_id")
        if not rtm_id_raw:
            # Generate a stable fallback ID from row number
            rtm_id_raw = f"RTM-ROW{row_idx:04d}"

        # Normalise rtm_id to RTM-NNN format if it looks numeric
        if re.fullmatch(r"\d+", rtm_id_raw):
            rtm_id = f"RTM-{int(rtm_id_raw):04d}"
        else:
            rtm_id = rtm_id_raw

        records.append(
            {
                "rtm_id": rtm_id,
                "req_id": get("req_id"),
                "document_location": get("document_location"),
                "listnum": get("listnum"),
                "listnum_heading": get("listnum_heading"),
                "status": get("status"),
                "notes": get("notes"),
                "_row": row_idx,
            }
        )

    wb.close()
    return records


def run(xlsx_path: Path, output_path: Path, sheet_name: str | None = None) -> dict:
    """
    Extract RTM matrix from *xlsx_path* and write canonical JSON to *output_path*.

    Returns the canonical artefact dict.
    """
    logger.info("Extracting RTM matrix from: %s", xlsx_path)
    records = extract_from_xlsx(xlsx_path, sheet_name=sheet_name)

    # Key by rtm_id
    keyed: dict[str, dict] = {}
    for r in records:
        key = r["rtm_id"]
        if key in keyed:
            suffix = 1
            while f"{key}-{suffix}" in keyed:
                suffix += 1
            key = f"{key}-{suffix}"
            r = dict(r, rtm_id=key)
        keyed[key] = r

    artefact = {
        "type": "rtm_matrix",
        "source": xlsx_path.name,
        "record_count": len(keyed),
        "rtm_entries": keyed,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(artefact, fh, indent=2, ensure_ascii=False)

    logger.info("Written %d RTM entries to %s", len(keyed), output_path)
    return artefact


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Extract RTM matrix from Excel workbook")
    parser.add_argument("xlsx", help="Path to source .xlsx file")
    parser.add_argument(
        "-o",
        "--output",
        default="canonical/artefacts/rtm_matrix_v1.json",
        help="Output JSON path (default: canonical/artefacts/rtm_matrix_v1.json)",
    )
    parser.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
    args = parser.parse_args()
    run(Path(args.xlsx), Path(args.output), sheet_name=args.sheet)


if __name__ == "__main__":
    _cli()
