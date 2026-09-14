# QPS TRIAGE Reliability — Global Roll-up and 3P/MIP Control v1.1

Status: **W1 3PR + MIP-M burned in / W2 3PC + MIP-I HOLD on repository-local runtime admission**  
Tooling / analytical consumer: `GBOGEB/DOCX_RTM_Automation`  
QPS engineering authority: `GBOGEB/cryoplant-project`  
Global controller semantics: `GBOGEB/CODEX`  
Independent runtime / measurement plane: `GBOGEB/ABACUS`  
Grand-mission / Mission Control: `GBOGEB/pipeline-automation-hub`

## 1. Executive conclusion

The QPS reliability work is no longer a repo-local reliability feature. It is a
controlled applicability profile spanning child engineering authority, tooling,
semantic challenge, independent measurement, and Mission Control.

The canonical selector is:

`3PR -> MIP only if a measured structural/recurrence gap exists -> 3PC if a bounded transaction remains -> one 3P3 if reusable propagation proof is missing -> STOP`

This selector is now the burn-in method for H4 QPS TRIAGE. Do not invent another
3P family or another reliability framework unless a new measured failure class
requires it.

Current state:

- W1 `3PR + MIP-M`: **CONTROL / bounded DoV**;
- P1 child content boundary: **PASS/CANONICAL**;
- P2 semantic/provenance challenge: **PASS/CANONICAL**;
- P3 five-atom independent baseline: **PASS/CANONICAL**;
- one retained P1 runtime KR: **DEFER / repository-local Actions admission**;
- W2 `3PC + MIP-I`: **HOLD**;
- W3 `3P3 + MIP-P`: **gated by W2 local DoV**.

The latest exact-head child probe is `GBOGEB/cryoplant-project#1135` at
`90322dc4d7f299f737e42bf45effa36300f367fa`. The intended applicability job
failed before execution with `runner_id=0` and zero steps. This is a platform /
repository admission first-red, not a validator, profile, model, semantic, or
engineering failure.

## 2. Global authority and mission map

| Plane | Repository | Authority / role | Current H4 relation |
|---|---|---|---|
| QPS child engineering | `GBOGEB/cryoplant-project` | engineering truth, source consequence, child disposition and re-entry | H1 source/authority + P1 runtime cell |
| Tooling / projection | `GBOGEB/DOCX_RTM_Automation` | parser, receipts, OFFER profile, reliability analytical consumer | controlled tooling projection |
| Semantic / governance | `GBOGEB/CODEX` | semantics, provenance, state separation, federation challenge | H2 PASS/CANONICAL; return to control |
| Independent runtime / measurement | `GBOGEB/ABACUS` | denominator, executable proof, independent readiness/measurement | H3 PASS/CANONICAL; return to control |
| Mission Control / fleet | `GBOGEB/pipeline-automation-hub` | H4 scheduling, veto, receipts, stop/re-entry, GM genealogy | coordinator only; no child authority |

Authority does not flow backwards from a dashboard, PCA, Bradley-Terry pressure,
Mission Control score, tooling merge, or model state into QPS engineering truth.

## 3. QPS TRIAGE applicability model

Reliability is cross-cutting. The child still has exactly four primary
engineering-routing lanes:

- `TRIAGE-QPS` — contractual reliability requirement, event/campaign obligation,
  availability or acceptance threshold;
- `TRIAGE-ADR` — redundancy, common cause, preserved state, architecture
  consequence and reliability design decision;
- `TRIAGE-OCD` — campaign state, degraded mode, recovery, maintenance and
  operating-state exposure;
- `TRIAGE-RTM-DTM` — exact source identity, evidence maturity, requirement and
  deliverable traceability.

`TRIAGE-RELIABILITY` is canonical only as a **non-authoritative analytical
overlay**. It may consume an atom and produce MTBF/lambda/state-exposure/P(0)/
P(>=1)/Poisson/provenance/readiness diagnostics, but it is not a fifth child
engineering lane and cannot grant `ACCEPT` or Table-10 credit.

