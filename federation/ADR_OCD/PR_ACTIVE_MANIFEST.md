# ADR_OCD Active PR Manifest

Status: **READY_TO_EDIT candidate — current-head runtime verification pending**

## Active PR

- Number: **43**
- Title: **QPS triage: Wave 9 external CI artifact registry receipt**
- Repository: `GBOGEB/DOCX_RTM_Automation`
- Branch: `feature/qps-triage-wave9-ci-registry-receipt`
- Base: `main`
- State: open; review/edit candidate
- Predecessor: PR #42, Wave 8 exact-SHA evidence governance, merged

## Purpose

Provide an editable, evidence-governed QPS Requirements pipeline in which parser-derived RTM/DTM and dashboard outputs are bound to exact source SHA and workflow identity, cryptographically inventoried, independently verified, uploaded to CI, and finally bound to the external GitHub Actions artifact object through a terminal registry receipt.

## Current architecture

`QPS parser -> triage enrichment -> persistent RTM/DTM exports -> QPS dashboard -> canonical dashboard -> evidence manifest -> governed receipt -> SHA256SUMS -> CI artifact -> provider artifact ID/URL/SHA256 -> CI registry receipt`

## Controlled terminology

- Preferred outward-facing term: **QPS Requirements**
- Internal legacy alias: **RFO**
- Procurement package/procedure: **Invitation to Tender**
- Applicant commercial response: **Fixed Price Offer**
- Formal amendment/correction: **Corrigendum**
- Intermediate rounds: **Negotiation Stage**
- ADR/OCD authority remains under `federation/ADR_OCD/`

## Implemented surfaces

### Governance and taxonomy
- `glossary/GLOSSARY.yaml`
- `federation/ADR_OCD/README.md`
- `federation/ADR_OCD/bridge_manifest.yaml`
- `federation/ADR_OCD/taxonomy.yaml`
- `federation/ADR_OCD/qps_triage_applicability.yaml`
- schemas and focused bridge validator/tests

### Parser and traceability
- `configs/qps_triage_parser_config.yaml`
- `parser/qps_triage_bridge.py`
- `parser/engine.py`
- QPS triage items
- flat traceability rows
- persistent RTM and DTM export rows
- downstream index

### Reporting
- `src/dashboard/qps_triage_dashboard.py`
- QPS triage JSON/Markdown/HTML outputs
- `src/dashboard/canonical_dashboard.py`
- canonical dashboard QPS triage index

### Orchestration and evidence
- `scripts/run_qps_triage_pipeline.py`
- `scripts/verify_qps_triage_receipt.py`
- `qps_triage_pipeline_manifest.json`
- `qps_triage_evidence_manifest.json`
- `qps_triage_governed_receipt.json`
- `SHA256SUMS`

### External artifact registry
- `scripts/create_qps_triage_ci_registry_receipt.py`
- `qps_triage_ci_registry_receipt.json`
- provider artifact ID/name/URL/SHA256 binding
- separate Wave 9 registry-receipt CI artifact

## Wave status

| Wave | Scope | State |
|---|---|---|
| 0 | Governance bridge bootstrap | COMPLETE |
| 1 | Schema validation and tests | COMPLETE |
| 2 | Parser taxonomy/config + triage emission | COMPLETE |
| 3 | Traceability export rows | COMPLETE |
| 4 | Engine integration + persistence/downstream index | COMPLETE |
| 5 | QPS triage report generation | COMPLETE |
| 6 | Canonical dashboard link | COMPLETE |
| 7 | One-command pipeline + CI archive | COMPLETE; superseded by governed Wave 8 pipeline |
| 8 | Exact-SHA SHA256 evidence governance + verifier | COMPLETE; merged PR #42 |
| 9 | External CI artifact registry receipt | IMPLEMENTED; current-head runtime gate pending |

## Observed Wave 9 diagnostic

The first PR #43 focused run demonstrated:

- bridge validation PASS
- focused tests PASS
- Wave 8 pipeline PASS
- Wave 8 hash/parity verifier PASS
- Wave 8 artifact upload PASS
- provider artifact ID/URL/digest observed
- Wave 9 registry receipt creation FAIL only on digest representation

Observed provider output used raw 64-character hexadecimal SHA256. The initial registry script accepted only `sha256:<64-hex>`. The implementation now accepts either form and normalizes to canonical `sha256:<64-hex>`. A regression test covers the observed raw upload-artifact representation.

## READY_TO_EDIT definition

The PR/handoff may be promoted from `READY_TO_EDIT candidate` to **READY_TO_EDIT** when the current head has all of:

1. Python CI PASS.
2. ADR_OCD Bridge Validation PASS.
3. Wave 8 governed pipeline fixture PASS.
4. Wave 8 receipt/hash/parity verification PASS.
5. Wave 8 evidence bundle upload PASS.
6. Wave 9 registry receipt creation PASS from actual provider outputs.
7. Wave 9 registry receipt upload PASS.
8. PR mergeable with no unresolved PR-induced failure.

This is a runtime evidence state, not a documentation assertion.

## Edit commands

Generate and verify the governed bundle:

```bash
python scripts/run_qps_triage_pipeline.py \
  --input-analysis tests/fixtures/qps_triage_pipeline_input.json \
  --output-dir .artifacts/qps-triage-wave8
python scripts/verify_qps_triage_receipt.py .artifacts/qps-triage-wave8
```

Run focused tests:

```bash
pytest -o addopts='' \
  tests/test_adr_ocd_bridge_validation.py \
  tests/test_qps_triage_bridge.py \
  tests/test_qps_triage_pipeline.py
```

## Next controlled edit after Wave 9

Consume the receipt rather than adding another parallel evidence layer. Preferred next increment: surface exact-SHA receipt/registry availability and ACCEPT/DEFER disposition in the canonical dashboard or release/contract-baseline manifest.

Engineering rule: **recurse on first red -> repair smallest causal defect -> rerun -> promote only from observed evidence.**
