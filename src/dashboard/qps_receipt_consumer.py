#!/usr/bin/env python3
"""Consume Wave 9 QPS triage registry receipts into a release disposition.

ACCEPT requires present PASS evidence, exact-SHA match, external artifact
binding and a valid provider SHA256. Every absent/stale/mismatched/incomplete
state resolves to DEFER with a machine-readable reason.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if not path:
        return None, "receipt_missing"
    target = Path(path)
    if not target.exists():
        return None, "receipt_missing"
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "receipt_invalid_json"
    if not isinstance(value, dict):
        return None, "receipt_invalid_root"
    return value, None


def evaluate_registry_receipt(receipt_path: str | Path | None, *, expected_git_sha: str | None) -> dict[str, Any]:
    receipt, load_error = _load_json(receipt_path)
    base = {
        "disposition": "DEFER",
        "reason": load_error or "unverified",
        "expected_git_sha": expected_git_sha,
        "observed_git_sha": None,
        "receipt_path": str(receipt_path) if receipt_path else None,
        "receipt_id": None,
        "artifact_id": None,
        "artifact_digest": None,
        "checks": {
            "receipt_present": False,
            "receipt_status_pass": False,
            "exact_sha_match": False,
            "external_artifact_bound": False,
            "provider_digest_present": False,
        },
    }
    if receipt is None:
        return base

    identity = receipt.get("identity", {}) if isinstance(receipt.get("identity"), dict) else {}
    governance = receipt.get("governance", {}) if isinstance(receipt.get("governance"), dict) else {}
    artifact = receipt.get("github_artifact", {}) if isinstance(receipt.get("github_artifact"), dict) else {}
    observed_sha = str(identity.get("git_sha", ""))
    artifact_digest = str(artifact.get("artifact_digest", ""))
    artifact_id = str(artifact.get("artifact_id", ""))
    status_pass = receipt.get("status") == "PASS"
    exact_sha_match = bool(expected_git_sha and observed_sha == expected_git_sha)
    external_bound = bool(governance.get("external_artifact_object_bound") and artifact_id)
    provider_digest = bool(
        governance.get("provider_digest_present")
        and artifact_digest.startswith("sha256:")
        and len(artifact_digest) == 71
        and all(char in "0123456789abcdef" for char in artifact_digest[7:].lower())
    )
    base.update({
        "observed_git_sha": observed_sha or None,
        "receipt_id": receipt.get("registry_receipt_id"),
        "artifact_id": artifact_id or None,
        "artifact_digest": artifact_digest or None,
        "checks": {
            "receipt_present": True,
            "receipt_status_pass": status_pass,
            "exact_sha_match": exact_sha_match,
            "external_artifact_bound": external_bound,
            "provider_digest_present": provider_digest,
        },
    })

    if not expected_git_sha:
        base["reason"] = "expected_git_sha_missing"
    elif len(expected_git_sha) != 40:
        base["reason"] = "expected_git_sha_invalid"
    elif not status_pass:
        base["reason"] = "receipt_status_not_pass"
    elif not exact_sha_match:
        base["reason"] = "exact_sha_mismatch"
    elif not external_bound:
        base["reason"] = "external_artifact_binding_missing"
    elif not provider_digest:
        base["reason"] = "provider_digest_missing_or_invalid"
    else:
        base["disposition"] = "ACCEPT"
        base["reason"] = "exact_sha_registry_evidence_verified"
    return base


def build_release_baseline_evidence(receipt_path: str | Path | None, *, expected_git_sha: str | None) -> dict[str, Any]:
    decision = evaluate_registry_receipt(receipt_path, expected_git_sha=expected_git_sha)
    return {
        "evidence_type": "qps_triage_registry_receipt",
        "expected_git_sha": expected_git_sha,
        "disposition": decision["disposition"],
        "reason": decision["reason"],
        "receipt": {
            "receipt_id": decision.get("receipt_id"),
            "artifact_id": decision.get("artifact_id"),
            "artifact_digest": decision.get("artifact_digest"),
            "observed_git_sha": decision.get("observed_git_sha"),
        },
        "checks": decision["checks"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve QPS registry receipt to ACCEPT/DEFER")
    parser.add_argument("receipt", help="Wave 9 registry receipt JSON")
    parser.add_argument("--expected-git-sha", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-accept", action="store_true", help="Return non-zero unless disposition is ACCEPT")
    args = parser.parse_args()
    evidence = build_release_baseline_evidence(args.receipt, expected_git_sha=args.expected_git_sha)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0 if not args.require_accept or evidence["disposition"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
