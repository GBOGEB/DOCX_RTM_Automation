#!/usr/bin/env python3
"""Resolve governed visual-style font requests against installed families.

The source style remains user-authored. This script emits a derived render-host
style plus a machine receipt so font substitution is explicit and reproducible.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


class FontResolutionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def installed_font_families() -> list[str]:
    try:
        result = subprocess.run(
            ["fc-list", "--format=%{family}\n"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise FontResolutionError("fontconfig fc-list is required for render-host resolution") from exc
    if result.returncode != 0:
        raise FontResolutionError(result.stderr.strip() or "fc-list failed")

    families: set[str] = set()
    for line in result.stdout.splitlines():
        for item in line.split(","):
            name = item.strip()
            if name:
                families.add(name)
    if not families:
        raise FontResolutionError("fc-list returned no installed font families")
    return sorted(families, key=str.casefold)


def _lookup(installed: list[str]) -> dict[str, str]:
    return {name.casefold(): name for name in installed}


def resolve_style(style: dict[str, Any], installed: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved = copy.deepcopy(style)
    lookup = _lookup(installed)
    role_receipts: dict[str, Any] = {}

    fonts = style.get("fonts", {})
    if not fonts:
        raise FontResolutionError("style contains no font roles")

    for role, spec in fonts.items():
        requested = str(spec.get("name", "")).strip()
        fallbacks = [str(x).strip() for x in spec.get("fallback", []) if str(x).strip()]
        candidates = [requested, *fallbacks]
        selected = next((lookup[c.casefold()] for c in candidates if c.casefold() in lookup), None)
        if selected is None:
            raise FontResolutionError(
                f"font role {role!r} has no installed candidate: {candidates}"
            )

        resolved["fonts"][role]["requested_name"] = requested
        resolved["fonts"][role]["name"] = selected
        role_receipts[role] = {
            "requested": requested,
            "candidates": candidates,
            "selected": selected,
            "fallback_used": selected.casefold() != requested.casefold(),
        }

    receipt = {
        "schema": "docx_rtm.visual_font_resolution/1.0.0",
        "resolver": "fontconfig-exact-family",
        "installed_family_count": len(installed),
        "roles": role_receipts,
        "status": "PASS",
    }
    resolved["font_resolution"] = receipt
    return resolved, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-style", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source_style.read_text(encoding="utf-8"))
    try:
        resolved, receipt = resolve_style(source, installed_font_families())
    except (OSError, json.JSONDecodeError, FontResolutionError) as exc:
        print(f"FAIL: {exc}")
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(resolved, indent=2) + "\n", encoding="utf-8")
    receipt["source_style_sha256"] = sha256_file(args.source_style)
    receipt["resolved_style_sha256"] = sha256_file(args.output)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
