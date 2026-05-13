#!/usr/bin/env python3
"""
Extract offer items from an Excel workbook (.xlsx).

Reads OFFER_ITEMS.xlsx (or equivalent) and maps columns to the canonical
offer-items schema:
  - offer_id     : stable identifier (e.g. "OFFER-001")
  - title        : offer item title / name
  - description  : full description text
  - req_id       : linked requirement identifier (cross-ref to master_requirements)
  - category     : item category or type
  - price        : price / cost if present
  - unit         : unit of measure
  - quantity     : quantity if present
  - notes        : freeform notes
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name normalisation
# ---------------------------------------------------------------------------

_COLUMN_ALIASES: dict[str, list[str]] = {
    "offer_id": [
        "offer id", "offer_id", "item id", "item number", "item#",
        "no", "no.", "#", "id",
    ],
    "title": ["title", "item title", "name", "item name", "description title"],
    "description": [
        "description", "desc", "detail", "details", "item description",
        "specification", "spec",
    ],
    "req_id": [
        "req id", "req_id", "requirement id", "requirement", "req number",
        "requirement number",
    ],
    "category": ["category", "type", "group", "section", "class"],
    "price": ["price", "unit price", "cost", "rate", "amount"],
    "unit": ["unit", "uom", "unit of measure"],
    "quantity": ["quantity", "qty", "count", "amount"],
    "notes": ["notes", "note", "comment", "comments", "remarks"],
}


def _normalise_header(header: str) -> str:
    return str(header).lower().strip()


def _map_columns(headers: list[str]) -> dict[str, int]:
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
    """Parse an Excel workbook and return a list of offer-item records."""
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

    header_row = [str(c.value or "").strip() for c in rows[0]]
    col_map = _map_columns(header_row)

    if not col_map:
        logger.warning(
            "No recognised columns found in %s. Headers: %s", xlsx_path, header_row
        )

    records: list[dict] = []
    offer_counter = 0

    for row_idx, row in enumerate(rows[1:], start=2):
        if all((c.value is None or str(c.value).strip() == "") for c in row):
            continue

        offer_counter += 1

        def get(field: str) -> str:
            idx = col_map.get(field)
            return _cell_value(row, idx) if idx is not None else ""

        offer_id_raw = get("offer_id")
        if not offer_id_raw:
            offer_id_raw = f"OFFER-ROW{row_idx:04d}"

        # Normalise to OFFER-NNN
        if re.fullmatch(r"\d+", offer_id_raw):
            offer_id = f"OFFER-{int(offer_id_raw):03d}"
        else:
            offer_id = offer_id_raw if offer_id_raw.upper().startswith("OFFER") else f"OFFER-{offer_id_raw}"

        records.append(
            {
                "offer_id": offer_id,
                "title": get("title"),
                "description": get("description"),
                "req_id": get("req_id"),
                "category": get("category"),
                "price": get("price"),
                "unit": get("unit"),
                "quantity": get("quantity"),
                "notes": get("notes"),
                "_row": row_idx,
            }
        )

    wb.close()
    return records


def run(xlsx_path: Path, output_path: Path, sheet_name: str | None = None) -> dict:
    """
    Extract offer items from *xlsx_path* and write canonical JSON to *output_path*.

    Returns the canonical artefact dict.
    """
    logger.info("Extracting offer items from: %s", xlsx_path)
    records = extract_from_xlsx(xlsx_path, sheet_name=sheet_name)

    keyed: dict[str, dict] = {}
    for r in records:
        key = r["offer_id"]
        if key in keyed:
            suffix = 1
            while f"{key}-{suffix}" in keyed:
                suffix += 1
            key = f"{key}-{suffix}"
            r = dict(r, offer_id=key)
        keyed[key] = r

    artefact = {
        "type": "offer_items",
        "source": xlsx_path.name,
        "record_count": len(keyed),
        "offer_items": keyed,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(artefact, fh, indent=2, ensure_ascii=False)

    logger.info("Written %d offer items to %s", len(keyed), output_path)
    return artefact


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Extract offer items from Excel workbook")
    parser.add_argument("xlsx", help="Path to source .xlsx file")
    parser.add_argument(
        "-o",
        "--output",
        default="canonical/artefacts/offer_items_v1.json",
        help="Output JSON path (default: canonical/artefacts/offer_items_v1.json)",
    )
    parser.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
    args = parser.parse_args()
    run(Path(args.xlsx), Path(args.output), sheet_name=args.sheet)


if __name__ == "__main__":
    _cli()
