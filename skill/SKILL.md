---
name: docx-rtm-level1
description: Use in DOCX_RTM_Automation to census, modernize, repair, innovate, or perpetuate repository capability; run Level-1 checks; coordinate document/RTM extraction worker receipts; and produce measured PCA or Bradley-Terry diagnostics while preserving source provenance and QPS authority boundaries.
---

# DOCX RTM Level 1

1. Read `LEVEL1.md` and `level1/ssot.json` before acting.
2. Run `python level1/runtime.py census` to establish the current 12-gate state.
3. Run `python level1/runtime.py mip` for the smallest Modernize -> Innovate -> Perpetuate action set.
4. Reuse `parser/engine.py`, `pipeline/main.py`, `orchestration_ts/server.ts`, and existing agent surfaces instead of cloning their logic.
5. Use `python level1/runtime.py pca --input <json>` only for real measured numeric rows. No input or inadequate observations must DEFER.
6. Use `python level1/runtime.py bt --input <json>` only for explicit winner/loser comparisons. No comparisons must DEFER.
7. Run `python level1/runtime.py orchestrate` to expose blocks, agents, role, federation targets, and authority limits.
8. Run `python level1/runtime.py self-test` before claiming Level-1.0. Synthetic PCA/BT fixtures prove the engine only; they are never project evidence.
9. The worker may emit extraction/runtime/source/output receipts but may not promote QPS engineering truth, compliance, negotiation status, or replace original source evidence with derived extraction.
