#!/usr/bin/env python3
"""Commit-backed lineage metadata utilities."""

from __future__ import annotations

import subprocess
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

logger = logging.getLogger(__name__)


def _git(repo_root: Path, *args: str) -> str:
    output = subprocess.check_output(
        ["git", "-C", str(repo_root), *args],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return output.strip()


def _safe_git(repo_root: Path, *args: str) -> str | None:
    try:
        return _git(repo_root, *args)
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError) as exc:
        logger.debug("Git metadata lookup failed for args %s: %s", args, exc)
        return None


def build_lineage_snapshot(
    repo_root: Path,
    artifacts: Iterable[Path],
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build commit-backed lineage snapshot for current run."""
    root = Path(repo_root).resolve()
    head = _safe_git(root, "rev-parse", "HEAD")
    branch = _safe_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    commit_time = _safe_git(root, "show", "-s", "--format=%cI", "HEAD")
    remote = _safe_git(root, "config", "--get", "remote.origin.url")

    artifact_entries = []
    for artifact in artifacts:
        artifact_path = Path(artifact)
        full_path = (
            artifact_path if artifact_path.is_absolute() else root / artifact_path
        )
        exists = full_path.exists()
        artifact_entries.append(
            {
                "path": (
                    str(full_path.relative_to(root))
                    if full_path.is_relative_to(root)
                    else str(full_path)
                ),
                "exists": exists,
                "sha256": (
                    hashlib.sha256(full_path.read_bytes()).hexdigest()
                    if exists
                    else None
                ),
                "size_bytes": full_path.stat().st_size if exists else 0,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "context": context or {},
        "git": {
            "head_commit": head,
            "branch": branch,
            "commit_time": commit_time,
            "remote_origin": remote,
        },
        "artifacts": artifact_entries,
    }
