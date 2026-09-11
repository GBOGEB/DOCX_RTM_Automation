#!/usr/bin/env python3
"""QPS triage downstream dashboard/report generator.

Consumes the Wave 4B export files produced by EnhancedParserEngine:

- qps_triage_downstream_index.json
- qps_triage_rtm_rows.csv
- qps_triage_dtm_rows.csv
- qps_triage_traceability_rows.csv
- qps_triage_items.json

The generator produces lightweight downstream artifacts that existing dashboard
or report launchers can serve or embed without depending on parser internals.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class QPSTriageDashboardGenerator:
    """Generate dashboard-ready QPS triage report artifacts from parser exports."""

    def __init__(self, export_dir: str | Path):
        self.export_dir = Path(export_dir)

    def load_exports(self) -> dict[str, Any]:
        """Load QPS triage export files if present."""
        downstream_index = self._load_json("qps_triage_downstream_index.json", default={})
        triage_items = self._load_json("qps_triage_items.json", default=[])
        traceability_rows = self._load_csv("qps_triage_traceability_rows.csv")
        rtm_rows = self._load_csv("qps_triage_rtm_rows.csv")
        dtm_rows = self._load_csv("qps_triage_dtm_rows.csv")
        return {
            "downstream_index": downstream_index,
            "triage_items": triage_items,
            "traceability_rows": traceability_rows,
            "rtm_rows": rtm_rows,
            "dtm_rows": dtm_rows,
        }

    def generate_report_data(self) -> dict[str, Any]:
        """Create normalized JSON report data for downstream dashboard artifacts."""
        exports = self.load_exports()
        items = exports["triage_items"] if isinstance(exports["triage_items"], list) else []
        rows = exports["traceability_rows"]
        rtm_rows = exports["rtm_rows"]
        dtm_rows = exports["dtm_rows"]
        downstream_index = exports["downstream_index"] if isinstance(exports["downstream_index"], dict) else {}

        by_disposition = self._count_by(items, "disposition")
        by_lane = self._count_by(items, "primary_lane")
        by_evidence_class = self._count_by(items, "evidence_class")
        by_relation = self._count_by(rows, "relation")

        return {
            "generated_at": datetime.now().isoformat(),
            "source_export_dir": str(self.export_dir),
            "summary": {
                "triage_item_count": len(items),
                "traceability_row_count": len(rows),
                "rtm_row_count": len(rtm_rows),
                "dtm_row_count": len(dtm_rows),
                "downstream_index_present": bool(downstream_index),
            },
            "counts": {
                "by_disposition": by_disposition,
                "by_lane": by_lane,
                "by_evidence_class": by_evidence_class,
                "by_relation": by_relation,
                "by_target_type": downstream_index.get("by_target_type_counts", {}),
            },
            "rtm_rows": rtm_rows,
            "dtm_rows": dtm_rows,
            "top_priority_items": self._top_priority_items(items),
            "source_files": {
                "downstream_index": "qps_triage_downstream_index.json",
                "rtm_rows": "qps_triage_rtm_rows.csv",
                "dtm_rows": "qps_triage_dtm_rows.csv",
                "traceability_rows": "qps_triage_traceability_rows.csv",
                "triage_items": "qps_triage_items.json",
            },
        }

    def write_outputs(self, output_dir: str | Path | None = None) -> dict[str, str]:
        """Write dashboard JSON, Markdown, and HTML outputs."""
        target_dir = Path(output_dir) if output_dir else self.export_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        report_data = self.generate_report_data()

        json_path = target_dir / "qps_triage_dashboard.json"
        md_path = target_dir / "qps_triage_dashboard.md"
        html_path = target_dir / "qps_triage_dashboard.html"

        json_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        md_path.write_text(self.render_markdown(report_data), encoding="utf-8")
        html_path.write_text(self.render_html(report_data), encoding="utf-8")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "html": str(html_path),
        }

    def render_markdown(self, data: dict[str, Any]) -> str:
        summary = data["summary"]
        counts = data["counts"]
        lines = [
            "# QPS Triage Dashboard",
            "",
            f"Generated: {data['generated_at']}",
            f"Source export directory: `{data['source_export_dir']}`",
            "",
            "## Summary",
            "",
            f"- Triage items: {summary['triage_item_count']}",
            f"- Traceability rows: {summary['traceability_row_count']}",
            f"- RTM rows: {summary['rtm_row_count']}",
            f"- DTM rows: {summary['dtm_row_count']}",
            f"- Downstream index present: {summary['downstream_index_present']}",
            "",
            "## Counts by disposition",
            "",
        ]
        lines.extend(self._markdown_counts(counts.get("by_disposition", {})))
        lines.extend(["", "## Counts by lane", ""])
        lines.extend(self._markdown_counts(counts.get("by_lane", {})))
        lines.extend(["", "## Counts by relation", ""])
        lines.extend(self._markdown_counts(counts.get("by_relation", {})))
        lines.extend(["", "## RTM / DTM downstream surfaces", ""])
        lines.append(f"- RTM rows exported: {summary['rtm_row_count']}")
        lines.append(f"- DTM rows exported: {summary['dtm_row_count']}")
        lines.extend(["", "## Top priority items", ""])
        for item in data.get("top_priority_items", []):
            lines.append(
                f"- `{item.get('triage_id')}` | lane={item.get('primary_lane')} | "
                f"disposition={item.get('disposition')} | priority={item.get('priority_score')}"
            )
        return "\n".join(lines) + "\n"

    def render_html(self, data: dict[str, Any]) -> str:
        markdown = self.render_markdown(data)
        escaped = html.escape(markdown)
        return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>QPS Triage Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.45; }
    pre { white-space: pre-wrap; background: #f6f8fa; padding: 1rem; border-radius: 8px; }
  </style>
</head>
<body>
  <pre>""" + escaped + """</pre>
</body>
</html>
"""

    def _load_json(self, filename: str, default: Any) -> Any:
        path = self.export_dir / filename
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_csv(self, filename: str) -> list[dict[str, str]]:
        path = self.export_dir / filename
        if not path.exists():
            return []
        with path.open("r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _count_by(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = str(row.get(field) or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts

    @staticmethod
    def _top_priority_items(items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
        def priority(item: dict[str, Any]) -> int:
            try:
                return int(item.get("priority_score", 0))
            except (TypeError, ValueError):
                return 0

        return sorted([item for item in items if isinstance(item, dict)], key=priority, reverse=True)[:limit]

    @staticmethod
    def _markdown_counts(counts: dict[str, int]) -> list[str]:
        if not counts:
            return ["- none"]
        return [f"- {key}: {value}" for key, value in sorted(counts.items())]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate QPS triage dashboard artifacts from parser exports.")
    parser.add_argument("--export-dir", required=True, help="Directory containing Wave 4B QPS triage export files.")
    parser.add_argument("--output-dir", default=None, help="Optional output directory for dashboard artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generator = QPSTriageDashboardGenerator(args.export_dir)
    outputs = generator.write_outputs(args.output_dir)
    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
