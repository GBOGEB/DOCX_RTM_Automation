#!/usr/bin/env python3
"""Manifest/index validation for recursive artifact alignment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.core.idempotency_contract import canonical_hash


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_index(repo_root: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Build hash index from manifest-defined artifacts."""
    root = Path(repo_root).resolve()
    entries: List[Dict[str, Any]] = []

    for item in manifest.get("artifacts", []):
        rel_path = item["path"]
        full_path = root / rel_path
        exists = full_path.exists()
        entries.append(
            {
                "path": rel_path,
                "required": bool(item.get("required", True)),
                "exists": exists,
                "sha256": canonical_hash(full_path.read_bytes()) if exists else None,
            }
        )

    return {"artifacts": entries}


def verify_alignment(
    repo_root: Path,
    manifest_path: Path,
    index_path: Path,
) -> Dict[str, Any]:
    """Verify current artifacts against locked alignment index."""
    manifest = _read_json(manifest_path)
    expected = _read_json(index_path)
    current = build_index(repo_root, manifest)

    expected_map = {entry["path"]: entry for entry in expected.get("artifacts", [])}

    missing: List[str] = []
    drifted: List[str] = []

    for entry in current.get("artifacts", []):
        path = entry["path"]
        required = entry.get("required", True)

        if required and not entry["exists"]:
            missing.append(path)
            continue

        expected_entry = expected_map.get(path)
        if not expected_entry:
            drifted.append(path)
            continue

        if entry["exists"] and expected_entry.get("sha256") != entry.get("sha256"):
            drifted.append(path)

    return {
        "ok": len(missing) == 0 and len(drifted) == 0,
        "missing": missing,
        "drifted": drifted,
        "checked": len(current.get("artifacts", [])),
    }
