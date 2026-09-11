from scripts.build_qps_release_baseline import STAGES, build_release_baseline

SHA = "0123456789abcdef0123456789abcdef01234567"


def accepted_evidence():
    return {
        "evidence_type": "qps_triage_registry_receipt",
        "expected_git_sha": SHA,
        "disposition": "ACCEPT",
        "reason": "exact_sha_registry_evidence_verified",
        "receipt": {
            "receipt_id": "QPS-TRIAGE-W9-0123456789ab",
            "artifact_id": "12345",
            "artifact_digest": "sha256:" + "a" * 64,
            "observed_git_sha": SHA,
        },
        "checks": {
            "receipt_present": True,
            "receipt_status_pass": True,
            "exact_sha_match": True,
            "external_artifact_bound": True,
            "provider_digest_present": True,
        },
    }


def test_release_baseline_promotes_exact_sha_accept():
    result = build_release_baseline(
        accepted_evidence(),
        stage="final_corrigendum",
        expected_git_sha=SHA,
    )
    assert result["release_disposition"] == "PROMOTE"
    assert result["release_reason"] == "exact_sha_release_evidence_accepted"
    assert result["gates"]["exact_sha_match"] is True
    assert result["gates"]["wave10_evidence_accept"] is True
    assert result["previous_stage"] == "negotiation_stage_2"
    assert result["next_stage"] == "contract_baseline"


def test_release_baseline_holds_deferred_evidence():
    evidence = accepted_evidence()
    evidence["disposition"] = "DEFER"
    evidence["reason"] = "provider_digest_missing_or_invalid"
    result = build_release_baseline(
        evidence,
        stage="contract_baseline",
        expected_git_sha=SHA,
    )
    assert result["release_disposition"] == "HOLD"
    assert result["release_reason"] == "provider_digest_missing_or_invalid"
    assert result["gates"]["wave10_evidence_accept"] is False


def test_release_baseline_holds_stale_sha():
    evidence = accepted_evidence()
    result = build_release_baseline(
        evidence,
        stage="negotiation_stage_1",
        expected_git_sha="f" * 40,
    )
    assert result["release_disposition"] == "HOLD"
    assert result["release_reason"] == "release_evidence_exact_sha_mismatch"
    assert result["gates"]["exact_sha_match"] is False


def test_procurement_stage_sequence_is_controlled():
    assert STAGES == [
        "publication_baseline",
        "negotiation_stage_1",
        "negotiation_stage_2",
        "final_corrigendum",
        "contract_baseline",
    ]
