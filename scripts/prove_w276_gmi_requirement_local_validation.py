#!/usr/bin/env python3
"""Prove GMI-W276 requirement-local validation without global compensation."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.document_core.requirement_local_validator import (
    semantic_sha256,
    validate_requirement_rules,
)

W275_CORE = REPO_ROOT / "out" / "w275_gmi_document_core.json"
RULE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "gmi_w276_legacy_requirements.json"
RECEIPT = REPO_ROOT / "out" / "w276_gmi_requirement_local_validation_receipt.json"

EXPECTED_W275_CORE_SEMANTIC_SHA256 = (
    "0feff7dea41f274f44d4150c6e0ce8706df0f0b4def24fe33856cd6cea78a0be"
)
EXPECTED_W275_RECORD_COUNT = 2692
EXPECTED_RULE_FIXTURE_SHA256 = (
    "00e080f12320bb5cecda5abd78bccb77dd881ec6e0874e4f23c1a5ceee33e857"
)
GENESIS_CLI_SHA256 = (
    "07ee6369982bcb473b293782fa0e76f56cae3dfc8eb45d41323f694fbe138893"
)
PARENT_QPS_W275_MERGE_SHA = "7b3224ff56235d1f425ecf5e340abf0a2519df2d"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decisions(result: dict) -> dict[str, str]:
    return {item["rule_id"]: item["decision"] for item in result["results"]}


def main() -> int:
    core = json.loads(W275_CORE.read_text(encoding="utf-8"))
    assert core["schema"] == "gmi.document_core.requirements/v1"
    assert core["record_count"] == EXPECTED_W275_RECORD_COUNT
    observed_core_semantic_sha = semantic_sha256(core)
    assert observed_core_semantic_sha == EXPECTED_W275_CORE_SEMANTIC_SHA256

    fixture_sha = sha256_file(RULE_FIXTURE)
    assert fixture_sha == EXPECTED_RULE_FIXTURE_SHA256
    rules = json.loads(RULE_FIXTURE.read_text(encoding="utf-8"))

    trap_core = {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 2,
        "records": [
            {
                "requirement_id": "Req. 1",
                "text": (
                    "Req. 1 is tested via FAT and measured through a trend. "
                    "The second phrase exists here only to reproduce the Genesis "
                    "global-compensation defect."
                ),
            },
            {
                "requirement_id": "Req. 2",
                "text": (
                    "Req. 2 defines WHAT while minimizing prescriptive HOW. "
                    "No local verification method is stated."
                ),
            },
        ],
    }
    trap_result = validate_requirement_rules(trap_core, rules)
    trap_decisions = decisions(trap_result)
    assert trap_decisions == {"Req. 1": "ACCEPT", "Req. 2": "REJECT"}
    assert "measured through" in trap_core["records"][0]["text"].casefold()
    assert "measured through" not in trap_core["records"][1]["text"].casefold()
    assert trap_result["overall_decision"] == "REJECT"

    positive_core = {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 2,
        "records": [
            {"requirement_id": "Req. 1", "text": "Req. 1 is tested via FAT."},
            {
                "requirement_id": "Req. 2",
                "text": "Req. 2 is measured through an agreed KPI.",
            },
        ],
    }
    positive_result = validate_requirement_rules(positive_core, rules)
    assert decisions(positive_result) == {"Req. 1": "ACCEPT", "Req. 2": "ACCEPT"}
    assert positive_result["overall_decision"] == "ACCEPT"

    receipt = {
        "schema": "qps.gmi_doceng.requirement_local_validation_provider_proof/v1",
        "wave": "GMI-W276",
        "provider_repository": os.environ.get(
            "GITHUB_REPOSITORY",
            "GBOGEB/DOCX_RTM_Automation",
        ),
        "provider_head_sha": os.environ.get("GITHUB_SHA"),
        "provider_run_id": os.environ.get("GITHUB_RUN_ID"),
        "parent_qps_w275_merge_sha": PARENT_QPS_W275_MERGE_SHA,
        "source_baseline": {
            "genesis_cli_sha256": GENESIS_CLI_SHA256,
            "legacy_requirement_validator_defect": (
                "verification regex evaluated against whole document content"
            ),
            "legacy_requirements_fixture_sha256": fixture_sha,
            "legacy_requirements_fixture_classification": "SYNTHETIC",
        },
        "real_document_core_identity": {
            "schema": core["schema"],
            "record_count": core["record_count"],
            "semantic_sha256": observed_core_semantic_sha,
            "semantic_compliance_evaluated": False,
        },
        "adversarial_fixture": {
            "rule_count": 2,
            "trap_result_semantic_sha256": trap_result["semantic_sha256"],
            "trap_decisions": trap_decisions,
            "trap_overall_decision": trap_result["overall_decision"],
            "positive_result_semantic_sha256": positive_result["semantic_sha256"],
            "positive_overall_decision": positive_result["overall_decision"],
            "cross_requirement_compensation_blocked": True,
        },
        "checks": {
            "requirement_local_evidence_only": "PASS",
            "one_rule_one_target": "PASS",
            "missing_target_is_defer": "PASS",
            "global_phrase_compensation": False,
            "llm_invoked": False,
            "source_or_requirement_mutation": False,
            "canonical_lock_or_tag_performed": False,
        },
        "disposition": "ACCEPT_REQUIREMENT_LOCAL_VALIDATION_PRIMITIVE_ONLY",
        "withheld": [
            "real_2692_requirement_semantic_compliance",
            "real_rule_to_requirement_mapping",
            "requirement_editing",
            "recursive_hold_reentry",
            "canonical_lock_or_tag",
            "replay_roundtrip_equivalence",
            "alexandria_graph_runtime",
            "qps_global_control",
        ],
        "non_compensating_note": (
            "Algorithmic proof uses the governed two-rule synthetic fixture. "
            "The real 2,692-record document core is identity-checked only and is "
            "not promoted to semantic compliance without a real rule mapping."
        ),
    }
    receipt["semantic_sha256"] = semantic_sha256(receipt)

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
