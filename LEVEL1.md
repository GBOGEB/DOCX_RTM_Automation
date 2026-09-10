# GBOGEB Level 1 — DOCX RTM Automation

Status: `PC3_LEVEL1_CANDIDATE`
Target: `LEVEL_1_0`
Role: `SOURCE_EXTRACTION_RTM_WORKER`

## Index

This file is the human Level-1 navigator. Machine state is in `level1/ssot.json`; the gate manifest is `level1/manifest.json`; the reusable ChatGPT skill is under `skill/`; the executable kernel is `level1/runtime.py`.

Existing capability is reused rather than duplicated:

- `parser/engine.py` — document/RTM extraction runtime.
- `pipeline/main.py` — existing DMAIC pipeline.
- `orchestration_ts/server.ts` — TypeScript orchestration/API surface.
- `AGENT_ENTRYPOINT.md` — existing agent-facing entrypoint.

Three bounded MIP cycles drive the bootstrap:

1. PC1 — census + control plane.
2. PC2 — executable Skill/runtime/blocks/functions/agents.
3. PC3 — DMAIC + measured-only statistical analysis + CI orchestration proof.

The structural target on this branch is 12/12 = 1.0000. Observed Level-1.0 is claimed only when the PC3 exact-head workflow executes green.

## AOD

AOD means **Architecture–Orchestration–Decision** for this Level-1 contract.

### Architecture

The repository owns source extraction, RTM/OTC/DEL transformation, document-analysis outputs and its existing local pipeline/orchestration runtime. Level-1 wraps those assets with a small interoperable control plane; it does not replace them.

### Orchestration

Local flow: `source -> parser -> RTM/evidence object -> DMAIC checks -> outward result`.

Federated flow: `worker receipt -> pipeline-automation-hub -> CODEX/KEB challenge -> ABACUS/DOW roll-up -> cryoplant child disposition` when the parent contract requests it.

### Decision authority

This repo may decide whether extraction/runtime execution succeeded and may emit exact-SHA/source/output digests. It may not promote QPS engineering truth, compliance, negotiation status, bidder acceptance or child authority. Derived extraction is never allowed to masquerade as original source evidence.

### Level-1 gates

The 12 gates are: index, manifest, skill, SSOT, AOD, DMAIC, PCA, BT, executable runtime, blocks/functions, agents, orchestration. Promotion is fail-closed and CI-observed.

## DMAIC

- **Define:** bind repo role, inputs/outputs, native runtime anchors, authority and the fixed 12-gate denominator.
- **Measure:** execute `python level1/runtime.py census`; record exact tested SHA, missing gates and native-runtime visibility.
- **Analyze:** use the MIP missing-gate list first; PCA/BT are secondary diagnostics and only consume measured observations or explicit comparisons.
- **Improve:** repair the smallest executable gap, prefer reuse over duplicate implementations, and add cross-capability edges only when authority remains explicit.
- **Control:** exact-head CI compiles the runtime, exercises census/MIP/orchestration, proves no-input PCA/BT DEFER, executes the full self-test, and uploads the receipt. The first red invariant becomes the next recursive repair.

MIP semantics are: **Modernize = repair/reuse stale or missing capability; Innovate = add useful nodes/edges/functions; Perpetuate = keep the capability in motion through repeatable exact-SHA execution and receipts.**

## PCA

PCA is a **measured multivariate priority diagnostic**, not a governance score generator. `python level1/runtime.py pca --input rows.json` accepts a JSON matrix of real numeric observations. Fewer than three observations, fewer than two variables or zero variance must DEFER. The built-in synthetic dataset exists only to prove the algorithm during self-test and is explicitly marked `fixture_is_project_evidence=false`. Explained variance may inform worker allocation after adequate measured data exists; it cannot create engineering/compliance credit.

## BT

Bradley–Terry (BT) is an **observed pairwise priority/ranking diagnostic**. `python level1/runtime.py bt --input comparisons.json` accepts JSON pairs `[winner, loser]` from real comparisons. No comparisons must DEFER. BT may rank repair/feature alternatives or worker priorities; it cannot replace source evidence, acceptance predicates, physics validation or child disposition.

## Level-1.0 DoV

`LEVEL_1_0` requires all 12 census gates true **and** a green exact-head `Level 1 MIP` workflow. A structurally complete branch without executed CI remains `CANDIDATE`, not confirmed. No engineering, compliance or negotiation credit is created by Level-1 bootstrap alone.
