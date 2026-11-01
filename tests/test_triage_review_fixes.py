import json

from triage.dmaic_mip_pulse_20261031.tools import (
    ci_stats,
    pandoc_scale,
    red_classify,
    wf_analyze,
    wf_harden,
)


def test_ci_stats_handles_empty_and_sparse_exports():
    empty = ci_stats.summarize([])
    assert empty["window_h"] is None
    assert empty["runs_per_h"] is None
    assert empty["dur_p50_s"] is None
    assert empty["workflow_elapsed_hours"] is None

    sparse = ci_stats.summarize([{
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-10-31T12:00:00Z",
        "name": "workflow",
        "head_branch": "main",
        "event": "push",
    }])
    assert sparse["window_h"] == 0
    assert sparse["runs_per_h"] is None
    assert sparse["dur_p90_s"] is None
    assert sparse["workflow_elapsed_hours"] is None
    assert "runner_hours" not in sparse


def test_pandoc_poc_counts_both_batches_and_all_inputs():
    small = ["/docs/one.md", "/docs/two.md"]
    first = [
        {"src": src, "ok": True, "err": ""}
        for src in small
    ]
    second = [
        {"src": small[0], "ok": True, "err": ""},
        {"src": small[1], "ok": False, "err": "failed"},
    ]
    report = pandoc_scale.poc_summary(
        small, first, second, {"one": "same", "two": "first"},
        {"one": "same"},
    )
    assert report["success_pct"] == 50
    assert report["deterministic_pct"] == 50
    assert report["failures"] == [("two.md", "failed")]


def test_usl_unbounded_optimum_is_strict_json():
    result = pandoc_scale.usl_fit([(1, 1.0), (2, 2.0)])
    assert result["kappa"] == 0
    assert result["N_star"] is None
    assert "Infinity" not in json.dumps(result, allow_nan=False)


def test_failed_pandoc_trial_has_no_eligible_timing():
    assert pandoc_scale.successful_trial_wall(1.2, [{"ok": True}]) == 1.2
    assert pandoc_scale.successful_trial_wall(
        0.1, [{"ok": True}, {"ok": False}]
    ) is None


def test_red_probe_paginates_jobs_and_checks_each_unstarted_failed_job(monkeypatch):
    calls = []

    def fake_gh(path):
        calls.append(path)
        if "/jobs?" in path and path.endswith("page=1"):
            return {"jobs": [
                {"id": i, "conclusion": "success", "steps": []}
                for i in range(100)
            ]}
        if "/jobs?" in path and path.endswith("page=2"):
            return {"jobs": [{"id": 101, "conclusion": "failure", "steps": []}]}
        if "/annotations?" in path:
            return [{"message": "spending limit exceeded"}]
        raise AssertionError(path)

    monkeypatch.setattr(red_classify, "gh", fake_gh)
    result = red_classify.probe({
        "id": 42, "name": "workflow", "head_branch": "main",
        "created_at": "2026-10-31T12:00:00Z",
    }, "repo")
    assert result["jobs"] == 101
    assert "spending limit" in result["annotation"]
    assert result["api_calls"] == len(calls) == 3


def test_timeout_hygiene_excludes_reusable_workflow_calls(tmp_path):
    wfdir = tmp_path / ".github" / "workflows"
    wfdir.mkdir(parents=True)
    (wfdir / "pages.yml").write_text(
        """on: push
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
  deploy:
    uses: owner/repo/.github/workflows/reusable.yml@main
""",
        encoding="utf-8",
    )
    summary = wf_analyze.summarize(wf_analyze.analyze_repo(str(tmp_path)))
    assert summary["jobs"] == 2
    assert summary["runner_jobs"] == 1
    assert summary["pct_jobs_timeout"] == 100
    assert summary["runner_jobs_without_timeout"] == 0


def test_harden_inserts_timeout_before_block_runs_on():
    source = """name: test
on: push
jobs:
  build:
    runs-on:
      - ubuntu-latest
    steps: []
"""
    hardened, added, _ = wf_harden.harden(source, 30)
    parsed = wf_harden.yaml.load(hardened, Loader=wf_harden.Loader)
    assert added == 1
    assert parsed["jobs"]["build"]["runs-on"] == ["ubuntu-latest"]
    assert parsed["jobs"]["build"]["timeout-minutes"] == 30
    assert hardened.index("timeout-minutes") < hardened.index("runs-on")
