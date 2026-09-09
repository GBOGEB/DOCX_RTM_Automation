#!/usr/bin/env python3
"""Direct DOCX -> enhanced RTM/OTC/DEL JSON entry point.

The historical EnhancedParserEngine direct path is incomplete.  This CLI uses the
new conservative DOCX extractor to populate the engine's existing analysis-data
contract, preserving the richer relationship/statistics output without silently
returning an empty parse.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from parser.direct_docx import extract_analysis_data
from parser.engine import EnhancedParserEngine


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--config")
    args = ap.parse_args()

    analysis = extract_analysis_data(args.input)
    result = EnhancedParserEngine(args.config).parse_document(str(args.input), analysis)
    result["direct_extraction"] = analysis["direct_extraction"]

    output = args.output or Path("output") / f"{args.input.stem}_enhanced_parse.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    counts = analysis["direct_extraction"]["counts"]
    print(
        f"Wrote {output}: RTM={counts['rtm']} OTC={counts['otc']} "
        f"DEL={counts['del']} sections={counts['sections']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
