import json
import math
from pathlib import Path

from src.dashboard.qps_reliability_bridge import build_bridge, evaluate_item


SHA = "a" * 40
FIXTURES = Path(__file__).parent / "fixtures"


def source_item(**overrides):
    item = {
        "component": "HP_COMPRESSOR",
        "triage_item_id": "T6.2",
        "triage_lane": "TRIAGE-QPS",
        "maturity_level": 0.8,
        "origin": "SOURCE_BOUND",
        "triage_disposition": "ACCEPT",
        "source_git_sha": SHA,
        "source_ref": "QPS reliability evidence",
        "reference_period": "calendar_year",
        "mtbf_years": 5.0,
        "architecture": {
            "redundancy_basis_known": True,
            "common_cause_basis_known": True,
            "degraded_state_known": True,
            "recovery_hours": 4.0,
        },
    }
    item.update(overrides)
    return item


def test_active_source_bound_item_derives_units_and_poisson():
    result = evaluate_item(source_item(), campaign_days=90)
    assert result["model_readiness"]["disposition"] == "ACTIVE"
    assert result["model_scope"] == "system"
    assert result["provenance"]["triage_lane"] == "TRIAGE-QPS"
    assert result["provenance"]["maturity_level"] == 0.8
    assert math.isclose(result["model"]["mtbf_hours"], 43800.0)
    assert math.isclose(result["model"]["lambda_per_year"], 0.2)
    assert math.isclose(result["model"]["p0"], math.exp(-0.2 * 90 / 365))
    assert math.isclose(result["model"]["p_ge_1"], 1 - result["model"]["p0"])
    assert len(result["model"]["poisson_counts"]) == 9


def test_source_bound_defer_is_scenario_only():
    result = evaluate_item(source_item(triage_disposition="DEFER"))
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"
    assert result["model"] is not None


def test_source_bound_needs_source_is_scenario_only():
    result = evaluate_item(source_item(triage_disposition="NEEDS_SOURCE"))
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"
    assert result["provenance"]["triage_disposition"] == "NEEDS_SOURCE"


def test_source_bound_reject_is_excluded():
    result = evaluate_item(source_item(triage_disposition="REJECT"))
    assert result["model_readiness"]["disposition"] == "EXCLUDED"


def test_missing_triage_context_prevents_active_source_model():
    result = evaluate_item(source_item(triage_lane=None, maturity_level=None))
    assert result["model_readiness"]["checks"]["triage_context"] is False
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"


def test_missing_architecture_limits_model_to_component_only():
    result = evaluate_item(source_item(architecture={}))
    assert result["model_scope"] == "component_only"
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"


def test_inconsistent_mtbf_and_lambda_is_excluded():
    result = evaluate_item(source_item(mtbf_years=5.0, lambda_per_year=1.0))
    assert result["model_readiness"]["disposition"] == "EXCLUDED"
    assert "reliability_values_inconsistent" in result["errors"]


def test_scenario_never_promotes_to_active_but_retains_provenance():
    result = evaluate_item(source_item(
        component="QPLANT_CLASS_A_SYSTEM",
        origin="SCENARIO",
        triage_disposition="DEFER",
        source_git_sha=None,
        triage_item_id=None,
        triage_lane=None,
        maturity_level=None,
        mtbf_years=4.8,
    ))
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"
    assert result["provenance"]["origin"] == "SCENARIO"
    assert result["provenance"]["source_sha_valid"] is False


def test_backward_compatible_evidence_disposition_alias_is_preserved():
    item = source_item()
    item.pop("triage_disposition")
    item["evidence_disposition"] = "DEFER"
    result = evaluate_item(item)
    assert result["provenance"]["triage_disposition"] == "DEFER"
    assert result["provenance"]["evidence_disposition"] == "DEFER"
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"


def test_bridge_summary_counts_pilot_records():
    payload = {"items": [
        source_item(),
        source_item(component="PVPS", triage_disposition="DEFER"),
        source_item(component="UNKNOWN_COMPONENT"),
    ]}
    result = build_bridge(payload)
    assert result["summary"] == {
        "item_count": 3,
        "active_count": 1,
        "scenario_only_count": 1,
        "excluded_count": 1,
    }
    assert result["schema_version"] == "1.1.0"


def test_real_alat_hp_atom_is_exact_source_bound_but_fail_closed():
    payload = json.loads((FIXTURES / "qps_reliability_alat_hp_bound.json").read_text(encoding="utf-8"))
    result = build_bridge(payload, campaign_days=90)
    atom = result["items"][0]

    assert atom["component"] == "HP_COMPRESSOR"
    assert atom["provenance"]["source_sha_valid"] is True
    assert atom["provenance"]["triage_disposition"] == "DEFER"
    assert atom["model_readiness"]["disposition"] == "SCENARIO_ONLY"
    assert atom["model_scope"] == "component_only"
    assert math.isclose(atom["model"]["mtbf_hours"], 333450.0)
    assert math.isclose(atom["model"]["mtbf_years"], 333450.0 / 8760.0)
    assert math.isclose(atom["model"]["lambda_per_year"], 8760.0 / 333450.0)
    assert atom["model_readiness"]["checks"]["source_identity"] is True
    assert atom["model_readiness"]["checks"]["evidence_accept"] is False
    assert atom["model_readiness"]["checks"]["architecture"] is False
