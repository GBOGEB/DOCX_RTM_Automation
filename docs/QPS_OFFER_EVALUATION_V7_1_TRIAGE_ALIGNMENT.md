# QPS OFFER Evaluation v7.1 — TRIAGE alignment

## Purpose

Bind the locked v7.1 OFFER evaluation package into the QPS TRIAGE applicability
surface without changing the evaluation method and without transferring QPS
engineering authority.

This is a **controlled projection** only.

```text
OFFER-01..50 static/cold rank
        |
        v
procurement evaluation method
        |
        +--> bidder evidence extraction
        +--> A/B comparison
        +--> risk overlay
        |
        v
QPS TRIAGE applicability
        |
        +--> priority / evidence review
        +--> RTM/DTM traceability
        +--> ADR/OCD/reliability impacts
        |
        v
QPS child engineering re-entry when promotion is required
```

## Locked evaluation method

The following order is preserved and must not be restated as a new method:

1. static requirement ranking first;
2. bidder scoring second;
3. risk overlay third.

The production method is deterministic and idempotent. Schedule is a gate. Cost
is conditional on technical near-equivalence.

Frozen precedence:

1. legal gate;
2. functional non-negotiable;
3. reliability / 2 K continuity;
4. performance / heat-load match;
5. verifiability / FAT / SAT / QA;
6. lifecycle / maintainability;
7. cost.

## Authority boundary

The governing machine-readable profile is:

`configs/qps_offer_evaluation_v7_1.yaml`

The profile is procurement-facing metadata, not QPS engineering truth.

- static rank = procurement requirement importance;
- seeded bidder A/B values = `POSTULATED` until exact-source bidder evidence exists;
- risk = delivery-confidence modifier, not static importance;
- gate failure overrides score;
- OFFER tier metadata does not replace TRIAGE disposition, maturity, or child authority;
- Word/Excel/PPT binary identity remains `DEFER` until governed hash/receipt binding exists.

## QPS TRIAGE alignment

Primary lane remains `TRIAGE-QPS` for procurement-facing OFFER evidence.
Secondary impacts depend on content:

- reliability / recovery / spares -> `TRIAGE-RELIABILITY`, `TRIAGE-OCD`, `TRIAGE-RTM-DTM` as applicable;
- controls / architecture -> `TRIAGE-ADR`, `TRIAGE-OCD`, `TRIAGE-RTM-DTM`;
- FAT / SAT / QAP / standards -> `TRIAGE-RTM-DTM` with QPS child re-entry where engineering acceptance is implied.

Before bidder evidence is source-bound, the default handling is:

- tooling disposition: `NEEDS_SOURCE`;
- maturity: `0.3`;
- seeded values: `POSTULATED`;
- engineering promotion: forbidden.

## Priority relationship

The v7.1 static rank may be used as one procurement-priority signal inside the
TRIAGE workflow. It may not bypass the existing TRIAGE priority fields or control
gates.

The high-value evidence cluster is:

- `OFFER-11` MTBF / recovery / intervention philosophy;
- `OFFER-04` transient substantiation;
- `OFFER-21` LOOP strategy;
- `OFFER-22` helium recovery / S-line handling;
- `OFFER-28` functional analysis / control sequence;
- `OFFER-39` FAT / SAT method;
- `OFFER-20` leak / loss / monitoring;
- `OFFER-41/42/43` spares / service / maintenance context;
- `OFFER-46` execution-risk plan.

These items are prioritized because they influence procurement decision quality,
not because their position automatically grants engineering acceptance.

## Reliability consumer relation

The merged reliability consumer remains a bounded analytical consumer.

### OFFER-11

May supply MTBF / MTTR / recovery evidence only after exact source identity and
an admissible upstream TRIAGE disposition are present. Component MTBF shall not
be promoted into system-event MTBF, Table-10 consumption, N+1 proof, or QPS
engineering acceptance without the existing architecture/consequence gates.

### OFFER-21 / OFFER-22

Provide degraded-state, abnormal-recovery, inventory-protection and operational
recovery context. They do not independently establish a reliability rate.

### OFFER-41 / OFFER-42 / OFFER-43

Provide spares, service-resource and maintenance-duration context needed to make
MTTR / recovery claims operationally credible.

### OFFER-46

Provides execution-risk context. It must not overwrite the locked OFFER risk
formula or alter the static rank.

## Mission Control / method-selection alignment

The v7.1 evaluation projection follows the same bounded method applicability
contract introduced in QPS TRIAGE v0.3:

- `3PR` to refresh the actual state and first blocker;
- `MIP` only when an observed structural or recurrence gap warrants it;
- `3PC` only for a bounded transaction / re-entry;
- `3P3` only after local DoV when a reusable propagation proof is missing.

Mission Control may route, measure and recommend. `authority_transfer=false`
remains mandatory.

## DoV for this alignment

This PR may claim OFFER-v7.1 TRIAGE alignment only when:

1. `configs/qps_offer_evaluation_v7_1.yaml` remains present and method-locked;
2. seeded values remain explicitly non-authoritative;
3. TRIAGE dispositions / maturity remain separate from OFFER tiers;
4. reliability consumer boundaries remain fail-closed;
5. exact binary artifact binding remains `DEFER` until a governed receipt exists;
6. focused tests verify the projection contract.

No engineering, compliance, negotiation, acceptance, release, or Table-10 credit
is created by this alignment.
