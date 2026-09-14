from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
APPLICABILITY = REPO_ROOT / "federation" / "ADR_OCD" / "qps_triage_applicability.yaml"


def load_applicability():
    return yaml.safe_load(APPLICABILITY.read_text(encoding="utf-8"))


def test_v03_registers_reliability_and_mission_control_without_authority_transfer():
    app = load_applicability()
    assert app["version"] == "0.3.0"
    assert "Reliability Analysis" in app["scope"]["applies_to"]
    assert app["scope"]["repositories"]["mission_control"] == ["GBOGEB/pipeline-automation-hub"]
    assert app["mission_control_projection"]["horizontal_lane"] == "H4_QPS_TRIAGE"
    assert app["mission_control_projection"]["authority_transfer"] is False
    assert app["qps_authority_source"]["engineering_promotion_forbidden"] is True


def test_reliability_lane_is_analytical_consumer_only():
    app = load_applicability()
    lanes = {lane["lane_id"]: lane for lane in app["triage_lanes"]}
    assert "TRIAGE-RELIABILITY" in lanes
    lane = lanes["TRIAGE-RELIABILITY"]
    assert "reliability_source_atom" in lane["accepted_inputs"]
    assert "reliability_model_candidate" in lane["outputs"]
    assert "Component MTBF" in lane["guard"]
    assert "Table-10" in lane["guard"]


def test_state_classes_are_separate_and_model_states_are_not_triage_dispositions():
    app = load_applicability()
    classes = app["state_class_policy"]["classes"]
    assert set(classes) == {
        "qps_child_engineering",
        "tooling_triage",
        "reliability_model",
        "mission_execution",
    }
    model_states = {item["state"] for item in app["reliability_model_states"]}
    triage_dispositions = {item["disposition"] for item in app["triage_dispositions"]}
    assert model_states == {"ACTIVE", "SCENARIO_ONLY", "EXCLUDED"}
    assert model_states.isdisjoint(triage_dispositions)


def test_reliability_contract_preserves_component_system_boundary():
    app = load_applicability()
    contract = app["reliability_input_contract"]
    assert set(contract["source_classes"]) == {"SOURCE_BOUND", "SCENARIO", "USER_OVERRIDE"}
    guards = set(contract["anti_overclaim"])
    assert "COMPONENT_MTBF_NE_SYSTEM_EVENT_MTBF" in guards
    assert "MODEL_ACTIVE_NE_QPS_ENGINEERING_ACCEPTED" in guards
    assert "TOOLING_ACCEPT_NE_CHILD_ACCEPT" in guards
    assert "POISSON_CONFIDENCE_NE_CONTRACT_COUNT_COMPLIANCE" in guards


def test_method_selector_reuses_existing_3p_and_mip_semantics():
    app = load_applicability()
    methods = app["method_applicability"]
    assert methods["controller_semantics_owner"] == "GBOGEB/CODEX"
    assert set(methods["methods"]) == {"3PR", "MIP", "3PC", "3P3"}
    assert methods["default_sequence"] == [
        "3PR",
        "MIP_IF_NEEDED",
        "3PC_IF_TRANSACTIONAL",
        "3P3_IF_GENERALISATION_MISSING",
    ]
    assert methods["no_ceremonial_repetition"] is True


def test_new_control_gates_fail_closed_on_authority_and_method_selection():
    app = load_applicability()
    gates = {gate["gate_id"]: gate for gate in app["control_gates"]}
    for gate_id in [
        "QPS-TRIAGE-GATE-007",
        "QPS-TRIAGE-GATE-008",
        "QPS-TRIAGE-GATE-009",
        "QPS-TRIAGE-GATE-010",
        "QPS-TRIAGE-GATE-011",
    ]:
        assert gate_id in gates
    assert "cannot self-promote" in gates["QPS-TRIAGE-GATE-007"]["rule"]
    assert "Table-10" in gates["QPS-TRIAGE-GATE-009"]["rule"]
    assert "authority_transfer remains false" in gates["QPS-TRIAGE-GATE-010"]["rule"]
    assert "otherwise STOP/REPEAT" in gates["QPS-TRIAGE-GATE-011"]["rule"]
