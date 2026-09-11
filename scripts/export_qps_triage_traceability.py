#!/usr/bin/env python3
"""Export QPS triage items and traceability rows from enhanced parser analysis."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from parser.qps_triage_bridge import QPSTriageBridge  # noqa: E402


def load_analysis(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at root of {path}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "triage_id",
        "from_object",
        "from_type",
        "relation",
        "to_object",
        "to_type",
        "disposition",
        "maturity_level",
        "priority_score",
        "evidence_class",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export QPS triage enrichment from enhanced parser analysis.")
    parser.add_argument("--input", required=True, type=Path, help="Input enhanced analysis JSON")
    parser.add_argument("--output-json", required=True, type=Path, help="Output enriched analysis JSON")
    parser.add_argument("--output-csv", required=True, type=Path, help="Output traceability rows CSV")
    parser.add_argument("--taxonomy", type=Path, default=REPO_ROOT / "federation" / "ADR_OCD" / "taxonomy.yaml")
    parser.add_argument("--applicability", type=Path, default=REPO_ROOT / "federation" / "ADR_OCD" / "qps_triage_applicability.yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analysis = load_analysis(args.input)
    bridge = QPSTriageBridge(taxonomy_path=args.taxonomy, applicability_path=args.applicability)
    enriched = bridge.enrich_analysis(analysis)
    write_json(args.output_json, enriched)
    write_csv(args.output_csv, enriched.get("qps_triage_traceability_rows", []))
    print(f"QPS triage items: {len(enriched.get('qps_triage_items', []))}")
    print(f"QPS triage traceability rows: {len(enriched.get('qps_triage_traceability_rows', []))}")
    print(f"Wrote enriched JSON: {args.output_json}")
    print(f"Wrote traceability CSV: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
