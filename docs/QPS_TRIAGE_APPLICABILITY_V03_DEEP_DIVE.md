# QPS TRIAGE Applicability v0.3 — Reliability + Mission Control Deep Dive

## Decision

The merged QPS reliability bridge is a **tooling/analytical consumer**, not a second engineering authority. The correct evolution is to widen the existing QPS TRIAGE applicability contract so the bridge, Mission Control and the established 3P/MIP methods have explicit places in the same authority-safe model.

## Current evidence anchor

`GBOGEB/DOCX_RTM_Automation` PR #54 established and merged the narrow reliability consumer:

```text
exact source / QPS disposition
        -> reliability input
        -> MTBF / lambda
        -> campaign mu
        -> P(0) / P(>=1) / Poisson P(k)
        -> provenance + readiness
        -> dashboard consumer
```

The first real atom is ALAT HP-compressor offer evidence. The component MTBF is usable as a component-level analytical input, but the source keeps N-1 capacity, preserved state, common-cause consequence, recovery/acceptance and Table-10 service-event allocation open. The bridge must therefore stay fail-closed at system consequence.

## Why v0.3 is needed

Applicability v0.2 correctly defines QPS/ADR/OCD/RTM-DTM lanes and protects child authority. It does not yet make four newer distinctions explicit:

1. reliability analysis as a triage consumer lane;
2. `ACTIVE / SCENARIO_ONLY / EXCLUDED` as **model states**, not triage or engineering dispositions;
3. Mission Control as an orchestration projection with `authority_transfer=false`;
4. when to use `3PR`, `MIP`, `3PC` and `3P3` and when to stop.

## Authority stack

```text
QPS source / contract / bidder evidence
                |
                v
GBOGEB/cryoplant-project
QPS CHILD ENGINEERING AUTHORITY
                |
        child re-entry required
                |
                +-------------------------+
                |                         |
                v                         v
DOCX_RTM_Automation                  CODEX / ABACUS
TOOLING + TRIAGE                     KEB / DOW parents
                |                         |
                +------------+------------+
                             v
                  pipeline-automation-hub
                    MISSION CONTROL H4
                    route / schedule / measure
                    authority_transfer=false
```

## State-class separation

A repeated source of false promotion is reuse of words such as ACCEPT or ACTIVE across different planes. v0.3 makes the classes explicit:

| State class | Example values | Authority meaning |
|---|---|---|
| QPS child engineering | ACCEPT / DEFER / REJECT | engineering disposition only in child |
| Tooling triage | ACCEPT / DEFER / NEEDS_SOURCE / ... | whether a tooling projection is reusable |
| Reliability model | ACTIVE / SCENARIO_ONLY / EXCLUDED | whether a bounded analysis can run |
| Mission execution | DIAGNOSE / PROVE / COMMIT / STOP | scheduler/controller state only |

No class self-promotes another.

## Reliability lane contract

`TRIAGE-RELIABILITY` accepts source-bound reliability atoms, explicit scenarios, operating-state exposure, architecture response, containment/propagation and recovery data. It emits deterministic analytical projections and child re-entry requests where engineering promotion is required.

The lane is designed around a two-step distinction:

```text
native initiating event
   lambda_native(state)
          |
          +--> exposure -> mu -> P(k)
          |
          v
architecture / containment
          |
          +--> preserved/degraded state
          +--> common cause
          +--> recovery / MDT
          +--> p_propagate
          +--> event class
          v
QPS child engineering disposition
```

### Hard anti-overclaim rules

- component MTBF is not system-event MTBF;
- model `ACTIVE` is not QPS engineering `ACCEPT`;
- tooling `ACCEPT` is not child `ACCEPT`;
- Poisson confidence is not contractual event-count compliance;
- PCA/BT/PB rank and diagnose; they do not create authority.

## Method applicability

The contract reuses the existing global mesh controller rather than creating another workflow vocabulary.

### 3PR — refresh / diagnose
Use when PR/repo/evidence state materially changed or the first blocker is stale. Output current `CG/BG/EX/QH/KR` and first-red.

### MIP — improve only on evidence
Use when a measured structural or recurrence gap exists. Modernize the defect, retain only a justified innovation, and add a perpetuation/control hook.

### 3PC — bounded transaction
Use when an exact publication, child re-entry, acceptance, release or exact-SHA transition must be crossed. Prepare exact inputs, prove execution/quality/receipt, then commit or explicitly HOLD/DEFER.

### 3P3 — one generalisation proof
Use only after local DoV when the reusable cross-repo propagation edge is still unproven. Run it once, retain the receipt, then stop.

Default selector:

```text
3PR -> MIP if needed -> 3PC if transactional -> 3P3 if generalisation missing -> STOP
```

## First three-pulse wave

`H4_QPS_TRIAGE:W1` is the burn-in wave.

- **P1 / H1_QPS** — exact child source + authority/re-entry boundary;
- **P2 / H2_KEB** — semantic/provenance/state-class challenge;
- **P3 / H3_DOW** — independent denominator/runtime/readiness measurement.

H4 coordinates and vetoes false promotion. The three pulses return receipts; they are not new authorities.

## Follow-on sequence

### W2 — 3PC + MIP-I
Bound one source atom through exact consumer identity and child re-entry, then introduce the shared operating-state ledger adapter. The ledger should carry at least:

- `state_id`, `exposure_h`;
- `lambda_native_by_failure_mode`;
- `p_propagate_to_beam`;
- `event_class`;
- `MTTR_h`, `MDT_h`;
- spares/recovery identifiers;
- source/evidence class.

### W3 — 3P3 + MIP-P
After local DoV, propagate the proven pattern once into Mission Control, recurrence/REX, restart and canonical control. Do not fan out to every repository merely to create symmetry.

## Session architecture

- H4 chat/session: portfolio, method selection, first-red, receipts and stop/reallocation.
- H1 child session: engineering source/consequence/Table-10 re-entry.
- H2 KEB session: semantics/provenance/state contract.
- H3 DOW session: executable proof, denominators, KPI and independent measurement.
- dashboard session: specialist UI after model/authority contract stabilizes.

Each specialist session returns a receipt to H4; no specialist chat becomes an authority.

## DoV for v0.3

1. schema/bridge validator remains green;
2. v0.3 tests prove the reliability lane and state-class separation;
3. Mission Control projection is explicit and authority-safe;
4. 3PR/MIP/3PC/3P3 selector is represented without duplicating controller semantics;
5. existing QPS lanes/dispositions/maturity levels remain backward compatible;
6. exact-head CI is retained before merge.

Engineering / negotiation / Table-10 credit delta for this applicability change: **0**.
