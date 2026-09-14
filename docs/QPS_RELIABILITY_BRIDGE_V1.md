# QPS Reliability Bridge v1 — narrow pilot

## Purpose

Prove one governed path from QPS Triage evidence to reliability analysis without importing the full negotiation corpus and without transferring engineering/compliance authority to the dashboard.

```text
QPS source / Triage
        |
        v
exact-source identity + canonical Triage disposition/lane/maturity
        |
        v
reliability bridge
        |
        +--> MTBF years + hours
        +--> lambda / year + / hour
        +--> campaign P(0) / P(>=1)
        +--> Poisson count distribution
        +--> provenance + readiness
        |
        v
canonical/dashboard consumer
```

The controlling Triage vocabulary is the contract in
`federation/ADR_OCD/qps_triage_applicability.yaml`: `ACCEPT`, `DEFER`, `REJECT`,
`NEEDS_SOURCE`, `NEEDS_IMPLEMENTATION`, and `NEEDS_REVIEW`, with one primary
Triage lane and a maturity level. Procurement OFFER tiers and seeded bidder
values do not replace those states.

## Pilot scope

Exactly five component classes are admitted in v1:

1. `HP_COMPRESSOR`
2. `PVPS`
3. `COLD_COMPRESSOR_TRAIN`
4. `TURBINE_EXPANDER`
5. `QPLANT_CLASS_A_SYSTEM`

The bridge intentionally does **not** ingest the full QPS agenda. Expansion follows only after this path has runtime evidence.

## Input contract

Input JSON contains an `items` array. Each item declares:

- `component`
- `triage_item_id` where source-bound (`qps_item_id` remains a compatibility alias)
- `triage_lane` and `maturity_level` where source-bound
- `origin`: `SOURCE_BOUND`, `SCENARIO`, or `USER_OVERRIDE`
- `triage_disposition`: one canonical QPS Triage disposition (`evidence_disposition` remains a compatibility alias)
- `source_git_sha` and `source_ref` where source-bound
- `reference_period`: `calendar_year`, `operating_hours_year`, or `custom_operating_hours`
- at least one of `mtbf_years`, `mtbf_hours`, `lambda_per_year`
- architecture evidence: redundancy basis, common-cause basis, degraded state, recovery hours

Multiple supplied reliability values must agree after deterministic conversion or the item is excluded.

## Model contract

The bridge uses `1 year = 8760 h` for display/unit conversion and derives:

- `lambda_per_year = 1 / mtbf_years`
- `lambda_per_hour = 1 / mtbf_hours`
- `mu = lambda_per_year * campaign_years`
- `P(0) = exp(-mu)`
- `P(>=1) = 1 - P(0)`
- `P(k) = exp(-mu) * mu^k / k!`

This is an exponential/Poisson analysis model. It must not be presented as demonstrated component physics unless the upstream evidence supports that modelling assumption.

## Readiness / stop gates

Six gates are emitted per item:

- source identity
- upstream Triage `ACCEPT` for source-bound activation
- Triage lane + maturity context
- unit/reference-period definition
- architecture completeness
- deterministic model consistency

Disposition:

- `ACTIVE`: source-bound item only; all six gates pass
- `SCENARIO_ONLY`: model is calculable but source/Triage/architecture gates prevent governed activation, or the origin is `SCENARIO` / `USER_OVERRIDE`
- `EXCLUDED`: rejected Triage item, invalid pilot component, invalid/missing unit basis, or inconsistent/missing reliability values

A non-source-bound scenario is therefore never `ACTIVE`, even if numerically complete. This protects the v7.1 locked-delta rule that seeded/postulated bidder values are analysis inputs, not evidence or engineering truth.

Incomplete architecture forces `component_only`; the bridge does not infer system reliability from component quantity alone.

## First real controlled atom — ALAT HP compressor

The pilot binds the child-authoritative record:

`GBOGEB/cryoplant-project:ocd-adr/20_canonical/analysis/QPS_HP_COMPRESSOR_ALAT_EVIDENCE_v0.1.yaml@63121ad911b65869783adfbd50e10b2703f6eb8e`

Bound reliability value:

- applicant: ALAT
- selected model: KAESER FSD 475 SFC
- component MTBF: `333450 h`
- total MTTR: `78 h`
- source locator: `C1462-TN-001 page 51`
- Triage lane: `TRIAGE-QPS`
- Triage maturity: `0.8` (`traceable`)
- Triage disposition: `DEFER`

The source keeps selected-design N-1 capacity, preserved state, common-cause consequence and acceptance trace open and prohibits converting the component MTBF into a Table-10 service-event rate. The bridge therefore emits `SCENARIO_ONLY` + `component_only`, not `ACTIVE` system reliability. This is the intended fail-closed result.

Fixture: `tests/fixtures/qps_reliability_alat_hp_bound.json`.

## OFFER v7.1 alignment

`configs/qps_offer_evaluation_v7_1.yaml` is a procurement-evaluation projection only. Its static order is locked to the canonical v7.1 narrative, while reliability candidates such as OFFER-11, OFFER-20, OFFER-21, OFFER-22 and OFFER-41..43 are routed into QPS Triage without converting rank, score, risk, or seeded bidder values into engineering acceptance.

The current Excel review candidate is named in the profile for traceability but remains `DEFER` until a governed exact-binary receipt exists.

## Authority boundary

This module is an **analysis consumer**. It does not:

- convert source coverage into compliance credit;
- promote any Triage disposition;
- infer N+1 from installed quantity;
- infer common-cause independence;
- establish procurement or engineering truth;
- treat seeded bidder values, static rank, PCA, or reverse-pressure outputs as evidence.

Upstream QPS governance remains authoritative.

## Execution

```bash
python src/dashboard/qps_reliability_bridge.py \
  --input path/to/qps_reliability_input.json \
  --output .artifacts/qps-reliability/qps_reliability_bridge.json \
  --campaign-days 90
```

## v1 DoV

1. focused tests pass;
2. one real source-bound reliability atom is exact-SHA bound and preserves its upstream Triage disposition without promotion;
3. all canonical Triage dispositions fail closed as defined;
4. non-source-bound scenarios cannot become `ACTIVE`;
5. MTBF/lambda conversions reproduce deterministically;
6. P(0), P(>=1), and Poisson counts reproduce deterministically;
7. provenance including Triage lane/maturity survives output;
8. no authority promotion occurs;
9. canonical dashboard can consume the bridge summary.

`ACTIVE` source-bound system-model promotion remains a separate gate: it requires upstream `ACCEPT`, valid Triage context, exact source identity, complete architecture evidence, valid units/reference period, and deterministic model consistency. The ALAT HP atom deliberately does not satisfy that gate yet.
