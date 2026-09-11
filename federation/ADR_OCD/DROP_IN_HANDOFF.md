# ADR_OCD Drop-In Engineering Handoff

Status: **READY_TO_EDIT candidate — Wave 9 runtime gate pending current-head CI**

Use this text at the start of the next engineering, coding, review, or chat-agent session.

---

You are continuing work on `GBOGEB/DOCX_RTM_Automation`.

Active implementation is PR **#43**, branch `feature/qps-triage-wave9-ci-registry-receipt`, based on `main` after merged Wave 8 PR #42.

## Objective

Keep ADR and OCD inside `DOCX_RTM_Automation` while providing a governed QPS Requirements pipeline from parser output through RTM/DTM traceability, dashboards, exact-SHA evidence receipts, and externally registered CI artifacts.

## Terminology controls

1. Use **QPS Requirements** as the preferred outward-facing term for procurement-facing technical requirements used by Applicants to prepare a Fixed Price Offer.
2. Treat **RFO** as an internal legacy alias only.
3. Use **Invitation to Tender** only for the procurement package or procedure.
4. Use **Corrigendum** for formal amendments/corrections after publication.
5. Use **Negotiation Stage** for intermediate procurement alignment rounds.
6. Reuse `glossary/GLOSSARY.yaml` before inventing new terms.

## Implemented waves

- Wave 0 — ADR/OCD governance bridge: COMPLETE.
- Wave 1 — schema validation and focused tests: COMPLETE.
- Wave 2 — parser taxonomy/config wiring and triage-item emission: COMPLETE.
- Wave 3 — QPS triage traceability rows: COMPLETE.
- Wave 4 — parser-engine integration plus persistent RTM/DTM exports: COMPLETE.
- Wave 5 — QPS triage JSON/Markdown/HTML report generation: COMPLETE.
- Wave 6 — canonical dashboard link: COMPLETE.
- Wave 7 — one-command parser -> export -> QPS dashboard -> canonical dashboard pipeline plus CI archive: COMPLETE/SUPERSEDED by governed pipeline.
- Wave 8 — SHA256 evidence governance, exact source SHA/run identity, parity verifier, governed receipt, `SHA256SUMS`: COMPLETE and merged in PR #42.
- Wave 9 — bind the Wave 8 governed bundle to the actual GitHub Actions artifact object and provider digest: IMPLEMENTED; current-head runtime verification is the remaining gate.

## Current one-command pipeline

```bash
python scripts/run_qps_triage_pipeline.py \
  --input-analysis tests/fixtures/qps_triage_pipeline_input.json \
  --output-dir .artifacts/qps-triage-wave8

python scripts/verify_qps_triage_receipt.py \
  .artifacts/qps-triage-wave8
```

The Wave 8 bundle contains parser/export outputs, QPS triage dashboard artifacts, canonical dashboard JSON, evidence manifest, governed receipt, and `SHA256SUMS`.

## Wave 9 terminal registry receipt

After `actions/upload-artifact@v4` uploads the Wave 8 bundle, CI passes the observed provider values to:

```bash
python scripts/create_qps_triage_ci_registry_receipt.py \
  .artifacts/qps-triage-wave8 \
  --artifact-id <provider-artifact-id> \
  --artifact-url <provider-artifact-url> \
  --artifact-digest <provider-sha256> \
  --artifact-name <artifact-name> \
  --output .artifacts/qps-triage-wave9/qps_triage_ci_registry_receipt.json
```

The receipt normalizes both raw 64-hex `actions/upload-artifact` digest output and `sha256:<64-hex>` REST-style representation to canonical `sha256:<64-hex>`.

## Evidence chain

`exact source SHA -> parser/export -> dashboard -> Wave 8 evidence manifest -> governed receipt -> SHA256SUMS -> verified Wave 8 CI bundle -> provider artifact ID/URL/SHA256 -> Wave 9 registry receipt -> registry receipt CI artifact`

Important distinction:

- `git_sha` = exact source/head SHA being evidenced.
- `checkout_sha` = GitHub pull-request merge checkout SHA when CI runs on a PR merge ref.

Do not substitute one for the other.

## Current runtime evidence

Wave 8 PR #42 passed Python CI and ADR_OCD Bridge Validation and was merged. Its focused workflow executed the parser pipeline, independent hash/parity verifier, and artifact upload successfully.

For Wave 9 PR #43, the first observed run passed all Wave 8 stages and uploaded the Wave 8 bundle, then failed only because `actions/upload-artifact@v4` returned its `artifact-digest` as raw 64-hex while the first registry-receipt implementation required a `sha256:` prefix. That format mismatch has been repaired and regression coverage added.

## READY_TO_EDIT gate

Promote this handoff/PR to **READY_TO_EDIT** only when the current PR head demonstrates:

1. Python CI PASS.
2. ADR_OCD Bridge Validation PASS.
3. Wave 8 pipeline PASS.
4. Wave 8 independent hash/parity verification PASS.
5. Wave 8 artifact upload PASS.
6. Wave 9 registry receipt creation PASS using provider-returned ID, URL, and digest.
7. Wave 9 registry receipt artifact upload PASS.
8. PR remains mergeable and no unresolved PR-induced red gate exists.

Until those are observed on the current head, use `READY_TO_EDIT candidate`, not a false completed claim.

## Files central to continuation

- `glossary/GLOSSARY.yaml`
- `federation/ADR_OCD/bridge_manifest.yaml`
- `federation/ADR_OCD/taxonomy.yaml`
- `federation/ADR_OCD/qps_triage_applicability.yaml`
- `configs/qps_triage_parser_config.yaml`
- `parser/qps_triage_bridge.py`
- `parser/engine.py`
- `scripts/run_qps_triage_pipeline.py`
- `scripts/verify_qps_triage_receipt.py`
- `scripts/create_qps_triage_ci_registry_receipt.py`
- `src/dashboard/qps_triage_dashboard.py`
- `src/dashboard/canonical_dashboard.py`
- `tests/test_qps_triage_bridge.py`
- `tests/test_qps_triage_pipeline.py`
- `.github/workflows/adr_ocd_bridge_validation.yml`

## Next edit surface after Wave 9 closes

Do not add another evidence framework layer merely because Wave 9 exists. The next useful edit should consume the governed receipt: expose receipt/registry status in the canonical dashboard and/or release/contract-baseline manifest, with explicit ACCEPT / DEFER when an exact-SHA receipt is present/missing.

Engineering rule: recurse on the first observed red gate; repair the smallest causal defect; rerun; promote only from observed evidence.

---
