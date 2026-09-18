from __future__ import annotations

from copy import deepcopy

import pytest

from src.qplant_auto.engine import (
    compute_diff,
    empty_project_state,
    enforce_immutable,
    validate_project_state,
)


def complete_requirement(req_id: str = "REQ-001") -> dict:
    return {
        "id": req_id,
        "title": "Example",
        "requirement": "",
        "measurability": "",
        "reference_standards": [],
        "verification": "",
        "validation": "",
        "rationale": "",
        "topic_epic": "",
        "related_requirements": [],
        "parent_stakeholder_ids": [],
        "requirement_type": "",
        "requirement_category": "",
        "source_refs": [],
        "status": "DRAFT",
        "confidence": "",
        "notes": "",
        "field_provenance": [],
        "immutable": False,
        "needs_review": True,
    }


def section(number: str, *, immutable: bool = False, body: str = "") -> dict:
    return {
        "pillar": "RFO",
        "outline_number": number,
        "level": len(number.split(".")),
        "title": "Example",
        "body_text": body,
        "parent_outline": "",
        "requirement_ids": [],
        "source_refs": [],
        "immutable": immutable,
        "status": "DRAFT",
    }


def test_empty_state_is_valid() -> None:
    state = empty_project_state()
    validate_project_state(state)


def test_requirement_empty_fields_are_preserved_and_valid() -> None:
    state = empty_project_state()
    state["requirements"] = [complete_requirement()]
    validate_project_state(state)


def test_outline_limited_to_level_three() -> None:
    state = empty_project_state()
    state["documents"]["RFO"]["sections"] = [section("1.2.3.4")]
    with pytest.raises(ValueError):
        validate_project_state(state)


def test_diff_detects_added_modified_and_unchanged_items() -> None:
    before = empty_project_state()
    before["requirements"] = [complete_requirement("REQ-001")]
    after = deepcopy(before)
    after["requirements"][0]["title"] = "Changed"
    after["requirements"].append(complete_requirement("REQ-002"))

    diff = compute_diff(before, after)

    assert diff["added_ids"] == ["REQ-002"]
    assert diff["modified_ids"] == ["REQ-001"]
    assert diff["superseded_ids"] == []


def test_immutable_section_cannot_change() -> None:
    before = empty_project_state()
    before["documents"]["RFO"]["sections"] = [section("1", immutable=True, body="verbatim")]
    after = deepcopy(before)
    after["documents"]["RFO"]["sections"][0]["body_text"] = "rewritten"

    with pytest.raises(ValueError):
        enforce_immutable(before, after)
