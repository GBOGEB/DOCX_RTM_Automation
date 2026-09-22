import copy
import json
from pathlib import Path

import pytest

from src.document_core.requirement_local_validator import (
    RequirementLocalValidationError,
    validate_requirement_rules,
)


FIXTURE = Path("tests/fixtures/gmi_w276_legacy_requirements.json")


def _rules() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _core(req1_text: str, req2_text: str) -> dict:
    return {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 2,
        "records": [
            {"requirement_id": "Req. 1", "text": req1_text},
            {"requirement_id": "Req. 2", "text": req2_text},
        ],
    }


def _decisions(result: dict) -> dict[str, str]:
    return {item["rule_id"]: item["decision"] for item in result["results"]}


def test_blocks_cross_requirement_compensation() -> None:
    core = _core(
        "Req. 1 is tested via FAT and measured through a trend.",
        "Req. 2 defines WHAT while avoiding prescriptive HOW.",
    )
    result = validate_requirement_rules(core, _rules())
    assert "measured through" in core["records"][0]["text"]
    assert "measured through" not in core["records"][1]["text"]
    assert _decisions(result) == {"Req. 1": "ACCEPT", "Req. 2": "REJECT"}
    assert result["overall_decision"] == "REJECT"
    assert result["non_compensating"] is True


def test_accepts_only_when_each_phrase_is_local() -> None:
    core = _core(
        "Req. 1 is tested via FAT.",
        "Req. 2 is measured through an agreed KPI.",
    )
    result = validate_requirement_rules(core, _rules())
    assert _decisions(result) == {"Req. 1": "ACCEPT", "Req. 2": "ACCEPT"}
    assert result["overall_decision"] == "ACCEPT"


def test_missing_target_defers_without_parent_compensation() -> None:
    core = {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 1,
        "records": [{"requirement_id": "Req. 1", "text": "tested via FAT"}],
    }
    result = validate_requirement_rules(core, _rules())
    assert _decisions(result)["Req. 2"] == "DEFER"
    assert result["overall_decision"] == "DEFER"


def test_duplicate_rule_target_fails_closed() -> None:
    rules = _rules()
    rules["Req. 2"]["target_requirement_id"] = "Req. 1"
    with pytest.raises(
        RequirementLocalValidationError,
        match="duplicate target_requirement_id",
    ):
        validate_requirement_rules(
            _core("tested via FAT", "measured through KPI"),
            rules,
        )


def test_missing_verification_method_fails_closed() -> None:
    rules = copy.deepcopy(_rules())
    del rules["Req. 2"]["verification_method"]
    with pytest.raises(
        RequirementLocalValidationError,
        match="verification_method",
    ):
        validate_requirement_rules(
            _core("tested via FAT", "measured through KPI"),
            rules,
        )


def test_duplicate_document_core_id_fails_closed() -> None:
    core = {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 2,
        "records": [
            {"requirement_id": "Req. 1", "text": "tested via FAT"},
            {"requirement_id": "Req. 1", "text": "another record"},
        ],
    }
    with pytest.raises(
        RequirementLocalValidationError,
        match="duplicate document_core requirement_id",
    ):
        validate_requirement_rules(core, _rules())


def test_validation_is_deterministic() -> None:
    core = _core("tested via FAT", "measured through KPI")
    first = validate_requirement_rules(core, _rules())
    second = validate_requirement_rules(core, _rules())
    assert first == second
    assert len(first["semantic_sha256"]) == 64
