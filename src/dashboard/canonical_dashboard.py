#!/usr/bin/env python3
"""Canonical Artefacts Dashboard with QPS triage evidence disposition."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTEFACTS_DIR = _REPO_ROOT / "canonical" / "artefacts"
_LOCK_PATH = _REPO_ROOT / "canonical" / "LOCK.json"

try:
    from src.dashboard.qps_receipt_consumer import build_release_baseline_evidence
except ModuleNotFoundError:
    sys.path.insert(0, str(_REPO_ROOT))
    from src.dashboard.qps_receipt_consumer import build_release_baseline_evidence

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open(encoding="utf-8") as fh:
            value = json.load(fh)
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _latest_artefacts() -> dict[str, Path]:
    found: dict[str, list[tuple[int, Path]]] = {}
    for path in _ARTEFACTS_DIR.glob("*_v*.json"):
        if path.name == "extraction_manifest.json":
            continue
        parts = path.stem.rsplit("_", 1)
        if len(parts) == 2 and parts[1].startswith("v") and parts[1][1:].isdigit():
            found.setdefault(parts[0], []).append((int(parts[1][1:]), path))
    return {name: sorted(versions)[-1][1] for name, versions in found.items()}


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_REPO_ROOT))
    except ValueError:
        return str(path)


def _load_qps_triage_dashboard(path_value: str | Path | None) -> dict:
    if not path_value:
        return {"present": False}
    path = Path(path_value)
    data = _load_json(path)
    if not isinstance(data, dict):
        return {"present": False, "path": _relative_or_absolute(path), "status": "missing_or_invalid"}
    summary = data.get("summary", {}) if isinstance(data.get("summary"), dict) else {}
    counts = data.get("counts", {}) if isinstance(data.get("counts"), dict) else {}
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


def collect_stats(
    qps_triage_dashboard_path: str | Path | None = None,
    qps_registry_receipt_path: str | Path | None = None,
    expected_git_sha: str | None = None,
) -> dict:
    lock = _load_json(_LOCK_PATH) or {}
    latest = _latest_artefacts()
    manifest_data = _load_json(_ARTEFACTS_DIR / "extraction_manifest.json") or {}
    release_evidence = build_release_baseline_evidence(
        qps_registry_receipt_path,
        expected_git_sha=expected_git_sha,
    )

    stats: dict = {
        "lock_tag": lock.get("tag", "not locked"),
        "locked_at": lock.get("locked_at", "—")[:10] if lock.get("locked_at") else "—",
        "artefacts": {},
        "qps_triage_dashboard": _load_qps_triage_dashboard(qps_triage_dashboard_path),
        "qps_triage_release_evidence": release_evidence,
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
            entry["record_count"] = len(data.get("requirements", {})); entry["label"] = "Requirements"
        elif a_type == "rtm_matrix":
            entries = data.get("rtm_entries", {})
            entry["record_count"] = len(entries)
            entry["covered"] = sum(1 for item in entries.values() if str(item.get("status", "")).lower() in ("covered", "complete", "yes"))
            entry["label"] = "RTM Entries"
        elif a_type == "offer_items":
            entry["record_count"] = len(data.get("offer_items", {})); entry["label"] = "Offer Items"
        elif a_type == "offer_tables":
            entry["record_count"] = sum(len(rows) for rows in data.get("offer_table_rows", {}).values()); entry["label"] = "Offer Table Rows"
        else:
            entry["record_count"] = data.get("record_count", "?"); entry["label"] = a_type or name
        stats["artefacts"][name] = entry

    master = stats["artefacts"].get("master_requirements", {})
    rtm = stats["artefacts"].get("rtm_matrix", {})
    total_reqs, total_rtm = master.get("record_count", 0), rtm.get("record_count", 0)
    stats["coverage_pct"] = round(100.0 * min(total_rtm, total_reqs) / total_reqs, 1) if total_reqs and total_rtm else None
    stats["extraction_runs"] = len(manifest_data.get("extractions", []))
    return stats


def render_plain(stats: dict) -> None:
    print("\nCANONICAL ARTEFACTS DASHBOARD\n")
    print(f"  Lock tag    : {stats['lock_tag']}")
    print(f"  Locked at   : {stats['locked_at']}")
    print(f"  Extract runs: {stats['extraction_runs']}")
    if stats["coverage_pct"] is not None:
        print(f"  RTM Coverage: {stats['coverage_pct']}%")
    qps = stats.get("qps_triage_dashboard", {})
    if qps.get("present"):
        print(f"  QPS Triage  : {qps.get('triage_item_count', 0)} items | RTM {qps.get('rtm_row_count', 0)} | DTM {qps.get('dtm_row_count', 0)}")
    evidence = stats["qps_triage_release_evidence"]
    print(f"  QPS Evidence: {evidence['disposition']} — {evidence['reason']}")
    print()
    print(f"  {'Artefact':<30} {'Version':<25} {'Records':>8}  {'Locked':>6}")
    print("  " + "-" * 75)
    for name, info in stats["artefacts"].items():
        print(f"  {name:<30} {info['version']:<25} {str(info.get('record_count', '?')):>8}  {('✓' if info['locked'] else '✗'):>6}")
    print()


def render_rich(stats: dict) -> None:
    console = Console()
    qps = stats.get("qps_triage_dashboard", {})
    evidence = stats["qps_triage_release_evidence"]
    disposition_colour = "green" if evidence["disposition"] == "ACCEPT" else "yellow"
    qps_suffix = ""
    if qps.get("present"):
        qps_suffix = f"   QPS: [green]{qps.get('triage_item_count', 0)}[/green] items RTM [green]{qps.get('rtm_row_count', 0)}[/green] DTM [green]{qps.get('dtm_row_count', 0)}[/green]"
    console.print(Panel.fit(
        f"[bold cyan]Canonical Artefacts Dashboard[/bold cyan]\n"
        f"Lock: [yellow]{stats['lock_tag']}[/yellow]   Runs: [yellow]{stats['extraction_runs']}[/yellow]"
        + qps_suffix
        + f"\nQPS Evidence: [{disposition_colour}]{evidence['disposition']}[/{disposition_colour}] — {evidence['reason']}",
        border_style="cyan",
    ))
    table = Table(show_header=True, header_style="bold magenta")
    for column in ("Artefact", "Version", "Label", "Records", "Locked"):
        table.add_column(column)
    for name, info in stats["artefacts"].items():
        table.add_row(name, info["version"], info.get("label", ""), str(info.get("record_count", "?")), "✓" if info["locked"] else "✗")
    console.print(table)


def render_json_output(stats: dict) -> None:
    print(json.dumps(stats, indent=2, ensure_ascii=False))


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Canonical artefacts dashboard")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--qps-triage-dashboard", default=None)
    parser.add_argument("--qps-registry-receipt", default=None, help="Wave 9 qps_triage_ci_registry_receipt.json")
    parser.add_argument("--expected-git-sha", default=None, help="Exact 40-character source Git SHA required for ACCEPT")
    args = parser.parse_args()
    stats = collect_stats(args.qps_triage_dashboard, args.qps_registry_receipt, args.expected_git_sha)
    if args.json:
        render_json_output(stats)
    elif _HAS_RICH:
        render_rich(stats)
    else:
        render_plain(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