One primary child lane plus optional analytical overlay and secondary impacts is
the governing assignment model.

## 4. Canonical W1 burn-in

W1 used `3PR + MIP-M` because the starting problem was applicability and
cross-repo state clarity rather than a new engineering transaction.

### Pulse 1 — Refresh / authority map

Resolved the current repo/PR/source state and kept QPS engineering authority in
the child. This prevented tooling and Grand Mission artifacts from becoming a
competing SSOT.

### Pulse 2 — Reconcile / semantic challenge

Bound the canonical TRIAGE dispositions, evidence/provenance semantics,
analytical-overlay boundary, and source-versus-scenario state separation. H2
closed and returned to control.

### Pulse 3 — Re-entry / independent proof

Bound the child-native applicability boundary and the independent five-atom
consumer baseline. H1 content and H3 measurement closed; only one child runtime
receipt remains externally deferred.

### MIP-M — Modernize

The structural gap was real: applicability existed across prose and tooling but
was not child-native and machine-readable. MIP-M therefore codified the child
profile, validator, exact-source rules, maturity vector, Mission Control hooks,
and no-promotion invariants. This is now canonical and should not be reworked
without a material source/repo/evidence change.

Canonical W1 result: `BOUNDED_DOV_WITH_ONE_EXTERNAL_RUNTIME_DEFER`.

## 5. Current first-red and control decision

The exact-head runtime probe deliberately re-triggered the existing child
workflow without changing validator logic.

Observed:

- child PR: `GBOGEB/cryoplant-project#1135`;
- exact head: `90322dc4d7f299f737e42bf45effa36300f367fa`;
- workflow: `QPS TRIAGE Reliability Applicability`;
- run: `34825502815`;
- job: `103916589064`;
- `runner_id = 0`;
- executed steps = `0`;
- conclusion = `failure`.

Classification: `REX_006_PREEXECUTION_REPO_LOCAL_ADMISSION`, mapped to the
existing non-compensating veto `QPS_REPO_LOCAL_RUNNER_923`.

Therefore:

- do not repair validator/profile/model code;
- do not start another method PR;
- do not release W2;
- repair/restore repository-local Actions admission or attach the supported
  runner path;
- rerun the same applicability workflow unchanged;
- platform victory is `runner_id != 0` and `steps > 0`;
- only the first real validator result may change the W2 entry decision.

## 6. W2 configuration — `3PC + MIP-I`

W2 is the correct next wave because the next problem is a bounded transaction,
not another refresh.

Preferred atom: `COLD_COMPRESSOR_TRAIN`.  
Fallback atom: the already source-bound ALAT `HP_COMPRESSOR`.

### P1 — Prepare

Bind one atom with:

- exact source identity and SHA;
- OFFER / QPS item identifiers where applicable;
- child locator and primary TRIAGE lane;
- tooling/profile/consumer version;
- unit/reference-period basis;
- architecture state: redundancy, common cause, preserved/degraded state,
  recovery duration;
- artifact/receipt/hash intent;
- explicit operating-state exposure fields.

### P2 — Prove

Run one deterministic consumer path and prove:

- exact-source preservation;
- upstream disposition preservation;
- fail-closed system consequence;
- exact-SHA runtime receipt;
- independent H2 semantic/provenance check;
- independent H3 executable/result check.

### P3 — Commit

Commit only a bounded child result: `ACCEPT`, `DEFER`, or `HOLD` under child
authority. Tooling cannot self-promote an atom to engineering acceptance.

### MIP-I — Innovate, only if justified

The only currently admitted innovation is a **shared operating-state/evidence
ledger adapter** if W2 proves duplicated or drifting state/exposure fields across
H1/H2/H3/tooling consumers. It is not a new reliability engine and not a new
provenance framework.

W2 entry condition remains one intended child exact-head validation with
`EX > 0` and durable KR, or an explicit bounded waiver that preserves the same
proof obligation.

## 7. W3 configuration — `3P3 + MIP-P`

W3 is not a fleet fan-out. It is one bounded propagation/generalisation proof
after W2 local DoV.

