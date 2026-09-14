from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE = REPO_ROOT / "configs" / "qps_offer_evaluation_v7_1.yaml"
APPLICABILITY = REPO_ROOT / "federation" / "ADR_OCD" / "qps_triage_applicability.yaml"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_offer_v71_profile_is_locked_and_non_authoritative():
    profile = load_yaml(PROFILE)
    assert profile["version"] == 7.1
    assert profile["authority_boundary"]["engineering_promotion_forbidden"] is True
    assert profile["authority_boundary"]["seeded_bidder_values_are_engineering_evidence"] is False
    assert profile["authority_boundary"]["seeded_bidder_values_evidence_class"] == "POSTULATED"
    assert profile["method_lock"]["static_requirement_ranking_first"] is True
    assert profile["method_lock"]["bidder_scoring_second"] is True
    assert profile["method_lock"]["risk_overlay_third"] is True
    assert profile["method_lock"]["deterministic"] is True
    assert profile["method_lock"]["schedule_policy"] == "gate_only"
    assert profile["method_lock"]["cost_activation"] == "only_if_technical_near_tie"


def test_offer_v71_ranking_and_risk_are_separate_state_dimensions():
    profile = load_yaml(PROFILE)
    rules = " ".join(profile["triage_projection"]["rules"])
    assert "Static rank may influence triage priority" in rules
    assert "Risk is independent of static rank" in rules
    assert "Gate failure overrides score" in rules
    assert "do not replace QPS Triage disposition" in rules


def test_offer_v71_artifacts_remain_deferred_until_exact_binary_binding():
    profile = load_yaml(PROFILE)
    assert profile["authority_boundary"]["exact_binary_hash_binding"] == "DEFER"
    assert profile["artifact_references"]["artifact_binding_status"] == "DEFER"


def test_offer_v71_reliability_candidates_preserve_qps_triage_gates():
    profile = load_yaml(PROFILE)
    by_offer = {item["offer_id"]: item for item in profile["reliability_bridge_candidates"]}
    assert "OFFER-11" in by_offer
    assert set(by_offer["OFFER-11"]["activation_requires"]) == {
        "exact_source_identity",
        "upstream_ACCEPT",
        "unit_reference_period",
        "architecture_completeness",
        "deterministic_model_consistency",
    }
    assert {"OFFER-20", "OFFER-21", "OFFER-22", "OFFER-41", "OFFER-42", "OFFER-43", "OFFER-46"}.issubset(by_offer)


def test_offer_v71_projection_is_compatible_with_qps_triage_v03_authority_boundary():
    profile = load_yaml(PROFILE)
    app = load_yaml(APPLICABILITY)
    assert app["version"] == "0.3.0"
    assert app["qps_authority_source"]["engineering_promotion_forbidden"] is True
    assert app["mission_control_projection"]["authority_transfer"] is False
    assert profile["authority_boundary"]["qps_engineering_authority"] == app["qps_authority_source"]["repo"]
    assert profile["triage_projection"]["primary_lane"] == "TRIAGE-QPS"
