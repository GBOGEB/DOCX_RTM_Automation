# DMAIC Click-Pulse Ledger - DOCX_RTM_Automation

Date: 2026-09-10
Mode: fast human-click analogue: click, observe, change, record, repeat.

## Pulse Rule

Every pulse must advance one frame only. A frame can be a census, command, repair, proof, or next-red capture. Brute force is allowed only when each attempt leaves a receipt.

## Cadence

| Pulse | Interval | DMAIC Phase | Effort Mode | Target | Exit Condition |
| --- | --- | --- | --- | --- | --- |
| P0 | 0-15 min | Define | Scan | DOCX/RTM role and pipeline boundary | MIP tracker merged or accepted |
| P1 | 15-30 min | Measure | Census | Entry points, schemas, tests, outputs | Canonical surface map exists |
| P2 | 30-60 min | Analyse | First red | Launcher/package/CI failure | First failure captured exactly |
| P3 | 60-90 min | Improve | Repair | One canonical CLI or health check | Command changes behaviour |
| P4 | 90-120 min | Control | Receipt | Minimal generated DOCX/RTM artifact | SHA-bound proof recorded |

## First Clicks

1. Count bat/sh/python launchers and decide canonical path.
2. Run syntax/health check before touching generation logic.
3. Recurse on first red: import error, missing dependency, path drift, or schema mismatch.
4. Once green, extract the reusable skill boundary.

## Brute Force Guard

Effort is welcome, but each attempt must reduce ambiguity: fewer launchers, clearer contract, better receipt, or a named next failure.
