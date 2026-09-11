# ADR_OCD Active PR Manifest

Status: **WAVE 11 ACTIVE — runtime verification pending**

## Active PR

- Number: **51**
- Title: **QPS triage: Wave 11 procurement release baseline gate**
- Repository: `GBOGEB/DOCX_RTM_Automation`
- Branch: `feature/qps-triage-wave11-release-baseline-gate`
- Base: `main`
- State: draft until current-head runtime gates pass
- Predecessor: PR #50, Wave 10 exact-SHA receipt consumption, merged as `2c9b0630d7ed272775111129ca52cd3979584fd8`

## Current architecture

`QPS parser -> triage -> RTM/DTM exports -> dashboards -> Wave 8 exact-SHA evidence -> Wave 9 external artifact receipt -> Wave 10 ACCEPT/DEFER -> Wave 11 PROMOTE/HOLD procurement baseline`

## Controlled procurement sequence

1. `publication_baseline`
2. `negotiation_stage_1`
3. `negotiation_stage_2`
4. `final_corrigendum`
5. `contract_baseline`

Wave 11 CI currently exercises `final_corrigendum` as the first concrete release-promotion boundary immediately before contract baseline.

## Wave status

| Wave | Scope | State |
|---|---|---|
| 0 | Governance bridge bootstrap | COMPLETE |
| 1 | Schema validation/tests | COMPLETE |
| 2 | Parser taxonomy/config + triage emission | COMPLETE |
| 3 | Traceability rows | COMPLETE |
| 4 | Engine integration + persistence | COMPLETE |
| 5 | QPS triage reports | COMPLETE |
| 6 | Canonical dashboard link | COMPLETE |
| 7 | One-command orchestration | COMPLETE; superseded by Wave 8 governed pipeline |
| 8 | Exact-SHA evidence governance | COMPLETE / runtime verified |
| 9 | External CI artifact registry receipt | COMPLETE / runtime verified |
| 10 | Registry receipt consumption to ACCEPT/DEFER | COMPLETE / runtime verified / merged PR #50 |
| 11 | Procurement release baseline PROMOTE/HOLD gate | IMPLEMENTED / runtime verification pending |

## Wave 11 implementation

- `scripts/build_qps_release_baseline.py`
- `tests/test_qps_release_baseline.py`
- `configs/qps_triage_parser_config.yaml` v0.8.0
- focused CI step `Promote Wave 11 procurement release baseline`
- CI output `qps_release_baseline_manifest.json`
- CI artifact `qps-triage-wave11-release-${exact_head_sha}`

Decision rule:

- **PROMOTE** = exact SHA matches and Wave 10 evidence disposition is `ACCEPT`.
- **HOLD** = Wave 10 evidence is `DEFER` or exact SHA mismatches.

## BD / TODO register

| Rank | Item | State | Blocker | Next action |
|---:|---|---|---|---|
| 1 | Wave 11 current-head runtime DoV | ACTIVE | CI queued/running | First red -> smallest repair; if green promote + merge PR #51 |
| 2 | Contract-baseline promotion after final Corrigendum | TODO | Wave 11 must prove release gate first | Reuse same manifest producer with `contract_baseline`; do not duplicate evidence stack |
| 3 | Real QPS/ADR/OCD source fixture instead of synthetic fixture | TODO | authoritative source binding not yet in this lane | Bind source document/version/SHA and run same pipeline |
| 4 | Negotiation-stage state transition history | TODO | no persistent stage-transition ledger yet | Add append-only transition/event rows after release gate stabilizes |
| 5 | Corrigendum impact completeness across QPS -> ADR -> OCD -> RTM -> DTM | TODO | current trace rows demonstrate path but not full production corpus | Measure denominator, missing edges, and DEFER reasons on real corpus |

## BT pressure

Reverse-pressure ranking from terminal contract usability:

`contract baseline`
<- requires `final Corrigendum PROMOTE`
<- requires Wave 10 `ACCEPT`
<- requires Wave 9 provider-bound registry receipt
<- requires Wave 8 exact-SHA governed evidence
<- requires parser/RTM/DTM/dashboard generation

Current dominant bottleneck is therefore **Wave 11 runtime promotion**, not more schema/evidence infrastructure.

Priority pressure:

1. **Close Wave 11** — highest downstream leverage, lowest ambiguity.
2. **Reuse Wave 11 for contract_baseline** — very low incremental effort after green final-Corrigendum gate.
3. **Replace synthetic fixture with real controlled QPS source** — largest DoV quality increase.
4. **Measure full-corpus missing-edge / DEFER distribution** — next PCA/BT input.
5. **Only then add stage-history/dashboard embellishment.**

## Closure rule

If PR #51 exact head shows Python CI PASS and ADR_OCD Bridge Validation PASS including Wave 11 `--require-promote` and artifact upload, mark ready and merge. If red, stop expansion and repair the first causal red only.
