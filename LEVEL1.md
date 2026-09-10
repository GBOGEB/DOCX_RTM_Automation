# GBOGEB Level 1 — DOCX RTM Automation

Status: `PC1_CONTROL_PLANE`
Target: `LEVEL_1_0`
Role: `SOURCE_EXTRACTION_RTM_WORKER`

## Index

This file is the human Level-1 navigator. Machine state is in `level1/ssot.json`; the gate manifest is `level1/manifest.json`; the reusable ChatGPT skill is under `skill/`; the executable kernel is `level1/runtime.py` once PC2 lands.

Existing capability is reused rather than duplicated:

- `parser/engine.py` — document/RTM extraction runtime.
- `pipeline/main.py` — existing DMAIC pipeline.
- `orchestration_ts/server.ts` — TypeScript orchestration/API surface.
- `AGENT_ENTRYPOINT.md` — existing agent-facing entrypoint.

Three bounded MIP cycles drive the bootstrap:

1. PC1 — census + control plane.
2. PC2 — executable Skill/runtime/blocks/functions/agents.
3. PC3 — DMAIC + measured-only statistical analysis + CI orchestration proof.

The expected structural levels are 4/12 = 0.3333 after PC1, 9/12 = 0.7500 after PC2, and 12/12 = 1.0000 only after PC3 content exists. Observed Level-1.0 is not claimed until the PC3 workflow executes green.

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
