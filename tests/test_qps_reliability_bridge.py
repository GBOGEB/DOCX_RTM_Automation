import math

from src.dashboard.qps_reliability_bridge import build_bridge, evaluate_item


SHA = "a" * 40


def source_item(**overrides):
    item = {
        "component": "HP_COMPRESSOR",
        "qps_item_id": "T6.2",
        "origin": "SOURCE_BOUND",
        "evidence_disposition": "ACCEPT",
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
    assert math.isclose(result["model"]["mtbf_hours"], 43800.0)
    assert math.isclose(result["model"]["lambda_per_year"], 0.2)
    assert math.isclose(result["model"]["p0"], math.exp(-0.2 * 90 / 365))
    assert math.isclose(result["model"]["p_ge_1"], 1 - result["model"]["p0"])
    assert len(result["model"]["poisson_counts"]) == 9


def test_source_bound_defer_is_scenario_only():
    result = evaluate_item(source_item(evidence_disposition="DEFER"))
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"
    assert result["model"] is not None


def test_missing_architecture_limits_model_to_component_only():
    result = evaluate_item(source_item(architecture={}))
    assert result["model_scope"] == "component_only"
    assert result["model_readiness"]["disposition"] == "SCENARIO_ONLY"


def test_inconsistent_mtbf_and_lambda_is_excluded():
    result = evaluate_item(source_item(mtbf_years=5.0, lambda_per_year=1.0))
    assert result["model_readiness"]["disposition"] == "EXCLUDED"
    assert "reliability_values_inconsistent" in result["errors"]


def test_scenario_does_not_require_source_sha_but_retains_provenance():
    result = evaluate_item(source_item(
        component="QPLANT_CLASS_A_SYSTEM",
        origin="SCENARIO",
        evidence_disposition="DEFER",
        source_git_sha=None,
        qps_item_id=None,
        mtbf_years=4.8,
    ))
    assert result["model_readiness"]["disposition"] == "ACTIVE"
    assert result["provenance"]["origin"] == "SCENARIO"
    assert result["provenance"]["source_sha_valid"] is False


def test_bridge_summary_counts_pilot_records():
    payload = {"items": [
        source_item(),
        source_item(component="PVPS", evidence_disposition="DEFER"),
        source_item(component="UNKNOWN_COMPONENT"),
    ]}
    result = build_bridge(payload)
    assert result["summary"] == {
        "item_count": 3,
        "active_count": 1,
        "scenario_only_count": 1,
        "excluded_count": 1,
    }
