"""Tests for canonical idempotency and commit-backed lineage metadata."""

from pathlib import Path

from src.core.idempotency_contract import canonical_hash, canonical_run_key
from src.core.lineage_metadata import build_lineage_snapshot
from pipeline.main import DMAICPipelineController, DMAICPhase


def test_canonical_hash_is_stable_for_reordered_dict():
    payload_a = {"b": 2, "a": 1}
    payload_b = {"a": 1, "b": 2}
    assert canonical_hash(payload_a) == canonical_hash(payload_b)


def test_pipeline_phase_execution_replays_identically():
    controller = DMAICPipelineController()
    controller.initialize_dmaic_cycle("sample_project", ["obj_a"])

    first = controller.execute_phase(
        DMAICPhase.DEFINE,
        deliverables=["D1", "D2"],
        results=["R1"],
    )
    second = controller.execute_phase(
        DMAICPhase.DEFINE,
        deliverables=["D2", "D1"],
        results=["R1"],
    )

    assert first["run_key"] == second["run_key"]
    assert second["idempotent_replay"] is True
    assert first["compliance_score"] == second["compliance_score"]


def test_lineage_snapshot_contains_commit_fields(project_root_path: Path):
    repo_root = project_root_path
    snapshot = build_lineage_snapshot(
        repo_root=repo_root,
        artifacts=[repo_root / "pipeline" / "main.py"],
        context={"test": "lineage"},
    )

    assert "git" in snapshot
    assert "head_commit" in snapshot["git"]
    assert "branch" in snapshot["git"]
    assert snapshot["artifacts"][0]["path"] == "pipeline/main.py"
