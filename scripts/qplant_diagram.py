#!/usr/bin/env python3
"""Generate a versioned Graphviz diagram for QPLANT-AI-AUTO."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def build_diagram(version: str, output_dir: Path) -> Path:
    try:
        from graphviz import Digraph
    except ImportError as exc:
        raise SystemExit(
            "Python graphviz package is missing. Install with: python -m pip install graphviz"
        ) from exc

    date = dt.date.today().isoformat()
    name = f"QPLANT_AI_AUTO_Algorithm_{version}_{date}"
    dot = Digraph(comment="QPLANT-AI-AUTO governed workflow", format="png")
    dot.attr(rankdir="LR")
    nodes = {
        "A": "Baseline Project_Data.json\nRFO + ADR + OCD + RTM",
        "B": "New Input + Intent\nNEW / UPDATE / REFINE / VERBATIM\nOVERRIDE / BRANCH / MASTER",
        "C": "Parse + SHA-256 Receipt",
        "D": "Structured Output Reconciliation\nComplete state, not patch",
        "E": "Cross-pillar propagation\nRFO <-> ADR <-> OCD <-> RTM",
        "F": "Local validation\noutline <= L3 / immutable / stable IDs",
        "G": "Versioned outputs\nJSON / CSV / XLSX / MD / DOCX",
        "H": "Human review + approval",
        "I": "Next approved baseline",
    }
    for key, label in nodes.items():
        dot.node(key, label)
    for left, right in zip(nodes, list(nodes)[1:]):
        dot.edge(left, right)
    dot.edge("H", "B", label="correction / new evidence")
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = Path(dot.render(str(output_dir / name), cleanup=True))
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v1.0")
    parser.add_argument("--output-dir", type=Path, default=Path("diagrams"))
    args = parser.parse_args()
    print(build_diagram(args.version, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
