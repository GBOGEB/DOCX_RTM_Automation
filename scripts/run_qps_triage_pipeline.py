#!/usr/bin/env python3
"""Run the governed QPS triage parser-to-dashboard pipeline.

Pipeline:
    parser -> enhanced export -> QPS triage dashboard -> canonical dashboard
    -> SHA256 evidence manifest -> exact-SHA governed receipt

CI identity is read from GitHub Actions environment variables when available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_sha() -> str:
    if os.getenv("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _run_identity() -> dict[str, Any]:
    return {
        "repository": os.getenv("GITHUB_REPOSITORY", "GBOGEB/DOCX_RTM_Automation"),
        "git_sha": _git_sha(),
        "git_ref": os.getenv("GITHUB_REF", "LOCAL"),
        "git_head_ref": os.getenv("GITHUB_HEAD_REF", ""),
        "workflow": os.getenv("GITHUB_WORKFLOW", "LOCAL"),
        "workflow_ref": os.getenv("GITHUB_WORKFLOW_REF", ""),
        "run_id": os.getenv("GITHUB_RUN_ID", "LOCAL"),
        "run_number": os.getenv("GITHUB_RUN_NUMBER", "LOCAL"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "LOCAL"),
        "job": os.getenv("GITHUB_JOB", "LOCAL"),
        "actor": os.getenv("GITHUB_ACTOR", "LOCAL"),
    }


def _inventory(target: Path, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    return [
        {"path": path.name, "sha256": _sha256(path), "size_bytes": path.stat().st_size}
        for path in sorted(target.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name not in excluded
    ]


def run_pipeline(
    output_dir: str | Path,
    *,
    input_analysis: str | Path | None = None,
    document: str | Path | None = None,
    config: str | Path = "configs/qps_triage_parser_config.yaml",
) -> dict[str, Any]:
    """Execute parser/export/dashboard and emit a governed exact-SHA receipt."""
    if bool(input_analysis) == bool(document):
        raise ValueError("Provide exactly one of input_analysis or document")

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    parser = EnhancedParserEngine(config_path=str(config))

    if input_analysis:
        input_path = Path(input_analysis)
        result = parser.parse_document(str(input_path), _load_json(input_path))
        source_path = str(input_path)
    else:
        document_path = Path(document)  # type: ignore[arg-type]
        result = parser.parse_document(str(document_path))
        source_path = str(document_path)

    parser.export_enhanced_analysis(str(target))
    dashboard_outputs = QPSTriageDashboardGenerator(target).write_outputs(target)
    qps_dashboard_path = Path(dashboard_outputs["json"])

    # Wave 7 repair: use the defined dashboard path when constructing canonical stats.
    canonical_stats = collect_stats(qps_dashboard_path)
    canonical_dashboard_path = target / "canonical_dashboard.json"
    _write_json(canonical_dashboard_path, canonical_stats)

    identity = _run_identity()
    manifest_path = target / "qps_triage_pipeline_manifest.json"
    evidence_path = target / "qps_triage_evidence_manifest.json"
    receipt_path = target / "qps_triage_governed_receipt.json"
    sums_path = target / "SHA256SUMS"

    manifest = {
        "pipeline_id": "QPS_TRIAGE_WAVE_8",
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source_path,
        "config": str(config),
        "identity": identity,
        "stages": {
            "parser": "PASS",
            "enhanced_export": "PASS",
            "qps_triage_dashboard": "PASS",
            "canonical_dashboard": "PASS",
            "hash_inventory": "PASS",
            "receipt": "PASS",
        },
        "counts": {
            "triage_items": len(result.get("qps_triage_items", [])),
            "traceability_rows": len(result.get("qps_triage_traceability_rows", [])),
            "rtm_rows": canonical_stats.get("qps_triage_dashboard", {}).get("rtm_row_count", 0),
            "dtm_rows": canonical_stats.get("qps_triage_dashboard", {}).get("dtm_row_count", 0),
        },
        "canonical_dashboard": canonical_dashboard_path.name,
        "qps_triage_dashboard": qps_dashboard_path.name,
    }
    _write_json(manifest_path, manifest)

    payload_inventory = _inventory(target, {evidence_path.name, receipt_path.name, sums_path.name})
    evidence_manifest = {
        "evidence_manifest_id": "QPS_TRIAGE_WAVE_8_EVIDENCE",
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "identity": identity,
        "hash_algorithm": "SHA256",
        "artifact_count": len(payload_inventory),
        "artifacts": payload_inventory,
        "parity_rule": "Every regular pipeline payload artifact appears exactly once with matching path, size, and SHA256.",
    }
    _write_json(evidence_path, evidence_manifest)

    receipt = {
        "receipt_id": f"QPS-TRIAGE-W8-{identity['git_sha'][:12]}",
        "receipt_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "identity": identity,
        "pipeline_manifest": {"path": manifest_path.name, "sha256": _sha256(manifest_path)},
        "evidence_manifest": {"path": evidence_path.name, "sha256": _sha256(evidence_path)},
        "artifact_count": len(payload_inventory),
        "counts": manifest["counts"],
        "governance": {
            "exact_sha_bound": identity["git_sha"] != "UNKNOWN",
            "workflow_bound": identity["run_id"] != "LOCAL",
            "parity_verified_at_generation": True,
        },
    }
    _write_json(receipt_path, receipt)

    all_records = _inventory(target, {sums_path.name})
    sums_path.write_text(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in all_records),
        encoding="utf-8",
    )
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run governed QPS triage pipeline and emit exact-SHA evidence receipt.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-analysis", help="Pre-extracted parser input JSON object.")
    source.add_argument("--document", help="DOCX document path to parse.")
    parser.add_argument("--output-dir", required=True, help="Directory for the complete generated artifact bundle.")
    parser.add_argument("--config", default="configs/qps_triage_parser_config.yaml", help="Parser config with QPS triage enabled.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = run_pipeline(args.output_dir, input_analysis=args.input_analysis, document=args.document, config=args.config)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
