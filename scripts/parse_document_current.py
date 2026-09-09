#!/usr/bin/env python3
"""Current direct-DOCX extraction entrypoint.

Produces source-structured JSON that can be passed to ``EnhancedParserEngine.parse_document``
as ``analysis_data``. This keeps lexical extraction separate from downstream compliance semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from parser.source_extractor import extract_document


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="DOCX source document")
    ap.add_argument("--output", type=Path, help="JSON output path")
    args = ap.parse_args()

    result = extract_document(args.input)
    output = args.output or Path("output") / f"{args.input.stem}_source_extraction.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
