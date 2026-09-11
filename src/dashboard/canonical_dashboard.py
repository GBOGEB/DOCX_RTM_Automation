#!/usr/bin/env python3
"""
Canonical Artefacts Dashboard.

Reads canonical/artefacts/ JSON files and canonical/LOCK.json and renders
a summary to the terminal (plain text or rich if available). Optionally links a
QPS triage dashboard JSON artifact into the canonical dashboard index.

Usage:
    python src/dashboard/canonical_dashboard.py
    python src/dashboard/canonical_dashboard.py --json
    python src/dashboard/canonical_dashboard.py --qps-triage-dashboard output/qps_triage_dashboard.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTEFACTS_DIR = _REPO_ROOT / "canonical" / "artefacts"
_LOCK_PATH = _REPO_ROOT / "canonical" / "LOCK.json"

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError:
        return None


def _latest_artefacts() -> dict[str, Path]:
    """Return {artefact_name: latest_version_path} for artefacts in artefacts dir."""
    found: dict[str, list[tuple[int, Path]]] = {}
    for p in _ARTEFACTS_DIR.glob("*_v*.json"):
        if p.name == "extraction_manifest.json":
            continue
        parts = p.stem.rsplit("_", 1)
        if len(parts) == 2 and parts[1].startswith("v") and parts[1][1:].isdigit():
            name = parts[0]
            version = int(parts[1][1:])
            found.setdefault(name, []).append((version, p))
    return {name: sorted(versions)[-1][1] for name, versions in found.items()}


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_REPO_ROOT))
    except ValueError:
        return str(path)


def _load_qps_triage_dashboard(qps_triage_dashboard_path: str | Path | None) -> dict:
    if not qps_triage_dashboard_path:
        return {"present": False}
    path = Path(qps_triage_dashboard_path)
    data = _load_json(path)
    if not isinstance(data, dict):
        return {
            "present": False,
            "path": _relative_or_absolute(path),
            "status": "missing_or_invalid",
        }

    summary = data.get("summary", {}) if isinstance(data.get("summary", {}), dict) else {}
    counts = data.get("counts", {}) if isinstance(data.get("counts", {}), dict) else {}
    return {
        "present": True,
        "path": _relative_or_absolute(path),
        "generated_at": data.get("generated_at", "—"),
        "triage_item_count": summary.get("triage_item_count", 0),
        "traceability_row_count": summary.get("traceability_row_count", 0),
        "rtm_row_count": summary.get("rtm_row_count", 0),
        "dtm_row_count": summary.get("dtm_row_count", 0),
        "by_disposition": counts.get("by_disposition", {}),
        "by_relation": counts.get("by_relation", {}),
    }


def collect_stats(qps_triage_dashboard_path: str | Path | None = None) -> dict:
    lock = _load_json(_LOCK_PATH) or {}
    latest = _latest_artefacts()
    manifest_data = _load_json(_ARTEFACTS_DIR / "extraction_manifest.json") or {}

    stats: dict = {
        "lock_tag": lock.get("tag", "not locked"),
        "locked_at": lock.get("locked_at", "—")[:10] if lock.get("locked_at") else "—",
        "artefacts": {},
        "qps_triage_dashboard": _load_qps_triage_dashboard(qps_triage_dashboard_path),
    }

    for name, path in latest.items():
        data = _load_json(path) or {}
        entry: dict = {
            "path": str(path.relative_to(_REPO_ROOT)),
            "version": path.stem,
            "locked": name in lock.get("locked_artefacts", {}),
        }

        a_type = data.get("type", "")
        if a_type == "master_requirements":
            reqs = data.get("requirements", {})
            entry["record_count"] = len(reqs)
            entry["label"] = "Requirements"
        elif a_type == "rtm_matrix":
            entries = data.get("rtm_entries", {})
            entry["record_count"] = len(entries)
            covered = sum(
                1 for e in entries.values()
                if str(e.get("status", "")).lower() in ("covered", "complete", "yes")
            )
            entry["covered"] = covered
            entry["label"] = "RTM Entries"
        elif a_type == "offer_items":
            items = data.get("offer_items", {})
            entry["record_count"] = len(items)
            entry["label"] = "Offer Items"
        elif a_type == "offer_tables":
            rows = data.get("offer_table_rows", {})
            total_rows = sum(len(v) for v in rows.values())
            entry["record_count"] = total_rows
            entry["label"] = "Offer Table Rows"
        else:
            entry["record_count"] = data.get("record_count", "?")
            entry["label"] = a_type or name

        stats["artefacts"][name] = entry

    # Coverage calculation
    master_stats = stats["artefacts"].get("master_requirements", {})
    rtm_stats = stats["artefacts"].get("rtm_matrix", {})
    total_reqs = master_stats.get("record_count", 0)
    total_rtm = rtm_stats.get("record_count", 0)
    covered = rtm_stats.get("covered", 0)

    if total_reqs and total_rtm:
        stats["coverage_pct"] = round(100.0 * min(total_rtm, total_reqs) / total_reqs, 1)
    else:
        stats["coverage_pct"] = None

    stats["extraction_runs"] = len(manifest_data.get("extractions", []))
    return stats


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_plain(stats: dict) -> None:
    print("\n╔══════════════════════════════════════════════╗")
    print("║       CANONICAL ARTEFACTS DASHBOARD          ║")
    print("╚══════════════════════════════════════════════╝\n")
    print(f"  Lock tag   : {stats['lock_tag']}")
    print(f"  Locked at  : {stats['locked_at']}")
    print(f"  Extract runs: {stats['extraction_runs']}")
    if stats["coverage_pct"] is not None:
        print(f"  RTM Coverage: {stats['coverage_pct']}%")
    qps = stats.get("qps_triage_dashboard", {})
    if qps.get("present"):
        print(
            f"  QPS Triage: {qps.get('triage_item_count', 0)} items | "
            f"RTM {qps.get('rtm_row_count', 0)} | DTM {qps.get('dtm_row_count', 0)}"
        )
    print()
    print(f"  {'Artefact':<30} {'Version':<25} {'Records':>8}  {'Locked':>6}")
    print("  " + "-" * 75)
    for name, info in stats["artefacts"].items():
        locked_str = "✓" if info["locked"] else "✗"
        print(
            f"  {name:<30} {info['version']:<25} {str(info.get('record_count', '?')):>8}  {locked_str:>6}"
        )
    print()


def render_rich(stats: dict) -> None:
    console = Console()
    qps = stats.get("qps_triage_dashboard", {})
    qps_suffix = ""
    if qps.get("present"):
        qps_suffix = (
            f"   QPS Triage: [green]{qps.get('triage_item_count', 0)}[/green] items "
            f"RTM [green]{qps.get('rtm_row_count', 0)}[/green] "
            f"DTM [green]{qps.get('dtm_row_count', 0)}[/green]"
        )
    console.print(
        Panel.fit(
            f"[bold cyan]Canonical Artefacts Dashboard[/bold cyan]\n"
            f"Lock tag: [yellow]{stats['lock_tag']}[/yellow]   "
            f"Locked: [yellow]{stats['locked_at']}[/yellow]   "
            f"Runs: [yellow]{stats['extraction_runs']}[/yellow]"
            + (
                f"   RTM Coverage: [green]{stats['coverage_pct']}%[/green]"
                if stats["coverage_pct"] is not None
                else ""
            )
            + qps_suffix,
            border_style="cyan",
        )
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Artefact", style="cyan")
    table.add_column("Version")
    table.add_column("Label")
    table.add_column("Records", justify="right")
    table.add_column("Locked", justify="center")

    for name, info in stats["artefacts"].items():
        locked_str = "[green]✓[/green]" if info["locked"] else "[red]✗[/red]"
        table.add_row(
            name,
            info["version"],
            info.get("label", ""),
            str(info.get("record_count", "?")),
            locked_str,
        )

    console.print(table)


def render_json_output(stats: dict) -> None:
    print(json.dumps(stats, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Canonical artefacts dashboard")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--qps-triage-dashboard",
        default=None,
        help="Optional path to qps_triage_dashboard.json for QPS triage index linking",
    )
    args = parser.parse_args()

    stats = collect_stats(args.qps_triage_dashboard)

    if args.json:
        render_json_output(stats)
    elif _HAS_RICH:
        render_rich(stats)
    else:
        render_plain(stats)

    return 0


if __name__ == "__main__":
    sys.exit(main())
