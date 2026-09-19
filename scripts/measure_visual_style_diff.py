#!/usr/bin/env python3
"""Measure visual delta between approved baseline PNGs and a style candidate.

This is a regression receipt, not a quality score. A style candidate is
expected to differ visually while preserving page geometry and semantic
content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops


def _pages(root: Path) -> list[Path]:
    return sorted(root.glob("ADR-001-page-*.png"))


def _changed_ratio(a: Image.Image, b: Image.Image, threshold: int) -> float:
    if a.size != b.size:
        return 1.0
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB")).convert("L")
    hist = diff.histogram()
    changed = sum(hist[threshold + 1 :])
    return changed / float(a.size[0] * a.size[1])


def measure(baseline_dir: Path, candidate_dir: Path, threshold: int = 8) -> dict:
    baseline = _pages(baseline_dir)
    candidate = _pages(candidate_dir)
    page_count_equal = len(baseline) == len(candidate) and len(candidate) > 0

    pages = []
    ratios = []
    for index in range(max(len(baseline), len(candidate))):
        if index >= len(baseline) or index >= len(candidate):
            pages.append(
                {
                    "page": index + 1,
                    "status": "MISSING_PAGE",
                    "baseline": str(baseline[index]) if index < len(baseline) else None,
                    "candidate": str(candidate[index]) if index < len(candidate) else None,
                }
            )
            ratios.append(1.0)
            continue

        with Image.open(baseline[index]) as base_img, Image.open(candidate[index]) as cand_img:
            ratio = _changed_ratio(base_img, cand_img, threshold)
            ratios.append(ratio)
            pages.append(
                {
                    "page": index + 1,
                    "status": "MEASURED",
                    "baseline_size": list(base_img.size),
                    "candidate_size": list(cand_img.size),
                    "size_equal": base_img.size == cand_img.size,
                    "changed_pixel_ratio": round(ratio, 8),
                }
            )

    total = sum(ratios) / len(ratios) if ratios else 0.0
    return {
        "schema": "docx_rtm.visual_style_diff/1.0.0",
        "page_count_equal": page_count_equal,
        "baseline_pages": len(baseline),
        "candidate_pages": len(candidate),
        "threshold": threshold,
        "mean_changed_pixel_ratio": round(total, 8),
        "visual_change_detected": total > 0.0005,
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=8)
    args = parser.parse_args()

    receipt = measure(args.baseline_dir, args.candidate_dir, args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))

    if not receipt["page_count_equal"]:
        return 2
    if not receipt["visual_change_detected"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
