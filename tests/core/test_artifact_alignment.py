"""Tests for recursive artifact alignment verification."""

import json
from pathlib import Path

from src.core.artifact_alignment import build_index, verify_alignment


def test_alignment_passes_with_fresh_index(tmp_path: Path):
    repo_root = tmp_path
    artifact = repo_root / "example.txt"
    artifact.write_text("stable-content", encoding="utf-8")

    manifest = {"artifacts": [{"path": "example.txt", "required": True}]}
    manifest_path = repo_root / "manifest.json"
    index_path = repo_root / "index.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    index_path.write_text(
        json.dumps(build_index(repo_root, manifest)), encoding="utf-8"
    )

    result = verify_alignment(repo_root, manifest_path, index_path)
    assert result["ok"] is True
    assert result["missing"] == []
    assert result["drifted"] == []


def test_alignment_detects_drift(tmp_path: Path):
    repo_root = tmp_path
    artifact = repo_root / "example.txt"
    artifact.write_text("v1", encoding="utf-8")

    manifest = {"artifacts": [{"path": "example.txt", "required": True}]}
    manifest_path = repo_root / "manifest.json"
    index_path = repo_root / "index.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    index_path.write_text(
        json.dumps(build_index(repo_root, manifest)), encoding="utf-8"
    )

    artifact.write_text("v2", encoding="utf-8")
    result = verify_alignment(repo_root, manifest_path, index_path)
    assert result["ok"] is False
    assert result["drifted"] == ["example.txt"]
