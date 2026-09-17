#!/usr/bin/env python3
"""Hosted byte and canonical-extraction proof for the W274 GMI DOCENG source.

This proof is intentionally read-mostly. It verifies the tracked DOCX bytes,
stages an ignored copy under canonical/inputs, runs the repository's native
canonical extractor, and emits a JSON receipt. It does not lock, tag, release,
or grant QPS engineering acceptance.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "addenda" / "QPS_Addendum_II_Master.docx"
STAGED = REPO_ROOT / "canonical" / "inputs" / "QPS_Addendum_II_Master.docx"
MANIFEST = REPO_ROOT / "canonical" / "artefacts" / "extraction_manifest.json"
RECEIPT = REPO_ROOT / "out" / "w274_gmi_source_byte_proof.json"

EXPECTED_SIZE = 5_063_178
EXPECTED_SHA256 = "ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9"
EXPECTED_GIT_BLOB = "d95e6a15e28e0bf9e810e434b79b62e396511aaf"
INDEXED_SOURCE_COMMIT = "193cafd25ea343c01036342400dca4eaa0252536"
QPS_W274_PR = 1445


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob(path: Path) -> str:
    result = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def latest_master_entry() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [
        item
        for item in data.get("extractions", [])
        if item.get("artefact_name") == "master_requirements"
        and item.get("source_file") == STAGED.name
    ]
    if not entries:
        raise RuntimeError("canonical extraction emitted no master_requirements manifest entry")
    return entries[-1]


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    observed_size = SOURCE.stat().st_size
    observed_sha256 = sha256_file(SOURCE)
    observed_blob = git_blob(SOURCE)

    if observed_size != EXPECTED_SIZE:
        raise RuntimeError(f"size mismatch: expected {EXPECTED_SIZE}, got {observed_size}")
    if observed_sha256 != EXPECTED_SHA256:
        raise RuntimeError(
            f"sha256 mismatch: expected {EXPECTED_SHA256}, got {observed_sha256}"
        )
    if observed_blob != EXPECTED_GIT_BLOB:
        raise RuntimeError(
            f"git blob mismatch: expected {EXPECTED_GIT_BLOB}, got {observed_blob}"
        )

    STAGED.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, STAGED)
    if sha256_file(STAGED) != EXPECTED_SHA256:
        raise RuntimeError("staged canonical input differs from tracked source")

    # Reuse the repository's native canonical extraction and verification paths.
    run([sys.executable, "main.py", "--extract-canonical", "--force"])
    run([sys.executable, "scripts/verify_canonical.py"])

    entry = latest_master_entry()
    if entry.get("source_sha256") != EXPECTED_SHA256:
        raise RuntimeError(
            "canonical manifest source_sha256 does not match verified source bytes"
        )

    output_path = REPO_ROOT / str(entry["output_file"])
    if not output_path.is_file():
        raise RuntimeError(f"canonical output missing: {output_path}")
    output_sha256 = sha256_file(output_path)
    if output_sha256 != entry.get("content_sha256"):
        raise RuntimeError("canonical output content SHA differs from manifest receipt")

    artefact = json.loads(output_path.read_text(encoding="utf-8"))
    record_count = int(artefact.get("record_count", 0))
    if record_count <= 0:
        raise RuntimeError("canonical master_requirements extraction is empty")

    receipt = {
        "schema": "qps.gmi_doceng.source_byte_provider_proof/v1",
        "wave": "W274",
        "provider_repository": os.environ.get(
            "GITHUB_REPOSITORY", "GBOGEB/DOCX_RTM_Automation"
        ),
        "provider_head_sha": os.environ.get("GITHUB_SHA"),
        "provider_run_id": os.environ.get("GITHUB_RUN_ID"),
        "qps_child_pr": QPS_W274_PR,
        "source": {
            "path": str(SOURCE.relative_to(REPO_ROOT)),
            "indexed_source_commit": INDEXED_SOURCE_COMMIT,
            "expected_size_bytes": EXPECTED_SIZE,
            "observed_size_bytes": observed_size,
            "expected_sha256": EXPECTED_SHA256,
            "observed_sha256": observed_sha256,
            "expected_git_blob": EXPECTED_GIT_BLOB,
            "observed_git_blob": observed_blob,
            "byte_equivalence": "PASS",
        },
        "canonical_extraction": {
            "staged_input": str(STAGED.relative_to(REPO_ROOT)),
            "manifest_path": str(MANIFEST.relative_to(REPO_ROOT)),
            "artefact_name": entry["artefact_name"],
            "output_file": entry["output_file"],
            "source_sha256": entry["source_sha256"],
            "content_sha256": entry["content_sha256"],
            "observed_output_sha256": output_sha256,
            "record_count": record_count,
            "native_verify_canonical": "PASS",
            "lock_or_tag_performed": False,
        },
        "disposition": "ACCEPT_SOURCE_BYTES_AND_CANONICAL_EXTRACTION_UNLATCHED",
        "withheld": [
            "canonical_lock",
            "git_tag_or_release",
            "replay_roundtrip_equivalence",
            "alexandria_graph_runtime",
            "qps_global_control",
        ],
        "non_compensating_note": (
            "Provider proof establishes source bytes and an unlocked canonical extraction only. "
            "QPS remains sole child acceptance authority."
        ),
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
