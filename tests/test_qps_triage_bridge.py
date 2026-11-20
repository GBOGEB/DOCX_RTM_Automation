from pathlib import Path
import csv
import json
import subprocess
import sys

import pytest

from parser.engine import EnhancedParserEngine
from parser.qps_triage_bridge import QPSTriageBridge
from src.dashboard.canonical_dashboard import collect_stats
from src.dashboard.qps_triage_dashboard import QPSTriageDashboardGenerator

REPO_ROOT = Path(__file__).resolve().parents[1]

ADVISORY_RELATIONS = {"proposed_mapping_to", "source_reference_to"}
ADVISORY_SIGNATURES = {
    ("proposed_mapping_to", "Triage Item", "Proposed ADR candidate"),
    ("proposed_mapping_to", "Triage Item", "Proposed OCD candidate"),
    ("proposed_mapping_to", "Triage Item", "Proposed Corrigendum candidate"),
    ("source_reference_to", "Triage Item", "Parser RTM source"),
    ("source_reference_to", "Triage Item", "Parser DTM source"),
}


def advisory_contracts(bridge):
    """Model consumers of each existing typed policy list independently."""
    for declarations in (
        bridge.taxonomy["traceability_relations"],
        bridge.applicability["qps_to_triage_edges"],
    ):
        rows = [row for row in declarations if row["relation"] in ADVISORY_RELATIONS]
        contract = {(row["relation"], row["from"], row["to"]): row for row in rows}
        assert len(contract) == len(rows), "duplicate typed advisory declaration"
        yield contract


def consume_advisory_row(row, contract):
    """A typed contract consumer never treats relation-name equality as approval."""
    signature = (row["relation"], row["from_type"], row["to_type"])
    declaration = contract.get(signature)
    if declaration is None:
        raise ValueError("undeclared advisory edge signature")
    if declaration.get("advisory") is not True or declaration.get("authority_transfer") is not False:
        raise ValueError("advisory edge cannot transfer authority")
    return dict(row)


def test_advisory_relations_have_five_explicit_typed_policy_signatures():
    bridge = QPSTriageBridge()
    for contract in advisory_contracts(bridge):
        assert set(contract) == ADVISORY_SIGNATURES
        assert all(row["advisory"] is True for row in contract.values())
        assert all(row["authority_transfer"] is False for row in contract.values())


def test_actual_advisory_exports_survive_both_policy_consumers():
    bridge = QPSTriageBridge()
    enriched = bridge.enrich_analysis(sample_analysis())
    rows = [row for row in enriched["qps_triage_traceability_rows"]
            if row["relation"] in ADVISORY_RELATIONS]
    assert {(row["relation"], row["from_type"], row["to_type"]) for row in rows} == ADVISORY_SIGNATURES
    for contract in advisory_contracts(bridge):
        assert [consume_advisory_row(row, contract) for row in rows] == rows
    assert enriched["parsing_metadata"]["qps_triage_bridge"]["authority_transfer"] is False
    assert all(item["disposition"] != "ACCEPT" and item["maturity_level"] < 0.8
               for item in enriched["qps_triage_items"])


@pytest.mark.parametrize("relation,from_type,to_type", [
    ("unknown_relation", "Triage Item", "Parser RTM source"),
    ("proposed_mapping_to", "QPS Requirement", "Proposed ADR candidate"),
    ("proposed_mapping_to", "Triage Item", "ADR Design Decision"),
    ("proposed_mapping_to", "Triage Item", "Any candidate"),
    ("source_reference_to", "Triage Item", "RTM Row"),
    ("source_reference_to", "Triage Item", "DTM Row"),
])
def test_policy_consumers_reject_untyped_or_controlled_target_substitutions(relation, from_type, to_type):
    row = {"relation": relation, "from_type": from_type, "to_type": to_type}
    for contract in advisory_contracts(QPSTriageBridge()):
        with pytest.raises(ValueError, match="undeclared advisory"):
            consume_advisory_row(row, contract)


