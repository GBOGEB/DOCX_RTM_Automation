# TRIAGE Renegade Self-Repo Analysis — W01

Repository: `GBOGEB/DOCX_RTM_Automation`  
Observed head: `e693802ecf0882c4d576fcfb2356bc19aff80524`  
Authority: discovery / independent replication only  
Release credit: none until accepted by the applicable primary repo at an exact SHA.

## Why this repo matters

This repository is a parallel QPLANT requirements/RTM lineage with working generators, SoR extraction, rendered outputs, and an already implemented ADR/OCD federation bridge. It is therefore too substantive to ignore, but too duplicative to merge wholesale into ABACUS or cryoplant-project.

## Nuance worth preserving

1. `federation/ADR_OCD/**` already models an isolated bridge pattern with schema validation, taxonomy, changelog, handoff, and CI.
2. `scripts/generate_rtm.py` and related automation provide an independent RTM regeneration path that can be used as replication evidence against current ABACUS/QPS outputs.
3. `config/requirements.yml` carries an alternate QSYS/QPLANT/QINFRA/QCELL/QDIST hierarchy that is useful for lineage/diff analysis, not automatic authority.
4. SoR extraction and document-rendering paths can reveal requirements omitted or transformed by newer pipelines.

## Duplication / collision policy

- Do **not** copy the full RTM generator into ABACUS.
- Do **not** promote matching requirement rows merely because two pipelines agree.
- Compare outputs by requirement ID and retain only meaningful deltas: missing/extra requirement, taxonomy mismatch, provenance difference, parser behavior, or verification nuance.
- Treat the existing ADR/OCD bridge as an implementation pattern that may be federated, not as a new global architecture.

## Smoke targets

- `python scripts/validate_adr_ocd_bridge.py`
- `pytest tests/test_adr_ocd_bridge_validation.py`
- existing `python-ci.yml`
- existing `render_canonical.yml`

## Proposed route

`DOCX_RTM_Automation -> ABACUS` for requirements/traceability analysis.  
`DOCX_RTM_Automation -> cryoplant-project` only where a requirement or architecture delta is engineering-authoritative.  
`DOCX_RTM_Automation -> CODEX` only for bridge/federation contract patterns.

## Promotion gate

A candidate item is promotable only when it has: exact source SHA, reproducible smoke result, a unique-delta statement, target primary owner, explicit disposition, and no authority collision.
