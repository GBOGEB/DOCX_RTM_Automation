#!/usr/bin/env python3
"""Verify or refresh recursive artifact alignment lock index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.artifact_alignment import build_index, verify_alignment


def main() -> int:
    parser = argparse.ArgumentParser(description="Recursive artifact alignment verifier")
    parser.add_argument(
        "--manifest",
        default="config/recursive_alignment_manifest.json",
        help="Path to recursive alignment manifest",
    )
    parser.add_argument(
        "--index",
        default="config/recursive_alignment_index.json",
        help="Path to locked recursive alignment index",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh lock index from current repository state",
    )
    args = parser.parse_args()

    manifest_path = PROJECT_ROOT / args.manifest
    index_path = PROJECT_ROOT / args.index

    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if args.refresh:
        index = build_index(PROJECT_ROOT, manifest)
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
        print(f"✅ Refreshed recursive alignment index: {index_path}")
        return 0

    if not index_path.exists():
        print(f"❌ Lock index missing: {index_path}")
        print("Run with --refresh to generate it.")
        return 1

    result = verify_alignment(PROJECT_ROOT, manifest_path, index_path)
    if result["ok"]:
        print(f"✅ Recursive artifact alignment OK ({result['checked']} artifacts)")
        return 0

    print("❌ Recursive artifact alignment FAILED")
    if result["missing"]:
        print(f"Missing: {', '.join(result['missing'])}")
    if result["drifted"]:
        print(f"Drifted: {', '.join(result['drifted'])}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