Propagation order:

1. `GBOGEB/CODEX` consumes the semantic/provenance contract without changing it;
2. `GBOGEB/ABACUS` independently consumes the executable/measurement contract;
3. Mission Control consumes the returned receipts and routes one child re-entry
   result without authority transfer.

Stop after one successful generalisation class.

### MIP-P — Perpetuate

Persist only what W1/W2/W3 prove useful:

- exact-SHA receipt pattern;
- restart/handover pointer;
- first-red classification;
- recurrence/REX rule;
- stop/re-entry predicates;
- selective pruning/no-growth guard.

Do not institutionalize unused dashboards, telemetry services, PCA layers or
frameworks merely because infrastructure exists.

## 8. Mission Control and adjacent missions

Primary horizontal: `H4_QPS_TRIAGE`.

Supporting horizontals:

- H1_QPS — child source, consequence, architecture and final engineering
  disposition only;
- H2_KEB — semantics, provenance and state-separation challenge only;
- H3_DOW — executable proof, denominators, independent calculation and delivery
  QA only;
- H4_QPS_TRIAGE — veto, BT/resource pressure, receipt/pointer, STOP/restart and
  false-promotion prevention.

Relevant global mission reuse:

- provenance/attestation patterns: reuse exact source/artifact/receipt semantics;
- MCP/control missions: reuse bounded recurrence and selective pruning;
- cryogenic analytical kernels: separate valid math from stale/project-source
  promotion;
- observed BT: use reverse pressure for scheduling only, never engineering truth;
- licensed Windows/Excel/HEPAK capacity: keep resource-separate from H4.

Parallel, non-compensating fronts remain separate: G6 release identity, visual
N200, OFFER workbook delta, W152 evidence return, and the repo-local runner
admission blocker.

## 9. Sub-chat / session topology

### QRT-A — Applicability control / runtime gate

Owner: H4 + H1.  
State: **ACTIVE but blocked on repository-local Actions admission**.  
Goal: obtain one real exact-head validator/test/receipt execution and make the W2
entry decision.

### QRT-B — Evidence burn-down

Owner: H1.  
State: **parallel preparation allowed, no promotion**.  
Goal: source/architecture census for the W2 preferred cold-compressor-train atom,
including exact source, unit basis, redundancy/common-cause/degraded-state/
recovery and RTM/DTM edges.

### QRT-C — W2 transaction / runtime proof

Owner: H3 with H2 support.  
State: **gated by W2 release**.  
Goal: execute Prepare -> Prove -> Commit and the ledger adapter only if evidence
shows duplicated state fields.

### QRT-D — Presentation reuse

Owner: tooling/presentation.  
State: **parked**.  
Goal: return only controlled outputs to DOCX/XLSX/PPTX/HTML after the model and
authority contract are stable. OFFER workbook logic remains a separate locked
method and must not be rewritten by the reliability work.

### Control sessions

- `S-H4`: portfolio roll-up, mission pointers, receipts, resource reallocation,
  STOP/restart decisions;
- `S-H1`: source/consequence/architecture/Table-10 engineering re-entry;
- `S-H2`: semantic/provenance challenge;
- `S-H3`: executable proof/metrics/independent calculations.

## 10. Next goals and DoD

Immediate P0 is not another QPS method improvement. It is the repository-local
runtime admission defect. Restore admission or runner attachment and rerun the
same child applicability workflow.

When `runner_id != 0` and `steps > 0`:

1. consume the first real validator result;
2. if green and receipt-complete, release W2 from HOLD;
3. execute one cold-compressor `3PC` transaction;
4. admit MIP-I only if measured duplication/drift exists;
5. after local W2 DoV, execute one 3P3 propagation proof;
6. burn restart/REX/STOP controls with MIP-P;
7. move the stable component from IMPROVE to CONTROL.

Global DoD is reached when the child authority, tooling projection, semantic
consumer, independent runtime consumer and Mission Control all reproduce the
same bounded transaction and authority boundary from exact identities, with no
unresolved first-red hidden by another framework layer.
