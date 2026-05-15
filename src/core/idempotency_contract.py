#!/usr/bin/env python3
"""Canonical idempotency helpers for repeat-safe execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


def canonical_serialize(payload: Any) -> str:
    """Serialize a payload in a deterministic, hash-safe way."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def canonical_hash(payload: Any) -> str:
    """Create canonical SHA256 hash for any payload."""
    if isinstance(payload, bytes):
        return hashlib.sha256(payload).hexdigest()
    return hashlib.sha256(canonical_serialize(payload).encode("utf-8")).hexdigest()


def canonical_run_key(scope: str, payload: Any) -> str:
    """Build stable run key for idempotent operations."""
    return f"{scope}:{canonical_hash(payload)}"


class IdempotencyStore:
    """File-backed idempotency store with replay-safe cached responses."""

    def __init__(self, state_file: Path):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if not self.state_file.exists():
            return {}
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self) -> None:
        self.state_file.write_text(
            json.dumps(self._state, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def get(self, run_key: str) -> Optional[Dict[str, Any]]:
        return self._state.get(run_key)

    def put(self, run_key: str, request_payload: Any, response_payload: Any) -> None:
        self._state[run_key] = {
            "request_hash": canonical_hash(request_payload),
            "response_hash": canonical_hash(response_payload),
            "response_payload": response_payload,
        }
        self._save()
