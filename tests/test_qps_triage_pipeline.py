from pathlib import Path
import json
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "qps_triage_pipeline_input.json"


def test_wave7_pipeline_cli_generates_complete_artifact_bundle(tmp_path):
    result = subprocess.run(
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
        "export_manifest.json",
    }
    generated = {path.name for path in tmp_path.iterdir() if path.is_file()}
    assert expected.issubset(generated)

    manifest = json.loads((tmp_path / "qps_triage_pipeline_manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["stages"].values()) == {"PASS"}
    assert manifest["counts"]["triage_items"] == 3
    assert manifest["counts"]["traceability_rows"] > 0
    assert manifest["counts"]["rtm_rows"] > 0
    assert manifest["counts"]["dtm_rows"] > 0

    canonical = json.loads((tmp_path / "canonical_dashboard.json").read_text(encoding="utf-8"))
    assert canonical["qps_triage_dashboard"]["present"] is True
    assert canonical["qps_triage_dashboard"]["triage_item_count"] == 3

    html = (tmp_path / "qps_triage_dashboard.html").read_text(encoding="utf-8")
    assert "QPS Triage Dashboard" in html
