#!/usr/bin/env python3
"""Reconcile independently extracted DOCX source atoms to a governed RTM export.

Production mode is intentionally strict: the canonical side must be a controlled export
with 722 unique RTM IDs plus semantic/source identity. The contract-mirror/source side
may provide text, clauses and locations, but never canonical identity or compliance state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

RTM_ID = re.compile(r"^RTM-(\d{3})$")
TOKEN = re.compile(r"[a-z0-9]+")


def norm(text: str) -> str:
    return " ".join(TOKEN.findall((text or "").lower()))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path, mode: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", data.get("source", {})) if isinstance(data, dict) else {}
    records = data.get("records", data.get("rows", [])) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("canonical input must contain records/rows list")

    normalized = []
    ids: set[str] = set()
    for row in records:
        rid = str(row.get("controlled_id") or row.get("rtm_id") or row.get("id") or "")
        statement = str(row.get("statement") or row.get("full_verbatim_requirement") or row.get("description") or "")
        locator = str(row.get("source_locator") or row.get("locator") or row.get("section") or "")
        if not RTM_ID.fullmatch(rid):
            raise ValueError(f"invalid canonical RTM id: {rid!r}")
        if rid in ids:
            raise ValueError(f"duplicate canonical RTM id: {rid}")
        if not statement.strip():
            raise ValueError(f"{rid}: empty canonical statement")
        ids.add(rid)
        normalized.append({"id": rid, "statement": statement, "locator": locator, "norm": norm(statement)})

    if mode == "PRODUCTION":
        if len(normalized) != 722:
            raise ValueError(f"production canonical denominator must be 722, got {len(normalized)}")
        expected = {f"RTM-{i:03d}" for i in range(1, 723)}
        if ids != expected:
            missing = sorted(expected - ids)[:10]
            extra = sorted(ids - expected)[:10]
            raise ValueError(f"production RTM identity not contiguous 001..722; missing={missing}, extra={extra}")
        semantic = str(meta.get("rtm_semantic_sha256") or meta.get("semantic_sha256") or "")
        source_sha = str(meta.get("workbook_sha256") or meta.get("source_sha256") or "")
        if not re.fullmatch(r"[a-f0-9]{64}", semantic):
            raise ValueError("production canonical input missing valid RTM semantic SHA256")
        if not re.fullmatch(r"[a-f0-9]{64}", source_sha):
            raise ValueError("production canonical input missing valid source/workbook SHA256")
    return normalized, meta


def reconcile(extraction: dict[str, Any], canonical: list[dict[str, Any]]) -> dict[str, Any]:
    by_norm: dict[str, list[dict[str, Any]]] = {}
    for row in canonical:
        by_norm.setdefault(row["norm"], []).append(row)

    results = []
    counts = {"EXACT_TEXT": 0, "EXPLICIT_ID": 0, "AMBIGUOUS": 0, "UNMATCHED": 0}
    for atom in extraction.get("rtm_requirements", []):
        sid = str(atom.get("id", ""))
        text = str(atom.get("description", ""))
        candidates: list[dict[str, Any]] = []
        method = "UNMATCHED"

        if RTM_ID.fullmatch(sid):
            candidates = [row for row in canonical if row["id"] == sid]
            method = "EXPLICIT_ID" if len(candidates) == 1 else "UNMATCHED"
        else:
            candidates = by_norm.get(norm(text), [])
            if len(candidates) == 1:
                method = "EXACT_TEXT"
            elif len(candidates) > 1:
                method = "AMBIGUOUS"

        counts[method] += 1
        results.append({
            "source_atom_id": sid,
            "source_clause": atom.get("source_clause"),
            "source_kind": atom.get("source_kind"),
            "source_index": atom.get("source_index"),
            "match_method": method,
            "canonical_candidates": [row["id"] for row in candidates],
            "promotion_allowed": method in {"EXACT_TEXT", "EXPLICIT_ID"} and len(candidates) == 1,
        })

    matched_ids = {c for r in results if r["promotion_allowed"] for c in r["canonical_candidates"]}
    return {
        "classification": "RECONCILIATION_RECEIPT_NOT_COMPLIANCE",
        "source_authority": "SOURCE_ONLY",
        "canonical_authority": "GOVERNED_CANONICAL_INPUT",
        "counts": {
            "source_atoms": len(results),
            "canonical_atoms": len(canonical),
            **counts,
            "unique_canonical_matched": len(matched_ids),
            "canonical_unmatched": len(canonical) - len(matched_ids),
        },
        "results": results,
        "rules": [
            "source clause or PDF/DOCX order never creates an RTM ID",
            "exact text or explicit governed ID can propose a one-to-one binding",
            "ambiguous and unmatched atoms remain unbound",
            "reconciliation never grants compliance or release credit",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extraction", type=Path, required=True)
    ap.add_argument("--canonical", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--mode", choices=["PRODUCTION", "TEST", "COMPARATIVE"], default="PRODUCTION")
    args = ap.parse_args()

    extraction = json.loads(args.extraction.read_text(encoding="utf-8"))
    canonical, meta = load_canonical(args.canonical, args.mode)
    receipt = reconcile(extraction, canonical)
    receipt["mode"] = args.mode
    receipt["inputs"] = {
        "extraction_sha256": digest(args.extraction),
        "canonical_file_sha256": digest(args.canonical),
        "canonical_semantic_sha256": meta.get("rtm_semantic_sha256") or meta.get("semantic_sha256"),
        "canonical_source_sha256": meta.get("workbook_sha256") or meta.get("source_sha256"),
    }
    if args.mode != "PRODUCTION":
        receipt["production_credit_allowed"] = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
