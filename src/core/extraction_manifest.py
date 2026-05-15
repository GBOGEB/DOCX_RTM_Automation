#!/usr/bin/env python3
"""
Canonical Extraction Manifest Engine.

Manages the extraction_manifest.json that records every extraction run.
Enforces idempotency (skip if source SHA-256 already extracted) and
content-addresses each output artefact with a SHA-256 of its own content.

Usage (library):
    from src.core.extraction_manifest import ExtractionManifest

    manifest = ExtractionManifest()

    # Check before extraction
    if manifest.is_already_extracted(source_path, artefact_name):
        print("Already extracted — skipping")
    else:
        artefact = run_extractor(source_path, output_path)
        manifest.record(
            source_path=source_path,
            artefact_name=artefact_name,
            output_path=output_path,
            extractor_version="1.0.0",
        )
        manifest.save()
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Canonical locations relative to repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST_PATH = _REPO_ROOT / "canonical" / "artefacts" / "extraction_manifest.json"
_LOCK_PATH = _REPO_ROOT / "canonical" / "LOCK.json"

# Tool version — bump when extractor logic changes
EXTRACTOR_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# SHA-256 helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path, chunk_size: int = 65536) -> str:
    """Return hex SHA-256 of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def sha256_dict(data: dict) -> str:
    """Return hex SHA-256 of a JSON-serialised dict (sorted keys)."""
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stamp_artefact(artefact: dict, source_sha256: str) -> dict:
    """
    Add a ``_meta`` block to *artefact* containing SHA-256, timestamps, and
    source provenance.  The SHA-256 is computed *after* removing any existing
    ``_meta`` so the hash is stable across re-runs with the same content.
    """
    clean = {k: v for k, v in artefact.items() if k != "_meta"}
    content_sha = sha256_dict(clean)
    meta = {
        "sha256": content_sha,
        "source_sha256": source_sha256,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "extractor_version": EXTRACTOR_VERSION,
    }
    return {**clean, "_meta": meta}


# ---------------------------------------------------------------------------
# ExtractionManifest
# ---------------------------------------------------------------------------

class ExtractionManifest:
    """
    Tracks all extraction runs in ``canonical/artefacts/extraction_manifest.json``.

    Each entry records:
        source_file      — original filename
        source_sha256    — SHA-256 of the source binary
        artefact_name    — logical name (e.g. "master_requirements")
        output_file      — relative path of the output JSON
        extracted_at     — ISO-8601 timestamp
        extractor_version— version of the extractor script
        content_sha256   — SHA-256 of the output JSON content
    """

    def __init__(self, manifest_path: Path = _MANIFEST_PATH) -> None:
        self.path = manifest_path
        self._data: dict = self._load()

    # ------------------------------------------------------------------
    # Load / save
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with self.path.open(encoding="utf-8") as fh:
                    return json.load(fh)
            except json.JSONDecodeError as exc:
                logger.warning("Corrupt manifest at %s: %s — starting fresh", self.path, exc)
        return {"extractions": []}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)
        logger.debug("Manifest saved to %s", self.path)

    # ------------------------------------------------------------------
    # Idempotency check
    # ------------------------------------------------------------------

    def is_already_extracted(self, source_path: Path, artefact_name: str) -> bool:
        """
        Return True if a previous extraction for (source_sha256, artefact_name)
        already exists in the manifest — meaning we can skip re-extraction.
        """
        source_sha = sha256_file(source_path)
        for entry in self._data["extractions"]:
            if (
                entry.get("source_sha256") == source_sha
                and entry.get("artefact_name") == artefact_name
            ):
                logger.info(
                    "Skipping %s — already extracted (source SHA-256 matches entry %s)",
                    source_path.name,
                    entry.get("output_file"),
                )
                return True
        return False

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        source_path: Path,
        artefact_name: str,
        output_path: Path,
        extractor_version: str = EXTRACTOR_VERSION,
    ) -> dict:
        """
        Record a completed extraction.  Computes and returns the manifest entry.
        The caller is responsible for calling ``save()`` afterwards.
        """
        source_sha = sha256_file(source_path)
        content_sha = sha256_file(output_path) if output_path.exists() else ""

        entry: dict = {
            "artefact_name": artefact_name,
            "source_file": source_path.name,
            "source_sha256": source_sha,
            "output_file": str(output_path.relative_to(_REPO_ROOT)),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "extractor_version": extractor_version,
            "content_sha256": content_sha,
        }
        self._data["extractions"].append(entry)
        logger.info("Recorded extraction of %s → %s", artefact_name, output_path)
        return entry

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def next_version_path(self, artefact_name: str, base_dir: Path) -> Path:
        """
        Return the next available versioned output path, e.g.:
            canonical/artefacts/master_requirements_v3.json
        if v1 and v2 already exist.
        """
        version = 1
        while True:
            candidate = base_dir / f"{artefact_name}_v{version}.json"
            if not candidate.exists():
                return candidate
            version += 1

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[dict]:
        return list(self._data.get("extractions", []))

    def summary(self) -> str:
        lines = [f"Extraction manifest — {len(self.entries)} entries"]
        for e in self.entries:
            lines.append(
                f"  {e['artefact_name']:30s}  {e['extracted_at'][:10]}  {e['output_file']}"
            )
        return "\n".join(lines)
