# QPS TRIAGE Reliability — Global Roll-up and 3P/MIP Control v1

Status: **3PR pulse 1 executed / MIP hardening admitted**  
Local tooling repo: `GBOGEB/DOCX_RTM_Automation`  
QPS engineering authority: `GBOGEB/cryoplant-project`  
Global controller semantics: `GBOGEB/CODEX`  
Runtime orchestration plane: `GBOGEB/ABACUS`  
Grand-mission control: `GBOGEB/pipeline-automation-hub`

## 1. Why this roll-up exists

The reliability work has now crossed three distinct boundaries and must not be treated as a slide-only or repo-local feature:

1. **Governed evidence runtime** — merged PR #53 proved exact-head Wave 8 -> Wave 9 -> Wave 10 ACCEPT -> Wave 11 PROMOTE and added measured intake/traceability census.
2. **Reliability analysis consumer** — merged PR #54 added the narrow five-atom reliability bridge and preserved source/architecture gates without engineering promotion.
3. **Federation/scout layer** — PR #55 exposes reusable PCA/math diagnostics while retaining QPS/visual/math-provider authority boundaries.

The next problem is therefore not another reliability framework. It is **canonical QPS TRIAGE applicability + controlled propagation**.

## 2. Authority map

| Plane | Repository | Authority / role |
|---|---|---|
| Global closure semantics | `GBOGEB/CODEX` | owns mesh closure-control method semantics; may route/classify, not promote QPS engineering truth |
| Runtime orchestration | `GBOGEB/ABACUS` | execution/orchestration plane for cross-repo runtime proof |
| QPS child engineering | `GBOGEB/cryoplant-project` | engineering truth, child dispositions, Mission Control H4_QPS_TRIAGE |
| Tooling / projection | `GBOGEB/DOCX_RTM_Automation` | QPS triage parser, governed receipts, reliability evidence consumer |
| Fleet / grand missions | `GBOGEB/pipeline-automation-hub` | grand-mission genealogy/scaling only; no child authority transfer |

## 3. QPS TRIAGE applicability conclusion

**Do not create a fifth `TRIAGE-RELIABILITY` lane.** Reliability is cross-cutting and already decomposes cleanly across the controlled lanes in `federation/ADR_OCD/qps_triage_applicability.yaml`:

- `TRIAGE-QPS` — contractual reliability requirement, event-count or campaign obligation;
- `TRIAGE-ADR` — redundancy, common-cause, preserved-state, architecture consequence and reliability design decisions;
- `TRIAGE-OCD` — campaign state, degraded mode, recovery, maintenance and operating scenario;
- `TRIAGE-RTM-DTM` — source identity, derivation, evidence maturity, deliverable and traceability edges.

A reliability item may have one primary lane and secondary lanes. Topic != lane. This avoids a competing reliability SSOT and preserves child authority.

## 4. Current measured state from the reliability pulses

### PR #53 — exact-SHA governed runtime

Observed repaired-head proof:

- RTM `3/3`, OTC `1/1`, DTM `1/1`;
- triage items `5/5`;
- traceability `5/5` items, `11` rows;
- source-intake fraction `1.0`;
- traceability fraction `1.0`;
- Wave 10 `ACCEPT`;
- Wave 11 `PROMOTE`.

Maturity remains intentionally non-closed: `DEFER=3`, `NEEDS_REVIEW=2`; evidence classes `structured=3`, `traceable=2`.

### PR #54 — reliability consumer

The five pilot component classes are:

- HP compressor;
- PVPS;
- cold-compressor train;
- turbine/expander;
- QPLANT Class-A system campaign.

The first real ALAT HP-compressor source atom is exact-source bound but remains `SCENARIO_ONLY / component_only`; selected-design N-1 capacity, common-cause consequence, preserved state and acceptance remain open. This is a correct fail-closed outcome.

## 5. Mesh-closure classification — first execution

Current classification: **HARDENING**.

- **CG** — canonical cross-repo reliability applicability profile is child-bound, exact-source aware, measurable, and reusable by Mission Control without creating a new authority lane.
- **BG** — the generic TRIAGE contract already accepts `reliability_decision`, but the cross-lane reliability evidence profile and Mission Control binding are not yet explicit/canonical.
- **EX** — local execution exists and is >0: #53 exact-SHA governed runtime and #54 focused reliability bridge both executed and merged.
- **QH** — local quality is acceptable; substantive reliability maturity is deliberately mixed and therefore cannot be blanket-promoted.
- **KR** — merged exact-SHA receipts and source-bound ALAT HP evidence provide durable evidence.
- **DR** — QPS child authority, H4_QPS_TRIAGE, and GM-IV F01 tooling pilot are all present.
- **SR** — existing lane semantics are compatible; no new reliability lane is required.
- **WD** — continue with one bounded MIP hardening pass, then one transactional 3PC, then one 3P3 propagation proof if generalisation is still missing.
- **PB** — measured intake/traceability may be reported; no engineering/compliance/negotiation/release credit is created by this roll-up.