def sample_analysis():
    return {
        "parsing_metadata": {"document_path": "sample-qps.docx"},
        "enhanced_rtm_elements": [
            {
                "id": "QPS-REQ-001",
                "type": "RTM",
                "content": "The QPS Requirements shall define an architecture decision and Corrigendum impact for the fixed price contract.",
                "requirement_text": "The QPS Requirements shall define an architecture decision and Corrigendum impact for the fixed price contract.",
                "confidence_score": 0.86,
            }
        ],
        "enhanced_otc_elements": [
            {
                "id": "OCD-OTC-001",
                "type": "OTC",
                "content": "Operational scenario workflow shall verify training and maintenance response.",
                "objective": "Operational scenario workflow shall verify training and maintenance response.",
                "confidence_score": 0.72,
            }
        ],
        "enhanced_del_elements": [
            {
                "id": "DTM-DEL-001",
                "type": "DEL",
                "content": "Deliverable traceability evidence package is missing source confirmation.",
                "description": "Deliverable traceability evidence package is missing source confirmation.",
                "confidence_score": 0.35,
            }
        ],
    }


def raw_parser_input():
    return {
        "sections": [],
        "rtm_requirements": [
            {
                "id": "QPS-REQ-001",
                "description": "The QPS Requirements shall define an architecture decision and Corrigendum impact for the fixed price contract.",
                "priority": "High",
                "verification_method": "Review",
                "acceptance_criteria": "Traceability row exists",
                "source_section": "1.1 - QPS",
            }
        ],
        "otc_elements": [
            {
                "id": "OCD-OTC-001",
                "name": "Operational scenario",
                "objective": "Operational scenario workflow shall verify training and maintenance response.",
                "preconditions": "QPS baseline exists",
                "test_steps": ["Review scenario"],
                "expected_results": "Scenario is traceable",
                "linked_requirements": ["QPS-REQ-001"],
            }
        ],
        "del_deliverables": [
            {
                "id": "DTM-DEL-001",
                "name": "Traceability package",
                "description": "Deliverable traceability evidence package is missing source confirmation.",
                "type": "DTM",
                "dependencies": ["QPS-REQ-001"],
            }
        ],
    }


def write_fixture_dashboard(tmp_path: Path) -> dict[str, str]:
    parser = EnhancedParserEngine(config_path="configs/qps_triage_parser_config.yaml")
    parser.parse_document("sample-qps.docx", raw_parser_input())
    parser.export_enhanced_analysis(str(tmp_path))
    return QPSTriageDashboardGenerator(tmp_path).write_outputs(tmp_path)


def test_bridge_emits_triage_items_and_traceability_rows():
    bridge = QPSTriageBridge()
    enriched = bridge.enrich_analysis(sample_analysis())

    items = enriched["qps_triage_items"]
    rows = enriched["qps_triage_traceability_rows"]

    assert len(items) == 3
    assert any(item["primary_lane"] == "TRIAGE-QPS" for item in items)
    assert any(item["primary_lane"] == "TRIAGE-OCD" for item in items)
    assert any(item["primary_lane"] == "TRIAGE-RTM-DTM" for item in items)
    assert any(item["disposition"] == "NEEDS_REVIEW" for item in items)
    assert not any(item["disposition"] == "ACCEPT" for item in items)
    assert any(item["disposition"] == "NEEDS_SOURCE" for item in items)
    assert any(row["relation"] == "classified_as" for row in rows)
    assert any(row["relation"] == "proposed_mapping_to" for row in rows)
    assert any(row["relation"] == "source_reference_to" for row in rows)


def test_enhanced_parser_engine_leaves_qps_triage_disabled_by_default():
    parser = EnhancedParserEngine()
    result = parser.parse_document("sample-qps.docx", raw_parser_input())
    assert "qps_triage_items" not in result
    assert result["parsing_metadata"]["qps_triage_bridge"]["enabled"] is False


def test_enhanced_parser_engine_enriches_when_config_flag_enabled():
    parser = EnhancedParserEngine(config_path="configs/qps_triage_parser_config.yaml")
    result = parser.parse_document("sample-qps.docx", raw_parser_input())
    assert "qps_triage_items" in result
    assert "qps_triage_traceability_rows" in result
    assert len(result["qps_triage_items"]) == 3
    assert result["parsing_metadata"]["qps_triage_bridge"]["triage_item_count"] == 3
    assert any(row["relation"] == "classified_as" for row in result["qps_triage_traceability_rows"])


