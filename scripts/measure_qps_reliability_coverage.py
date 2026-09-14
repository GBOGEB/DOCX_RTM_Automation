#!/usr/bin/env python3
"""Measure reliability-pack coverage from governed QPS Wave 8 outputs.

This is a measurement layer, not a new governance gate. It reports explicit
observed denominators/counts from qps_triage_items.json and
qps_triage_traceability_rows.json and can fail CI when the expected reliability
fixture composition is not actually processed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _read_list(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {path}")
    return [row for row in data if isinstance(row, dict)]


def build_coverage(
    output_dir: Path,
    expected_rtm: int,
    expected_otc: int,
    expected_dtm: int,
) -> dict[str, Any]:
    items_path = output_dir / "qps_triage_items.json"
    trace_path = output_dir / "qps_triage_traceability_rows.json"
    if not items_path.exists() or not trace_path.exists():
        missing = [str(p.name) for p in (items_path, trace_path) if not p.exists()]
        raise FileNotFoundError(f"Missing Wave 8 coverage inputs: {', '.join(missing)}")

    items = _read_list(items_path)
    trace_rows = _read_list(trace_path)

    source_counts = Counter(str(item.get("source_type", "UNKNOWN")) for item in items)
    disposition_counts = Counter(str(item.get("disposition", "UNKNOWN")) for item in items)
    evidence_counts = Counter(str(item.get("evidence_class", "UNKNOWN")) for item in items)
    lane_counts = Counter(str(item.get("primary_lane", "UNKNOWN")) for item in items)

    expected = {"RTM": expected_rtm, "OTC": expected_otc, "DTM": expected_dtm}
    expected_total = sum(expected.values())
    observed_total = len(items)

    triage_ids = {str(item.get("triage_id")) for item in items if item.get("triage_id")}
    traced_ids = {str(row.get("triage_id")) for row in trace_rows if row.get("triage_id")}
    untraced_ids = sorted(triage_ids - traced_ids)

    source_type_complete = all(source_counts.get(kind, 0) == count for kind, count in expected.items())
    total_complete = observed_total == expected_total
    traceability_complete = bool(triage_ids) and triage_ids.issubset(traced_ids)
    complete = source_type_complete and total_complete and traceability_complete

    return {
        "metric_type": "qps_reliability_pack_coverage",
        "metric_version": "1.0.0",
        "scope": "phase_7_5_measured_coverage",
        "expected": {
            "source_counts": expected,
            "triage_items": expected_total,
        },
        "observed": {
            "source_counts": dict(sorted(source_counts.items())),
            "triage_items": observed_total,
            "traceability_rows": len(trace_rows),
            "triage_items_with_traceability": len(triage_ids & traced_ids),
            "dispositions": dict(sorted(disposition_counts.items())),
            "evidence_classes": dict(sorted(evidence_counts.items())),
            "primary_lanes": dict(sorted(lane_counts.items())),
        },
        "coverage": {
            "source_intake_fraction": (observed_total / expected_total) if expected_total else 1.0,
            "traceability_fraction": (len(triage_ids & traced_ids) / len(triage_ids)) if triage_ids else 0.0,
            "source_type_complete": source_type_complete,
            "total_complete": total_complete,
            "traceability_complete": traceability_complete,
            "complete": complete,
        },
        "gaps": {
            "untraced_triage_ids": untraced_ids,
            "source_count_delta": {
                kind: source_counts.get(kind, 0) - count for kind, count in expected.items()
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--expected-rtm", type=int, default=3)
    parser.add_argument("--expected-otc", type=int, default=1)
    parser.add_argument("--expected-dtm", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    coverage = build_coverage(
        args.output_dir,
        expected_rtm=args.expected_rtm,
        expected_otc=args.expected_otc,
        expected_dtm=args.expected_dtm,
    )
    output = args.output or (args.output_dir / "qps_reliability_coverage.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(coverage, indent=2))

    if args.require_complete and not coverage["coverage"]["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
