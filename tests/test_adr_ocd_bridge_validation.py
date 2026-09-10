from pathlib import Path
import subprocess
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str):
    with (REPO_ROOT / relative_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_adr_ocd_bridge_validator_cli_passes():
    result = subprocess.run(
        [sys.executable, "scripts/validate_adr_ocd_bridge.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "ADR_OCD bridge validation passed" in result.stdout
    assert "validated QPS triage applicability" in result.stdout


def test_qps_is_preferred_and_rfo_is_legacy_alias():
    glossary = load_yaml("glossary/GLOSSARY.yaml")
    qps_terms = [term for term in glossary["terms"] if term["standard_term"] == "QPS Requirements"]
    assert len(qps_terms) == 1
    qps = qps_terms[0]
    assert "RFO" in qps["aliases"]
    assert "RFO" in qps.get("avoid_when_outward_facing", [])
    assert qps["outward_facing"] is True


def test_manifest_contains_corrigendum_stage_and_traceability_edges():
    manifest = load_yaml("federation/ADR_OCD/bridge_manifest.yaml")
    assert "final_corrigendum" in manifest["change_process"]["stages"]
    relations = {edge["relation"] for edge in manifest["traceability_edges"]}
    assert "amended_by" in relations
    assert "incorporated_into" in relations


def test_taxonomy_contains_qps_adr_ocd_triage_document_roles():
    taxonomy = load_yaml("federation/ADR_OCD/taxonomy.yaml")
    role_terms = {role["standard_term"] for role in taxonomy["document_roles"]}
    assert "QPS Requirements" in role_terms
    assert "Architecture Design Report" in role_terms
    assert "Operational Concept Document" in role_terms
    assert "Triage" in role_terms


def test_taxonomy_contains_triage_extraction_categories():
    taxonomy = load_yaml("federation/ADR_OCD/taxonomy.yaml")
    categories = set(taxonomy["extraction_categories"])
    assert "triage_item" in categories
    assert "triage_disposition" in categories
    assert "maturity_level" in categories
    assert "qps_disposition" in categories


def test_qps_triage_applicability_lanes_and_dispositions():
    applicability = load_yaml("federation/ADR_OCD/qps_triage_applicability.yaml")
    lanes = {lane["lane_id"] for lane in applicability["triage_lanes"]}
    assert "TRIAGE-QPS" in lanes
    assert "TRIAGE-ADR" in lanes
    assert "TRIAGE-OCD" in lanes
    assert "TRIAGE-RTM-DTM" in lanes

    dispositions = {item["disposition"] for item in applicability["triage_dispositions"]}
    assert "ACCEPT" in dispositions
    assert "DEFER" in dispositions
    assert "REJECT" in dispositions
    assert "NEEDS_SOURCE" in dispositions
    assert "NEEDS_IMPLEMENTATION" in dispositions
    assert "NEEDS_REVIEW" in dispositions


def test_qps_triage_applicability_maturity_and_edges():
    applicability = load_yaml("federation/ADR_OCD/qps_triage_applicability.yaml")
    maturity_levels = {str(item["level"]) for item in applicability["maturity_levels"]}
    assert {"0.0", "0.3", "0.6", "0.8", "1.0"}.issubset(maturity_levels)

    edge_relations = {edge["relation"] for edge in applicability["qps_to_triage_edges"]}
    assert "classified_as" in edge_relations
    assert "design_impact_to" in edge_relations
    assert "operational_impact_to" in edge_relations
    assert "traceability_impact_to" in edge_relations
    assert "deliverable_impact_to" in edge_relations
    assert "amendment_impact_to" in edge_relations
