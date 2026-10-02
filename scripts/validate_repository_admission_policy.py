#!/usr/bin/env python3
"""Validate the repository-side P0-B admission policy fail-closed."""

from __future__ import annotations

import json
import re
from pathlib import Path


class AdmissionPolicyError(RuntimeError):
    pass


REQUIRED = {
    ".github/workflows/release-identity.yml": "release-identity",
    ".github/workflows/python-ci.yml": "test-coverage-lineage",
    ".github/workflows/repository-integrity.yml": "gitlink-integrity",
    ".github/workflows/admission-policy.yml": "admission-policy",
}


def _read(path: Path) -> str:
    if not path.is_file():
        raise AdmissionPolicyError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> None:
    policy_path = root / "configs" / "repository_admission_policy.json"
    policy = json.loads(_read(policy_path))

    if policy.get("repository") != "GBOGEB/DOCX_RTM_Automation":
        raise AdmissionPolicyError("repository mismatch")
    if policy.get("target_branch") != "main":
        raise AdmissionPolicyError("target_branch must be main")

    desired = policy.get("desired_enforcement", {})
    expected = {
        "protected": True,
        "require_pull_request": True,
        "dismiss_stale_reviews": True,
        "require_last_push_approval": True,
        "required_conversation_resolution": True,
        "enforce_admins": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "strict_required_status_checks": True,
    }
    for key, value in expected.items():
        if desired.get(key) is not value:
            raise AdmissionPolicyError(f"desired_enforcement.{key} must be {value!r}")

    approvals = desired.get("required_approving_reviews")
    if not isinstance(approvals, int) or approvals < 1:
        raise AdmissionPolicyError("at least one approving review must be required")

    checks = desired.get("required_checks", [])
    mapped = {item.get("workflow"): item.get("job") for item in checks}
    if mapped != REQUIRED:
        raise AdmissionPolicyError(
            f"required-check map mismatch: expected {REQUIRED!r}, got {mapped!r}"
        )

    for workflow_path, job in REQUIRED.items():
        text = _read(root / workflow_path)
        if not re.search(r"(?m)^\s*pull_request\s*:", text):
            raise AdmissionPolicyError(f"{workflow_path} is not pull_request-triggered")
        if not re.search(rf"(?m)^\s{{2}}{re.escape(job)}\s*:", text):
            raise AdmissionPolicyError(
                f"{workflow_path} does not define required job {job!r}"
            )
        if not re.search(r"(?m)^\s*steps\s*:", text):
            raise AdmissionPolicyError(f"{workflow_path} has no steps block")
        if not re.search(r"(?m)^\s*-\s+(?:name|uses|run)\s*:", text):
            raise AdmissionPolicyError(f"{workflow_path} has no executable step")

    baseline = policy.get("baseline", {})
    if baseline.get("protected") is not False:
        raise AdmissionPolicyError(
            "baseline must preserve the measured unprotected state until owner gate closes"
        )

    owner_gate = policy.get("owner_gate", {})
    if owner_gate.get("state") != "OPEN_CONNECTOR_ADMIN_SCOPE":
        raise AdmissionPolicyError("unexpected owner-gate state")

    workflow_config = _read(root / "configs" / "workflow_config.yaml")
    required_config_fragments = (
        "branch_protection: false",
        "branch_protection_desired: true",
        'admission_policy: "configs/repository_admission_policy.json"',
        'enforcement_state: "owner_gate"',
    )
    for fragment in required_config_fragments:
        if fragment not in workflow_config:
            raise AdmissionPolicyError(
                f"workflow_config.yaml missing truth-state fragment: {fragment}"
            )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate(root)
    print("repository admission policy: PASS (repository-side controls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
