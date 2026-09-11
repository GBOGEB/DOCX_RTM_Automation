#!/usr/bin/env python3
"""Build a QPS procurement release-baseline decision from Wave 10 evidence.

This is a downstream consumer, not a new evidence framework. It converts the
Wave 10 ACCEPT/DEFER evidence decision into a controlled procurement-baseline
promotion decision across the agreed sequence:

publication baseline -> negotiation stage 1 -> negotiation stage 2
-> final Corrigendum -> contract baseline

PROMOTE requires exact-SHA Wave 10 evidence with disposition ACCEPT.
Anything else is HOLD with the original reason preserved.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = [
    "publication_baseline",
    "negotiation_stage_1",
    "negotiation_stage_2",
    "final_corrigendum",
    "contract_baseline",
]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return value


def build_release_baseline(
    evidence: dict[str, Any],
    *,
    stage: str,
    expected_git_sha: str,
) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"Unsupported stage: {stage}")
    if len(expected_git_sha) != 40:
        raise ValueError("expected_git_sha must be a 40-character Git SHA")

    evidence_sha = str(evidence.get("expected_git_sha", ""))
    evidence_disposition = str(evidence.get("disposition", "DEFER"))
    evidence_reason = str(evidence.get("reason", "evidence_reason_missing"))
    exact_sha_match = evidence_sha == expected_git_sha
    evidence_accept = evidence_disposition == "ACCEPT"
    promote = exact_sha_match and evidence_accept

    stage_index = STAGES.index(stage)
    previous_stage = STAGES[stage_index - 1] if stage_index > 0 else None
    next_stage = STAGES[stage_index + 1] if stage_index + 1 < len(STAGES) else None

    if not exact_sha_match:
        hold_reason = "release_evidence_exact_sha_mismatch"
    elif not evidence_accept:
        hold_reason = evidence_reason
    else:
        hold_reason = None

    return {
        "manifest_type": "qps_procurement_release_baseline",
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "stage_sequence": STAGES,
        "previous_stage": previous_stage,
        "next_stage": next_stage,
        "expected_git_sha": expected_git_sha,
        "source_evidence": {
            "evidence_type": evidence.get("evidence_type"),
            "disposition": evidence_disposition,
            "reason": evidence_reason,
            "expected_git_sha": evidence_sha or None,
            "receipt": evidence.get("receipt", {}),
            "checks": evidence.get("checks", {}),
        },
        "gates": {
            "exact_sha_match": exact_sha_match,
            "wave10_evidence_accept": evidence_accept,
        },
        "release_disposition": "PROMOTE" if promote else "HOLD",
        "release_reason": "exact_sha_release_evidence_accepted" if promote else hold_reason,
        "outward_facing_terms": {
            "requirements": "QPS Requirements",
            "commercial_response": "Fixed Price Offer",
            "amendment": "Corrigendum",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build QPS release baseline promotion decision")
    parser.add_argument("--evidence", required=True, help="Wave 10 qps_release_baseline_evidence.json")
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--expected-git-sha", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-promote", action="store_true", help="Return non-zero unless disposition is PROMOTE")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence = _load_json(Path(args.evidence))
    manifest = build_release_baseline(
        evidence,
        stage=args.stage,
        expected_git_sha=args.expected_git_sha,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if args.require_promote and manifest["release_disposition"] != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