def test_engine_export_persists_qps_triage_outputs(tmp_path):
    parser = EnhancedParserEngine(config_path="configs/qps_triage_parser_config.yaml")
    parser.parse_document("sample-qps.docx", raw_parser_input())
    parser.export_enhanced_analysis(str(tmp_path))

    expected_files = {
        "enhanced_analysis.json",
        "enhanced_rtm_elements.json",
        "enhanced_otc_elements.json",
        "enhanced_del_elements.json",
        "relationship_mapping.json",
        "recursive_mapping.json",
        "parsing_statistics.json",
        "qps_triage_items.json",
        "qps_triage_traceability_rows.json",
        "qps_triage_traceability_rows.csv",
        "qps_triage_downstream_index.json",
        "qps_triage_rtm_rows.csv",
        "qps_triage_dtm_rows.csv",
        "export_manifest.json",
    }
    assert expected_files.issubset({path.name for path in tmp_path.iterdir()})

    manifest = json.loads((tmp_path / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["qps_triage_enabled"] is True
    assert manifest["triage_item_count"] == 3
    assert manifest["traceability_row_count"] > 0

    downstream_index = json.loads((tmp_path / "qps_triage_downstream_index.json").read_text(encoding="utf-8"))
    assert downstream_index["rtm_rows"]
    assert downstream_index["dtm_rows"]

    with (tmp_path / "qps_triage_traceability_rows.csv").open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {"row_id", "triage_id", "relation", "evidence_class"}.issubset(rows[0].keys())


def test_parser_to_dashboard_e2e_generates_report_artifacts(tmp_path):
    outputs = write_fixture_dashboard(tmp_path)

    assert Path(outputs["json"]).exists()
    assert Path(outputs["markdown"]).exists()
    assert Path(outputs["html"]).exists()

    dashboard = json.loads(Path(outputs["json"]).read_text(encoding="utf-8"))
    assert dashboard["summary"]["triage_item_count"] == 3
    assert dashboard["summary"]["rtm_row_count"] > 0
    assert dashboard["summary"]["dtm_row_count"] > 0
    assert dashboard["counts"]["by_relation"]["classified_as"] >= 3
    assert dashboard["rtm_rows"]
    assert dashboard["dtm_rows"]

    markdown = Path(outputs["markdown"]).read_text(encoding="utf-8")
    html = Path(outputs["html"]).read_text(encoding="utf-8")
    assert "# QPS Triage Dashboard" in markdown
    assert "RTM rows exported" in markdown
    assert "DTM rows exported" in markdown
    assert "QPS Triage Dashboard" in html
    assert "RTM rows exported" in html
    assert "DTM rows exported" in html


def test_canonical_dashboard_indexes_qps_triage_dashboard_json(tmp_path):
    outputs = write_fixture_dashboard(tmp_path)
    stats = collect_stats(outputs["json"])

    qps = stats["qps_triage_dashboard"]
    assert qps["present"] is True
    assert qps["triage_item_count"] == 3
    assert qps["rtm_row_count"] > 0
    assert qps["dtm_row_count"] > 0
    assert qps["by_relation"]["classified_as"] >= 3


def test_export_cli_writes_json_and_csv(tmp_path):
    input_path = tmp_path / "analysis.json"
    output_json = tmp_path / "qps_triage_enriched_analysis.json"
    output_csv = tmp_path / "qps_triage_traceability_rows.csv"
    input_path.write_text(json.dumps(sample_analysis()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_qps_triage_traceability.py",
            "--input",
            str(input_path),
            "--output-json",
            str(output_json),
            "--output-csv",
            str(output_csv),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    enriched = json.loads(output_json.read_text(encoding="utf-8"))
    assert len(enriched["qps_triage_items"]) == 3
    with output_csv.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {"row_id", "triage_id", "relation", "evidence_class"}.issubset(rows[0].keys())
