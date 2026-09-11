from pathlib import Path
import hashlib
import json
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "qps_triage_pipeline_input.json"

sys.path.insert(0, str(REPO_ROOT))
from scripts.create_qps_triage_ci_registry_receipt import build_registry_receipt


def run_pipeline(tmp_path: Path):
    return subprocess.run(
        [
            sys.executable,
            "scripts/run_qps_triage_pipeline.py",
            "--input-analysis",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_verifier(tmp_path: Path):
    return subprocess.run(
        [sys.executable, "scripts/verify_qps_triage_receipt.py", str(tmp_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_wave8_pipeline_cli_generates_governed_artifact_bundle(tmp_path):
    result = run_pipeline(tmp_path)
    assert result.returncode == 0, result.stderr + result.stdout

    expected = {
        "enhanced_analysis.json",
        "qps_triage_items.json",
        "qps_triage_traceability_rows.json",
        "qps_triage_traceability_rows.csv",
        "qps_triage_downstream_index.json",
        "qps_triage_rtm_rows.csv",
        "qps_triage_dtm_rows.csv",
        "qps_triage_dashboard.json",
        "qps_triage_dashboard.md",
        "qps_triage_dashboard.html",
        "canonical_dashboard.json",
        "qps_triage_pipeline_manifest.json",
        "qps_triage_evidence_manifest.json",
        "qps_triage_governed_receipt.json",
        "SHA256SUMS",
        "export_manifest.json",
    }
    generated = {path.name for path in tmp_path.iterdir() if path.is_file()}
    assert expected.issubset(generated)

    manifest = json.loads((tmp_path / "qps_triage_pipeline_manifest.json").read_text(encoding="utf-8"))
    assert manifest["pipeline_id"] == "QPS_TRIAGE_WAVE_8"
    assert set(manifest["stages"].values()) == {"PASS"}
    assert manifest["counts"]["triage_items"] == 3
    assert manifest["counts"]["traceability_rows"] > 0
    assert manifest["counts"]["rtm_rows"] > 0
    assert manifest["counts"]["dtm_rows"] > 0
    assert len(manifest["identity"]["git_sha"]) == 40

    evidence = json.loads((tmp_path / "qps_triage_evidence_manifest.json").read_text(encoding="utf-8"))
    assert evidence["hash_algorithm"] == "SHA256"
    assert evidence["artifact_count"] == len(evidence["artifacts"])
    assert all(len(record["sha256"]) == 64 for record in evidence["artifacts"])

    receipt = json.loads((tmp_path / "qps_triage_governed_receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    assert receipt["identity"]["git_sha"] == manifest["identity"]["git_sha"]
    assert receipt["governance"]["exact_sha_bound"] is True

    manifest_digest = hashlib.sha256((tmp_path / "qps_triage_pipeline_manifest.json").read_bytes()).hexdigest()
    evidence_digest = hashlib.sha256((tmp_path / "qps_triage_evidence_manifest.json").read_bytes()).hexdigest()
    assert receipt["pipeline_manifest"]["sha256"] == manifest_digest
    assert receipt["evidence_manifest"]["sha256"] == evidence_digest

    canonical = json.loads((tmp_path / "canonical_dashboard.json").read_text(encoding="utf-8"))
    assert canonical["qps_triage_dashboard"]["present"] is True
    assert canonical["qps_triage_dashboard"]["triage_item_count"] == 3

    verify = run_verifier(tmp_path)
    assert verify.returncode == 0, verify.stderr + verify.stdout
    assert "PASS" in verify.stdout


def test_wave8_verifier_detects_payload_tampering(tmp_path):
    result = run_pipeline(tmp_path)
    assert result.returncode == 0, result.stderr + result.stdout

    target = tmp_path / "qps_triage_dashboard.json"
    target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    verify = run_verifier(tmp_path)
    assert verify.returncode == 1
    assert "mismatch" in verify.stdout.lower()


def _write_wave9_source_receipt(tmp_path: Path):
    governed = {
        "receipt_id": "QPS-TRIAGE-W8-0123456789ab",
        "identity": {
            "git_sha": "0123456789abcdef0123456789abcdef01234567",
            "run_id": "34562560294",
            "run_number": "37",
            "workflow": "ADR_OCD Bridge Validation",
        },
    }
    (tmp_path / "qps_triage_governed_receipt.json").write_text(
        json.dumps(governed), encoding="utf-8"
    )
    (tmp_path / "SHA256SUMS").write_text("abc  example.json\n", encoding="utf-8")
    return governed


def test_wave9_registry_receipt_binds_external_artifact_object(tmp_path):
    governed = _write_wave9_source_receipt(tmp_path)

    receipt = build_registry_receipt(
        tmp_path,
        artifact_id="10184837991",
        artifact_url="https://github.com/GBOGEB/DOCX_RTM_Automation/actions/runs/34562560294/artifacts/10184837991",
        artifact_digest="sha256:" + "a" * 64,
        artifact_name="qps-triage-wave8-0123456789abcdef0123456789abcdef01234567",
    )

    assert receipt["status"] == "PASS"
    assert receipt["github_artifact"]["artifact_id"] == "10184837991"
    assert receipt["github_artifact"]["artifact_digest"] == "sha256:" + "a" * 64
    assert receipt["governance"]["external_artifact_object_bound"] is True
    assert receipt["identity"]["git_sha"] == governed["identity"]["git_sha"]


def test_wave9_registry_receipt_normalizes_raw_upload_artifact_digest(tmp_path):
    _write_wave9_source_receipt(tmp_path)

    receipt = build_registry_receipt(
        tmp_path,
        artifact_id="10186575972",
        artifact_url="https://github.com/GBOGEB/DOCX_RTM_Automation/actions/runs/34567601222/artifacts/10186575972",
        artifact_digest="e6129142f68301ebf2b69fa9392b97fb8c1808e6ccecd6d01052c507cb2f3492",
        artifact_name="qps-triage-wave8-0123456789abcdef0123456789abcdef01234567",
    )

    assert receipt["github_artifact"]["artifact_digest"] == (
        "sha256:e6129142f68301ebf2b69fa9392b97fb8c1808e6ccecd6d01052c507cb2f3492"
    )
