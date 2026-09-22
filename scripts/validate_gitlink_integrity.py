#!/usr/bin/env python3
"""Fail closed when tracked gitlinks and .gitmodules disagree."""

from __future__ import annotations

import configparser
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GITMODULES = ROOT / ".gitmodules"


def run_git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def tracked_gitlinks() -> dict[str, str]:
    rows: dict[str, str] = {}
    output = run_git("ls-files", "-s")
    for line in output.splitlines():
        if not line:
            continue
        mode, obj_sha, rest = line.split(maxsplit=2)
        if mode != "160000":
            continue
        _stage, path = rest.split("\t", 1)
        rows[path] = obj_sha
    return rows


def declared_submodules() -> dict[str, str]:
    if not GITMODULES.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(GITMODULES, encoding="utf-8")
    declared: dict[str, str] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        path = parser.get(section, "path", fallback="").strip()
        url = parser.get(section, "url", fallback="").strip()
        if path:
            declared[path] = url
    return declared


def main() -> int:
    gitlinks = tracked_gitlinks()
    declared = declared_submodules()

    errors: list[str] = []

    orphan_gitlinks = sorted(set(gitlinks) - set(declared))
    if orphan_gitlinks:
        errors.append(
            "tracked gitlink(s) missing .gitmodules declaration: "
            + ", ".join(orphan_gitlinks)
        )

    dangling_declarations = sorted(set(declared) - set(gitlinks))
    if dangling_declarations:
        errors.append(
            ".gitmodules path(s) not tracked as gitlinks: "
            + ", ".join(dangling_declarations)
        )

    missing_urls = sorted(path for path, url in declared.items() if not url)
    if missing_urls:
        errors.append(
            ".gitmodules declaration(s) missing URL: " + ", ".join(missing_urls)
        )

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    print(
        "PASS repository gitlink integrity "
        f"gitlinks={len(gitlinks)} declared_submodules={len(declared)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
