#!/usr/bin/env python3
"""Run the QPS triage parser-to-dashboard pipeline in one command.

Pipeline:
    parser -> enhanced export -> QPS triage dashboard -> canonical dashboard JSON

The CLI accepts either a pre-extracted parser input JSON object or a DOCX path.
Generated files are written under a single output directory so CI can archive the
whole evidence bundle as one artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from parser.engine import EnhancedParserEngine
from src.dashboard.canonical_dashboard import collect_stats
from src.dashboard.qps_triage_dashboard import QPSTriageDashboardGenerator


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return data


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_pipeline(
    output_dir: str | Path,
    *,
    input_analysis: str | Path | None = None,
    document: str | Path | None = None,
    config: str | Path = "configs/qps_triage_parser_config.yaml",
) -> dict[str, Any]:
    """Execute parser, exports, QPS dashboard, and canonical dashboard index."""
    if bool(input_analysis) == bool(document):
        raise ValueError("Provide exactly one of input_analysis or document")

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    parser = EnhancedParserEngine(config_path=str(config))

    if input_analysis:
        input_path = Path(input_analysis)
        analysis_data = _load_json(input_path)
        source_path = str(input_path)
        result = parser.parse_document(source_path, analysis_data)
    else:
        document_path = Path(document)  # type: ignore[arg-type]
        source_path = str(document_path)
        result = parser.parse_document(source_path)

    parser.export_enhanced_analysis(str(target))

    dashboard_generator = QPSTriageDashboardGenerator(target)
    dashboard_outputs = dashboard_generator.write_outputs(target)
    qps_dashboard_path = Path(dashboard_outputs["json"])

    canonical_stats = collect_stats(qps_triage_dashboard_path)
    canonical_dashboard_path = target / "canonical_dashboard.json"
    _write_json(canonical_dashboard_path, canonical_stats)

    artifact_files = sorted(path.name for path in target.iterdir() if path.is_file())
    manifest = {
        "pipeline_id": "QPS_TRIAGE_WAVE_7",
        "generated_at": datetime.now().isoformat(),
        "source": source_path,
        "config": str(config),
        "output_dir": str(target),
        "stages": {
            "parser": "PASS",
            "enhanced_export": "PASS",
            "qps_triage_dashboard": "PASS",
            "canonical_dashboard": "PASS",
        },
        "counts": {
            "triage_items": len(result.get("qps_triage_items", [])),
            "traceability_rows": len(result.get("qps_triage_traceability_rows", [])),
            "rtm_rows": canonical_stats.get("qps_triage_dashboard", {}).get("rtm_row_count", 0),
            "dtm_rows": canonical_stats.get("qps_triage_dashboard", {}).get("dtm_row_count", 0),
        },
        "canonical_dashboard": canonical_dashboard_path.name,
        "qps_triage_dashboard": qps_dashboard_path.name,
        "artifacts": artifact_files,
    }
    manifest_path = target / "qps_triage_pipeline_manifest.json"
    _write_json(manifest_path, manifest)
    manifest["artifacts"] = sorted(path.name for path in target.iterdir() if path.is_file())
    _write_json(manifest_path, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run parser -> export -> QPS triage dashboard -> canonical dashboard JSON.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-analysis", help="Pre-extracted parser input JSON object.")
    source.add_argument("--document", help="DOCX document path to parse.")
    parser.add_argument("--output-dir", required=True, help="Directory for the complete generated artifact bundle.")
    parser.add_argument("--config", default="configs/qps_triage_parser_config.yaml", help="Parser config with QPS triage enabled.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = run_pipeline(
        args.output_dir,
        input_analysis=args.input_analysis,
        document=args.document,
        config=args.config,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
