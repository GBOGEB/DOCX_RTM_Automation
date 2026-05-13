#!/usr/bin/env python3
"""
Lock canonical artefacts and optionally create a git tag + GitHub Release.

Usage:
    python scripts/lock_canonical.py           # Lock artefacts only
    python scripts/lock_canonical.py --tag     # Lock + create git tag
    python scripts/lock_canonical.py --release # Lock + tag + GitHub Release

What it does:
  1. Reads all *_v*.json files in canonical/artefacts/ (excluding manifest).
  2. Computes SHA-256 for each.
  3. Stamps each with a _meta block (content SHA-256, timestamp, version).
  4. Writes canonical/LOCK.json with locked artefact registry.
  5. Updates canonical/POINTER.md with the new release info.
  6. (--tag)     Creates git tag  canonical/v{YYYYMMDD}-{short_sha}
  7. (--release) Creates GitHub Release via gh CLI and uploads artefacts.

Once locked, artefact files become immutable — the lock engine refuses to
overwrite them until a new version (_v2, _v3, …) is explicitly created.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("lock_canonical")

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTEFACTS_DIR = _REPO_ROOT / "canonical" / "artefacts"
_LOCK_PATH = _REPO_ROOT / "canonical" / "LOCK.json"
_POINTER_PATH = _REPO_ROOT / "canonical" / "POINTER.md"
_MANIFEST_PATH = _ARTEFACTS_DIR / "extraction_manifest.json"

LOCK_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _sha256_dict(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_REPO_ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def _stamp_artefact_file(path: Path, source_sha256: str = "") -> str:
    """
    Add / update _meta block in an artefact JSON file.
    Returns the content SHA-256.
    """
    data = _load_json(path) or {}
    clean = {k: v for k, v in data.items() if k != "_meta"}
    content_sha = _sha256_dict(clean)
    meta = {
        "sha256": content_sha,
        "source_sha256": source_sha256,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "lock_version": LOCK_VERSION,
    }
    stamped = {**clean, "_meta": meta}
    with path.open("w", encoding="utf-8") as fh:
        json.dump(stamped, fh, indent=2, ensure_ascii=False)
    return content_sha


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------

def find_artefact_files() -> list[Path]:
    """Return all *_v*.json artefact files (not manifest, not LOCK)."""
    return sorted(
        p for p in _ARTEFACTS_DIR.glob("*_v*.json")
        if p.name not in ("extraction_manifest.json",)
    )


def lock_artefacts() -> tuple[dict, str]:
    """
    Stamp and lock all artefacts in canonical/artefacts/.

    Returns (lock_data, tag_name).
    """
    artefact_files = find_artefact_files()
    if not artefact_files:
        logger.warning("No artefact files found in %s — nothing to lock.", _ARTEFACTS_DIR)

    locked: dict[str, dict] = {}

    for path in artefact_files:
        # Derive logical name: "master_requirements_v1.json" → "master_requirements"
        stem = path.stem  # e.g. "master_requirements_v1"
        name = "_".join(stem.split("_")[:-1]) if stem[-2] == "v" and stem[-1].isdigit() else stem

        # Find matching source_sha256 from manifest (best-effort)
        source_sha = ""
        manifest = _load_json(_MANIFEST_PATH)
        if manifest:
            for entry in manifest.get("extractions", []):
                if entry.get("artefact_name") == name:
                    source_sha = entry.get("source_sha256", "")
                    break

        content_sha = _stamp_artefact_file(path, source_sha)
        rel = str(path.relative_to(_REPO_ROOT))

        locked[name] = {
            "output_file": rel,
            "content_sha256": content_sha,
            "source_sha256": source_sha,
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "version": path.stem,  # e.g. "master_requirements_v1"
        }
        logger.info("  Locked: %s  (%s…)", rel, content_sha[:12])

    today = date.today().strftime("%Y%m%d")
    short_sha = _git_short_sha()
    tag_name = f"canonical/v{today}-{short_sha}"

    lock_data = {
        "lock_version": LOCK_VERSION,
        "tag": tag_name,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "locked_artefacts": locked,
    }

    with _LOCK_PATH.open("w", encoding="utf-8") as fh:
        json.dump(lock_data, fh, indent=2, ensure_ascii=False)
    logger.info("LOCK.json written to %s", _LOCK_PATH)

    return lock_data, tag_name


# ---------------------------------------------------------------------------
# POINTER.md update
# ---------------------------------------------------------------------------

def update_pointer(lock_data: dict, tag_name: str, release_url: str = "") -> None:
    today_str = lock_data["locked_at"][:10]
    artefact_list = "\n".join(
        f"| `{name}` | `{info['version']}` | `{info['content_sha256'][:16]}…` |"
        for name, info in lock_data["locked_artefacts"].items()
    )

    release_cell = release_url or f"*(run with --release to publish)*"

    content = f"""# Latest Canonical Release

> **Auto-updated by `scripts/lock_canonical.py`.**

## Latest Release

| Field | Value |
|-------|-------|
| Tag | `{tag_name}` |
| Release URL | {release_cell} |
| Locked at | {today_str} |

## Locked Artefacts

| Artefact | Version | SHA-256 (first 16) |
|----------|---------|-------------------|
{artefact_list}

## How to Use

Reference artefacts via the stable GitHub Release asset URL above —
**never** the raw binary source files.

## All Canonical Releases

| Tag | Date |
|-----|------|
| `{tag_name}` | {today_str} |
"""
    with _POINTER_PATH.open("w", encoding="utf-8") as fh:
        fh.write(content)
    logger.info("POINTER.md updated")


# ---------------------------------------------------------------------------
# Git tag
# ---------------------------------------------------------------------------

def create_git_tag(tag_name: str) -> None:
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Canonical lock: {tag_name}"],
            cwd=_REPO_ROOT,
            check=True,
        )
        logger.info("Git tag created: %s", tag_name)
        logger.info("Push with: git push origin %s", tag_name)
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to create git tag: %s", exc)


# ---------------------------------------------------------------------------
# GitHub Release
# ---------------------------------------------------------------------------

def create_github_release(tag_name: str, lock_data: dict) -> str:
    """Create a GitHub Release using the gh CLI and upload artefact files."""
    artefact_files = find_artefact_files()
    upload_args = []
    for p in artefact_files:
        upload_args += [str(p)]

    title = f"Canonical artefacts {lock_data['locked_at'][:10]}"
    body = (
        f"Immutable canonical artefacts locked at {lock_data['locked_at']}.\n\n"
        "Download individual artefacts from the Assets section below."
    )

    cmd = [
        "gh", "release", "create", tag_name,
        "--title", title,
        "--notes", body,
    ] + upload_args

    try:
        result = subprocess.run(cmd, cwd=_REPO_ROOT, check=True, capture_output=True, text=True)
        release_url = result.stdout.strip()
        logger.info("GitHub Release created: %s", release_url)
        return release_url
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to create GitHub Release: %s\n%s", exc, exc.stderr)
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lock canonical artefacts and optionally publish a release"
    )
    parser.add_argument(
        "--tag", action="store_true", help="Create a git tag after locking"
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Create git tag + GitHub Release (requires gh CLI)",
    )
    args = parser.parse_args()

    logger.info("=== Locking canonical artefacts ===")
    lock_data, tag_name = lock_artefacts()

    release_url = ""
    if args.release or args.tag:
        create_git_tag(tag_name)
    if args.release:
        release_url = create_github_release(tag_name, lock_data)

    update_pointer(lock_data, tag_name, release_url)

    logger.info("=== Lock complete — tag: %s ===", tag_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
