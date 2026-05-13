#!/usr/bin/env python3
"""
Render canonical artefact reports.

Called by .github/workflows/render_canonical.yml.
Generates:
  - canonical/REPORT.md          (human-readable summary committed to repo)
  - docs/CANONICAL_SSOT.md       (rendered index for documentation)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Reuse stats collector from dashboard
sys.path.insert(0, str(_REPO_ROOT / "src"))
from dashboard.canonical_dashboard import collect_stats  # type: ignore


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _badge(value: bool, yes: str = "✅", no: str = "❌") -> str:
    return yes if value else no


def _pct_bar(pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# REPORT.md
# ---------------------------------------------------------------------------

def render_report(stats: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lock_tag = stats["lock_tag"]
    locked_at = stats["locked_at"]
    runs = stats["extraction_runs"]

    lines = [
        "# Canonical Artefacts Report",
        "",
        f"> Auto-generated at {now} by `scripts/render_canonical_report.py`.",
        "",
        "## Overview",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Lock tag | `{lock_tag}` |",
        f"| Locked at | {locked_at} |",
        f"| Total extraction runs | {runs} |",
    ]

    if stats["coverage_pct"] is not None:
        pct = stats["coverage_pct"]
        bar = _pct_bar(pct)
        lines += [
            f"| RTM coverage | `{bar}` {pct}% |",
        ]

    lines += [
        "",
        "## Artefacts",
        "",
        "| Artefact | Version | Records | Locked |",
        "|----------|---------|---------|--------|",
    ]

    for name, info in stats["artefacts"].items():
        locked_str = _badge(info["locked"])
        lines.append(
            f"| `{name}` | `{info['version']}` | {info.get('record_count', '?')} | {locked_str} |"
        )

    lines += [
        "",
        "## Hierarchy",
        "",
        "```",
        "master_requirements  ← ROOT: all requirements (keyed by req_id)",
        "       ↑",
        "rtm_matrix           ← references req_ids + listnum hooks",
        "       ↑",
        "offer_items          ← 50 offer items, references req_ids",
        "       ↑",
        "offer_tables         ← PDF table rows, keyed by offer_id",
        "```",
        "",
        "## User Workflow",
        "",
        "```bash",
        "# 1. Drop binaries (gitignored)",
        "cp /path/to/MASTER.docx canonical/inputs/",
        "",
        "# 2. Extract (idempotent)",
        "python main.py --extract-canonical",
        "",
        "# 3. Verify",
        "python scripts/verify_canonical.py",
        "",
        "# 4. Lock + tag",
        "python scripts/lock_canonical.py --tag",
        "",
        "# 5. Delete binaries",
        "rm canonical/inputs/*.docx canonical/inputs/*.xlsx canonical/inputs/*.pdf",
        "",
        "# 6. Push",
        "git push && git push --tags",
        "```",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# docs/CANONICAL_SSOT.md
# ---------------------------------------------------------------------------

def render_ssot_index(stats: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lock_tag = stats["lock_tag"]

    lines = [
        "# Canonical SSOT — Artefact Index",
        "",
        f"> Auto-generated at {now}.",
        "> Source of truth for all structured requirements, RTM, and offer data.",
        "",
        "## Latest Lock",
        "",
        f"Tag: `{lock_tag}`",
        "",
        "## Artefact Files",
        "",
    ]

    for name, info in stats["artefacts"].items():
        lines += [
            f"### `{name}`",
            "",
            f"- **File**: `{info['path']}`",
            f"- **Version**: `{info['version']}`",
            f"- **Records**: {info.get('record_count', '?')}",
            f"- **Locked**: {_badge(info['locked'])}",
            "",
        ]

    lines += [
        "## Cross-References",
        "",
        "| From | → | To | Field |",
        "|------|---|-----|-------|",
        "| `rtm_matrix` | → | `master_requirements` | `req_id` |",
        "| `offer_items` | → | `master_requirements` | `req_id` |",
        "| `offer_tables` | → | `offer_items` | `offer_id` |",
        "",
        "See [canonical/README.md](../canonical/README.md) for full documentation.",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    stats = collect_stats()

    report_path = _REPO_ROOT / "canonical" / "REPORT.md"
    ssot_path = _REPO_ROOT / "docs" / "CANONICAL_SSOT.md"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    ssot_path.parent.mkdir(parents=True, exist_ok=True)

    report_path.write_text(render_report(stats), encoding="utf-8")
    print(f"Written: {report_path.relative_to(_REPO_ROOT)}")

    ssot_path.write_text(render_ssot_index(stats), encoding="utf-8")
    print(f"Written: {ssot_path.relative_to(_REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
