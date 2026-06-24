from pathlib import Path
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_adr_ocd_bridge.py"

spec = importlib.util.spec_from_file_location("validate_adr_ocd_bridge", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def test_adr_ocd_bridge_artifacts_validate():
    messages = validator.validate_all(
        REPO_ROOT / "glossary" / "GLOSSARY.yaml",
        REPO_ROOT / "federation" / "ADR_OCD" / "bridge_manifest.yaml",
        REPO_ROOT / "federation" / "ADR_OCD" / "taxonomy.yaml",
    )
    assert len(messages) == 3
    assert any("glossary" in message for message in messages)
    assert any("bridge manifest" in message for message in messages)
    assert any("taxonomy" in message for message in messages)


def test_qps_is_preferred_and_rfo_is_legacy_alias():
    glossary = validator.load_yaml(REPO_ROOT / "glossary" / "GLOSSARY.yaml")
    qps_terms = [term for term in glossary["terms"] if term["standard_term"] == "QPS Requirements"]
    assert len(qps_terms) == 1
    qps = qps_terms[0]
    assert "RFO" in qps["aliases"]
    assert "RFO" in qps.get("avoid_when_outward_facing", [])
    assert qps["outward_facing"] is True


def test_manifest_contains_corrigendum_stage_and_traceability_edges():
    manifest = validator.load_yaml(REPO_ROOT / "federation" / "ADR_OCD" / "bridge_manifest.yaml")
    assert "final_corrigendum" in manifest["change_process"]["stages"]
    relations = {edge["relation"] for edge in manifest["traceability_edges"]}
    assert "amended_by" in relations
    assert "incorporated_into" in relations
