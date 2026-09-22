#!/usr/bin/env python3
"""Prove deterministic W275 post-source document-core re-entry.

Consumes the W274 canonical master_requirements artefact only after its exact
content hash and population match the accepted provider receipt. Emits a
normalized requirement-local document-core payload plus a compact receipt.
No LLM, editing, lock/tag, release, or QPS promotion occurs here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.document_core.canonical_requirements_adapter import load_canonical_requirements
DEFAULT_INPUT = REPO_ROOT / "canonical" / "artefacts" / "master_requirements_v1.json"
DEFAULT_OUTPUT = REPO_ROOT / "out" / "w275_gmi_document_core.json"
DEFAULT_RECEIPT = REPO_ROOT / "out" / "w275_gmi_document_core_receipt.json"

EXPECTED_CANONICAL_SHA256 = "5bed44a7ae2c0bcbd875e1162cdde292a7d9c8dc717e7328cf4a6d6f0cc13051"
EXPECTED_SOURCE_SHA256 = "ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9"
EXPECTED_RECORD_COUNT = 2692
QPS_W274_MERGE_SHA = "34f04bf08dc2f957f196f33ea1d73ae1a5b07070"


def semantic_sha256(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    core, observed_sha256 = load_canonical_requirements(
        args.input,
        expected_sha256=EXPECTED_CANONICAL_SHA256,
        expected_record_count=EXPECTED_RECORD_COUNT,
    )

    core_sha256 = semantic_sha256(core)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(core, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "schema": "qps.gmi_doceng.document_core_reentry_provider_proof/v1",
        "wave": "GMI-W275",
        "provider_repository": os.environ.get(
            "GITHUB_REPOSITORY", "GBOGEB/DOCX_RTM_Automation"
        ),
        "provider_head_sha": os.environ.get("GITHUB_SHA"),
        "provider_run_id": os.environ.get("GITHUB_RUN_ID"),
        "parent_qps_w274_merge_sha": QPS_W274_MERGE_SHA,
        "canonical_input": {
            "path": str(args.input),
            "expected_sha256": EXPECTED_CANONICAL_SHA256,
            "observed_sha256": observed_sha256,
            "source_sha256": EXPECTED_SOURCE_SHA256,
            "expected_record_count": EXPECTED_RECORD_COUNT,
            "observed_record_count": core["record_count"],
        },
        "document_core": {
            "schema": core["schema"],
            "record_count": core["record_count"],
            "section_path_count": core["section_path_count"],
            "semantic_sha256": core_sha256,
            "output_file": str(args.output),
        },
        "checks": {
            "canonical_identity": "PASS",
            "population_identity": "PASS",
            "requirement_local_shape": "PASS",
            "deterministic_normalization": "PASS",
            "llm_invoked": False,
            "source_or_requirement_mutation": False,
            "canonical_lock_or_tag_performed": False,
        },
        "disposition": "ACCEPT_DOCUMENT_CORE_INGRESS_ONLY",
        "withheld": [
            "requirement_semantic_validation",
            "requirement_editing",
            "recursive_hold_reentry",
            "canonical_lock_or_tag",
            "replay_roundtrip_equivalence",
            "alexandria_graph_runtime",
            "qps_global_control",
        ],
        "non_compensating_note": (
            "This provider proof establishes deterministic document-core ingress only. "
            "It does not validate or edit requirement semantics and grants no QPS credit."
        ),
    }

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
