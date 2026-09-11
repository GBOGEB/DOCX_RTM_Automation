import json

from src.dashboard.canonical_dashboard import collect_stats
from src.dashboard.qps_receipt_consumer import (
    build_release_baseline_evidence,
    evaluate_registry_receipt,
)


SHA = "0123456789abcdef0123456789abcdef01234567"


def write_receipt(path, *, git_sha=SHA, status="PASS", digest="sha256:" + "a" * 64, bound=True):
    receipt = {
        "registry_receipt_id": "QPS-TRIAGE-W9-0123456789ab",
        "status": status,
        "identity": {"git_sha": git_sha, "run_id": "12345"},
        "github_artifact": {
            "artifact_id": "999",
            "artifact_digest": digest,
            "artifact_url": "https://github.com/example/actions/runs/12345/artifacts/999",
        },
        "governance": {
            "external_artifact_object_bound": bound,
            "provider_digest_present": True,
        },
    }
    path.write_text(json.dumps(receipt), encoding="utf-8")
    return path


def test_exact_sha_registry_receipt_is_accepted(tmp_path):
    path = write_receipt(tmp_path / "registry.json")
    decision = evaluate_registry_receipt(path, expected_git_sha=SHA)
    assert decision["disposition"] == "ACCEPT"
    assert decision["reason"] == "exact_sha_registry_evidence_verified"
    assert all(decision["checks"].values())


def test_missing_receipt_is_deferred():
    decision = evaluate_registry_receipt(None, expected_git_sha=SHA)
    assert decision["disposition"] == "DEFER"
    assert decision["reason"] == "receipt_missing"


def test_stale_or_mismatched_receipt_is_deferred(tmp_path):
    path = write_receipt(tmp_path / "registry.json", git_sha="f" * 40)
    decision = evaluate_registry_receipt(path, expected_git_sha=SHA)
    assert decision["disposition"] == "DEFER"
    assert decision["reason"] == "exact_sha_mismatch"
    assert decision["checks"]["exact_sha_match"] is False


def test_invalid_provider_binding_is_deferred(tmp_path):
    path = write_receipt(tmp_path / "registry.json", bound=False)
    decision = evaluate_registry_receipt(path, expected_git_sha=SHA)
    assert decision["disposition"] == "DEFER"
    assert decision["reason"] == "external_artifact_binding_missing"


def test_release_baseline_object_carries_accept_disposition(tmp_path):
    path = write_receipt(tmp_path / "registry.json")
    evidence = build_release_baseline_evidence(path, expected_git_sha=SHA)
    assert evidence["evidence_type"] == "qps_triage_registry_receipt"
    assert evidence["disposition"] == "ACCEPT"
    assert evidence["receipt"]["observed_git_sha"] == SHA


def test_canonical_dashboard_consumes_registry_receipt(tmp_path):
    path = write_receipt(tmp_path / "registry.json")
    stats = collect_stats(None, path, SHA)
    evidence = stats["qps_triage_release_evidence"]
    assert evidence["disposition"] == "ACCEPT"
    assert evidence["checks"]["exact_sha_match"] is True
