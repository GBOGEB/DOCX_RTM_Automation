# QPS TRIAGE v0.3.1 — reliability cross-cut fix

## Why this fix exists

The W1 deep-dive found a semantic conflict after applicability v0.3 merged: tooling introduced `TRIAGE-RELIABILITY` as a fifth triage lane, while the child-authority control and global roll-up require reliability to remain a cross-cutting analytical profile over the four canonical lanes.

This fix resolves that conflict without changing the reliability model, OFFER v7.1 method, Mission Control method selector, or QPS engineering authority.

## Canonical lane model

Exactly four primary triage lanes remain:

- `TRIAGE-QPS`
- `TRIAGE-ADR`
- `TRIAGE-OCD`
- `TRIAGE-RTM-DTM`

Reliability is a topic/profile, not a fifth primary lane.

## Reliability cross-cut mapping

- contractual reliability obligation -> `TRIAGE-QPS`
- redundancy/common-cause/architecture consequence -> `TRIAGE-ADR`
- degraded/recovery/maintenance operational state -> `TRIAGE-OCD`
- source/evidence/RTM/DTM lineage -> `TRIAGE-RTM-DTM`

The bounded reliability consumer remains valid and may derive MTBF/lambda/exposure/Poisson diagnostics, but its model state (`ACTIVE`, `SCENARIO_ONLY`, `EXCLUDED`) is not a triage disposition and not an engineering disposition.

## W1 / MIP-Modernize effect

This is the structural repair identified by `H4_QPS_TRIAGE:W1`.

- Modernize: remove fifth-lane conflict and encode cross-cut profile.
- Innovate: none yet; do not add new adapter abstractions until W2 proves a repeated field-mapping need.
- Perpetuate: new control gate `QPS-TRIAGE-GATE-012` and tests prevent reintroduction of `TRIAGE-RELIABILITY` as a primary lane.

## Authority boundary

No engineering/compliance/negotiation/acceptance/release/Table-10/award credit is created.

`GBOGEB/cryoplant-project` remains QPS engineering authority. Mission Control retains `authority_transfer=false`.

## Next gate

Run exact-head tests for this branch. If green, W1 can close its applicability first-red and W2 may enter bounded `3PC + MIP-I` planning. W2 should use one real source-bound OFFER/reliability transaction and should not ingest the full OFFER-01..50 corpus at once.
