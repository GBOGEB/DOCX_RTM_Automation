import json
from pathlib import Path

import pytest

from src.document_core.canonical_requirements_adapter import (
    CanonicalRequirementsError,
    adapt_canonical_requirements,
    load_canonical_requirements,
    sha256_file,
)


def _payload() -> dict:
    return {
        "type": "master_requirements",
        "source": "Master.docx",
        "record_count": 2,
        "requirements": {
            "REQ-P20": {
                "req_id": "REQ-P20",
                "listnum": "",
                "listnum_heading": "Section B",
                "section_path": ["B"],
                "paragraph_text": "Second requirement.",
                "style": "Normal",
                "page_approx": 20,
            },
            "REQ-P10": {
                "req_id": "REQ-P10",
                "listnum": "",
                "listnum_heading": "Section A",
                "section_path": ["A"],
                "paragraph_text": "First requirement.",
                "style": "Normal",
                "page_approx": 10,
            },
        },
    }


def test_adapts_requirement_local_records_deterministically() -> None:
    core = adapt_canonical_requirements(_payload())
    assert core["schema"] == "gmi.document_core.requirements/v1"
    assert core["record_count"] == 2
    assert core["section_path_count"] == 2
    assert [r["requirement_id"] for r in core["records"]] == ["REQ-P10", "REQ-P20"]


def test_rejects_declared_count_mismatch() -> None:
    payload = _payload()
    payload["record_count"] = 3
    with pytest.raises(CanonicalRequirementsError, match="record_count mismatch"):
        adapt_canonical_requirements(payload)


def test_rejects_key_to_req_id_mismatch() -> None:
    payload = _payload()
    payload["requirements"]["REQ-P10"]["req_id"] = "REQ-WRONG"
    with pytest.raises(CanonicalRequirementsError, match="req_id mismatch"):
        adapt_canonical_requirements(payload)


def test_rejects_blank_requirement_text() -> None:
    payload = _payload()
    payload["requirements"]["REQ-P10"]["paragraph_text"] = "   "
    with pytest.raises(CanonicalRequirementsError, match="missing paragraph_text"):
        adapt_canonical_requirements(payload)


def test_load_rejects_wrong_artifact_identity(tmp_path: Path) -> None:
    path = tmp_path / "master_requirements.json"
    path.write_text(json.dumps(_payload()), encoding="utf-8")
    assert len(sha256_file(path)) == 64
    with pytest.raises(CanonicalRequirementsError, match="SHA-256 mismatch"):
        load_canonical_requirements(path, expected_sha256="0" * 64)


def test_load_accepts_exact_identity_and_population(tmp_path: Path) -> None:
    path = tmp_path / "master_requirements.json"
    path.write_text(json.dumps(_payload()), encoding="utf-8")
    expected = sha256_file(path)
    core, observed = load_canonical_requirements(
        path,
        expected_sha256=expected,
        expected_record_count=2,
    )
    assert observed == expected
    assert core["record_count"] == 2
