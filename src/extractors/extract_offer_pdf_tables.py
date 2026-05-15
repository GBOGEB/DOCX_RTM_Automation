#!/usr/bin/env python3
"""
Extract offer tables from a PDF document.

Reads OFFER_TABLES.pdf (or equivalent) and extracts tabular data using
pdfplumber, mapping rows to the canonical offer-tables schema:
  - offer_id       : stable identifier linked to offer_items (cross-ref)
  - table_index    : source table index within the PDF (0-based)
  - page           : source page number (1-based)
  - row_index      : row position within the table (0-based, header excluded)
  - columns        : dict of {header: cell_value} for each row
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(val) -> str:
    """Normalise a cell value to a clean string."""
    if val is None:
        return ""
    return " ".join(str(val).split())


def _infer_offer_id(row: dict, fallback_idx: int) -> str:
    """
    Try to find an offer_id from row data.
    Looks for columns whose lowercased name contains 'offer', 'id', 'no', 'item'.
    """
    for key, val in row.items():
        k = key.lower()
        if any(tok in k for tok in ("offer", "item id", "item no", "no.", "id")):
            cleaned = _clean(val)
            if cleaned:
                if re.fullmatch(r"\d+", cleaned):
                    return f"OFFER-{int(cleaned):03d}"
                if not cleaned.upper().startswith("OFFER"):
                    return f"OFFER-{cleaned}"
                return cleaned
    return f"OFFER-TABLE{fallback_idx:04d}"


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Parse all tables from a PDF and return a list of row records.

    Returns a flat list — one entry per data row across all tables.
    """
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        logger.error("pdfplumber is required: pip install pdfplumber")
        raise

    records: list[dict] = []
    global_row_idx = 0

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue

            for table_idx, table in enumerate(tables):
                if not table:
                    continue

                # First non-empty row is treated as header
                header_row_raw = None
                data_rows = []
                for row in table:
                    cleaned = [_clean(c) for c in (row or [])]
                    if not any(cleaned):
                        continue  # skip blank rows
                    if header_row_raw is None:
                        header_row_raw = cleaned
                    else:
                        data_rows.append(cleaned)

                if not header_row_raw:
                    continue

                # De-duplicate header names
                headers: list[str] = []
                seen: dict[str, int] = {}
                for h in header_row_raw:
                    h_clean = h or f"col_{len(headers)}"
                    if h_clean in seen:
                        seen[h_clean] += 1
                        h_clean = f"{h_clean}_{seen[h_clean]}"
                    else:
                        seen[h_clean] = 0
                    headers.append(h_clean)

                for row_idx, row in enumerate(data_rows):
                    # Pad / trim row to header length
                    padded = (row + [""] * len(headers))[: len(headers)]
                    row_dict = dict(zip(headers, padded))

                    offer_id = _infer_offer_id(row_dict, global_row_idx)

                    records.append(
                        {
                            "offer_id": offer_id,
                            "table_index": table_idx,
                            "page": page_num,
                            "row_index": row_idx,
                            "columns": row_dict,
                        }
                    )
                    global_row_idx += 1

    return records


def run(pdf_path: Path, output_path: Path) -> dict:
    """
    Extract offer tables from *pdf_path* and write canonical JSON to *output_path*.

    Returns the canonical artefact dict.
    """
    logger.info("Extracting offer tables from: %s", pdf_path)
    records = extract_from_pdf(pdf_path)

    # Key by offer_id; append sequential suffix for duplicates
    keyed: dict[str, list[dict]] = {}
    for r in records:
        key = r["offer_id"]
        keyed.setdefault(key, []).append(r)

    artefact = {
        "type": "offer_tables",
        "source": pdf_path.name,
        "record_count": len(records),
        "offer_table_rows": keyed,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(artefact, fh, indent=2, ensure_ascii=False)

    logger.info("Written %d offer table rows to %s", len(records), output_path)
    return artefact


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Extract offer tables from PDF")
    parser.add_argument("pdf", help="Path to source .pdf file")
    parser.add_argument(
        "-o",
        "--output",
        default="canonical/artefacts/offer_tables_v1.json",
        help="Output JSON path (default: canonical/artefacts/offer_tables_v1.json)",
    )
    args = parser.parse_args()
    run(Path(args.pdf), Path(args.output))


if __name__ == "__main__":
    _cli()
