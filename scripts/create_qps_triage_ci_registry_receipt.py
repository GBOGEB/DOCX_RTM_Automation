#!/usr/bin/env python3
"""Bind a GitHub Actions artifact object back to the governed QPS receipt.

Wave 8 governs files inside the uploaded bundle. Wave 9 records the external
GitHub artifact identity returned by actions/upload-artifact@v4 so a consumer
can prove which CI artifact object carried that exact-SHA evidence bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_registry_receipt(
    bundle_dir: str | Path,
    *,
    artifact_id: str,
    artifact_url: str,
    artifact_digest: str,
    artifact_name: str,
) -> dict[str, Any]:
    bundle = Path(bundle_dir)
    governed_path = bundle / "qps_triage_governed_receipt.json"
    sums_path = bundle / "SHA256SUMS"
    governed = _load_json(governed_path)

    if not artifact_id or not artifact_url:
        raise ValueError("Artifact id and URL are required")
    if not artifact_digest.startswith("sha256:") or len(artifact_digest) != 71:
        raise ValueError("Artifact digest must be a sha256:<64-hex> value")

    identity = governed.get("identity", {})
    git_sha = str(identity.get("git_sha", ""))
    run_id = str(identity.get("run_id", ""))
    if len(git_sha) != 40:
        raise ValueError("Governed receipt is not bound to a 40-character Git SHA")
    if run_id in {"", "LOCAL"}:
        raise ValueError("Governed receipt is not bound to a CI workflow run")

    return {
        "registry_receipt_id": f"QPS-TRIAGE-W9-{git_sha[:12]}",
        "registry_receipt_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "identity": identity,
        "source_governed_receipt": {
            "path": governed_path.name,
            "sha256": _sha256(governed_path),
            "receipt_id": governed.get("receipt_id"),
        },
        "source_sha256sums": {
            "path": sums_path.name,
            "sha256": _sha256(sums_path),
        },
        "github_artifact": {
            "artifact_id": str(artifact_id),
            "artifact_name": artifact_name,
            "artifact_url": artifact_url,
            "artifact_digest": artifact_digest,
            "digest_algorithm": "SHA256",
        },
        "governance": {
            "exact_sha_bound": True,
            "workflow_run_bound": True,
            "external_artifact_object_bound": True,
            "provider_digest_present": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Wave 9 GitHub artifact registry receipt")
    parser.add_argument("bundle_dir")
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--artifact-url", required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = build_registry_receipt(
        args.bundle_dir,
        artifact_id=args.artifact_id,
        artifact_url=args.artifact_url,
        artifact_digest=args.artifact_digest,
        artifact_name=args.artifact_name,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
