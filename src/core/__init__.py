"""Core package exports for pipeline contracts and lineage utilities."""

from src.core.artifact_alignment import build_index, verify_alignment
from src.core.idempotency_contract import (
    IdempotencyStore,
    canonical_hash,
    canonical_run_key,
)
from src.core.lineage_metadata import build_lineage_snapshot

__all__ = [
    "IdempotencyStore",
    "canonical_hash",
    "canonical_run_key",
    "build_lineage_snapshot",
    "build_index",
    "verify_alignment",
]
