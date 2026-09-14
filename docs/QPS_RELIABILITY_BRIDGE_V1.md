# QPS Reliability Bridge v1 — narrow pilot

## Purpose

Prove one governed path from QPS triage evidence to reliability analysis without importing the full negotiation corpus and without transferring engineering/compliance authority to the dashboard.

```text
QPS source / triage
        |
        v
exact-source identity + ACCEPT/DEFER
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
- `qps_item_id` where source-bound
- `origin`: `SOURCE_BOUND`, `SCENARIO`, or `USER_OVERRIDE`
- `evidence_disposition`: `ACCEPT` or `DEFER`
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

Five gates are emitted per item:

- source identity
- evidence ACCEPT (required for source-bound activation)
- unit/reference-period definition
- architecture completeness
- deterministic model consistency

Disposition:

- `ACTIVE`: all five gates pass
- `SCENARIO_ONLY`: model is calculable but one or more governance/architecture gates prevent governed activation
- `EXCLUDED`: invalid pilot component, invalid/missing unit basis, or inconsistent/missing reliability values

Incomplete architecture forces `component_only`; the bridge does not infer system reliability from component quantity alone.

## Authority boundary

This module is an **analysis consumer**. It does not:

- convert source coverage into compliance credit;
- promote DEFER evidence to ACCEPT;
- infer N+1 from installed quantity;
- infer common-cause independence;
- establish procurement or engineering truth.

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
2. one source-bound reliability atom is exact-SHA and ACCEPT-bound;
3. MTBF/lambda conversions reproduce deterministically;
4. P(0), P(>=1), and Poisson counts reproduce deterministically;
5. provenance survives output unchanged;
6. no authority promotion occurs;
7. canonical dashboard can consume the bridge summary.

Only after v1 DoV should the pilot expand to additional QPS triage rows or bidder-return/minute-resolution evidence.
