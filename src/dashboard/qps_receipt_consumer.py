#!/usr/bin/env python3
"""Consume Wave 9 QPS triage registry receipts into a release disposition.

Policy:
- ACCEPT only when a registry receipt is present, structurally valid, PASS,
  exact-SHA matched, externally artifact-bound, and provider digest-bound.
- DEFER for absent, invalid, stale, mismatched, or incomplete evidence.

The output is intentionally small and reusable by canonical dashboards,
release manifests, Corrigendum packs, and contract-baseline packaging.
"""

from __future__ import annotations

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


def evaluate_registry_receipt(
    receipt_path: str | Path | None,
    *,
    expected_git_sha: str | None,
) -> dict[str, Any]:
    """Return an ACCEPT/DEFER decision for a Wave 9 registry receipt."""
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
    )

    base.update(
        {
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
        }
    )

    if not expected_git_sha:
        base["reason"] = "expected_git_sha_missing"
        return base
    if len(expected_git_sha) != 40:
        base["reason"] = "expected_git_sha_invalid"
        return base
    if not status_pass:
        base["reason"] = "receipt_status_not_pass"
        return base
    if not exact_sha_match:
        base["reason"] = "exact_sha_mismatch"
        return base
    if not external_bound:
        base["reason"] = "external_artifact_binding_missing"
        return base
    if not provider_digest:
        base["reason"] = "provider_digest_missing_or_invalid"
        return base

    base["disposition"] = "ACCEPT"
    base["reason"] = "exact_sha_registry_evidence_verified"
    return base


def build_release_baseline_evidence(
    receipt_path: str | Path | None,
    *,
    expected_git_sha: str | None,
) -> dict[str, Any]:
    """Build a small release/contract-baseline evidence object."""
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
