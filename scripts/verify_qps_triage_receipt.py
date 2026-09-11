#!/usr/bin/env python3
"""Verify a Wave 8 QPS triage evidence bundle and governed receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def verify_bundle(bundle: Path) -> list[str]:
    errors: list[str] = []
    evidence_path = bundle / "qps_triage_evidence_manifest.json"
    receipt_path = bundle / "qps_triage_governed_receipt.json"
    sums_path = bundle / "SHA256SUMS"

    for required in (evidence_path, receipt_path, sums_path):
        if not required.is_file():
            errors.append(f"missing required governance artifact: {required.name}")
    if errors:
        return errors

    evidence = load_json(evidence_path)
    receipt = load_json(receipt_path)
    records = evidence.get("artifacts", [])
    if not isinstance(records, list):
        return ["evidence manifest artifacts must be a list"]

    expected_names = {str(record.get("path")) for record in records if isinstance(record, dict)}
    excluded = {evidence_path.name, receipt_path.name, sums_path.name}
    actual_names = {path.name for path in bundle.iterdir() if path.is_file() and path.name not in excluded}
    if expected_names != actual_names:
        errors.append(f"payload parity mismatch: expected={sorted(expected_names)} actual={sorted(actual_names)}")
    if evidence.get("artifact_count") != len(records):
        errors.append("evidence artifact_count does not match record count")

    for record in records:
        if not isinstance(record, dict):
            errors.append("invalid non-object artifact record")
            continue
        path = bundle / str(record.get("path"))
        if not path.is_file():
            errors.append(f"missing payload artifact: {path.name}")
            continue
        if path.stat().st_size != record.get("size_bytes"):
            errors.append(f"size mismatch: {path.name}")
        if sha256(path) != record.get("sha256"):
            errors.append(f"SHA256 mismatch: {path.name}")

    manifest_ref = receipt.get("pipeline_manifest", {})
    evidence_ref = receipt.get("evidence_manifest", {})
    manifest_path = bundle / str(manifest_ref.get("path", ""))
    if not manifest_path.is_file() or sha256(manifest_path) != manifest_ref.get("sha256"):
        errors.append("pipeline manifest receipt hash mismatch")
    if sha256(evidence_path) != evidence_ref.get("sha256"):
        errors.append("evidence manifest receipt hash mismatch")

    sum_lines = [line for line in sums_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sum_map: dict[str, str] = {}
    for line in sum_lines:
        try:
            digest, name = line.split("  ", 1)
        except ValueError:
            errors.append(f"invalid SHA256SUMS line: {line}")
            continue
        sum_map[name] = digest
    expected_sum_names = {path.name for path in bundle.iterdir() if path.is_file() and path.name != sums_path.name}
    if set(sum_map) != expected_sum_names:
        errors.append("SHA256SUMS file parity mismatch")
    for name, digest in sum_map.items():
        path = bundle / name
        if path.is_file() and sha256(path) != digest:
            errors.append(f"SHA256SUMS mismatch: {name}")

    if receipt.get("status") != "PASS":
        errors.append("governed receipt status is not PASS")
    identity = receipt.get("identity", {})
    if not identity.get("git_sha") or identity.get("git_sha") == "UNKNOWN":
        errors.append("receipt is not bound to an exact Git SHA")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify QPS triage Wave 8 governed evidence bundle.")
    parser.add_argument("bundle", help="Generated Wave 8 artifact directory")
    args = parser.parse_args()
    errors = verify_bundle(Path(args.bundle))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: QPS triage governed receipt, hashes, and artifact parity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