## 6. Three-pulse wave configuration

### Pulse R — `3PR-QRT-01` — Refresh / diagnose / re-entry map

Purpose: establish exact current state before changing contracts.

Outputs:

1. bind #53/#54/#55 lineage;
2. map every reliability atom to existing QPS TRIAGE lanes;
3. identify current BG and next CG;
4. bind Mission Control `H4_QPS_TRIAGE` and Grand Mission `GM-IV/F01` relationship;
5. freeze no-new-lane decision unless evidence disproves it.

**Pulse R is now STARTED and its first diagnosis is recorded in this document.**

### Pulse C — `3PC-QRT-02` — Prepare / Prove / Commit child transaction

Purpose: make the profile child-native and exact-SHA transactional.

Target transaction:

- prepare a machine-readable reliability applicability profile;
- prove lane assignment + authority preservation + source identity + maturity semantics on exact SHA;
- commit it through the QPS child control lane;
- return the child receipt to the tooling consumer without self-promotion.

### Pulse G — `3P3-QRT-03` — Propagation/generalisation proof

Purpose: prove reuse once local child DoV is satisfied.

Consumers to prove without authority transfer:

- `GBOGEB/CODEX` — controller/semantic routing;
- `GBOGEB/ABACUS` — runtime/orchestration consumption;
- `GBOGEB/pipeline-automation-hub` — GM-IV/F01 mission-status consumption;
- `GBOGEB/DOCX_RTM_Automation` — tooling projection/reliability consumer.

Stop after one successful generalisation proof. Do not repeat propagation ceremonially.

## 7. MIP sequence between Pulse R and Pulse C

### M — Modernize

- codify the reliability cross-lane profile rather than relying on prose;
- add exact source / evidence maturity / architecture completeness fields where the current generic contract is too implicit;
- retain the four existing TRIAGE lanes.

### I — Innovate

Add a measured reliability maturity vector that separates:

1. source identity;
2. upstream disposition;
3. model/unit consistency;
4. architecture completeness;
5. system-consequence eligibility;
6. traceability/deliverable binding.

This vector is diagnostic/control evidence, not engineering acceptance.

### P — Perpetuate

Burn the method into durable controls:

- machine-readable profile;
- validator/tests;
- exact-SHA receipt;
- Mission Control pointer;
- restart/handover card;
- stop/re-entry rules.

## 8. Mission alignment

### Horizontal Mission Control

Primary horizontal lane: **H4_QPS_TRIAGE**.

The reliability roll-up is a TRIAGE applicability/control concern. H1/H2/H3 remain supporting evidence/semantic/consumer surfaces only where exact payloads are required; they must not be promoted merely because reliability math exists.

### Local QPS mission

The work is a tooling/analysis projection under QPS child authority. Any engineering promotion must re-enter `GBOGEB/cryoplant-project` against child-controlled evidence.

### Grand Mission fleet

`GBOGEB/DOCX_RTM_Automation` is already a controlled `GM-IV` pilot frontier (`F01`). The reliability bridge is therefore a useful GM-IV propagation specimen, but **GM-IV status must only change after Pulse G exact-SHA propagation proof**.

## 9. Sub-chat / session split

Recommended bounded sessions:

1. **QRT-A / Applicability** — child profile, lane mapping, authority and maturity vector;
2. **QRT-B / Evidence burn-down** — bind the five pilot atoms to real source/architecture evidence, starting with ALAT HP compressor;
3. **QRT-C / Propagation** — CODEX + ABACUS + Mission Fleet consumer proof after child DoV;
4. **QRT-D / Presentation reuse** — feed only accepted/controlled outputs back into PPT/Word/Excel engineering pack generation.

These sessions are parallel only where they do not share the same first blocker.

## 10. Next narrow victory

**MIP-Modernize first:** create and child-bind the machine-readable reliability applicability profile using the four existing lanes, then validate the five current reliability atoms against it. No new dashboard or global score before that exact-SHA child receipt exists.
