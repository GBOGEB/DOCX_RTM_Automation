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


def test_taxonomy_contains_qps_adr_ocd_document_roles():
    taxonomy = load_yaml("federation/ADR_OCD/taxonomy.yaml")
    role_terms = {role["standard_term"] for role in taxonomy["document_roles"]}
    assert "QPS Requirements" in role_terms
    assert "Architecture Design Report" in role_terms
    assert "Operational Concept Document" in role_terms
