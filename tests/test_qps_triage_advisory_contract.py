"""Generic source/proposal boundary and native parser integration regressions."""
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch

from docx import Document

from parser.engine import EnhancedParserEngine
from parser.qps_triage_bridge import QPSTriageBridge


def test_confidence_and_unverified_receipt_cannot_promote_authority():
    bridge = QPSTriageBridge()
    item = bridge._item_from_entry("RTM", {
        "id":"RTM-7", "content":"Control interface shall satisfy the amendment.",
        "confidence_score":0.99, "authority_receipt":{"approved":True},
    })
    assert item.disposition == "NEEDS_REVIEW"
    assert item.evidence_class == "structured"
    assert item.maturity_level < 0.8
    assert item.parser_confidence == 0.99
    assert not item.adr_refs and not item.corrigendum_refs
    assert all(p["status"] == "PROPOSED_UNRESOLVED" for p in item.proposed_refs)


def test_malformed_confidence_and_keyword_refs_stay_advisory():
    bridge = QPSTriageBridge()
    for value in ("bad", float("nan"), float("inf"), True, {}, -100):
        item = bridge._item_from_entry("RTM", {
            "id":"RTM-8", "content":"Operational control workflow shall be reviewed.",
            "confidence_score":value,
        })
        assert item.parser_confidence == 0.0
        assert item.disposition != "ACCEPT"
        assert not item.adr_refs and not item.ocd_refs
        assert all(p["candidate_id"].startswith("PROPOSED-") for p in item.proposed_refs)


def test_provenance_survives_without_mutating_input_metadata():
    bridge = QPSTriageBridge()
    provenance = {"source_sha256":"a" * 64, "part":"word/document.xml", "block_ordinal":7}
    analysis = {
        "parsing_metadata":{"source_role":"REVIEW_MARKUP"},
        "enhanced_rtm_elements":[{"id":"RTM-7", "content":"Valve shall be retained.",
                                  "source_provenance":provenance, "confidence_score":0.9}],
    }
    before = deepcopy(analysis)
    enriched = bridge.enrich_analysis(analysis)
    assert analysis == before
    assert enriched["qps_triage_items"][0]["source_provenance"] == provenance
    assert enriched["parsing_metadata"]["qps_triage_bridge"]["authority_transfer"] is False


def test_native_docx_reaches_existing_reader_and_retains_source_hash(tmp_path):
    path = tmp_path / "generic.docx"
    document = Document()
    document.add_heading("Generic requirements", level=1)
    document.add_paragraph("RTM-7 The system shall retain the source reference.")
    document.save(path)
    parser = EnhancedParserEngine(config_path="configs/qps_triage_parser_config.yaml")
    result = parser.parse_document(str(path))
    assert len(result["enhanced_rtm_elements"]) == 1
    item = result["qps_triage_items"][0]
    assert item["source_id"] == "RTM-7"
    assert item["source_provenance"]["source_sha256"] == sha256(path.read_bytes()).hexdigest()
    assert item["source_provenance"]["part"] == "word/document.xml"
    assert item["source_provenance"]["block_ordinal"] == 2
    assert item["disposition"] != "ACCEPT"


def test_advisory_source_references_remain_in_downstream_exports():
    bridge = QPSTriageBridge()
    analysis = {
        "enhanced_rtm_elements":[{"id":"RTM-7", "content":"Control interface shall be retained.", "confidence_score":0.9}],
        "enhanced_del_elements":[{"id":"DEL-2", "description":"Deliverable is a report.", "confidence_score":0.9}],
    }
    enriched = bridge.enrich_analysis(analysis)
    index = EnhancedParserEngine()._build_qps_triage_downstream_index(enriched)
    assert len(index["rtm_rows"]) == 1 and len(index["dtm_rows"]) == 1
    assert index["rtm_rows"][0]["relation"] == "source_reference_to"
    assert index["dtm_rows"][0]["relation"] == "source_reference_to"
    assert index["proposed_reference_rows"]
    assert not index["adr_rows"]


def test_explicit_empty_analysis_does_not_open_an_unrequested_file():
    result = EnhancedParserEngine().parse_document("does-not-exist.docx", {})
    assert result["enhanced_rtm_elements"] == []


def test_native_parser_hash_binds_the_same_immutable_bytes(tmp_path):
    from parser import direct_docx
    path = tmp_path / "changing.docx"
    original = Document()
    original.add_paragraph("RTM-7 Original source shall remain bound.")
    original.save(path)
    expected_sha = sha256(path.read_bytes()).hexdigest()
    native_document = direct_docx.Document
    def replace_path_before_parse(source):
        replacement = Document()
        replacement.add_paragraph("RTM-999 Replacement shall not inherit the old hash.")
        replacement.save(path)
        return native_document(source)
    with patch.object(direct_docx, "Document", side_effect=replace_path_before_parse):
        result = direct_docx.extract_analysis_data(path)
    assert result["rtm_requirements"][0]["id"] == "RTM-7"
    assert result["rtm_requirements"][0]["source_provenance"]["source_sha256"] == expected_sha
