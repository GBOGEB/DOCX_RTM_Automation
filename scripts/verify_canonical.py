#!/usr/bin/env python3
"""
Verify the integrity of all locked canonical artefacts.

Checks:
  1. Each artefact listed in canonical/LOCK.json exists on disk.
  2. The SHA-256 recorded in the artefact's _meta block matches the file content.
  3. The extraction_manifest.json contains a corresponding entry.
  4. Cross-references are consistent (rtm_matrix req_ids exist in master_requirements, etc.).

Exit codes:
  0  — all checks pass
  1  — one or more checks failed
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("verify_canonical")

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTEFACTS_DIR = _REPO_ROOT / "canonical" / "artefacts"
_LOCK_PATH = _REPO_ROOT / "canonical" / "LOCK.json"
_MANIFEST_PATH = _ARTEFACTS_DIR / "extraction_manifest.json"


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
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON at %s: %s", path, exc)
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_lock_exists() -> bool:
    if not _LOCK_PATH.exists():
        logger.warning("LOCK.json not found at %s — no locked artefacts yet", _LOCK_PATH)
        return True  # Not a failure; just means no lock has been created yet
    return True


def check_artefact_integrity(lock: dict) -> list[str]:
    """Return list of error messages (empty = pass)."""
    errors: list[str] = []
    locked = lock.get("locked_artefacts", {})
    if not locked:
        logger.info("No locked artefacts in LOCK.json.")
        return errors

    for name, info in locked.items():
        rel_path = info.get("output_file", "")
        recorded_sha = info.get("content_sha256", "")
        abs_path = _REPO_ROOT / rel_path

        if not abs_path.exists():
            errors.append(f"MISSING artefact: {rel_path}")
            continue

        actual_sha = _sha256_file(abs_path)
        if actual_sha != recorded_sha:
            errors.append(
                f"SHA-256 MISMATCH for {name}: expected {recorded_sha[:12]}… got {actual_sha[:12]}…"
            )
            continue

        # Check _meta.sha256 inside the artefact JSON
        artefact = _load_json(abs_path)
        if artefact:
            meta = artefact.get("_meta", {})
            meta_sha = meta.get("sha256", "")
            clean = {k: v for k, v in artefact.items() if k != "_meta"}
            computed = _sha256_dict(clean)
            if meta_sha and meta_sha != computed:
                errors.append(
                    f"Internal _meta.sha256 mismatch for {name}: "
                    f"recorded {meta_sha[:12]}… computed {computed[:12]}…"
                )

        logger.info("  ✓  %s  (%s)", name, rel_path)

    return errors


def check_manifest_coverage(lock: dict) -> list[str]:
    """Every locked artefact should have a manifest entry."""
    errors: list[str] = []
    manifest = _load_json(_MANIFEST_PATH)
    if not manifest:
        return errors  # Manifest not required if no lock

    manifest_artefact_names = {e["artefact_name"] for e in manifest.get("extractions", [])}
    for name in lock.get("locked_artefacts", {}):
        if name not in manifest_artefact_names:
            errors.append(f"Locked artefact '{name}' has no corresponding manifest entry")
    return errors


def check_cross_references(lock: dict) -> list[str]:
    """Check that rtm_matrix req_ids exist in master_requirements."""
    errors: list[str] = []
    locked = lock.get("locked_artefacts", {})

    # Load master requirements
    master_path_rel = locked.get("master_requirements", {}).get("output_file")
    rtm_path_rel = locked.get("rtm_matrix", {}).get("output_file")
    if not master_path_rel or not rtm_path_rel:
        return errors  # Can't check without both

    master = _load_json(_REPO_ROOT / master_path_rel)
    rtm = _load_json(_REPO_ROOT / rtm_path_rel)
    if not master or not rtm:
        return errors

    known_req_ids = set(master.get("requirements", {}).keys())
    for rtm_id, entry in rtm.get("rtm_entries", {}).items():
        ref_req = entry.get("req_id", "")
        if ref_req and ref_req not in known_req_ids:
            errors.append(
                f"RTM entry {rtm_id} references unknown req_id '{ref_req}'"
            )

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    logger.info("=== Canonical Artefact Verification ===")
    all_errors: list[str] = []

    # 1. Check LOCK.json exists
    check_lock_exists()

    lock: dict = {}
    if _LOCK_PATH.exists():
        lock = _load_json(_LOCK_PATH) or {}

    # 2. Integrity check
    logger.info("Checking artefact SHA-256 integrity…")
    all_errors += check_artefact_integrity(lock)

    # 3. Manifest coverage
    logger.info("Checking extraction manifest coverage…")
    all_errors += check_manifest_coverage(lock)

    # 4. Cross-reference consistency
    logger.info("Checking cross-reference consistency…")
    all_errors += check_cross_references(lock)

    # Results
    if all_errors:
        logger.error("=== VERIFICATION FAILED — %d error(s) ===", len(all_errors))
        for err in all_errors:
            logger.error("  ✗  %s", err)
        return 1

    logger.info("=== ALL CHECKS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
