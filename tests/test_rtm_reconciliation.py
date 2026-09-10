import json
from pathlib import Path

import pytest

from scripts.reconcile_source_to_canonical_rtm import load_canonical, reconcile


def test_exact_text_and_unmatched_are_separated(tmp_path: Path):
    canonical_path = tmp_path / "canonical.json"
    canonical_path.write_text(json.dumps({
        "records": [
            {"controlled_id": "RTM-001", "statement": "The QPS shall provide redundant links.", "source_locator": "p1"},
            {"controlled_id": "RTM-002", "statement": "The Contractor shall provide a dossier.", "source_locator": "p2"},
        ]
    }), encoding="utf-8")
    canonical, _ = load_canonical(canonical_path, "TEST")
    extraction = {"rtm_requirements": [
        {"id": "SRC-4.1", "description": "The QPS shall provide redundant links.", "source_clause": "4.1"},
        {"id": "SRC-4.2", "description": "Different wording.", "source_clause": "4.2"},
    ]}
    receipt = reconcile(extraction, canonical)
    assert receipt["counts"]["EXACT_TEXT"] == 1
    assert receipt["counts"]["UNMATCHED"] == 1
    assert receipt["results"][0]["canonical_candidates"] == ["RTM-001"]
    assert receipt["results"][1]["promotion_allowed"] is False


def test_production_rejects_non_722_fixture(tmp_path: Path):
    p = tmp_path / "canonical.json"
    p.write_text(json.dumps({"metadata": {
        "rtm_semantic_sha256": "a" * 64,
        "workbook_sha256": "b" * 64,
    }, "records": [{"controlled_id": "RTM-001", "statement": "x"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="denominator must be 722"):
        load_canonical(p, "PRODUCTION")


def test_source_clause_never_manufactures_canonical_id():
    canonical = [{"id": "RTM-001", "statement": "Canonical statement", "locator": "p1", "norm": "canonical statement"}]
    receipt = reconcile({"rtm_requirements": [{
        "id": "SRC-4.2.1",
        "source_clause": "4.2.1",
        "description": "Not the canonical statement",
    }]}, canonical)
    row = receipt["results"][0]
    assert row["canonical_candidates"] == []
    assert row["promotion_allowed"] is False
