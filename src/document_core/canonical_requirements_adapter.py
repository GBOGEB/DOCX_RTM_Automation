"""Fail-closed adapter from canonical master requirements to document-core records.

This module is deliberately deterministic and does not call an LLM. It accepts
only the canonical master_requirements JSON shape produced by the provider
extractor, verifies identity/count invariants, and emits a normalized
requirement-local representation suitable for later Schrijfeditor validation.

W275 scope stops at ingress normalization. It does not edit requirements,
create a canonical lock/tag, or grant QPS acceptance.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class CanonicalRequirementsError(ValueError):
    """Raised when canonical requirements violate the document-core contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CanonicalRequirementsError(message)


def _normalize_record(key: str, record: dict[str, Any], source_file: str) -> dict[str, Any]:
    req_id = record.get("req_id")
    _require(isinstance(req_id, str) and bool(req_id.strip()), f"{key}: missing req_id")
    _require(req_id == key, f"{key}: req_id mismatch ({req_id!r})")

    text = record.get("paragraph_text")
    _require(isinstance(text, str) and bool(text.strip()), f"{key}: missing paragraph_text")

    section_path = record.get("section_path", [])
    _require(isinstance(section_path, list), f"{key}: section_path must be a list")
    _require(
        all(isinstance(item, str) for item in section_path),
        f"{key}: section_path entries must be strings",
    )

    page_approx = record.get("page_approx")
    _require(
        isinstance(page_approx, int) and not isinstance(page_approx, bool) and page_approx >= 0,
        f"{key}: page_approx must be a non-negative integer",
    )

    return {
        "requirement_id": req_id,
        "text": text.strip(),
        "section_path": section_path,
        "listnum": str(record.get("listnum") or ""),
        "heading": str(record.get("listnum_heading") or ""),
        "style": str(record.get("style") or ""),
        "page_approx": page_approx,
        "source_file": source_file,
    }


def adapt_canonical_requirements(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize a canonical master-requirements object into document-core v1."""
    _require(isinstance(data, dict), "canonical payload must be an object")
    _require(data.get("type") == "master_requirements", "type must be master_requirements")

    source_file = data.get("source")
    _require(
        isinstance(source_file, str) and bool(source_file.strip()),
        "source must be a non-empty string",
    )

    requirements = data.get("requirements")
    _require(isinstance(requirements, dict), "requirements must be an object keyed by req_id")

    declared_count = data.get("record_count")
    _require(
        isinstance(declared_count, int) and not isinstance(declared_count, bool),
        "record_count must be an integer",
    )
    _require(
        declared_count == len(requirements),
        f"record_count mismatch: declared {declared_count}, observed {len(requirements)}",
    )
    _require(declared_count > 0, "canonical requirements must not be empty")

    normalized = [
        _normalize_record(key, record, source_file)
        for key, record in requirements.items()
    ]
    normalized.sort(key=lambda item: (item["page_approx"], item["requirement_id"]))

    positions = [item["page_approx"] for item in normalized]
    _require(positions == sorted(positions), "normalized page_approx sequence is not monotonic")

    section_paths = {
        tuple(item["section_path"]) for item in normalized if item["section_path"]
    }

    return {
        "schema": "gmi.document_core.requirements/v1",
        "source_file": source_file,
        "record_count": len(normalized),
        "section_path_count": len(section_paths),
        "records": normalized,
    }


def load_canonical_requirements(
    path: Path,
    *,
    expected_sha256: str | None = None,
    expected_record_count: int | None = None,
) -> tuple[dict[str, Any], str]:
    """Load, identity-check and adapt a canonical requirements JSON file."""
    _require(path.is_file(), f"canonical input not found: {path}")
    observed_sha256 = sha256_file(path)
    if expected_sha256 is not None:
        _require(
            observed_sha256 == expected_sha256,
            f"canonical SHA-256 mismatch: expected {expected_sha256}, got {observed_sha256}",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CanonicalRequirementsError(f"invalid canonical JSON: {exc}") from exc

    adapted = adapt_canonical_requirements(payload)
    if expected_record_count is not None:
        _require(
            adapted["record_count"] == expected_record_count,
            "canonical record-count mismatch: "
            f"expected {expected_record_count}, got {adapted['record_count']}",
        )
    return adapted, observed_sha256
