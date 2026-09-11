from pathlib import Path
import csv
import json
import subprocess
import sys

from parser.engine import EnhancedParserEngine
from parser.qps_triage_bridge import QPSTriageBridge

REPO_ROOT = Path(__file__).resolve().parents[1]


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


def test_bridge_emits_triage_items_and_traceability_rows():
    bridge = QPSTriageBridge()
    enriched = bridge.enrich_analysis(sample_analysis())

    items = enriched["qps_triage_items"]
    rows = enriched["qps_triage_traceability_rows"]

    assert len(items) == 3
    assert any(item["primary_lane"] == "TRIAGE-QPS" for item in items)
    assert any(item["primary_lane"] == "TRIAGE-OCD" for item in items)
    assert any(item["primary_lane"] == "TRIAGE-RTM-DTM" for item in items)
    assert any(item["disposition"] == "ACCEPT" for item in items)
    assert any(item["disposition"] == "NEEDS_SOURCE" for item in items)
    assert any(row["relation"] == "classified_as" for row in rows)
    assert any(row["relation"] == "design_impact_to" for row in rows)
    assert any(row["relation"] == "amendment_impact_to" for row in rows)


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
